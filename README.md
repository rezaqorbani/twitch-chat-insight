# twitch-chat-insight
Twitch chat insight helps to see the sentiment of the 'chat' in a give Twitch livestream in real-time. The sentiment is represented as a emoji and is displayed alongside the stream using a Chrome extension.

## Setup

<!-- ### AstraPy Requirements

```bash
pip install astrapy

pip install appengine-python-standard
``` -->
* make sure to have a venev activated and then install the requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

* change the name of the file `.env.example` to `.env` and keep the values as they are or change them to your own values

### Kafka

* Get kafka from [here](https://kafka.apache.org/downloads)

```bash
wget https://dlcdn.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
```

* (optionl, relevant to mac) Build the project first if necessary

```bash
./gradlew jar -PscalaVersion=2.13.11
```

* Start zookeeper and kafka (in separate terminals)

```bash
cd path/to/kafka_2.13-3.6.0/
bin/zookeeper-server-start.sh config/zookeeper.properties
```

```bash
cd path/to/kafka_2.13-3.6.0/
bin/kafka-server-start.sh config/server.properties
```

* Create topic (in separate terminal), if not already created

```bash
bin/kafka-topics.sh --create --topic twitch_chat_analyzer --bootstrap-server localhost:9092
```

### Producer

* start producer (in separate terminal)

```bash
python ingestion/producer.py
```

<!-- ### (optional) Consumer

* start consumer (in separate terminal)

```bash
python ingestion/consumer.py
``` -->

<!-- ### Spark

* Start Spark (in separate terminal)

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /path/to/project/inference/pysparkScript.py 
``` -->

### Cassandra

* Get cassandra from [here](https://cassandra.apache.org/download/)
* Start Cassandra before running Spark (in separate terminal):

```bash
cd path/to/cassandra
bin/cassandra
```

* start cqlsh (in separate terminal):

```bash
cd path/to/cassandra
bin/cqlsh
```

* In cqlsh create a keyspace and table schema for example(Primary key can be changed):
  
```sql
CREATE KEYSPACE IF NOT EXISTS twitch_chat_keyspace
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE twitch_chat_keyspace;

CREATE TABLE IF NOT EXISTS twitch_chat_messages (
    channel_name TEXT,
    message TEXT,
    username TEXT,
    sentiment TEXT,
    timestamp TIMESTAMP,
    PRIMARY KEY (channel_name, username)
); 
```

### Consumer

* Run the pysparkScriptLocal.py

```bash
spark-submit --packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0  ./processing/pysparkScriptLocal.py
```

* (optional) In cqlsh you can query the data in the table by using:

```sql
SELECT * FROM twitch_chat_messages; 
```

### API

* Start the REST API (in separate terminal):

```bash
spark-submit --packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0  ./flask/cassandra_rest_api.py
```

* You can now get the lastest row from the server with the REST API:

```bash
curl http://localhost:5000/
```
