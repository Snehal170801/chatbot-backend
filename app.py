from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from chat import chat_bp
import os
 
load_dotenv()
 
app = Flask(__name__)
CORS(app, origins=os.getenv("FRONTEND_ORIGIN"))
app.register_blueprint(chat_bp, url_prefix="/api")
 
if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=True
    )

 