"""
Handle optional imports for dependencies that may not be available in serverless environments
"""

import logging

logger = logging.getLogger(__name__)

# Try to import heavy ML libraries with fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    logger.warning("NumPy not available - some advanced features will be disabled")
    HAS_NUMPY = False
    np = None

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    logger.warning("Pandas not available - some advanced features will be disabled")
    HAS_PANDAS = False
    pd = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    logger.warning("Scikit-learn not available - some advanced features will be disabled")
    HAS_SKLEARN = False
    TfidfVectorizer = None
    cosine_similarity = None

try:
    import redis
    HAS_REDIS = True
except ImportError:
    logger.warning("Redis not available - will use in-memory session storage")
    HAS_REDIS = False
    redis = None

def get_feature_availability():
    """Return dictionary of available optional features"""
    return {
        'numpy': HAS_NUMPY,
        'pandas': HAS_PANDAS,
        'sklearn': HAS_SKLEARN,
        'redis': HAS_REDIS,
        'advanced_ml': HAS_NUMPY and HAS_PANDAS and HAS_SKLEARN,
        'session_persistence': HAS_REDIS
    }

def require_numpy():
    """Check if numpy is available, raise error if not"""
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for this feature but not available")
    return np

def require_pandas():
    """Check if pandas is available, raise error if not"""
    if not HAS_PANDAS:
        raise ImportError("Pandas is required for this feature but not available")
    return pd

def require_sklearn():
    """Check if sklearn is available, raise error if not"""
    if not HAS_SKLEARN:
        raise ImportError("Scikit-learn is required for this feature but not available")
    return TfidfVectorizer, cosine_similarity

def fallback_similarity(text1: str, text2: str) -> float:
    """
    Simple text similarity fallback when sklearn is not available
    Uses basic word overlap ratio
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def safe_cosine_similarity(text1: str, text2: str) -> float:
    """
    Calculate text similarity with fallback when sklearn is not available
    """
    if HAS_SKLEARN:
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.warning(f"Error in sklearn similarity calculation: {e}")
            return fallback_similarity(text1, text2)
    else:
        return fallback_similarity(text1, text2)