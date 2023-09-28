import os
import socket
import logging
import dotenv
from emoji import demojize


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('chat.log', encoding='utf-8')])


"""
Get token here: https://twitchapps.com/tmi/
"""


# dotenv.load_dotenv()
# server = os.getenv('SERVER')
# port = int(os.getenv('PORT'))
# nickname = os.getenv('USERNAME')
# token = os.getenv('TWITCH_OAUTH_TOKEN')
# channel = '#ohnepixel'

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'justinfan67420'
token = 'SCHMOOPIIE'
channel = '#lirik'

def main():
    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\r\n".encode())
    sock.send(f"NICK {nickname}\r\n".encode())
    sock.send(f"JOIN {channel}\r\n".encode())

    try:
        while True:
            resp = sock.recv(2048).decode('utf-8')
            if resp.startswith('PING'):
                # sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))
                sock.send("PONG\n".encode('utf-8'))
            elif len(resp) > 0:
                logging.info(demojize(resp))

    except KeyboardInterrupt:
        sock.close()
        exit()

if __name__ == '__main__':
    main()