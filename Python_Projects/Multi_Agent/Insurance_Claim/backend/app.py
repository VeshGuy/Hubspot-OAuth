from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes import claim_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(claim_routes)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
