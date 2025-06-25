from flask import Blueprint, request, jsonify
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crew.workflows import run_claim_workflow

logging.basicConfig(level=logging.DEBUG)

claim_routes = Blueprint("claim_routes", __name__)

@claim_routes.route("/upload", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join("data", file.filename)
    logging.debug(f"Saving file to: {filepath}")
    try:
        file.save(filepath)
    except Exception as e:
        logging.error(f"Error saving file: {str(e)}")
        return jsonify({"error": str(e)}), 500

    try:
        output = run_claim_workflow(filepath)
        logging.debug(f"Workflow output: {output}")
        return jsonify(output)
    except Exception as e:
        logging.error(f"Error in workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500
