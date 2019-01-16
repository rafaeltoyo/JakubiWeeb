import sys
from app.application import Application
from utils.log.manager import LogManager


def main():
    LogManager().redefine_default_files()

    print('=' * 80)
    print("Starting application ...")
    print('=' * 80)

    app = None

    try:
        LogManager().out.println("Starting")
        app = Application(*(sys.argv[1:]))
        LogManager().out.println("Running")
        app.run()
        LogManager().out.println("Stopping")
    except Exception as e:
        LogManager().err.println(e)
        exit(-1)
    finally:
        if app is not None:
            del app
        exit(0)


if __name__ == "__main__":
    main()
