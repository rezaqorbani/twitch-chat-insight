# twitch-chat-insight

## Setup

### Kafka

* Get kafka from [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.6.0/kafka_2.13-3.6.0.tgz)

```bash
wget https://dlcdn.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
```

* Start zookeeper and kafka (in separate terminals)

```bash

bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

* Create topic (in separate terminal)

```bash
bin/kafka-topics.sh --create --topic twitch_chat_analyzer --bootstrap-server localhost:9092
```

