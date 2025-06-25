from datetime import datetime

class ValidationAgent:
    def __init__(self, extracted_data: dict):
        self.data = extracted_data
        self.errors = []

    def check_missing_fields(self):
        required = ["name", "dob", "claim_amount", "incident_date", "policy_number"]
        for field in required:
            if not self.data.get(field):
                self.errors.append(f"Missing field: {field}")

    def check_date_format(self, field):
        try:
            datetime.strptime(self.data.get(field, ""), "%Y-%m-%d")
        except (ValueError, TypeError):
            self.errors.append(f"Invalid date format for: {field}")

    def check_future_date(self):
        try:
            incident_date = datetime.strptime(self.data["incident_date"], "%Y-%m-%d")
            if incident_date > datetime.today():
                self.errors.append("Incident date cannot be in the future")
        except Exception:
            pass  

    def run(self):
        self.check_missing_fields()
        self.check_date_format("dob")
        self.check_date_format("incident_date")
        self.check_future_date()

        if self.errors:
            return {
                "validation_status": "failed",
                "errors": self.errors
            }

        return {
            "validation_status": "passed"
        }
