import matplotlib.pyplot as plt
import pandas as pd
from models import AnalysisSummary, SentimentResult
from typing import List
import seaborn as sns
from datetime import datetime

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class SentimentVisualizer:
    """Creates visualizations for sentiment analysis results"""

    def __init__(self):
        self.colors = {
            'positive': '#4CAF50',  # Green
            'neutral': '#9E9E9E',   # Gray
            'negative': '#F44336'   # Red
        }

    def create_dashboard(self, summary: AnalysisSummary, results: List[SentimentResult]):
        """
        Create comprehensive visualization dashboard
        """
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(
            f'Sentiment Analysis Dashboard: "{summary.phrase}"', fontsize=16, fontweight='bold')

        # 1. Overall sentiment distribution (pie chart)
        ax1 = plt.subplot(2, 3, 1)
        self._plot_sentiment_distribution(summary, ax1)

        # 2. Sentiment by source (stacked bar)
        ax2 = plt.subplot(2, 3, 2)
        self._plot_sentiment_by_source(summary, ax2)

        # 3. Sentiment over time (line chart)
        ax3 = plt.subplot(2, 3, 3)
        self._plot_sentiment_over_time(summary, ax3)

        # 4. Score distribution (histogram)
        ax4 = plt.subplot(2, 3, 4)
        self._plot_score_distribution(results, ax4)

        # 5. Top senders (horizontal bar)
        ax5 = plt.subplot(2, 3, 5)
        self._plot_top_senders(summary, ax5)

        # 6. Subjectivity vs Sentiment (scatter)
        ax6 = plt.subplot(2, 3, 6)
        self._plot_subjectivity_vs_sentiment(results, ax6)

        plt.tight_layout()

        # Save and show
        filename = f"sentiment_analysis_{summary.phrase.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n📊 Visualization saved as: {filename}")
        plt.show()

    def _plot_sentiment_distribution(self, summary: AnalysisSummary, ax):
        """Pie chart of overall sentiment distribution"""
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [summary.positive_count,
                 summary.neutral_count, summary.negative_count]
        colors = [self.colors['positive'],
                  self.colors['neutral'], self.colors['negative']]

        ax.pie(sizes, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=90)
        ax.set_title('Overall Sentiment Distribution')

    def _plot_sentiment_by_source(self, summary: AnalysisSummary, ax):
        """Stacked bar chart of sentiment by source"""
        sources = list(summary.sentiment_by_source.keys())
        positive = [summary.sentiment_by_source[s]['positive']
                    for s in sources]
        neutral = [summary.sentiment_by_source[s]['neutral'] for s in sources]
        negative = [summary.sentiment_by_source[s]['negative']
                    for s in sources]

        x = range(len(sources))
        ax.bar(x, positive, label='Positive', color=self.colors['positive'])
        ax.bar(x, neutral, bottom=positive, label='Neutral',
               color=self.colors['neutral'])
        ax.bar(x, negative, bottom=[p+n for p, n in zip(positive, neutral)],
               label='Negative', color=self.colors['negative'])

        ax.set_xlabel('Source')
        ax.set_ylabel('Message Count')
        ax.set_title('Sentiment by Source')
        ax.set_xticks(x)
        ax.set_xticklabels([s.upper() for s in sources])
        ax.legend()

    def _plot_sentiment_over_time(self, summary: AnalysisSummary, ax):
        """Line chart of sentiment trends over time"""
        if not summary.sentiment_over_time:
            ax.text(0.5, 0.5, 'No time data available',
                    ha='center', va='center')
            ax.set_title('Sentiment Over Time')
            return

        dates = [item['date'] for item in summary.sentiment_over_time]
        positive = [item['positive'] for item in summary.sentiment_over_time]
        neutral = [item['neutral'] for item in summary.sentiment_over_time]
        negative = [item['negative'] for item in summary.sentiment_over_time]

        ax.plot(dates, positive, marker='o', label='Positive',
                color=self.colors['positive'], linewidth=2)
        ax.plot(dates, neutral, marker='s', label='Neutral',
                color=self.colors['neutral'], linewidth=2)
        ax.plot(dates, negative, marker='^', label='Negative',
                color=self.colors['negative'], linewidth=2)

        ax.set_xlabel('Time Period')
        ax.set_ylabel('Message Count')
        ax.set_title('Sentiment Trends Over Time')
        ax.legend()
        ax.tick_params(axis='x', rotation=45)

    def _plot_score_distribution(self, results: List[SentimentResult], ax):
        """Histogram of sentiment score distribution"""
        scores = [r.sentiment_score for r in results]

        ax.hist(scores, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        ax.axvline(x=0, color='black', linestyle='--',
                   linewidth=1, label='Neutral (0)')
        ax.axvline(x=sum(scores)/len(scores), color='red', linestyle='--',
                   linewidth=2, label=f'Average ({sum(scores)/len(scores):.2f})')

        ax.set_xlabel('Sentiment Score')
        ax.set_ylabel('Frequency')
        ax.set_title('Sentiment Score Distribution')
        ax.legend()

    def _plot_top_senders(self, summary: AnalysisSummary, ax):
        """Horizontal bar chart of top senders by sentiment"""
        if not summary.top_senders:
            ax.text(0.5, 0.5, 'No sender data available',
                    ha='center', va='center')
            ax.set_title('Top Senders by Sentiment')
            return

        top_10 = summary.top_senders[:10]
        senders = [s['sender'][:30] for s in top_10]  # Truncate long emails
        scores = [s['avg_score'] for s in top_10]
        colors_list = [self.colors['positive'] if s > 0.1 else
                       self.colors['negative'] if s < -0.1 else
                       self.colors['neutral'] for s in scores]

        y_pos = range(len(senders))
        ax.barh(y_pos, scores, color=colors_list)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(senders)
        ax.set_xlabel('Average Sentiment Score')
        ax.set_title('Top 10 Senders by Average Sentiment')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

    def _plot_subjectivity_vs_sentiment(self, results: List[SentimentResult], ax):
        """Scatter plot of subjectivity vs sentiment score"""
        scores = [r.sentiment_score for r in results]
        subjectivity = [r.subjectivity for r in results]
        colors_list = [self.colors[r.sentiment_label] for r in results]

        ax.scatter(scores, subjectivity, c=colors_list, alpha=0.6, s=50)
        ax.set_xlabel('Sentiment Score')
        ax.set_ylabel('Subjectivity (0=Objective, 1=Subjective)')
        ax.set_title('Sentiment vs Subjectivity')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
        ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=0.5)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['positive'], label='Positive'),
            Patch(facecolor=self.colors['neutral'], label='Neutral'),
            Patch(facecolor=self.colors['negative'], label='Negative')
        ]
        ax.legend(handles=legend_elements)

    def create_simple_summary(self, summary: AnalysisSummary):
        """Create a simple text-based summary matrix"""
        print("\n" + "="*70)
        print(f"SENTIMENT ANALYSIS MATRIX: '{summary.phrase}'")
        print("="*70)

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Messages: {summary.total_messages}")
        print(
            f"   Average Sentiment: {summary.avg_sentiment_score:.3f} (-1 for Negative to +1 for Positive)")
        print(
            f"   Average Subjectivity: {summary.avg_subjectivity:.3f} (0 for Pure Facts  to 1 for Pure Opinions)")

        print(f"\n🎯 SENTIMENT BREAKDOWN:")
        print(
            f"   ✅ Positive: {summary.positive_count} ({summary.positive_count/summary.total_messages*100:.1f}%)")
        print(
            f"   ⚪ Neutral:  {summary.neutral_count} ({summary.neutral_count/summary.total_messages*100:.1f}%)")
        print(
            f"   ❌ Negative: {summary.negative_count} ({summary.negative_count/summary.total_messages*100:.1f}%)")

        print(f"\n📍 BY SOURCE:")
        for source, counts in summary.sentiment_by_source.items():
            total_source = sum(counts.values())
            print(f"   {source.upper()}:")
            print(
                f"      Positive: {counts['positive']} ({counts['positive']/total_source*100:.1f}%)")
            print(
                f"      Neutral:  {counts['neutral']} ({counts['neutral']/total_source*100:.1f}%)")
            print(
                f"      Negative: {counts['negative']} ({counts['negative']/total_source*100:.1f}%)")

        if summary.top_senders:
            print(f"\n👥 TOP 5 SENDERS:")
            for i, sender in enumerate(summary.top_senders[:5], 1):
                print(f"   {i}. {sender['sender'][:40]}")
                print(
                    f"      Avg Sentiment: {sender['avg_score']:.3f} | Messages: {sender['count']}")

        print("\n" + "="*70 + "\n")
