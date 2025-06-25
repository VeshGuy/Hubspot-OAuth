from backend.services.extract_utils import extract_text_from_pdf
from backend.services.llm_utils import call_groq_llm
import logging

logging.basicConfig(level=logging.DEBUG)

class IntakeAgent:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        logging.debug(f"Initialized IntakeAgent with file: {pdf_path}")

    def run(self):
        try:
            logging.debug(f"Running IntakeAgent on file: {self.pdf_path}")
            raw_text = extract_text_from_pdf(self.pdf_path)
            prompt = f"""Extract the following fields from the text:
            - name
            - dob
            - claim_amount
            - incident_date
            - policy_number

            Also output only in JSON format and do not include any additional text or explanations. 
            Ensure the JSON is well-formed and contains all required fields.
            If any field is missing, return an empty string for that field.
            Also convert the date fields to ISO format (YYYY-MM-DD).

            Output in this JSON format:
            {{"name": "...", "dob": "...", "claim_amount": "...", "incident_date": "...", "policy_number": "..."}}.

            Text:
            {raw_text}
            """
            
            result = call_groq_llm(prompt)
            logging.debug(f"IntakeAgent result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in IntakeAgent: {str(e)}")
            raise
