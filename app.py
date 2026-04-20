import streamlit as st
from contract_utils import ContractUtils
from storage_utils import StorageUtils

st.set_page_config(page_title="AgentMart", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for marketplace feel
st.markdown("""
    <style>
    .market-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    .agent-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e3a8a;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛒 AgentMart")
st.markdown("**Decentralized Agent-as-a-Service Marketplace on 0G**")
st.caption("Track 3: Agentic Economy & Autonomous Applications")

if "contracts" not in st.session_state:
    st.session_state.contracts = ContractUtils()
    st.session_state.storage = StorageUtils()
    st.session_state.registered_agents = []
    st.session_state.my_tasks = []

contracts = st.session_state.contracts
storage = st.session_state.storage

tab1, tab2, tab3, tab5, tab6, tab4 = st.tabs(
    ["🏠 Marketplace", "📋 My Tasks", "🤖 Register Agent", "👥 Registered Agents", "🧠 Agent Memory", "📊 Dashboard"])

# ====================== REGISTER AGENT (Improved Logic) ======================
with tab3:
    st.subheader("Register Your Autonomous Agent")
    col1, col2 = st.columns([1, 2])
    with col1:
        name = st.text_input("Agent Name", placeholder="YieldOptimizer-Pro or MemecoinSniper", key="agent_name")
    with col2:
        desc = st.text_area("Description", placeholder="I do yield farming / I trade memecoins...", height=100, key="agent_desc")

    if st.button("🚀 Register Agent on 0G Chain", type="primary"):
        if not name.strip() or not desc.strip():
            st.warning("Please fill both Agent Name and Description")
        else:
            with st.spinner("Checking name availability and minting Agent ID..."):
                try:
                    registry = contracts.get_registry_contract()

                    # Try to register
                    tx_function = registry.functions.registerAgent(name.strip(), desc.strip())
                    _, tx_hash = contracts.send_transaction(tx_function)
                    agent_id = registry.functions.getAgentId(
                        contracts.account.address).call()  # This returns count actually

                    st.success("🎉 Agent successfully registered on 0G!", icon="✅")
                    st.info(f"**Unique Agent ID:** #{agent_id}")
                    st.write(f"**Name:** {name.strip()}")

                    st.session_state.registered_agents.append({
                        "id": agent_id,
                        "name": name.strip(),
                        "description": desc.strip(),
                        "reputation": 0,
                        "owner": "You"
                    })

                except Exception as e:
                    error_str = str(e).lower()
                    if "you already have an agent with this name" in error_str or "nameused" in error_str:
                        st.error(f"❌ You already have an agent named **{name}** on this wallet.")
                        st.info("Please choose a different name for this new agent.")
                    else:
                        st.error(f"Registration failed: {str(e)}")

# ====================== MARKETPLACE ======================
with tab1:
    st.subheader("🛍️ Available Agents for Hire")
    st.write("Browse and hire autonomous agents to perform tasks for you")
    if not st.session_state.registered_agents:
        st.info("No agents registered yet. Go to Register Agent tab.")
    else:
        cols = st.columns(2)
        for idx, agent in enumerate(st.session_state.registered_agents):
            with cols[idx % 2]:
                st.markdown(f"""
                                <div class="market-card">
                                    <div class="agent-name">#{agent['id']} — {agent['name']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                st.write(agent['description'])


                col_price, col_action = st.columns([1, 2])
                with col_price:
                    reward = st.number_input(
                        "Reward (OG)",
                        min_value=0.01,
                        value=0.05,
                        step=0.01,
                        key=f"reward_{agent['id']}_{idx}"
                    )
                with col_action:
                    task_desc = st.text_input(
                        "Task Description",
                        placeholder="Optimize my portfolio for maximum yield...",
                        key=f"task_desc_{agent['id']}_{idx}"  # Unique key
                    )

                if st.button(f"Create Task & Pay {reward} OG", type="primary", key=f"create_btn_{agent['id']}_{idx}"):
                    if task_desc.strip():
                        with st.spinner("Creating task on-chain..."):
                            try:
                                marketplace = contracts.get_marketplace_contract()
                                value_wei = int(reward * 10 ** 18)
                                tx_function = marketplace.functions.createTask(agent['id'], task_desc.strip(),
                                                                               value_wei)
                                _, tx_hash = contracts.send_transaction_with_value(tx_function, value_wei)

                                st.success("✅ Task created successfully!")

                                st.session_state.my_tasks.append({
                                    "id": len(st.session_state.my_tasks) + 1,
                                    "agentId": agent['id'],
                                    "agentName": agent['name'],
                                    "description": task_desc.strip(),
                                    "reward": value_wei,
                                    "completed": False,
                                    "timestamp": "Just now"
                                })
                            except Exception as e:
                                st.error(f"Failed: {str(e)}")
                    else:
                        st.warning("Please enter a task description")

# ====================== MY TASKS ======================
with tab2:
    st.subheader("📋 My Tasks")
    if st.button("🔄 Refresh My Tasks", type="primary"):
        st.rerun()

    if st.session_state.my_tasks:
        st.success(f"You have {len(st.session_state.my_tasks)} task(s)")

        for task in reversed(st.session_state.my_tasks):
            status = "✅ Completed" if task["completed"] else "⏳ Active"
            color = "green" if task["completed"] else "orange"

            with st.expander(f"Task #{task['id']} — {status}"):
                st.write(f"**Agent:** {task.get('agentName', {task['agentId']})}")
                st.write(f"**Description:** {task['description']}")
                st.write(f"**Reward:** {task['reward'] / 10 ** 18:.4f} OG")

                # col1, col2 = st.columns(2)
                # with col1:
                #     if not task["completed"]:
                #         if st.button("Mark as Completed", key=f"complete_{task['id']}"):
                #             task["completed"] = True
                #             st.success("Task marked as completed!")
                #             st.rerun()
    else:
        st.info("No tasks created yet. Create some in the Marketplace tab.")

# Registered Agents Tab
with tab5:
    st.subheader("👥 Registered Agents & Reputation")
    if st.button("🔄 Refresh"):
        st.rerun()
    for agent in st.session_state.registered_agents:
        # Calculate reputation dynamically
        completed = len(
            [t for t in st.session_state.my_tasks if t.get("agentId") == agent["id"] and t.get("completed")])
        agent["reputation"] = completed
        with st.expander(f"#{agent['id']} - {agent['name']}"):
            st.success(f"**Unique Agent ID:** #{agent['id']}")
            st.caption(f"Owner: {agent['owner']}")
            st.write(agent['description'])
            st.metric("Reputation", f"{agent['reputation']} completed tasks", delta=None)

# ====================== AGENT MEMORY TAB ======================
with tab6:
    st.subheader("🧠 Agent Memory Vault")
    st.write("Persistent long-term memory for autonomous agents")

    if not st.session_state.registered_agents:
        st.info("No agents registered yet. Register some agents first.")
    else:
        # Agent selector
        agent_options = [f"#{a['id']} — {a['name']}" for a in st.session_state.registered_agents]
        selected = st.selectbox("Select Agent", agent_options)
        selected_agent = st.session_state.registered_agents[agent_options.index(selected)]
        agent_id = selected_agent["id"]

        # Add new memory
        st.write("### Add New Memory")
        memory_input = st.text_area(
            "What should this agent remember?",
            height=120,
            placeholder="User prefers low-risk yield strategies. Last successful APY was 7.8%. Avoid volatile memecoins..."
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("💾 Save Memory", type="primary"):
                if memory_input.strip():
                    success, msg = storage.save_agent_memory(agent_id, memory_input.strip())
                    if success:
                        st.success("✅ Memory saved persistently!")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter some memory content")

        # Display existing memories
        memories = storage.get_agent_memories(agent_id)
        if memories:
            st.write("### Memory History")
            for mem in reversed(memories):
                with st.expander(f"{mem['timestamp']}"):
                    st.write(mem['memory'])
        else:
            st.info("This agent has no memories yet.")

# Dashboard
with tab4:
    st.subheader("Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Agents", len(st.session_state.registered_agents))
    col2.metric("Total Tasks", len(st.session_state.my_tasks))
    col3.metric("Active Agents", len(st.session_state.registered_agents))
    col4.metric("Total Volume", "1.84k OG")

st.caption("AgentMart • 0G APAC Hackathon 2026 • Track 3")