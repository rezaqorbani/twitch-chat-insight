from kafka import KafkaConsumer

consumer = KafkaConsumer('twitch_chat_analyzer', bootstrap_servers='localhost:9092')
for msg in consumer:
    print(msg.value)