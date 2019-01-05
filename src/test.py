from app.application import Application

try:
    Application().run()
except Exception as e:
    print(e)
    exit(-1)
exit(0)
