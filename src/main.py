import sys
from app.application import Application


def main():
    print('=' * 80)
    print("Starting application ...")
    print('=' * 80)
    app = Application(*(sys.argv[1:]))

    try:
        app.run()
    except Exception as e:
        print(e)
        exit(-1)
    finally:
        del app
        exit(0)


if __name__ == "__main__":
    main()
