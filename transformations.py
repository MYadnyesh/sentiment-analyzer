from models import Message, SentimentResult, AnalysisConstraints
from textblob import TextBlob
from typing import List


def clean_text(message: Message) -> tuple[Message, str]:
    """Pure function: Message → (Message, cleaned_text)"""
    text = message.text.strip()
    # Remove extra whitespace
    text = ' '.join(text.split())
    return message, text


def extract_phrase_context(text: str, phrase: str, context_words: int = 10) -> str:
    """
    Extract context around the phrase for better sentiment analysis
    NEW FUNCTION
    """
    text_lower = text.lower()
    phrase_lower = phrase.lower()

    # Find all occurrences of the phrase
    contexts = []
    start = 0
    while True:
        index = text_lower.find(phrase_lower, start)
        if index == -1:
            break

        # Get words before and after the phrase
        words = text.split()
        phrase_words = phrase.split()

        # Find approximate position in word list
        word_index = len(text[:index].split())

        # Extract context window
        context_start = max(0, word_index - context_words)
        context_end = min(len(words), word_index +
                          len(phrase_words) + context_words)

        context = ' '.join(words[context_start:context_end])
        contexts.append(context)

        start = index + len(phrase)

    # Return combined context or full text if phrase not found
    return ' ... '.join(contexts) if contexts else text


def calculate_sentiment(data: tuple[Message, str], phrase: str) -> tuple[Message, float, str, float]:
    """
    Pure function: (Message, text) → (Message, score, label, subjectivity)
    Enhanced to analyze phrase context - MODIFIED
    """
    message, text = data

    # Extract context around the phrase for focused analysis
    context = extract_phrase_context(text, phrase)

    # Using TextBlob for sentiment analysis
    blob = TextBlob(context if context else text)
    score = blob.sentiment.polarity  # -1 to +1
    # 0 to 1 (0=objective, 1=subjective)
    subjectivity = blob.sentiment.subjectivity

    # Classify sentiment with refined thresholds
    if score > 0.1:
        label = 'positive'
    elif score < -0.1:
        label = 'negative'
    else:
        label = 'neutral'

    return message, score, label, subjectivity


def create_result(data: tuple[Message, float, str, float], phrase: str) -> SentimentResult:
    """
    Pure function: (Message, score, label, subjectivity) → SentimentResult
    MODIFIED to include subjectivity
    """
    message, score, label, subjectivity = data

    return SentimentResult(
        message_id=message.id,
        text=message.text[:200],  # Truncate for CSV
        sender=message.sender,
        source=message.source,
        timestamp=message.timestamp,
        sentiment_score=score,
        sentiment_label=label,
        phrase=phrase,
        subjectivity=subjectivity
    )


def apply_constraints(results: List[SentimentResult], constraints: AnalysisConstraints) -> List[SentimentResult]:
    """
    Filter results based on constraints
    NEW FUNCTION
    """
    filtered = results

    # Filter by sentiment score range
    if constraints.min_sentiment_score is not None:
        filtered = [r for r in filtered if r.sentiment_score >=
                    constraints.min_sentiment_score]

    if constraints.max_sentiment_score is not None:
        filtered = [r for r in filtered if r.sentiment_score <=
                    constraints.max_sentiment_score]

    # Filter by sentiment labels
    if constraints.sentiment_labels:
        filtered = [
            r for r in filtered if r.sentiment_label in constraints.sentiment_labels]

    # Filter by source
    if constraints.sources:
        filtered = [r for r in filtered if r.source in constraints.sources]

    # Filter by date range
    if constraints.date_from:
        filtered = [r for r in filtered if r.timestamp >=
                    constraints.date_from]

    if constraints.date_to:
        filtered = [r for r in filtered if r.timestamp <= constraints.date_to]

    # Filter by subjectivity
    if constraints.min_subjectivity is not None:
        filtered = [r for r in filtered if r.subjectivity >=
                    constraints.min_subjectivity]

    if constraints.max_subjectivity is not None:
        filtered = [r for r in filtered if r.subjectivity <=
                    constraints.max_subjectivity]

    # Filter by senders
    if constraints.senders:
        filtered = [r for r in filtered if any(
            sender.lower() in r.sender.lower() for sender in constraints.senders)]

    return filtered
