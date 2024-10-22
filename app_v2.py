from flask import Flask, request, jsonify, render_template, session
from faq_search_v2 import FAQSearch
from datetime import datetime
import json
import logging

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# Initialize the FAQSearch class
faq_search = FAQSearch('faqs.json')

# Configure logging
logging.basicConfig(filename='feedback.log', level=logging.INFO)

@app.route('/')
def home():
    return render_template('index_v2.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_query = data['query']
    results = faq_search.search(user_query)

    # Update session history
    if 'history' not in session:
        session['history'] = []
    session['history'].append(user_query)
    session['history'] = session['history'][-10:]  # Keep only last 10 searches

    return jsonify({'results': results, 'history': session['history']}), 200

@app.route('/suggestions', methods=['POST'])
def suggestions():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_query = data['query']
    suggestions = faq_search.get_suggestions(user_query)
    return jsonify(suggestions), 200

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    if not data or 'question' not in data or 'feedback' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    question = data['question']
    feedback = data['feedback']
    timestamp = datetime.utcnow().isoformat()

    # Log the feedback
    feedback_entry = {
        'timestamp': timestamp,
        'question': question,
        'feedback': feedback
    }
    with open('feedback.log', 'a') as f:
        f.write(json.dumps(feedback_entry) + '\n')

    return jsonify({'message': 'Feedback received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    print("Server is running on http://localhost:5000/")
