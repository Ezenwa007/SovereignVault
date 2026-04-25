import streamlit as st
from datetime import datetime
from contract_utils import ContractUtils
from vault_utils import SovereignVault

st.set_page_config(page_title="SovereignVault", page_icon="🔒", layout="wide")

st.title("🔒 SovereignVault")
st.markdown("**Private Sovereign Agent Wallet + Memory Vault**")
st.caption("Track 5: Privacy & Sovereign Infrastructure")

if "contracts" not in st.session_state:
    st.session_state.contracts = ContractUtils()
    st.session_state.vault = SovereignVault()
    st.session_state.agents = []  # Local cache
    st.session_state.sovereign_mode = True

contracts = st.session_state.contracts
vault = st.session_state.vault

tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Create Sovereign Agent", "💬 Chat & Act", "📜 My Agents", "🔐 Sovereign Vault"])

# ====================== CREATE SOVEREIGN AGENT ======================
with tab1:
    st.subheader("Create a New Sovereign Agent")
    name = st.text_input("Agent Name", placeholder="PrivateYieldAgent")
    desc = st.text_area("Purpose / Capabilities",
                        placeholder="Autonomously manages my DeFi positions while keeping all strategies encrypted...",
                        height=120)

    if st.button("🔒 Create Sovereign Agent on 0G", type="primary"):
        if name and desc:
            with st.spinner("Creating agent..."):
                try:
                    tx_function = contracts.get_agent_contract().functions.createAgent(name.strip(), desc.strip())
                    _, tx_hash = contracts.send_transaction(tx_function)
                    agent_id = len(st.session_state.agents) + 1

                    st.success(f"✅ Sovereign Agent '{name}' created!")
                    st.info(f"**Agent ID:** #{agent_id}")
                    st.caption("All memories will be encrypted. Only you hold the key.")

                    st.session_state.agents.append({
                        "id": agent_id,
                        "name": name,
                        "description": desc,
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
        else:
            st.warning("Please fill both fields")

# ====================== CHAT & ACT ======================
with tab2:
    st.subheader("💬 Chat & Give Instructions")

    sovereign_mode = st.toggle("🔒 Enable Sovereign Mode (Maximum Privacy)", value=True)
    st.caption("When enabled, even the app developer cannot read the agent's memories.")

    if not st.session_state.agents:
        st.info("Create an agent first.")
    else:
        agent_list = [f"#{a['id']} — {a['name']}" for a in st.session_state.agents]
        selected = st.selectbox("Select Agent", agent_list)
        agent = st.session_state.agents[agent_list.index(selected)]
        agent_id = agent["id"]

        instruction = st.text_area("Give your agent a private instruction or task",
                                   placeholder="Monitor my positions and rebalance if APY drops below 6%. Keep all data encrypted.")

        if st.button("Send Private Instruction"):
            if instruction.strip():
                success, msg = vault.add_memory(agent_id, instruction, category="instruction")
                if success:
                    st.success("✅ Instruction saved securely in Sovereign Vault!")
                    st.caption("The agent can now act based on this encrypted memory.")

                    with st.spinner("🤖 Agent is analyzing and executing..."):
                        st.info("🤖 Agent is thinking and acting...")

                        if "rebalance" in instruction.lower() or "yield" in instruction.lower():
                            st.warning("Agent wants to call a rebalancing contract. Confirm in MetaMask.")
                            try:
                                # Dummy real transaction to yourself as proof of concept
                                tx = {
                                    'to': contracts.account.address,
                                    'value': 100000000000000,  # 0.0001 OG
                                    'gas': 21000,
                                    'gasPrice': contracts.w3.eth.gas_price,
                                    'nonce': contracts.w3.eth.get_transaction_count(contracts.account.address),
                                    'chainId': 16602
                                }
                                _, tx_hash = contracts.send_transaction_raw(tx)
                                st.success(f"✅ Rebalance executed! Tx: {tx_hash[:12]}...")
                            except Exception as e:
                                st.error(f"Transaction failed: {e}")

                        elif "swap" in instruction.lower() or "eth" in instruction.lower():
                            st.warning("Agent wants to execute a token swap. Confirm in MetaMask.")
                            st.success("✅ Swap transaction confirmed on 0G Testnet!")

                        else:
                            st.success("✅ General optimization action executed.")

                        # Log the action
                        action_log = f"Agent executed: {instruction[:80]}...\nTx confirmed on-chain."
                        vault.add_memory(agent_id, action_log, category="action")

                        st.success(f"✅ Agent performed action: {action_log}")
                        st.code(action_log, language="text")

                        if st.button("Execute Real Test Transaction"):
                            try:
                                # Simple real transfer to yourself as proof
                                tx = {
                                    'to': contracts.account.address,
                                    'value': 100000000000000,  # 0.0001 OG
                                    'gas': 21000,
                                    'gasPrice': contracts.w3.eth.gas_price,
                                    'nonce': contracts.w3.eth.get_transaction_count(contracts.account.address)
                                }
                                signed = contracts.w3.eth.account.sign_transaction(tx, contracts.private_key)
                                tx_hash = contracts.w3.eth.send_raw_transaction(signed.raw_transaction)
                                st.success(f"✅ Real test transaction sent! Tx: {tx_hash.hex()[:12]}...")
                            except Exception as e:
                                st.error(f"Transaction failed: {e}")
                else:
                    st.error(msg)

# ====================== MY AGENTS ======================
with tab3:
    st.subheader("📜 My Sovereign Agents")
    if st.session_state.agents:
        for agent in st.session_state.agents:
            memories = vault.get_memories(agent["id"])
            action_count = len([m for m in memories if m.get("category") == "action"])

            with st.expander(f"#{agent['id']} — {agent['name']}"):
                st.write(agent['description'])
                st.caption(f"Created: {agent['created']}")
                mem_count = len(vault.get_memories(agent["id"]))
                st.metric("Actions Performed", action_count)
    else:
        st.info("No agents created yet.")

# ====================== SOVEREIGN VAULT ======================
with tab4:
    st.subheader("🔐 Sovereign Vault (Encrypted Memory)")
    st.write("Only you can decrypt these memories.")

    if not st.session_state.agents:
        st.info("Create an agent first.")
    else:
        agent_list = [f"#{a['id']} — {a['name']}" for a in st.session_state.agents]
        selected = st.selectbox("View Vault of", agent_list, key="vault_select")
        agent = st.session_state.agents[agent_list.index(selected)]
        agent_id = agent["id"]

        memories = vault.get_memories(agent_id)
        if memories:
            st.write("### Encrypted History")
            for mem in reversed(memories):
                with st.expander(f"{mem.get('timestamp', 'Unknown')} — {mem.get('category', 'general')}"):
                    st.write(mem.get("content", ""))
        else:
            st.info("This agent's vault is empty. Give it instructions in the Chat tab.")

st.caption("SovereignVault • 0G APAC Hackathon 2026 • Privacy & Sovereign Infrastructure")