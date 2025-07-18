import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib
import string
import os
import json

try:
    nltk.data.find('corpora/stopwords.zip')
    nltk.data.find('corpora/wordnet.zip')
    nltk.data.find('tokenizers/punkt.zip')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')

# Replace dummy data with real-world data for production!
data = {
    'text': [
        "I love this product! It's amazing.",
        "This is terrible, I hate it.",
        "Neutral comment here.",
        "Bad product not good.",
        "Great service, truly excellent!"
    ],
    'sentiment': [
        "positive",
        "negative",
        "neutral",
        "negative",
        "positive"
    ]
}
df = pd.DataFrame(data)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
PUNCTUATION_TO_REMOVE = string.punctuation

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(PUNCTUATION_TO_REMOVE), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [lemmatizer.lemmatize(token) for token in text.split() if token not in stop_words]
    return ' '.join(tokens)

df['cleaned_text'] = df['text'].apply(clean_text)
print("\nOriginal vs. Cleaned Text (first 5 rows):")
print(df[['text', 'cleaned_text']].head())

tfidf_vectorizer = TfidfVectorizer(max_features=5000)
X = tfidf_vectorizer.fit_transform(df['cleaned_text'])
y = df['sentiment']

if len(y) > 1 and len(y.unique()) > 1 and len(y) >= 2 * len(y.unique()):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    test_evaluated = True
else:
    print("Warning: Dataset too small or single-class for stratified split. Using full data for training.")
    X_train, y_train = X, y
    X_test, y_test = X, y
    test_evaluated = False

model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate and save metrics
if test_evaluated:
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    metrics = {
        "accuracy": round(acc, 3),
        "f1_score": round(f1, 3),
        "report": classification_report(y_test, y_pred, output_dict=True)
    }
else:
    metrics = {"info": "No separate test set; training set results only."}

if not os.path.exists('models'):
    os.makedirs('models')
joblib.dump(tfidf_vectorizer, 'models/tfidf_vectorizer.pkl')
joblib.dump(model, 'models/sentiment_model.pkl')
with open('models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("\nModel, vectorizer, and metrics saved to 'models/' directory!")
