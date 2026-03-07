from fetchers import GmailFetcher, ChatFetcher
from analyzer import SentimentAnalyzer
from models import SentimentResult, AnalysisConstraints
from visualizer import SentimentVisualizer
import pandas as pd
from typing import List
import os
from datetime import datetime


class SentimentAnalyzerApp:
    """Main application - ties everything together"""

    def __init__(self):
        print("Initializing Gmail and Chat fetchers...")
        self.gmail_fetcher = GmailFetcher()
        self.chat_fetcher = ChatFetcher()
        self.analyzer = SentimentAnalyzer()
        self.visualizer = SentimentVisualizer()
        self.csv_file = 'results.csv'
        print(" Ready!\n")

    def run(self):
        """Main application loop"""
        print("=== Gmail & Google Chat Sentiment Analyzer (Enhanced) ===\n")

        while True:
            phrase = input(
                "Enter phrase to search (or 'quit' to exit): ").strip()

            if phrase.lower() == 'quit':
                print("Goodbye!")
                break

            if not phrase:
                print("Please enter a valid phrase.\n")
                continue

            print(f"\n🔍 Searching for '{phrase}'...")

            # Fetch messages from both sources
            print(" Fetching Gmail messages...")
            gmail_messages = self.gmail_fetcher.fetch_by_keyword(phrase)

            print(" Fetching Google Chat messages...")
            chat_messages = self.chat_fetcher.fetch_by_keyword(phrase)

            all_messages = gmail_messages + chat_messages

            if not all_messages:
                print(f" No messages found containing '{phrase}'\n")
                continue

            print(
                f"Found {len(all_messages)} messages ({len(gmail_messages)} Gmail, {len(chat_messages)} Chat)")

            # Analyze sentiment
            print("🤖 Analyzing sentiment...")
            results = self.analyzer.analyze_messages(all_messages, phrase)

            # Ask user about constraints
            results = self.apply_user_constraints(results)

            if not results:
                print(" No results match your constraints.\n")
                continue

            # Generate summary
            summary = self.analyzer.generate_summary(results, phrase)

            # Save to CSV
            self.save_results(results)

            # Display text summary
            self.visualizer.create_simple_summary(summary)

            # Ask about visualization
            viz_choice = input(
                "Would you like to see visualizations? (yes/no): ").strip().lower()
            if viz_choice in ['yes', 'y']:
                print("\n Generating visualizations...")
                self.visualizer.create_dashboard(summary, results)

            print()

    def apply_user_constraints(self, results: List[SentimentResult]) -> List[SentimentResult]:
        """
        Ask user for constraints and filter results
        """
        print("\n  Apply constraints? (press Enter to skip)")

        constraints = AnalysisConstraints()

        # Sentiment label filter
        filter_labels = input(
            "  Filter by sentiment (positive/neutral/negative, comma-separated, or Enter to skip): ").strip()
        if filter_labels:
            constraints.sentiment_labels = [
                l.strip().lower() for l in filter_labels.split(',')]

        # Source filter
        filter_sources = input(
            "  Filter by source (gmail/chat, comma-separated, or Enter to skip): ").strip()
        if filter_sources:
            constraints.sources = [s.strip().lower()
                                   for s in filter_sources.split(',')]

        # Score range
        min_score = input(
            "  Minimum sentiment score (-1 to 1, or Enter to skip): ").strip()
        if min_score:
            try:
                constraints.min_sentiment_score = float(min_score)
            except ValueError:
                print("   Invalid score, skipping...")

        max_score = input(
            "  Maximum sentiment score (-1 to 1, or Enter to skip): ").strip()
        if max_score:
            try:
                constraints.max_sentiment_score = float(max_score)
            except ValueError:
                print("    Invalid score, skipping...")

        # Subjectivity filter
        min_subj = input(
            "  Minimum subjectivity (0 to 1, or Enter to skip): ").strip()
        if min_subj:
            try:
                constraints.min_subjectivity = float(min_subj)
            except ValueError:
                print("    Invalid value, skipping...")

        # Apply constraints
        filtered = self.analyzer.filter_results(results, constraints)

        if len(filtered) < len(results):
            print(f"\n Filtered: {len(results)} → {len(filtered)} messages")

        return filtered

    def save_results(self, results: List[SentimentResult]):
        """Save results to CSV file with clean formatting"""

        # Convert results to clean format
        clean_data = []
        for r in results:
            clean_data.append({
                'Date': r.timestamp.strftime('%Y-%m-%d'),
                'Time': r.timestamp.strftime('%H:%M:%S'),
                'Source': r.source.upper(),
                'Sender': self._clean_sender(r.sender),
                'Phrase': r.phrase,
                'Sentiment': r.sentiment_label.capitalize(),
                'Score': f"{r.sentiment_score:.2f}",
                'Subjectivity': f"{r.subjectivity:.2f}",
                'Message Preview': self._truncate_text(r.text, 100),
                'Message ID': r.message_id
            })

        df = pd.DataFrame(clean_data)

        # Reorder columns for better readability
        column_order = [
            'Date', 'Time', 'Source', 'Sender', 'Phrase',
            'Sentiment', 'Score', 'Subjectivity',
            'Message Preview', 'Message ID'
        ]
        df = df[column_order]

        # Append to existing file or create new
        if os.path.exists(self.csv_file):
            df.to_csv(self.csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.csv_file, index=False)

        print(f" Results saved to {self.csv_file}")

    def _clean_sender(self, sender: str) -> str:
        """Extract clean email or name from sender"""
        # Extract email if in format "Name <email@example.com>"
        if '<' in sender and '>' in sender:
            email = sender.split('<')[1].split('>')[0]
            return email
        return sender[:50]  # Truncate long names

    def _truncate_text(self, text: str, max_length: int = 100) -> str:
        """Truncate text with ellipsis"""
        text = text.strip().replace('\n', ' ').replace('\r', '')
        text = ' '.join(text.split())  # Remove extra whitespace
        if len(text) > max_length:
            return text[:max_length] + '...'
        return text


if __name__ == "__main__":
    app = SentimentAnalyzerApp()
    app.run()
