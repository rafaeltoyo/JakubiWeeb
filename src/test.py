from localmusic.core import LocalMusicController
from utils.singleton import Singleton2

LocalMusicController().load("")


class Teste1(metaclass=Singleton2):
    def __init__(self):
        self.value = 1
        Teste2()


class Teste2(metaclass=Singleton2):
    def __init__(self):
        self.value = 2


t1 = Teste1()

print(Teste1().value)
print(t1.value)

t1.value += 1

print(Teste1().value)
print(t1.value)

Teste1().value += 1

print(Teste1().value)
print(t1.value)
