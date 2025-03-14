from flask import Flask, request, jsonify
import base64
from sys import platform

from app.run import start_geoprocess

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LOGGER")

app = Flask(__name__)

def safe_base64_decode(encoded_str):
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_str + "==")
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        logging.error(f"Error decoding message: {e}")
        return None

def run(request, event=""):
    try:
        message = request.get_json().get("message", {})
        encoded_data = message.get("data", "")

        decoded_str = safe_base64_decode(encoded_data)
        if decoded_str is None:
            return {"error": "Invalid Base64 format"}, 400

        logging.info(f"Message received and decoded: {decoded_str}")
        start_geoprocess(decoded_str, logger, env="dev")
        return {"message": "Success"}, 200

    except Exception as e:
        logging.error(f"Server error: {e}")
        return {"error": "Server error", "details": str(e)}, 500

@app.route("/main_flask", methods=["POST"])
def main_route():
    return run(request)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    if platform in ["win32", "win64"]:
        app.run(host="127.0.0.1", port=8000, debug=False)
