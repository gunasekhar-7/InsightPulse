# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging
import os
import json

# Logging setup (write errors/info to file)
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/app.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

# Ensure NLTK data is downloaded
try:
    nltk.data.find('corpora/stopwords.zip')
    nltk.data.find('corpora/wordnet.zip')
    nltk.data.find('tokenizers/punkt.zip')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# Load model and vectorizer
try:
    tfidf_vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    sentiment_model = joblib.load('models/sentiment_model.pkl')
except FileNotFoundError:
    logging.error("Model or vectorizer not found. Please train the model.")
    tfidf_vectorizer = None
    sentiment_model = None

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    # Identical to training
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r"[^\w\s]", '', text)   # Simplifies punctuation removal
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [lemmatizer.lemmatize(token) for token in text.split() if token not in stop_words]
    return ' '.join(tokens)

def load_metrics():
    try:
        with open('models/metrics.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {}

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    if sentiment_model is None or tfidf_vectorizer is None:
        return jsonify({'error': 'Model or vectorizer is not loaded!'}), 500
    data = request.get_json()
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({'error': 'No valid text provided'}), 400
    cleaned_text = clean_text(text)
    text_vectorized = tfidf_vectorizer.transform([cleaned_text])
    prediction = sentiment_model.predict(text_vectorized)[0]
    prediction_proba = sentiment_model.predict_proba(text_vectorized)[0]
    class_probabilities = {cls: round(prob * 100, 2) 
                           for cls, prob in zip(sentiment_model.classes_, prediction_proba)}
    return jsonify({
        'sentiment': prediction,
        'probabilities': class_probabilities,
        'cleaned_text': cleaned_text
    })

@app.route('/health')
def health():
    status = "ok" if sentiment_model is not None and tfidf_vectorizer is not None else "model_missing"
    return jsonify({
        'status': status,
        'model_loaded': sentiment_model is not None,
        'metrics': load_metrics()
    })

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {e}")
    return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "InsightPulse Backend is Running!"

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "False")=="True", port=5000)
