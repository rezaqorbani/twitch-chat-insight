from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract,split, udf
from pyspark.sql.types import StringType
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#import com.datastax.spark.connector.streaming._
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
checkpoint_location = "/mnt/c/Users/Admin/twitch-chat-insight/checkpoint"
spark = SparkSession.builder.appName("TwitchChatProcessing").config("spark.sql.streaming.checkpointLocation", checkpoint_location).getOrCreate()

# Set the log level to WARN (you can use INFO, ERROR, or OFF)
spark.sparkContext.setLogLevel("WARN")

# Define the Cassandra connection properties
cassandra_host = "localhost"  # Update this with your Cassandra host
cassandra_port = "9042"       # Update this with your Cassandra port

# Set Cassandra configuration in Spark
spark.conf.set("spark.cassandra.connection.host", cassandra_host)
spark.conf.set("spark.cassandra.connection.port", cassandra_port)

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
# Filter out records with empty channel_name or username
split_message = split_message.filter((col("channel_name") != "") & (col("username") != ""))

# Define the Cassandra keyspace and table
cassandra_keyspace = "twitch_chat_keyspace"  # Your keyspace name
cassandra_table = "twitch_chat_messages"      # Your table name

# Write the data to Cassandra
query_cassandra=split_message.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", cassandra_keyspace) \
    .option("table", cassandra_table) \
    .option("checkpointLocation", checkpoint_location) \
    .outputMode("append") \
    .start()

#Start the Kafka stream processing
query = split_message.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
# Wait for the stream to terminate

query_cassandra.awaitTermination()
query.awaitTermination()
