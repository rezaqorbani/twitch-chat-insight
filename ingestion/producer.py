import os
import socket
import logging
import dotenv
from emoji import demojize
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s — %(message)s', datefmt='%Y-%m-%d_%H:%M:%S', handlers=[logging.FileHandler('chat.log', encoding='utf-8')])

dotenv.load_dotenv()
server = os.getenv('SERVER')
port = int(os.getenv('PORT'))
nickname = os.getenv('USERNAME')
token = os.getenv('TWITCH_OAUTH_TOKEN')

# Define a list of channels you want to listen to
channels = ['#caedrel' ]

def main():
    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\r\n".encode())
    sock.send(f"NICK {nickname}\r\n".encode())

    # Join all the specified channels
    for channel in channels:
        sock.send(f"JOIN {channel}\r\n".encode())

    try:
        while True:
            resp = sock.recv(2048).decode('utf-8')
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            elif len(resp) > 0:
                producer.send('twitch_chat_analyzer', demojize(resp).encode('utf-8'))

    except KeyboardInterrupt:
        sock.close()
        exit()

if __name__ == '__main__':
    main()

