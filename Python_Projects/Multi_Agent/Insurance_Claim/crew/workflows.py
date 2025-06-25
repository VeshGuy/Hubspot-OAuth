from agents.intake_agent import IntakeAgent
from agents.validation_agent import ValidationAgent
from agents.filler_agent import FillerAgent
import json
import logging

logging.basicConfig(level=logging.DEBUG)

def run_claim_workflow(pdf_path):
    logging.debug(f"Starting workflow with file: {pdf_path}")

    # Extract data
    try:
        intake_agent = IntakeAgent(pdf_path)
        raw_output = intake_agent.run()
        logging.debug(f"Raw output from IntakeAgent: {raw_output}")
    except Exception as e:
        logging.error(f"Error in IntakeAgent: {str(e)}")
        raise

    try:
        extracted = json.loads(raw_output)
        logging.debug(f"Extracted data: {extracted}")
    except json.JSONDecodeError as e:
        logging.error("LLM output was not valid JSON")
        raise Exception("LLM output was not valid JSON") from e

    # Validate data
    try:
        validator = ValidationAgent(extracted)
        validation = validator.run()
        logging.debug(f"Validation output: {validation}")
        extracted.update(validation)
    except Exception as e:
        logging.error(f"Error in ValidationAgent: {str(e)}")
        raise

    # Fill to JSON file
    try:
        filler = FillerAgent(extracted)
        filler_result = filler.run()
        logging.debug(f"Filler result: {filler_result}")
    except Exception as e:
        logging.error(f"Error in FillerAgent: {str(e)}")
        raise

    final_response = {**extracted, **filler_result}
    logging.debug(f"Final response: {final_response}")
    return final_response
