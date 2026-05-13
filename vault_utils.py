import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from og_sync import OGSync
from vault_index_db import save_root_hash, get_root_hash

load_dotenv()


class SovereignVault:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "vaults")
        os.makedirs(self.data_dir, exist_ok=True)

        # Generate or load encryption key (this is the user's sovereign key)
        key_file = os.path.join(self.data_dir, "sovereign_master.key")
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.key)

        self.cipher = Fernet(self.key)
        self.sovereign_mode = True

    def toggle_sovereign_mode(self, enabled: bool):
        """Sovereign Mode: Extra layer of protection"""
        self.sovereign_mode = enabled
        return enabled

    def encrypt_and_save(self, agent_id: int, data: dict):
        """Encrypt data with optional Sovereign Mode"""
        try:
            filename = os.path.join(self.data_dir, f"agent_{agent_id}_vault.json")

            # Add timestamp
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["sovereign_mode"] = self.sovereign_mode

            # Encrypt the data
            json_data = json.dumps(data).encode()
            encrypted = self.cipher.encrypt(json_data)

            with open(filename, "wb") as f:
                f.write(encrypted)

            sync = OGSync()
            synced, result = sync.upload_file(filename)

            if synced:
                root_hash = None

                if isinstance(result, dict):
                    root_hash = result.get("rootHash") or result.get("root")

                    if root_hash:
                        save_root_hash(agent_id, root_hash)

                return True, "Saved + synced to 0G"
            else:
                return True, f"Saved locally (0G sync failed: {result})"

        except Exception as e:
                return False, str(e)

    def decrypt_and_load(self, agent_id: int):
        """Decrypt and load the agent's private vault"""
        try:
            filename = os.path.join(self.data_dir, f"agent_{agent_id}_vault.json")
            if not os.path.exists(filename):
                return {
                    "memories": [],
                    "preferences": {},
                    "history": [],
                    "sovereign_mode": True
                }
            with open(filename, "rb") as f:
                encrypted = f.read()

            decrypted = self.cipher.decrypt(encrypted)
            return json.loads(decrypted)
        except FileNotFoundError:
            return {"memories": [], "preferences": {}, "history": [], "sovereign_mode": True}
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def add_memory(self, agent_id: int, memory_text: str, category: str = "general"):
        """Add encrypted memory to the agent's vault"""
        vault = self.decrypt_and_load(agent_id) or {"memories": [], "preferences": {}, "history": []}

        if "memories" not in vault:
            vault["memories"] = []

        vault["memories"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": memory_text,
            "category": category
        })

        return self.encrypt_and_save(agent_id, vault)

    def get_memories(self, agent_id: int):
        """Return decrypted memories"""
        vault = self.decrypt_and_load(agent_id)
        return vault.get("memories", []) if vault else []

    def restore_from_0g(self, agent_id: int, root_hash: str):
        from og_sync import OGSync

        filename = os.path.join(self.data_dir, f"agent_{agent_id}_vault.json")

        sync = OGSync()
        restored = sync.download_file(root_hash, filename)

        return restored
