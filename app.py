from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import Counter
import re

app = Flask(__name__)

def analyze_sentiment(reviews):
    # Simple sentiment analysis
    return ['Positive' if 'good' in review.lower() else 'Negative' for review in reviews]

def create_pie_chart(sentiment_counts):
    labels = sentiment_counts.index
    sizes = sentiment_counts.values
    plt.figure(figsize=(6, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie chart is a circle
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')

def extract_common_words(reviews):
    common_words = ['good', 'bad', 'improve', 'excellent', 'poor', 'satisfied', 'dissatisfied']
    all_words = ' '.join(reviews).lower()
    word_list = re.findall(r'\b\w+\b', all_words)
    word_counts = Counter(word_list)
    relevant_counts = {word: count for word, count in word_counts.items() if word in common_words}
    return relevant_counts

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    df_reviews = pd.read_csv(file)

    # Ensure 'Review' column exists
    if 'Review' not in df_reviews.columns:
        return "Error: The uploaded file must contain a 'Review' column."

    df_reviews['Sentiment_Label'] = analyze_sentiment(df_reviews['Review'])
    sentiment_counts = df_reviews['Sentiment_Label'].value_counts()
    pie_chart = create_pie_chart(sentiment_counts)

    # Extract common words
    common_word_counts = extract_common_words(df_reviews['Review'])
    common_words_display = ', '.join(f"{word}: {count}" for word, count in common_word_counts.items())

    return render_template('results.html', 
                           pie_chart=pie_chart, 
                           sentiment_counts=sentiment_counts.to_dict(),
                           common_words=common_words_display)

if __name__ == '__main__':
    app.run(debug=True)
