from menu_bot import send_all
from datetime import date

if date.today().weekday() < 5:
    send_all()
