import sys
from bot.controller import Controller
from bot.dbcontroller import DBController
from utils.log import Log


def main():

    # Main controller
    c = Controller(*sys.argv[1:])

    try:
        DBController().set_db(c.db)
        print('=' * 80)
        c.run()
    except Exception as e:
        Log().write("Runtime error: " + str(e))
        print(e)
    finally:
        del c


if __name__ == "__main__":
    main()
