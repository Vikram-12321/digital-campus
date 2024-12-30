from rapidfuzz import process  # pip install rapidfuzz

def correct_spelling(input_word, dictionary_words, scorer_threshold=75):
    """
    Use rapidfuzz to find the closest match in dictionary_words to input_word.
    Only return a suggestion if it meets the scorer_threshold.
    """
    # process.extractOne returns a tuple: (best_match, score, index)
    best_match = process.extractOne(input_word, dictionary_words)
    if best_match and best_match[1] >= scorer_threshold:
        return best_match[0]  # The best matching word
    return input_word  # Return original if no decent match found