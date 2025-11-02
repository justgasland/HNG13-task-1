import hashlib
import re
from collections import Counter


def calculate_sha256(value):
   
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def check_palindrome(value):
   
    # Convert to lowercase for case-insensitive comparison
    cleaned = value.lower()
    return cleaned == cleaned[::-1]


def count_unique_characters(value):
    
    return len(set(value))


def count_words(value):
    
    return len(value.split())


def calculate_character_frequency(value):
    """
    Calculate the frequency of each character in a string
    
    Args:
        value (str): The string to analyze
    
    Returns:
        dict: Dictionary mapping each character to its occurrence count
    """
    return dict(Counter(value))


def analyze_string(value):
    """
    Analyze a string and compute all properties
    
    Args:
        value (str): The string to analyze
    
    Returns:
        dict: Dictionary containing all computed properties
    """
    return {
        'value': value,
        'sha256_hash': calculate_sha256(value),
        'length': len(value),
        'is_palindrome': check_palindrome(value),
        'unique_characters': count_unique_characters(value),
        'word_count': count_words(value),
        'character_frequency_map': calculate_character_frequency(value)
    }


def parse_natural_language_query(query):
    """
    Parse natural language query and convert to filters
    
    Args:
        query (str): Natural language query string
    
    Returns:
        dict: Dictionary of parsed filters
    
    Raises:
        ValueError: If query cannot be parsed
    """
    query_lower = query.lower().strip()
    filters = {}
    
    # Handle empty query
    if not query_lower:
        raise ValueError("Query cannot be empty")
    
    # Check for palindrome keywords
    palindrome_keywords = ['palindrome', 'palindromic', 'reads the same']
    if any(keyword in query_lower for keyword in palindrome_keywords):
        filters['is_palindrome'] = True
    
    # Check for word count
    # "single word" or "one word"
    if 'single word' in query_lower or 'one word' in query_lower:
        filters['word_count'] = 1
    elif 'two word' in query_lower:
        filters['word_count'] = 2
    elif 'three word' in query_lower:
        filters['word_count'] = 3
    
    # Extract specific word count: "strings with 5 words"
    word_count_match = re.search(r'with (\d+) words?', query_lower)
    if word_count_match:
        filters['word_count'] = int(word_count_match.group(1))
    
    # Check for length constraints
    # "longer than X characters"
    longer_match = re.search(r'longer than (\d+)', query_lower)
    if longer_match:
        filters['min_length'] = int(longer_match.group(1)) + 1
    
    # "shorter than X characters"
    shorter_match = re.search(r'shorter than (\d+)', query_lower)
    if shorter_match:
        filters['max_length'] = int(shorter_match.group(1)) - 1
    
    # "at least X characters"
    at_least_match = re.search(r'at least (\d+) characters?', query_lower)
    if at_least_match:
        filters['min_length'] = int(at_least_match.group(1))
    
    # "at most X characters"
    at_most_match = re.search(r'at most (\d+) characters?', query_lower)
    if at_most_match:
        filters['max_length'] = int(at_most_match.group(1))
    
    # Check for character contains
    # "containing the letter X" or "contains X" or "with the letter X"
    contains_patterns = [
        r'contain(?:ing|s)?(?: the letter)? ([a-z])',
        r'with(?: the letter)? ([a-z])',
        r'that have(?: the letter)? ([a-z])'
    ]
    
    for pattern in contains_patterns:
        contains_match = re.search(pattern, query_lower)
        if contains_match:
            filters['contains_character'] = contains_match.group(1)
            break
    
    # Special case: "first vowel" = 'a'
    if 'first vowel' in query_lower:
        filters['contains_character'] = 'a'
    
    # Check for conflicts
    if 'min_length' in filters and 'max_length' in filters:
        if filters['min_length'] > filters['max_length']:
            raise ValueError("Conflicting length filters: min_length > max_length")
    
    # If no filters were parsed, raise error
    if not filters:
        raise ValueError("Unable to extract any filters from the query")
    
    return filters
