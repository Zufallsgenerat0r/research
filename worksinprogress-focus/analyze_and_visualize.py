#!/usr/bin/env python3
"""
Works in Progress Magazine - Author & Topic Analysis with Visualizations
"""

import os
import json
from collections import Counter, defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
import numpy as np

from wip_data import ARTICLES, TOPIC_CATEGORIES, AUTHOR_BIOS, EDITORIAL_TEAM

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_dataframe():
    """Convert article data to a pandas DataFrame."""
    rows = []
    for issue, title, authors, topics, year in ARTICLES:
        for author in authors:
            for topic in topics:
                rows.append({
                    "issue": issue,
                    "title": title,
                    "author": author,
                    "topic": topic,
                    "year": year,
                    "n_authors": len(authors),
                    "n_topics": len(topics),
                })
    return pd.DataFrame(rows)


def get_broad_category(topic):
    """Map a fine-grained topic to a broad category."""
    for cat, topics in TOPIC_CATEGORIES.items():
        if topic in topics:
            return cat
    return "Other"


def analyze_authors(df):
    """Author-level analysis."""
    # Unique articles per author
    author_articles = df.groupby("author")["title"].nunique().sort_values(ascending=False)

    # Topics per author
    author_topics = defaultdict(set)
    for _, row in df.iterrows():
        author_topics[row["author"]].add(row["topic"])

    # Broad categories per author
    author_categories = defaultdict(Counter)
    for _, row in df.iterrows():
        cat = get_broad_category(row["topic"])
        author_categories[row["author"]][cat] += 1

    # Author categorization
    author_cats = {}
    for author, cats in author_categories.items():
        primary = cats.most_common(1)[0][0]
        author_cats[author] = {
            "primary_category": primary,
            "all_categories": dict(cats),
            "article_count": author_articles.get(author, 0),
            "topic_breadth": len(author_topics[author]),
        }

    return author_articles, author_topics, author_cats


def analyze_topics(df):
    """Topic-level analysis."""
    topic_counts = df.groupby("topic")["title"].nunique().sort_values(ascending=False)
    category_counts = Counter()
    for _, row in df.iterrows():
        cat = get_broad_category(row["topic"])
        category_counts[cat] += 1

    # Topics by year
    topics_by_year = df.groupby(["year", "topic"])["title"].nunique().reset_index()
    topics_by_year.columns = ["year", "topic", "count"]

    return topic_counts, category_counts, topics_by_year


