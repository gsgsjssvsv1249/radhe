from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load personality traits
def load_personality():
    try:
        with open('personality.txt', 'r') as f:
            return json.load(f)
    except:
        return {
            "name": "Luna",
            "traits": ["kind", "playful", "supportive"],
            "voice": "female"
        }

# AI Response Generator (mock - replace with your actual implementation)
def generate_response(user_input):
    personality = load_personality()
    responses = {
        "hello": f"Hello! I'm {personality['name']}. How are you today?",
        "how are you": f"I'm feeling {personality['traits'][0]} today! What about you?",
        "default": "That's interesting! Tell me more."
    }
    
    user_input = user_input.lower()
    if "hello" in user_input:
        return responses["hello"]
    elif "how are you" in user_input:
        return responses["how are you"]
    else:
        return responses["default"]

# Audio Processing (mock - replace with your VTSController)
def process_audio(audio_path):
    # In a real implementation, this would call VTSController
    output_path = f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    return output_path

# Routes
@app.route('/')
def home():
    return jsonify({
        "status": "running", 
        "ai_name": load_personality().get("name", "AI Companion"),
        "endpoints": {
            "/chat": "POST text message, get AI response",
            "/upload_voice": "POST audio file, get processed response"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        response_text = generate_response(data['message'])
        
        # Log conversation
        with open('message_history.txt', 'a') as f:
            f.write(f"User: {data['message']}\nAI: {response_text}\n\n")
            
        return jsonify({
            "reply": response_text,
            "personality": load_personality()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{str(uuid.uuid4())}.wav")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Process audio (would call VTSController in real implementation)
            processed_path = process_audio(filepath)
            
            return send_file(
                processed_path,
                mimetype="audio/mpeg",
                as_attachment=True,
                download_name="response.mp3"
            )
        except Exception as e:
            return jsonify({"error": f"Audio processing failed: {str(e)}"}), 500
            
    return jsonify({"error": "File type not allowed"}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
