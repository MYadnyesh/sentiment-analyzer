from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Message:
    """Represents a message from Gmail or Google Chat"""
    id: str
    text: str
    sender: str
    source: str  # 'gmail' or 'chat'
    timestamp: datetime
    subject: Optional[str] = None


@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    message_id: str
    text: str
    sender: str
    source: str
    timestamp: datetime
    sentiment_score: float  # -1 (negative) to +1 (positive)
    sentiment_label: str    # 'positive', 'neutral', 'negative'
    phrase: str  # Changed from 'keyword' to 'phrase'
    subjectivity: float  # 0 (objective) to 1 (subjective) - NEW


@dataclass
class AnalysisConstraints:
    """Constraints for filtering and analyzing results - NEW"""
    min_sentiment_score: Optional[float] = None  # e.g., -1.0 to 1.0
    max_sentiment_score: Optional[float] = None
    # e.g., ['positive', 'negative']
    sentiment_labels: Optional[List[str]] = None
    sources: Optional[List[str]] = None  # e.g., ['gmail', 'chat']
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_subjectivity: Optional[float] = None  # Filter subjective/objective
    max_subjectivity: Optional[float] = None
    senders: Optional[List[str]] = None  # Filter by specific senders


@dataclass
class AnalysisSummary:
    """Summary statistics for visualization - NEW"""
    phrase: str
    total_messages: int
    positive_count: int
    neutral_count: int
    negative_count: int
    avg_sentiment_score: float
    avg_subjectivity: float
    # {'gmail': {'pos': 5, 'neu': 2, 'neg': 3}, 'chat': {...}}
    sentiment_by_source: dict
    # [{'date': '2024-01', 'positive': 5, 'negative': 2}, ...]
    sentiment_over_time: List[dict]
    # [{'sender': 'john@x.com', 'avg_score': 0.5}, ...]
    top_senders: List[dict]
