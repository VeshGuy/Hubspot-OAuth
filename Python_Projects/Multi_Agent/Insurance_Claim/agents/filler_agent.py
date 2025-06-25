import os
import json
from datetime import datetime
from uuid import uuid4

class FillerAgent:
    def __init__(self, claim_data: dict, output_dir="data/"):
        self.claim_data = claim_data
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_filename(self):
        claim_id = self.claim_data.get("policy_number") or str(uuid4())
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"claim_{claim_id}_{timestamp}.json"

    def run(self):
        filename = self.generate_filename()
        full_path = os.path.join(self.output_dir, filename)

        with open(full_path, "w") as f:
            json.dump(self.claim_data, f, indent=4)

        return {
            "output_file": full_path,
            "status": "saved"
        }
