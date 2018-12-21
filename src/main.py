from bot.controller import Controller

c = Controller()
try:
    c.run()
finally:
    del c
