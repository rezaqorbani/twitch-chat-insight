# twitch-chat-insight

## Setup

### AstraPy Requirements

```bash
pip install astrapy

pip install appengine-python-standard
```

### Kafka

* Get kafka from [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.6.0/kafka_2.13-3.6.0.tgz)

```bash
wget https://dlcdn.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
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
### Consumer

* start consumer (in separate terminal)

```bash
python ingestion/consumer.py
```

### Spark

* Start Spark (in separate terminal)

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /path/to/project/inference/pysparkScript.py 
```

### Cassandra(if used locally)
* Install cassandra
* Start Cassandra before running Spark(in separate terminal)
* start cqlsh(in separate terminal)
* In cqlsh create a keyspace and table schema for example(Primary key can be changed):
```cqlsh
CREATE KEYSPACE IF NOT EXISTS twitch_chat_keyspace
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE twitch_chat_keyspace;

CREATE TABLE IF NOT EXISTS twitch_chat_messages (
    channel_name TEXT,
    message TEXT,
    username TEXT,
    sentiment TEXT,
    PRIMARY KEY (channel_name, username)
); 
```
* start zookeeper, kafka server, producer.py, consumer.py in separate terminals.
* Run the pysparkScriptLocal.py
```bash
spark-submit --packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0  pysparkScriptLocal.py
```
* In cqlsh query the data in the table by using:
```cqlsh
SELECT * FROM twitch_chat_messages; 
```
