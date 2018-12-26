import sys
from bot.controller import Controller
from bot.dbcontroller import DBController


def main():

    create = False
    delete = False

    for arg in sys.argv[1:]:
        if arg == "reset":
            create = True
            delete = True
        elif arg == "init":
            create = True
        elif arg == "clean":
            delete = True
        else:
            raise Exception("Invalid flag!")

    # Main controller
    c = Controller()
    try:
        # Delete database.
        if delete:
            c.delete_database()

        # Create database using config file.
        if create:
            c.create_database()
            c.create_monolith()

        DBController().set_db(c.db)

        print('=' * 80)
        c.run()
    except Exception as e:
        print(e)
    finally:
        del c


if __name__ == "__main__":
    main()

