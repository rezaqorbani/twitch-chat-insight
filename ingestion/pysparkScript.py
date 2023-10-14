from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, split

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

# Output the results to the console (you can replace this with your desired sink)
query = split_message \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Wait for the stream to terminate (you can stop it with Ctrl+C)
query.awaitTermination()