def plot_top_authors(author_articles):
    """Bar chart of most prolific authors."""
    top = author_articles.head(20)
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = sns.color_palette("viridis", len(top))
    bars = ax.barh(range(len(top)), top.values, color=colors)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top.index, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Number of Articles", fontsize=12)
    ax.set_title("Works in Progress: Most Prolific Authors", fontsize=14, fontweight="bold")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, val in zip(bars, top.values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_top_authors.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 01_top_authors.png")


def plot_topic_distribution(topic_counts):
    """Bar chart of topic frequency."""
    top = topic_counts.head(20)
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = sns.color_palette("magma", len(top))
    bars = ax.barh(range(len(top)), top.values, color=colors)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top.index, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Number of Articles Tagged", fontsize=12)
    ax.set_title("Works in Progress: Most Common Topics", fontsize=14, fontweight="bold")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, val in zip(bars, top.values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_topic_distribution.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 02_topic_distribution.png")


def plot_category_pie(category_counts):
    """Pie chart of broad categories."""
    labels = list(category_counts.keys())
    values = list(category_counts.values())

    # Sort by size
    sorted_pairs = sorted(zip(values, labels), reverse=True)
    values, labels = zip(*sorted_pairs)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = sns.color_palette("Set2", len(labels))
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='%1.1f%%',
        colors=colors, startangle=140,
        pctdistance=0.85
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)

    ax.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
    ax.set_title("Works in Progress: Article Categories", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_category_pie.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 03_category_pie.png")


def plot_topics_over_time(df):
    """Stacked area chart of broad categories over time."""
    df_copy = df.copy()
    df_copy["category"] = df_copy["topic"].apply(get_broad_category)

    # Count unique articles per year per category
    yearly = df_copy.groupby(["year", "category"])["title"].nunique().reset_index()
    yearly.columns = ["year", "category", "count"]
    pivot = yearly.pivot(index="year", columns="category", values="count").fillna(0)

    fig, ax = plt.subplots(figsize=(14, 7))
    colors = sns.color_palette("tab10", len(pivot.columns))
    pivot.plot.bar(stacked=True, ax=ax, color=colors, width=0.7)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Number of Articles", fontsize=12)
    ax.set_title("Works in Progress: Topics Over Time", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_topics_over_time.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 04_topics_over_time.png")


def plot_author_topic_heatmap(df):
    """Heatmap of top authors vs broad categories."""
    df_copy = df.copy()
    df_copy["category"] = df_copy["topic"].apply(get_broad_category)

    # Top 15 authors by article count
    top_authors = df_copy.groupby("author")["title"].nunique().nlargest(15).index.tolist()
    filtered = df_copy[df_copy["author"].isin(top_authors)]

    cross = filtered.groupby(["author", "category"])["title"].nunique().reset_index()
    cross.columns = ["author", "category", "count"]
    pivot = cross.pivot(index="author", columns="category", values="count").fillna(0)

    # Sort authors by total
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=True)
    pivot = pivot.drop("total", axis=1)

    fig, ax = plt.subplots(figsize=(14, 9))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=0.5, ax=ax)
    ax.set_title("Works in Progress: Author-Topic Matrix (Top 15 Authors)", fontsize=14, fontweight="bold")
    ax.set_ylabel("")
    ax.set_xlabel("")
    plt.xticks(rotation=35, ha='right', fontsize=9)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_author_topic_heatmap.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 05_author_topic_heatmap.png")


def plot_wordcloud_topics(df):
    """Word cloud of all topics."""
    all_topics = " ".join(df["topic"].tolist())
    wc = WordCloud(width=1200, height=600, background_color="white",
                   colormap="viridis", max_words=50, min_font_size=12)
    wc.generate(all_topics)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title("Works in Progress: Topic Word Cloud", fontsize=16, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_topic_wordcloud.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 06_topic_wordcloud.png")


def plot_articles_per_issue(df):
    """Articles per issue over time."""
    articles_per_issue = df.groupby("issue")["title"].nunique()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(articles_per_issue.index, articles_per_issue.values,
           color=sns.color_palette("coolwarm", len(articles_per_issue)))
    ax.set_xlabel("Issue Number", fontsize=12)
    ax.set_ylabel("Number of Articles", fontsize=12)
    ax.set_title("Works in Progress: Articles Per Issue", fontsize=14, fontweight="bold")
    ax.set_xticks(articles_per_issue.index)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add trend line
    z = np.polyfit(articles_per_issue.index, articles_per_issue.values, 1)
    p = np.poly1d(z)
    ax.plot(articles_per_issue.index, p(articles_per_issue.index),
            "r--", alpha=0.7, linewidth=2, label=f"Trend (slope={z[0]:.2f})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_articles_per_issue.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 07_articles_per_issue.png")


def plot_author_categorization(author_cats):
    """Categorize authors by their primary focus."""
    cat_counts = Counter()
    for author, info in author_cats.items():
        cat_counts[info["primary_category"]] += 1

    fig, ax = plt.subplots(figsize=(10, 7))
    labels = list(cat_counts.keys())
    values = list(cat_counts.values())
    sorted_pairs = sorted(zip(values, labels), reverse=True)
    values, labels = zip(*sorted_pairs)

    colors = sns.color_palette("husl", len(labels))
    bars = ax.barh(range(len(labels)), values, color=colors)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Number of Authors", fontsize=12)
    ax.set_title("Author Categorization by Primary Focus Area", fontsize=14, fontweight="bold")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "08_author_categorization.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 08_author_categorization.png")


def plot_collaboration_network(df):
    """Simple collaboration visualization - co-authorship."""
    coauthored = []
    for issue, title, authors, topics, year in ARTICLES:
        if len(authors) > 1:
            coauthored.append((title, authors, year))

    if not coauthored:
        print("No co-authored articles found")
        return

    fig, ax = plt.subplots(figsize=(14, 8))

    # Collect all collaborating authors
    collab_pairs = []
    for title, authors, year in coauthored:
        for i, a1 in enumerate(authors):
            for a2 in authors[i+1:]:
                collab_pairs.append((a1, a2, title))

    # Create a simple table visualization
    pair_counts = Counter()
    for a1, a2, _ in collab_pairs:
        key = tuple(sorted([a1, a2]))
        pair_counts[key] += 1

    y_pos = 0
    colors = sns.color_palette("Set2", len(coauthored))
    for idx, (title, authors, year) in enumerate(coauthored):
        authors_str = " + ".join(authors)
        short_title = title[:50] + "..." if len(title) > 50 else title
        ax.text(0.02, y_pos, f"{authors_str}", fontsize=9, fontweight='bold',
                transform=ax.transAxes, color=colors[idx % len(colors)])
        ax.text(0.5, y_pos, f'"{short_title}" ({year})', fontsize=8,
                transform=ax.transAxes, color='#333333')
        y_pos -= 0.04

    ax.axis('off')
    ax.set_title("Works in Progress: Co-Authored Articles", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "09_collaborations.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: 09_collaborations.png")


def generate_summary_json(author_articles, author_cats, topic_counts, category_counts):
    """Generate a JSON summary of the analysis."""
    summary = {
        "total_articles": len(set((a[0], a[1]) for a in ARTICLES)),
        "total_issues": len(set(a[0] for a in ARTICLES)),
        "total_unique_authors": len(set(a for art in ARTICLES for a in art[2])),
        "years_covered": sorted(set(a[4] for a in ARTICLES)),
        "top_10_authors": {
            name: int(count) for name, count in author_articles.head(10).items()
        },
        "top_10_topics": {
            name: int(count) for name, count in topic_counts.head(10).items()
        },
        "broad_categories": dict(category_counts),
        "author_categorization": {
            author: info for author, info in
            sorted(author_cats.items(), key=lambda x: -x[1]["article_count"])[:20]
        },
        "editorial_team": EDITORIAL_TEAM,
    }

    path = os.path.join(OUTPUT_DIR, "analysis_summary.json")

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(path, "w") as f:
        json.dump(summary, f, indent=2, cls=NpEncoder)
    print(f"Created: analysis_summary.json")
    return summary


def main():
    print("=" * 60)
    print("Works in Progress Magazine - Analysis & Visualization")
    print("=" * 60)

    # Build DataFrame
    df = build_dataframe()
    print(f"\nDataset: {len(ARTICLES)} articles across {df['issue'].nunique()} issues")
    print(f"Unique authors: {df['author'].nunique()}")
    print(f"Unique topics: {df['topic'].nunique()}")
    print(f"Years: {sorted(df['year'].unique())}")

    # Analyze
    author_articles, author_topics, author_cats = analyze_authors(df)
    topic_counts, category_counts, topics_by_year = analyze_topics(df)

    # Print top authors
    print("\n--- Top 10 Most Prolific Authors ---")
    for name, count in author_articles.head(10).items():
        topics = ", ".join(sorted(author_topics[name])[:5])
        print(f"  {name}: {count} articles | Topics: {topics}")

    # Print topic distribution
    print("\n--- Top 10 Topics ---")
    for topic, count in topic_counts.head(10).items():
        print(f"  {topic}: {count} articles")

    # Print author categorization
    print("\n--- Author Categorization (Top 15) ---")
    sorted_authors = sorted(author_cats.items(), key=lambda x: -x[1]["article_count"])
    for author, info in sorted_authors[:15]:
        bio = AUTHOR_BIOS.get(author, "")
        print(f"  {author}")
        print(f"    Primary: {info['primary_category']} | "
              f"Articles: {info['article_count']} | "
              f"Topic breadth: {info['topic_breadth']}")
        if bio:
            print(f"    Bio: {bio}")

    # Generate visualizations
    print("\n--- Generating Visualizations ---")
    plot_top_authors(author_articles)
    plot_topic_distribution(topic_counts)
    plot_category_pie(category_counts)
    plot_topics_over_time(df)
    plot_author_topic_heatmap(df)
    plot_wordcloud_topics(df)
    plot_articles_per_issue(df)
    plot_author_categorization(author_cats)
    plot_collaboration_network(df)

    # Generate JSON summary
    summary = generate_summary_json(author_articles, author_cats, topic_counts, category_counts)

    print("\n" + "=" * 60)
    print("Analysis complete! Generated 9 visualizations and summary JSON.")
    print("=" * 60)

    return summary


if __name__ == "__main__":
    main()
