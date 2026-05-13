import os
import requests


class OGSync:
    def __init__(self):
        self.upload_endpoint = "https://indexer-storage-testnet-turbo.0g.ai/file/segment"

    def upload_file(self, file_path: str):
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(self.upload_endpoint, files=files, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return True, data

            return False, response.text

        except Exception as e:
            return False, str(e)

    def download_file(self, root_hash: str, save_path: str):
        try:
            download_url = f"https://gateway.0g.ai/file?root={root_hash}"

            response = requests.get(download_url, timeout=30)

            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True

            return False

        except Exception:
            return False
