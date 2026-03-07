from models import Message, SentimentResult, AnalysisConstraints, AnalysisSummary
from transformations import clean_text, calculate_sentiment, create_result, apply_constraints
from typing import List
from collections import defaultdict
from datetime import datetime


class SentimentAnalyzer:

    def analyze_messages(self, messages: List[Message], phrase: str) -> List[SentimentResult]:
        """
        Run the pipeline: messages → clean → analyze → results
        """
        results = []

        for message in messages:
            # Pipeline: transform data step by step
            message, cleaned = clean_text(message)
            message, score, label, subjectivity = calculate_sentiment(
                (message, cleaned), phrase)
            result = create_result(
                (message, score, label, subjectivity), phrase)
            results.append(result)

        return results

    def filter_results(self, results: List[SentimentResult], constraints: AnalysisConstraints) -> List[SentimentResult]:
        """
        Apply constraints to filter results
        """
        return apply_constraints(results, constraints)

    def generate_summary(self, results: List[SentimentResult], phrase: str) -> AnalysisSummary:
        """
        Generate summary statistics for visualization
        
        """
        if not results:
            return AnalysisSummary(
                phrase=phrase,
                total_messages=0,
                positive_count=0,
                neutral_count=0,
                negative_count=0,
                avg_sentiment_score=0.0,
                avg_subjectivity=0.0,
                sentiment_by_source={},
                sentiment_over_time=[],
                top_senders=[]
            )

        # Basic counts
        total = len(results)
        positive = sum(1 for r in results if r.sentiment_label == 'positive')
        negative = sum(1 for r in results if r.sentiment_label == 'negative')
        neutral = sum(1 for r in results if r.sentiment_label == 'neutral')

        # Averages
        avg_score = sum(r.sentiment_score for r in results) / total
        avg_subj = sum(r.subjectivity for r in results) / total

        # Sentiment by source
        source_stats = defaultdict(
            lambda: {'positive': 0, 'neutral': 0, 'negative': 0})
        for r in results:
            source_stats[r.source][r.sentiment_label] += 1

        # Sentiment over time (group by month)
        time_stats = defaultdict(
            lambda: {'positive': 0, 'neutral': 0, 'negative': 0})
        for r in results:
            month_key = r.timestamp.strftime('%Y-%m')
            time_stats[month_key][r.sentiment_label] += 1

        sentiment_over_time = [
            {
                'date': date,
                'positive': counts['positive'],
                'neutral': counts['neutral'],
                'negative': counts['negative']
            }
            for date, counts in sorted(time_stats.items())
        ]

        # Top senders by average sentiment
        sender_scores = defaultdict(list)
        for r in results:
            sender_scores[r.sender].append(r.sentiment_score)

        top_senders = [
            {
                'sender': sender,
                'avg_score': sum(scores) / len(scores),
                'count': len(scores)
            }
            for sender, scores in sender_scores.items()
        ]
        top_senders.sort(key=lambda x: x['avg_score'], reverse=True)

        return AnalysisSummary(
            phrase=phrase,
            total_messages=total,
            positive_count=positive,
            neutral_count=neutral,
            negative_count=negative,
            avg_sentiment_score=avg_score,
            avg_subjectivity=avg_subj,
            sentiment_by_source=dict(source_stats),
            sentiment_over_time=sentiment_over_time,
            top_senders=top_senders[:10]  # Top 10 senders
        )
