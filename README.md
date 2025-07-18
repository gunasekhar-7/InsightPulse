InsightPulse


InsightPulse is an end-to-end sentiment analysis web application that leverages machine learning and NLP techniques to identify the sentiment in user-inputted text. The platform offers a modern, accessible UI with real-time analysis, robust backend, metrics tracking, and a reproducible workflow.



🚀 Features
Real-time Sentiment Detection: Positive, negative, or neutral classification.

Cleaned Text Display: Visualizes how your input is preprocessed before analysis.

Probability Breakdown: Interactive chart of sentiment probabilities.

Modern UI/UX: Responsive, accessible interface with dark/light mode toggle.

Health and Metrics Endpoints: Easily monitor model status and view evaluation scores.

Production-Ready Backend: Modular code, logging, error handling, and deployment readiness.

Easy Customization: Plug in your own model or dataset for flexible extension.




📁 Project Structure
text
InsightPulse/
├── .gitignore
├── README.md
├── backend/
│   ├── venv/
│   ├── app.py
│   ├── train_model.py
│   ├── models/
│   │   ├── tfidf_vectorizer.pkl
│   │   ├── sentiment_model.pkl
│   │   └── metrics.json
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js




⚙️ Installation & Usage

1. Clone the Repository
bash
git clone https://github.com/your-username/InsightPulse.git
cd InsightPulse


2. Backend Setup
bash
cd backend
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train the model (ensure you have a real dataset for best results)
python train_model.py

# Start the backend server
python app.py
Backend is served at http://127.0.0.1:5000

Health check endpoint: http://127.0.0.1:5000/health


3. Frontend Setup
You can open frontend/index.html directly in your browser, or serve with a simple HTTP server:

bash
cd frontend
python -m http.server 8000  # Access via http://localhost:8000
For production, deploy via Netlify/Vercel and ensure API endpoint in script.js matches your backend location.



🧠 Model Details
Algorithm: Multinomial Naive Bayes (default), pluggable with other classifiers.

Vectorization: TF-IDF (max 5000 features).

Preprocessing: Lowercase, lemmatization, punctuation/stopword removal, and URL/mention stripping.

Training Data: Ships with sample data; replace with a real-world dataset (IMDB/Yelp/Twitter) for production.

Metrics: Model evaluation accuracy and F1-score are logged automatically to models/metrics.json.



🕹️ Usage
Type or paste any text into the main input box.

Click Analyze Sentiment.

View:

Overall Sentiment: With icon

Probability Breakdown: As a bar chart

Cleaned Text: Processed input used for prediction

Use the “Try Example” button for a demo, or explore in dark/light modes.



💡 Customization
Train on Your Data: Replace training data in train_model.py.

Plug in Other Models: Swap out model and vectorizer; ensure matching cleaning logic.

Deploy Publicly: Backend can be deployed to Railway/Render; frontend to Netlify/Vercel.

Batch Analysis: Extend API for batch processing as shown in code comments.



📝 Example API Usage


text
POST /analyze_sentiment
Content-Type: application/json

{
  "text": "The service was friendly and prompt, but the food was just average."
}

Response:
{
  "sentiment": "positive",
  "probabilities": {
    "positive": 78.2,
    "neutral": 12.5,
    "negative": 9.3
  },
  "cleaned_text": "service friendly prompt food average"
}




🏅 Resume-Ready Highlights
Production-grade preprocessing and strict consistency between training and inference.

Interactive, accessible SPA frontend.

Integrated health/metrics API endpoints and robust error logging.

Customizable model pipeline, compatible with latest deployment workflows.



🤝 Contributing
Pull requests are welcome. Open an issue for bug fixes or new features. Please follow standard Python and frontend style guides.



📣 Authors
Developed by [Your Name].
For professional inquiries, please contact: [your.email@example.com]

Happy Analyzing! 🚀