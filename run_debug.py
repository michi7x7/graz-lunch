import logging
logging.basicConfig(level=logging.INFO)

from menu_bot import get_messages, send_debug


for message in get_messages():
    print(message)

#send_debug()
