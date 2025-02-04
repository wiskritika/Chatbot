import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(name)

# Configure the Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Define the model
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Send the user message to the Gemini model
    response = model.send_message(user_message)
    
    return jsonify({"response": response})

if name == 'main':
    app.run(debug=True)