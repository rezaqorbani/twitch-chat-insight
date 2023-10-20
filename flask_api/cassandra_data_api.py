# Import libraries
from flask import Flask, jsonify
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext

import os

app = Flask(__name__)

# Connect Spark with Cassandra
checkpoint_location = "./checkpoint/"
if not os.path.exists(checkpoint_location):
    os.makedirs(checkpoint_location)


@app.route('/')
def get_latest_row():
    spark = SparkSession.builder.appName("TwitchChatProcessing").config("spark.sql.streaming.checkpointLocation", checkpoint_location).getOrCreate()
        
    # Read recent data from Cassandra table (Replace 'keyspace' and 'table' with your keyspace and table name)
    df = spark.read.format("org.apache.spark.sql.cassandra").options(table="twitch_chat_messages", keyspace="twitch_chat_keyspace").load()
    
    # Use Spark SQL to get the latest row considering your table has a timestamp named 'timestamp'
    result = df.orderBy(df.timestamp.desc()).limit(1)
    
    # Convert pyspark DataFrame to json
    result = [row.asDict() for row in result.collect()]

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
