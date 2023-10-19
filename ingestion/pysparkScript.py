from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, split, udf
from pyspark.sql.types import StringType
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from astrapy.client import create_astra_client
import uuid

# Database information
ASTRA_DB_ID = 'c59f29c8-a71a-430b-a1e5-bc1a7045a21e'
ASTRA_DB_REGION = 'us-east1'
ASTRA_DB_APPLICATION_TOKEN = 'AstraCS:nLrfGSfCZySFpUKEoPKevCRP:ddfaa3d6111b7510e4b3dd423c05c025e3f179b4f6604eab38724b9c85302f29'
ASTRA_DB_KEYSPACE = 'keyspace_twitch_chat_insight'

TABLE_NAME = 'twitch_inputs_table'

# Database client
astra_client = create_astra_client(astra_database_id=ASTRA_DB_ID,
                                 astra_database_region=ASTRA_DB_REGION,
                                 astra_application_token=ASTRA_DB_APPLICATION_TOKEN)

def write_to_cassandra(channel_name, message, username, sentiment):
    row_definition = {"channel_name": channel_name,
                      "message": message,
                      "username": username,
                      "sentiment": sentiment,
                      "timestamp": str(uuid.uuid1()),
                      }
    row = astra_client.rest.add_row(keyspace=ASTRA_DB_KEYSPACE,
                                    table=TABLE_NAME,
                                    row=row_definition)

# Define your custom emote values
twitch_emotes = {
    '<3': 0.4,
    '4head': 1,
    'LUL':1.5,
    'LuL':1.5,
    'LULW':1.5,
    'KEKW':1.5,
    'POG':1.5,
    'pog':1.5,
    'Pog':1.5,
    'OMEGALUL':1.5,
    'POGGERS':1.5,
    'EZ':1.5,
    'GIGA':1.5,
    'CHAD':1.5,
    'babyrage': -0.7,
    'biblethump': -0.7,
    'blessrng': 0.7,
    'bloodtrail': 0.7,
    'coolstorybob': -1,
    'residentsleeper': -1,
    'kappa': 0.5,
    'lul': 1,
    'pogchamp': 1.5,
    'heyguys': 1,
    'wutface': -1.5,
    'kreygasm': 1,
    'seemsgood': 0.7,
    'kappapride': 0.7,
    'feelsgoodman': 1,
    'notlikethis': -1
}

# Create a SparkSession
spark = SparkSession.builder.appName("TwitchChatProcessing").getOrCreate()
# Set the log level to WARN (you can use INFO, ERROR, or OFF)
spark.sparkContext.setLogLevel("WARN")

# Define the Kafka stream
kafka_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "twitch_chat_analyzer") \
    .load()

# Convert the Kafka message value to a string
kafka_stream = kafka_stream.selectExpr("CAST(value AS STRING) as raw_message")

# Extract the message, channel name, and username using regular expressions
split_message = kafka_stream.select(
    regexp_extract(col("raw_message"), r'PRIVMSG (\#\w+) :(.*)\r\n', 1).alias("channel_name"),
    regexp_extract(col("raw_message"), r'PRIVMSG (\#\w+) :(.*)\r\n', 2).alias("message"),
    regexp_extract(col("raw_message"), r':(\w+)!', 1).alias("username")
)

# Define a UDF for sentiment analysis
def get_sentiment(message):
    analyzer = SentimentIntensityAnalyzer()
    # Update the analyzer's lexicon with custom emote values
    analyzer.lexicon.update(twitch_emotes)
    sentiment = analyzer.polarity_scores(message)

    if sentiment["compound"] >= 0.05:
        return "positive"
    elif sentiment["compound"] <= -0.05:
        return "negative"
    else:
        return "neutral"

# Create a UDF from the sentiment analysis function
sentiment_udf = udf(get_sentiment, StringType())

# Add the calculated sentiment as a new column
split_message = split_message.withColumn("sentiment", sentiment_udf(col("message")))

# Output the results to the console (you can replace this with your desired sink)
query = split_message \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Wait for the stream to terminate (you can stop it with Ctrl+C)
query.awaitTermination()

