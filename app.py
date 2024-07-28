from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import nltk
import pickle
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# Initialize the Flask application
app = Flask(__name__, static_url_path='', static_folder='static')

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_question = db.Column(db.String(500), nullable=False)

# Create the database and table
with app.app_context():
    db.create_all()

# Load the trained model
with open('chatbot_model.pkl', 'rb') as model_file:
    classifier = pickle.load(model_file)

# Define responses
answers = {
    'Greetings': 'Hello. I am Dexter. I will serve your leave enquiries.',
    'Morning': 'Good Morning. I am Dexter. I will serve your leave enquiries.',
    'Afternoon': 'Good afternoon. I am Dexter. I will serve your leave enquiries.',
    'Evening': 'Good evening. I am Dexter. I will serve your leave enquiries.',
    'Goodbye': 'Good night. Take care.',
    'Opening': "I'm fine! Thank you. How can I help you?",
    'Help': 'How can I help you?',
    'No-Help': 'Ok sir/madam. No problem. Have a nice day.',
    'Closing': "It's glad to know that I have been helpful. Have a good day!",
    'Leaves-Type': 'Currently I know about two: annual and optional leaves.',
    'Default-Utilized-Annual-Leaves': 'You have used 12 annual leaves.',
    'Utilized-Annual-Leaves': 'You have taken 12 annual leaves.',
    'Utilized-Optional-Leaves': 'You have taken 1 optional leaves.',
    'Default-Balance-Annual-Leaves': 'You have 25 annual leaves left.',
    'Balance-Annual-Leaves': 'You have 25 annual leaves remaining.',
    'Balance-Optional-Leaves': 'You have 2 optional leaves remaining.',
    'CF': 'You have 30 carry forward leaves.'
}

# Preprocessing functions
def preprocess(sentence):
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    filtered_words = [w for w in tokens if not w in stopwords.words('english')]
    return filtered_words

# Feature extraction functions
def extract_feature(text):
    words = preprocess(text)
    return {word: True for word in words}

# Reply generation function
def reply(input_sentence):
    features = extract_feature(input_sentence)
    label = classifier.classify(features)
    response = answers.get(label, "I'm sorry, I didn't understand that. Can you please rephrase your question?")
    return response

# API endpoint to get chatbot response
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    # Store the user's question in the database
    new_question = Question(user_question=user_input)
    db.session.add(new_question)
    db.session.commit()
    
    bot_reply = reply(user_input)
    return jsonify({'response': bot_reply})

# Serve the index.html
@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)