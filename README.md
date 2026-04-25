# SovereignVault

**Private Sovereign Agent Wallet + Encrypted Memory Vault on 0G**

### Overview
**SovereignVault** is a self-custodial privacy-focused platform that allows users to create and manage autonomous AI agents while keeping all sensitive data (instructions, memories, strategies, and history) **encrypted and under full user control**.

### Key Features
- **On chain Sovereign Agent Creation:** Unique Agent ID minted on 0G Chain
- **Encrypted Memory Vault:** All agent memories and user instructions are encrypted using AES (Fernet)
- **Sovereign Mode:** Maximum privacy toggle (even the developer cannot read the data)
- **Chat & Action System:** Users give private instructions; agents simulate realistic actions with transaction logs
- **Real MetaMask Integration:** Agents can trigger real on-chain transactions with user approval
- **Self-Custodial Design:** Only the user holds the decryption key

### Tech Stack
- **Blockchain**: 0G Galileo Testnet
- **Smart Contract**: Solidity (SovereignAgent)
- **Encryption**: `cryptography.fernet` (AES-128)
- **Frontend**: Streamlit
- **Backend**: Python + web3.py

### Deployed Contract
- SovereignAgent: `0x55072806A808Ad2FA4972136d06388058Ce5156E`

### How It Works
1. User creates a sovereign agent on-chain.
2. Gives encrypted private instructions via chat.
3. Agent analyzes and "executes" (semi-real actions with MetaMask triggers).
4. All memories and actions are stored in the user's encrypted Sovereign Vault.

### Future Roadmap
- Full 0G decentralized storage integration
- ZK proofs for access control
- Real DeFi integrations (Uniswap, Aave, etc.)
- Agent reputation and cross-agent collaboration

