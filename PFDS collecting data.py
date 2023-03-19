#Georgios Papageorgiou
#Simela Moisiadoy

import tweepy as tw
import mysql.connector
import re
from textblob import TextBlob

# Inserting Credentials
CONSUMER_KEY = '33sOuUOYVSkH5aEOlageHz0dA'
CONSUMER_KEY_SECRET = 'l14ovpLo3j2Qn5y62OVBOvAQ5MUD2SO8CxLFIwsKORdfB2VcVu'
ACCESS_TOKEN = '1342134650886565888-YXPBtB7cGc01hUQKZz8RKn7XP56hhF'
ACCESS_TOKEN_SECRET = 'wPdvM0HOiu3aAGJGGvYG4nIafoP56nU1IPp4I4WzbzJ07'

# Connect to MySQL Server
mydb = mysql.connector.connect(host="localhost", user="root", password="", database="twitter")
mycursor = mydb.cursor()
stmt = "SHOW TABLES LIKE 'tweets'"  # Check if table exists.
mycursor.execute(stmt)
result = mycursor.fetchone()
if result:
    print('Table data already exists')
else:  # Create the table, if you run this for first time
    create_table = "CREATE TABLE tweets (ID int(11) NOT NULL AUTO_INCREMENT,USERNAME varchar(28) NOT NULL,NUM_FOLLOWERS int(11) NOT NULL,NUM_TWEETS int(11) NOT NULL,TWEET_TEXT varchar(1000) NOT NULL,NUM_RETWEET int(11) NOT NULL,LIKES int(11) NOT NULL,DATETIME datetime NOT NULL,LOCATION varchar(50) NOT NULL,HASHTAGS varchar(280) NOT NULL,SENTIMENT set('POSITIVE','NEUTRAL','NEGATIVE') NOT NULL, PRIMARY KEY (ID));"
    mycursor.execute(create_table)
    mydb.commit()
    mycursor.execute("SHOW TABLES")


# Making a function that cleaning tweet's text by emoticons, symbols, URLS etc.
def clean(txt):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    clean_txt = emoji_pattern.sub(r'', txt)
    clean_txt = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', clean_txt)
    clean_txt = re.sub(r"[^a-zA-Z0-9,!.?:$%()&/'-]", " ", clean_txt)
    return clean_txt


# Making a function that set polarity to positive/negative/neutral,
# according to sentiment value of the text (using TextBlob)
def sentiment(ctext):
    if TextBlob(ctext).sentiment.polarity > 0:
        pol = 'POSITIVE'
    elif TextBlob(ctext).sentiment.polarity < 0:
        pol = 'NEGATIVE'
    else:
        pol = 'NEUTRAL'
    return pol


# Authenticate Access
auth = tw.OAuthHandler(CONSUMER_KEY, CONSUMER_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tw.API(auth)

# Set our search words, the date that we start our extracting from twitter,
# also use a variable to count how many tweets are inserted,
# and set filter for no downloading retweets.
search_words = "#PS5" + " -filter:retweets"
# We are searching for: PS5, XBOXSERIESX, NINTENDOSWITCH
date_since = "2020-02-06"
count = 0
# Using api.search to collect the tweets
tweets = tw.Cursor(api.search, tweet_mode="extended", q=search_words, lang="en", since=date_since).items(66)

# Set a variable on what exists in our database.
mycursor.execute("SELECT * FROM tweets")
database = mycursor.fetchall()

# Iterate tweets and add them to the database
# Using api.search from above to insert every tweet in out database.
for tweet in tweets:

    clean_text = clean(
        tweet.full_text)  # Set to a variable the clean text from tweet(using the function 'clean' from above).
    username = tweet.user.screen_name  # Set to a variable the username from the tweet.
    num_followers = tweet.user.followers_count  # Set to a variable the number of account’s followers.
    num_tweets = tweet.user.statuses_count  # Set to a variable the number of account’s tweets.
    num_retweets = tweet.retweet_count  # Set to a variable Number of accounts retweets.
    likes = tweet.favorite_count  # Set to a variable how many likes tweet gets so far.
    date = tweet.created_at  # Set to a variable the date that tweet was created.
    location = tweet.user.location  # Set to a variable the location that tweet was created.
    hashtag_list = re.findall(r"#(\w+)", tweet.full_text)  # Finding hashtags
    hashtags = ' '.join([str(elem) for elem in hashtag_list])  # Set to a variable the hashtags that tweet includes.
    polarity = sentiment(clean_text)  # Set the polarity of the tweet (using the function 'sentiment' from above).

    # Add our data variables to our database table.
    sql = "INSERT INTO tweets (USERNAME, NUM_FOLLOWERS, NUM_TWEETS, TWEET_TEXT, NUM_RETWEET, LIKES, DATETIME, LOCATION, HASHTAGS, SENTIMENT) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    data = (username, num_followers, num_tweets, clean_text, num_retweets,
            likes, date, location, hashtags, polarity)
    if data not in database:  # Check for duplicates.
        try:
            mycursor.execute(sql, data)
            mydb.commit()
            count = count + mycursor.rowcount
            print(count, "records inserted.")
        except Exception:  # In case of an error proceed to the next tweet
            pass
