import hashlib
from collections import Counter


def calculate_sha256(value):
    
    return hashlib.sha256(value.encode()).hexdigest()


def check_palindrome(value):
    
    cleaned = ''.join(value.lower().split())
    return cleaned == cleaned[::-1]


def analyze_string(value):
    return {
        'length': len(value),
        'is_palindrome': check_palindrome(value),
        'unique_characters': len(set(value)),
        'word_count': len(value.split()),
        'sha256_hash': calculate_sha256(value),
        'char_frequency': dict(Counter(value))
    }


def parse_natural_language_query(query):
    
    query_lower = query.lower()
    filters = {}
    
    
    if 'palindrome' in query_lower or 'palindromic' in query_lower:
        filters['is_palindrome'] = True
    
    
    if 'single word' in query_lower:
        filters['word_count'] = 1
    elif 'two word' in query_lower:
        filters['word_count'] = 2
    
    
    import re
    
    
    longer_match = re.search(r'longer than (\d+)', query_lower)
    if longer_match:
        filters['min_length'] = int(longer_match.group(1)) + 1
    
    
    shorter_match = re.search(r'shorter than (\d+)', query_lower)
    if shorter_match:
        filters['max_length'] = int(shorter_match.group(1)) - 1
    

    contains_match = re.search(r'contain(?:ing)?(?: the letter)? ([a-z])', query_lower)
    if contains_match:
        filters['contains_character'] = contains_match.group(1)
    
    
    if 'first vowel' in query_lower:
        filters['contains_character'] = 'a'
    
    return filters