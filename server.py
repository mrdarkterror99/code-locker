import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# --- Firebase Admin SDK Initialization ---
# The service account key is loaded from an environment variable for security.
# On Render, you can set this as a "Secret File".
try:
    cred_json_str = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    if cred_json_str is None:
        print("FATAL: FIREBASE_CREDENTIALS_JSON environment variable not set.")
        # In a real app, you might exit or handle this more gracefully.
        # For this example, we'll let it raise an error when used.
    else:
        cred_json = json.loads(cred_json_str)
        cred = credentials.Certificate(cred_json)
        firebase_admin.initialize_app(cred)
        
except json.JSONDecodeError:
    print("FATAL: FIREBASE_CREDENTIALS_JSON is not valid JSON.")
except Exception as e:
    print(f"FATAL: An error occurred during Firebase initialization: {e}")

# Get a client instance for Firestore
db = firestore.client()
# --- End of Firebase Initialization ---


@app.route('/save_code', methods=['POST'])
def save_code():
    """
    API endpoint to save a new code snippet to Firestore.
    Expects a JSON body with 'name' and 'code'.
    """
    data = request.json
    if not data or 'name' not in data or 'code' not in data:
        return jsonify({"error": "Invalid request body"}), 400

    unique_name = data['name']
    code_content = data['code']

    try:
        # Create a reference to a document in the 'codes' collection with the unique name as ID
        doc_ref = db.collection('codes').document(unique_name)
        # Set the document data
        doc_ref.set({'code': code_content})
        return jsonify({"message": "Code saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save to Firestore: {e}"}), 500


@app.route('/get_code/<unique_name>', methods=['GET'])
def get_code(unique_name):
    """
    API endpoint to retrieve a single code snippet from Firestore by name.
    """
    try:
        doc_ref = db.collection('codes').document(unique_name)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Code not found"}), 404
        
        # The R script and frontend expect a JSON object with a 'code' key
        return jsonify(doc.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve from Firestore: {e}"}), 500


@app.route('/get_all_codes', methods=['GET'])
def get_all_codes():
    """
    API endpoint to retrieve all saved code snippets from Firestore.
    """
    try:
        codes_ref = db.collection('codes')
        docs = codes_ref.stream()
        # Format the data into a dictionary of {name: code}
        codes = {doc.id: doc.to_dict().get('code', '') for doc in docs}
        return jsonify(codes), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve from Firestore: {e}"}), 500


@app.route('/delete_code/<unique_name>', methods=['DELETE'])
def delete_code(unique_name):
    """
    API endpoint to delete a code snippet from Firestore by name.
    """
    try:
        doc_ref = db.collection('codes').document(unique_name)
        # Check if the document exists before attempting to delete
        if doc_ref.get().exists:
            doc_ref.delete()
            return jsonify({"message": "Code deleted successfully"}), 200
        else:
            return jsonify({"error": "Code not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete from Firestore: {e}"}), 500


@app.route('/', methods=['GET'])
def home():
    """A final check to make sure the server is running."""
    return "Your server is running and connected to Firestore!"

if __name__ == '__main__':
    # Get the port from the environment variable provided by Render, or use a default
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 to be accessible from outside the container
    app.run(host='0.0.0.0', port=port)
