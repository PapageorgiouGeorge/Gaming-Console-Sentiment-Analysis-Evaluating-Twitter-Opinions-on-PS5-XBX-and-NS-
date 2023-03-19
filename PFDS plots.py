#Georgios Papageorgiou
#Simela Moisiadoy

import mysql.connector
import pandas as pd
import nltk
from wordcloud import WordCloud
import numpy as np
import matplotlib.pyplot as plt

# Connect to MySQL Server
connection = mysql.connector.connect(host="localhost", user="root", password="", database="twitter")


# Setting our Dataframe with a Fuction.
def sqldf(query):
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=['SENTIMENT', 'TWEET_TEXT', 'HASHTAGS', 'NUM_FOLLOWERS'])
    return df


# Create Dataframes for each of our gaming console category and one dataframe with the sum of the dataset.
dfall = sqldf(
    "SELECT SENTIMENT, TWEET_TEXT, HASHTAGS, NUM_FOLLOWERS FROM `twitter`.tweets ;")  # Dataframe with the Sum of the dataset.
dfps5 = sqldf(
    "SELECT SENTIMENT, TWEET_TEXT, HASHTAGS, NUM_FOLLOWERS FROM `twitter`.tweets WHERE HASHTAGS LIKE '%PS5%' ;")  # Dataframe with PS5 data.
dfxbox = sqldf(
    "SELECT SENTIMENT, TWEET_TEXT, HASHTAGS, NUM_FOLLOWERS FROM `twitter`.tweets WHERE HASHTAGS LIKE '%XBOXSERIESX%' ;")  # Dataframe with XboxSeriesX data.
dfnintendo = sqldf(
    "SELECT SENTIMENT, TWEET_TEXT, HASHTAGS, NUM_FOLLOWERS FROM `twitter`.tweets WHERE HASHTAGS LIKE '%NINTENDOSWITCH%' ;")  # Dataframe with NintendoSwitch data.


# print(dfps5)
# print(dfxbox)
# print(dfnintendo)

# Creating a fuction tracking the sentiment for each tweet and calculate the percentage for each sentiment in our dataset.
def Counter(df):
    positives = 0
    negatives = 0
    neutrals = 0
    famous_positives = 0
    famous_negatives = 0
    famous_neutrals = 0
    for row in range(0, len(df['SENTIMENT'])):  # In General for all of the dataset
        if df['SENTIMENT'][row] == {'POSITIVE'}:
            positives = positives + 1
        elif df['SENTIMENT'][row] == {'NEGATIVE'}:
            negatives = 1 + negatives
        else:
            neutrals = 1 + neutrals

        if dfall['NUM_FOLLOWERS'][row] > 10000:  # Tracking accounts with more than 10000 followers
            if dfall['SENTIMENT'][row] == {'POSITIVE'}:
                famous_positives = famous_positives + 1
            elif dfall['SENTIMENT'][row] == {'NEGATIVE'}:
                famous_negatives = 1 + famous_negatives
            else:
                famous_neutrals = 1 + famous_neutrals

    perc_pos = positives / (positives + negatives + neutrals)
    perc_neg = negatives / (positives + negatives + neutrals)
    perc_neu = neutrals / (positives + negatives + neutrals)

    famous_perc_pos = famous_positives / (famous_positives + famous_negatives + famous_neutrals)
    famous_perc_neg = famous_negatives / (famous_positives + famous_negatives + famous_neutrals)
    famous_perc_neu = famous_neutrals / (famous_positives + famous_negatives + famous_neutrals)
    return perc_pos, perc_neg, perc_neu, famous_perc_pos, famous_perc_neg, famous_perc_neu


#print(Counter(dfps5))
#print(Counter(dfxbox))
#print(Counter(dfnintendo))

#Creating a pie chart about the sentiment from the sum of the dataset
labels = 'Positive', 'Negative', 'Neutral'
sizes = [Counter(dfall)[0], Counter(dfall)[1], Counter(dfall)[2]]
explode = (0.07, 0.01, 0.01)

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title("Pie chart about the sum of the dataset", fontweight='bold')
plt.show()

# Creating a Word Cloud from the most frequent words in our dataset.
stop = nltk.corpus.stopwords.words('english')
stop.append('URL')
stop.append('amp')
plt.subplots(figsize=(5, 4))
wordcloud = WordCloud(background_color='white', stopwords=stop, width=1000, height=800).generate(
    " ".join(dfall['TWEET_TEXT']))
plt.imshow(wordcloud)
plt.title('Word Cloud with the most frequent words', fontweight='bold')
plt.axis('off')
plt.show()

# Creating side by side percentage bar plot about the polarities for each gaming console.
barWidth = 0.25
bars1 = [Counter(dfps5)[0], Counter(dfxbox)[0], Counter(dfnintendo)[0]]
bars2 = [Counter(dfps5)[1], Counter(dfxbox)[1], Counter(dfnintendo)[1]]
bars3 = [Counter(dfps5)[2], Counter(dfxbox)[2], Counter(dfnintendo)[2]]

r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]

plt.bar(r1, bars1, color='#7f6d5f', width=barWidth, edgecolor='white', label='Positive')
plt.bar(r2, bars2, color='#557f2d', width=barWidth, edgecolor='white', label='Neutral')
plt.bar(r3, bars3, color='#2d7f5e', width=barWidth, edgecolor='white', label='Negative')
plt.title('Side by side percentage bar plot with the polarities for every gaming console', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], ['PS5', 'XBOXSERIESX', 'NINTENDOSWITCH'])
plt.legend()
plt.show()

# Creating Stacked bar plot about the polarities for each gaming console from accounts with more than 10000 followers.
plotfamous = pd.DataFrame({
    "Negatives": [Counter(dfps5)[5], Counter(dfxbox)[5], Counter(dfnintendo)[5]],
    "Neutral": [Counter(dfps5)[4], Counter(dfxbox)[4], Counter(dfnintendo)[4]],
    "Positives": [Counter(dfps5)[3], Counter(dfxbox)[3], Counter(dfnintendo)[3]]
}, index=["PS5", "XboxSeriesX", "NintendoSwitch"]
)
plotfamous.plot(kind='bar', stacked=True)
plt.title("Stacked bar plot for polarity from tweets by famous people", fontweight='bold')
plt.xlabel("Console")
plt.ylabel("Percentage")
plt.show()
