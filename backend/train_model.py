#!/usr/bin/env python
"""Train and export a sentiment analysis model for InsightPulse.

Usage:
    python train_model.py --data_path data/train.csv [--model_dir models]

Trains a Multinomial Naive Bayes classifier on cleaned text, evaluates,
and exports the model, vectorizer, and metrics to a timestamped directory.
"""

import argparse
from pathlib import Path
from datetime import datetime
import json
import os
import sys
import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
import joblib
from sklearn import __version__ as sklearn_version
from platform import python_version
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# NLTK setup
NLTK_RESOURCES = ["stopwords", "wordnet", "punkt"]

def nltk_setup():
    """Ensure NLTK resources are available."""
    for resource in NLTK_RESOURCES:
        try:
            nltk.data.find(f"corpora/{resource}.zip")
        except LookupError:
            logger.info(f"Downloading NLTK resource: {resource}")
            nltk.download(resource)

def clean_text(text, lemmatizer, stop_words):
    """Clean and normalize text for sentiment analysis."""
    text = str(text).lower()
    # Remove unwanted patterns
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Lemmatize and remove stopwords
    tokens = [lemmatizer.lemmatize(token) for token in text.split() if token not in stop_words]
    return ' '.join(tokens)

def load_data(data_path):
    """Load dataset from CSV/JSON. Expected columns: 'text', 'sentiment'."""
    logger.info(f"Loading data from: {data_path}")
    if data_path.endswith(".csv"):
        df = pd.read_csv(data_path)
    elif data_path.endswith(".json"):
        df = pd.read_json(data_path)
    else:
        raise ValueError("Unsupported file type. Use CSV or JSON.")
    # Ensure required columns exist
    if not all(col in df.columns for col in ["text", "sentiment"]):
        raise ValueError("Data must contain 'text' and 'sentiment' columns.")
    return df

def train_and_evaluate(df, output_dir):
    """Train, evaluate, and export the sentiment analysis model."""
    logger.info("Preparing data...")
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    df["cleaned_text"] = df["text"].apply(
        lambda x: clean_text(x, lemmatizer, stop_words)
    )
    logger.info("\nOriginal vs. Cleaned Text (sample):")
    print(df[["text", "cleaned_text"]].head())

    # Vectorize
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(df["cleaned_text"])
    y = df["sentiment"]

    # Train-test split (stratified if possible)
    labels = y.unique()
    test_evaluated = False
    if len(y) > 1 and len(labels) > 1 and len(y) >= 2 * len(labels):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        test_evaluated = True
    else:
        logger.warning(
            "Dataset too small or single-class for stratified split. "
            "Using full data for training and evaluation."
        )
        X_train, y_train = X, y
        X_test, y_test = X, y

    # Train
    logger.info("Training model...")
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Evaluate
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    metrics = {
        "accuracy": round(acc, 4),
        "f1_score": round(f1, 4),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "model": "MultinomialNB",
        "python_version": python_version(),
        "sklearn_version": sklearn_version,
        "nltk_resources": NLTK_RESOURCES,
        "training_date": datetime.utcnow().isoformat(),
        "params": {
            "vectorizer": "TfidfVectorizer(max_features=5000)",
            "classifier": "MultinomialNB()",
        },
        "notes": "No separate test set." if not test_evaluated else "",
    }

    # Export
    logger.info(f"Saving model to: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, output_dir / "tfidf_vectorizer.pkl")
    joblib.dump(model, output_dir / "sentiment_model.pkl")
    with open(output_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Training complete.")

    return metrics

def main():
    parser = argparse.ArgumentParser(
        description="Train and export a sentiment analysis model."
    )
    parser.add_argument(
        "--data_path", type=str, default="data/train.csv",
        help="Path to training data (CSV/JSON). Must have 'text' and 'sentiment' columns."
    )
    parser.add_argument(
        "--model_dir", type=str, default="models",
        help="Directory for saving models and metrics."
    )
    args = parser.parse_args()

    nltk_setup()
    df = load_data(args.data_path)

    out_dir = Path(args.model_dir) / datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    metrics = train_and_evaluate(df, out_dir)

    # Print summary
    print("\nMetrics Summary:")
    print(json.dumps({k: v for k, v in metrics.items() if k != "classification_report"}, indent=2))
    print(f"\nSaved to: {out_dir}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
