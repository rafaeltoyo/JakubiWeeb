from bot.controller import Controller

c = Controller()
try:
    c.run()
except Exception as e:
    print(e)
finally:
    del c
