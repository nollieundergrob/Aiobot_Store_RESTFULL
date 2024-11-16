import daphne
import threading
import os
from bot import bot
import socket

# ip = '0.0.0.0'
# ip = 'localhost'
# ip = socket.gethostbyname(socket.gethostname())
ip = '217.196.101.222'
#172.18.0.3:25565
port = 25565
verbosity = 3
bot_path = '.\\bot\\bot.py'

# def start_api():
#     os.system(f'daphne -p {port} -b {ip} -v {verbosity} -s NOLLIEUNDERGROB conifg.asgi:application')

def start_bot():
    bot.start_bot(ip,port)
start_bot()

# th1 = threading.Thread(target=start_api)
# th1.start()
# th2 = threading.Thread(target=start_bot)
# th2.start()
# th1.join()
# th2.join()
    