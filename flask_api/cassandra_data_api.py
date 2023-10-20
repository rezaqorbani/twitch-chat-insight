# Import libraries
from flask import Flask, jsonify
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

app = Flask(__name__)

# Connect spark with cassandra
spark = SparkSession.builder \
    .appName('SparkCassandraApp') \
    .config('spark.cassandra.connection.host', '127.0.0.1') \
    .config('spark.cassandra.connection.port', '9042') \
    .getOrCreate()

# Read data from Cassandra table. Replace 'keyspace' and 'table' with your keyspace and table name
df = spark.read.format("org.apache.spark.sql.cassandra").options(table="table", keyspace="keyspace").load()

# Define a route '/'
@app.route('/')
def get_latest_row():
    # Use spark sql to get the latest row considering your table has a timestamp named 'time'
    result = df.orderBy(df.time.desc()).limit(1)
    
    # Convert pyspark DataFrame to json
    result = [row.asDict() for row in result.collect()]
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)