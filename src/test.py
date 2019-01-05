from bot import Bot

try:
    bot = Bot()
    bot.load_music()
    del bot

except Exception as e:
    print(e)
    exit(-1)

exit(0)
