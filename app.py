import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import re
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Flask app
app = Flask(__name__, template_folder='templates') # Serve static files
CORS(app)

# Initialize the Google Generative AI model
llm = GoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

# Initialize conversation memory
memory = ConversationBufferMemory()

user_info = {}  # Store user info for appointment booking

@app.route('/')

def home():
    return send_from_directory(app.template_folder, 'index.html')  # Serve index.html

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    # Date extraction and formatting (Improved)
    def extract_and_format_date(date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            now = datetime.now()
            if "next monday" in date_string.lower():
                days_until_monday = (7 - now.weekday() + 7) % 7
                next_monday = now + timedelta(days=days_until_monday)
                return next_monday.strftime("%Y-%m-%d")
            # Add more relative date handling as needed (e.g., "tomorrow", "next friday")
            else:
                return None

    def validate_phone(phone):
        return re.match(r"^[0-9]{10}$", phone)

    def validate_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    # Appointment booking logic (Improved)
    def book_appointment(name, phone, email, date, time):
        print(f"Appointment booked for {name} ({email}, {phone}) on {date} at {time}.")
        return "Appointment booked successfully!"

    # Prompt template (Improved)
    prompt_template = """You are a helpful assistant. Maintain conversation context and handle both general queries 
    and appointment booking requests. When users ask to book appointments, collect: name, phone, email, and date.
    Validate phone and email formats.  Extract and format dates to YYYY-MM-DD.

    Current conversation:
    {history}

    User: {message}
    AI:"""

    prompt = PromptTemplate(
        input_variables=["history", "message"],
        template=prompt_template
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

    response = chain.run({"message": user_message})

    # Handle appointment booking requests (Improved)
    if "book an appointment" in user_message.lower() or "call me" in user_message.lower():
        if 'name' not in user_info:
            user_info['name'] = ""  # Initialize
            return jsonify({"response": "Please provide your name:"})
        elif 'phone' not in user_info:
            phone = user_message.replace("phone:", "").strip() # Extract Phone number
            if validate_phone(phone):
                user_info['phone'] = phone
                return jsonify({"response": "Please provide your email address:"})
            else:
                return jsonify({"response": "Invalid phone number format. Please enter 10 digits."})
        elif 'email' not in user_info:
            email = user_message.replace("email:", "").strip() # Extract Email
            if validate_email(email):
                user_info['email'] = email
                return jsonify({"response": "What date would you like to book the appointment for?"})
            else:
                return jsonify({"response": "Invalid email format. Please provide a valid email."})
        elif 'date' not in user_info:
            date_str = user_message.replace("date:", "").strip()  # Extract Date
            date = extract_and_format_date(date_str)
            if date:
                user_info['date'] = date
                return jsonify({"response": "What time would you like to book the appointment for?"})
            else:
                return jsonify({"response": "Invalid date format. Please use YYYY-MM-DD or relative formats like 'next monday'."})
        elif 'time' not in user_info:
            time = user_message.replace("time:", "").strip() # Extract Time
            book_appointment(user_info['name'], user_info['phone'], user_info['email'], user_info['date'], time)
            user_info.clear() # Reset user info after booking
            return jsonify({"response": "Appointment booked successfully!"})

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)