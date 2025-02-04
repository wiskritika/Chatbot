import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Google Generative AI model
llm = GoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

# Initialize conversation memory
memory = ConversationBufferMemory()

@app.route('/')
def home():
    return send_from_directory('templates', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Create a prompt template with conversation history
    prompt_template = """You are a helpful assistant. Maintain conversation context and handle both general queries 
    and appointment booking requests. When users ask to book appointments, collect: name, phone, email, and date.
    
    Current conversation:
    {history}
    
    User: {message}
    AI:"""
    
    prompt = PromptTemplate(
        input_variables=["history", "message"],
        template=prompt_template
    )
    
    # Create chain with memory
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )
    
    # Generate response
    response = chain.run({"message": user_message})
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)