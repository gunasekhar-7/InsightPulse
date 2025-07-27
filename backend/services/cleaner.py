"""Text preprocessing utilities for InsightPulse sentiment analysis.

clean(text)     --> Normalizes, tokenizes, and cleans text for ML.
The result is compatible with vectorizer/model trained on the same pipeline.
"""

import re
import string
import logging
import nltk
from typing import Optional, List
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Ensure NLTK data is available for all workers
try:
    nltk.data.find("corpora/stopwords.zip")
    nltk.data.find("corpora/wordnet.zip")
    nltk.data.find("tokenizers/punkt.zip")
except LookupError:
    logger.info("Downloading NLTK data for text cleaning")
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("punkt", quiet=True)

lemmatizer = WordNetLemmatizer()
STOPWORDS = set(stopwords.words("english"))
PUNCT = string.punctuation

# Precompile regexes for performance
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
BRACKETS_PATTERN = re.compile(r"[\[\]{}()<>]")
PUNCT_PATTERN = re.compile(f"[{re.escape(PUNCT)}]")
DIGITS_PATTERN = re.compile(r"\d+")
MENTIONS_HASHTAGS_PATTERN = re.compile(r"[@#]\w+")
WHITESPACE_PATTERN = re.compile(r"\s+")

def clean(text: Optional[str]) -> str:
    """Clean and normalize text for sentiment analysis.
    
    Lowercases, removes URLs, brackets, punctuation, numbers, mentions, hashtags,
    excess whitespace, and English stopwords. Applies lemmatization.

    Args:
        text: Input text. If None or empty, returns empty string.

    Returns:
        str: Cleaned, normalized text. May be empty if input is empty or only noise.
    """
    if not text:
        return ""

    text = text.lower()
    text = URL_PATTERN.sub("", text)
    text = BRACKETS_PATTERN.sub("", text)
    text = PUNCT_PATTERN.sub("", text)
    text = DIGITS_PATTERN.sub("", text)
    text = MENTIONS_HASHTAGS_PATTERN.sub("", text)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()

    # Tokenize, lemmatize, and remove stopwords in one pass
    words = []
    for token in text.split():
        token = lemmatizer.lemmatize(token)
        if token and token not in STOPWORDS and not token.isspace():
            words.append(token)
    
    cleaned = " ".join(words)
    if not cleaned:
        logger.debug("Cleaning produced empty result for input: %r", text)
    return cleaned
