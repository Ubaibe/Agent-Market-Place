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

if "contracts" not in st.session_state:
    st.session_state.contracts = ContractUtils()
    st.session_state.storage = StorageUtils()
    st.session_state.registered_agents = []
    st.session_state.my_tasks = []

contracts = st.session_state.contracts
storage = st.session_state.storage

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Register Agent",
    "🛍️ Hire an Agent",
    "✨ Features",
    "🧠 Agent Memories",
    "📊 Dashboard"
])

# ====================== REGISTER AGENT (Improved Logic) ======================
with tab1:
    st.subheader("Register Your Autonomous Agent")
    st.write("Create a new agent on the 0G Chain."
             "\nAll fields are required")
    col1, col2 = st.columns([1, 1])
    with col1:
        name = st.text_input("Agent Name", placeholder="Name", key="agent_name")
        reward = st.number_input(
            "Price (OG)",
            min_value=0.05,
            value=0.05,
            step=0.02,
            key="Price"
        )
    with col2:
        desc = st.text_area("Agent Description", placeholder="Brief overview of your Agent", height=100, key="agent_desc")
        task_desc = st.text_area(
            "Task Description",
            placeholder="E.g., Optimize my portfolio for maximum yield...",
            key="Register_task_desc"  # Unique key
        )

    if st.button("🚀 Register Agent on 0G Chain", type="primary"):
        if not name.strip() or not desc.strip() or not task_desc.strip():
            st.warning("Please fill all fields: Agent Name, Description and Task Description")
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
                        "default_reward": float(reward),
                        "default_task_desc": task_desc.strip(),
                        "features": [],
                        "reputation": 0,
                        "owner": "You"
                    })

                    marketplace = contracts.get_marketplace_contract()
                    value_wei = int(reward * 10 ** 18)
                    tx_function = marketplace.functions.createTask(agent_id, task_desc.strip(), value_wei)
                    _, tx_hash = contracts.send_transaction_with_value(tx_function, value_wei)

                    st.success(f"✅ Initial task created with reward of **{reward} OG**!")

                    st.session_state.my_tasks.append({
                        "id": len(st.session_state.my_tasks) + 1,
                        "agentId": agent_id,
                        "agentName": name.strip(),
                        "description": task_desc.strip(),
                        "reward": value_wei,
                        "completed": False,
                        "timestamp": "Just now"
                    })

                except Exception as e:
                    error_str = str(e).lower()
                    if "you already have an agent with this name" in error_str or "nameused" in error_str:
                        st.error(f"❌ You already have an agent named **{name}** on this wallet.")
                        st.info("Please choose a different name for this new agent.")
                    else:
                        st.error(f"Registration failed: {str(e)}")

# ====================== MARKETPLACE ======================
with tab2:
    st.subheader("🛍️ Hire an Agent")
    st.write("Browse and hire autonomous agents to perform tasks for you")

    if not st.session_state.registered_agents:
        st.info("No agents registered yet. Go to Register Agent tab.")
    else:
        for idx, agent in enumerate(st.session_state.registered_agents):
            st.markdown(f"""
                            <div class="market-card">
                                <div class="agent-name">#{agent['id']} — {agent['name']}</div>
                            </div>
                            """, unsafe_allow_html=True)
            st.write(f"**What this agent does:** {agent['default_task_desc']}")
            st.write(f"**Price:** {agent['default_reward']:.2f} OG")

            # Display Features (updated from Features tab)
            if agent.get("features"):
                st.write("**Features:**")
                for feature in agent["features"]:
                    st.markdown(f'<span class="feature-tag">{feature}</span>', unsafe_allow_html=True)
            else:
                st.write("**Additional Features:** None yet")

                # Simple Hire Button
                if st.button(f"💰 Hire This Agent (Pay {agent['default_reward']:.2f} OG)",
                             type="primary",
                             key=f"hire_btn_{agent['id']}"):

                    with st.spinner("Creating task on-chain using default settings..."):
                        try:
                            marketplace = contracts.get_marketplace_contract()
                            value_wei = int(agent['default_reward'] * 10 ** 18)

                            tx_function = marketplace.functions.createTask(
                                agent['id'],
                                agent['default_task_desc'],
                                value_wei
                            )
                            _, tx_hash = contracts.send_transaction_with_value(tx_function, value_wei)

                            st.success(f"✅ Successfully hired **{agent['name']}** with default task & reward!")

                            st.session_state.my_tasks.append({
                                "id": len(st.session_state.my_tasks) + 1,
                                "agentId": agent['id'],
                                "agentName": agent['name'],
                                "description": agent['default_task_desc'],
                                "reward": value_wei,
                                "completed": False,
                                "timestamp": "Just now"
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Transaction failed: {str(e)}")

                st.divider()
# ====================== Features ======================
with tab3:
    st.subheader("✨ Add New Features / Capabilities to Registered Agents")

    if not st.session_state.registered_agents:
        st.info("No agents registered yet.")
    else:
        agent_options = [f"#{a['id']} — {a['name']}" for a in st.session_state.registered_agents]
        selected = st.selectbox("Select Agent to Enhance", range(len(agent_options)),
                                   format_func=lambda x: agent_options[x])
        selected_agent = st.session_state.registered_agents[selected]

        st.write(f"**Current Description:** {selected_agent['id']}— {selected_agent['name']}")

        new_feature = st.text_input("New Feature / Capability",
                                   placeholder="e.g. Supports flash loans, Real-time risk analysis, Multi-chain execution...")

        if st.button("➕ Add Feature to Agent", type="primary"):
            if new_feature.strip():
                if "features" not in selected_agent:
                    selected_agent["features"] = []
                selected_agent["features"].append(new_feature.strip())
                st.success(f"✅ Feature added to **{selected_agent['name']}**!")
                st.rerun()
            else:
                st.warning("Please enter a feature description")

        # Show current features
        if selected_agent.get("features"):
            st.write("**Current Features:**")
            for f in selected_agent["features"]:
                st.write(f"• {f}")
# Registered Agents Tab
# with tab5:
#     st.subheader("👥 Registered Agents & Reputation")
#     if st.button("🔄 Refresh"):
#         st.rerun()
#     for agent in st.session_state.registered_agents:
#         # Calculate reputation dynamically
#         completed = len(
#             [t for t in st.session_state.my_tasks if t.get("agentId") == agent["id"] and t.get("completed")])
#         agent["reputation"] = completed
#         with st.expander(f"#{agent['id']} - {agent['name']}"):
#             st.success(f"**Unique Agent ID:** #{agent['id']}")
#             st.caption(f"Owner: {agent['owner']}")
#             st.write(agent['description'])
#             st.metric("Reputation", f"{agent['reputation']} completed tasks", delta=None)

# ====================== AGENT MEMORY TAB ======================
with tab4:
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
with tab5:
    st.subheader("Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Agents", len(st.session_state.registered_agents))
    col2.metric("Total Tasks", len(st.session_state.my_tasks))
    col3.metric("Active Agents", len(st.session_state.registered_agents))
    col4.metric("Total Volume", "1.84k OG")

st.caption("AgentMart • 0G APAC Hackathon 2026")
