import numpy as np
import asyncio
from typing import List, Any

from .request import Request


class SongQueue:

    def __init__(self, start_zero: bool = False):

        self.__iter: int = -1
        self.__items: List[Request] = []
        self.__start_zero = start_zero

        self.__lock = asyncio.Lock()
        self.__waiter = asyncio.Event()

    def stopped(self):
        return self.__iter < 0

    @property
    def current(self):
        return self.__items[self.__iter] if self.__iter >= 0 else None

    @current.setter
    def current(self, request: Request):
        self.__items[self.__iter] = request

    @property
    def size(self):
        return len(self.__items)

    # ================================================================================================================ #
    #   Queue utils
    # ---------------------------------------------------------------------------------------------------------------- #

    def display(self, page=1, n_items=10):
        page = max(1, page)
        n_items = max(1, n_items)

        max_items = self.size
        max_pages = np.ceil(max_items/n_items)

        start = (min(page, max_pages) - 1) * n_items
        end = min(max_items, start + n_items)

        count = 0 if self.__start_zero else 1
        iter = 0
        content = ""
        for item in self.__items[start:end]:
            content += ('>' if iter == self.__iter else '') + "[{}] {}\n".format(count, str(item))
            count += 1
            iter += 1
        return content

    def __str__(self):

        count = 0 if self.__start_zero else 1
        iter = 0
        content = ""
        for item in self.__items:
            content += ('>' if iter == self.__iter else '') + "[{}] {}\n".format(count, str(item))
            count += 1
            iter += 1
        return content

    def __check_index(self, i):

        if not self.__start_zero:
            i = i - 1
        if self.size == 0:
            # FIXME: Raise "Empty queue" error
            raise RuntimeError
        size = len(self.__items)
        if not (0 <= i < size):
            # FIXME: Raise "Invalid song position" error
            raise IndexError
        return i

    # ================================================================================================================ #
    #   Queue items manipulation
    # ---------------------------------------------------------------------------------------------------------------- #

    async def wait(self):
        self.__waiter.clear()
        if self.stopped():
            await self.__waiter.wait()
        current = self.current
        try:
            await self.next()
        except:
            await self.finish()
        return current

    async def add(self, request: Request):

        async with self.__lock:
            self.__items.append(request)

            if self.__iter < 0:
                # Resume queue
                self.__iter = self.__items.index(request)
            self.__waiter.set()

    async def remove(self, pos: int):

        async with self.__lock:
            i = self.__check_index(pos)
            item = self.__items[i]
            self.__items.remove(self.__items[i])

            if self.size == 0:
                # Empty queue -> Queue ended
                self.set_iter(-1)

            elif i == self.__iter:
                # Removed current song
                if i == (self.size - 1):
                    # Last song removed -> Queue ended
                    self.set_iter(self.__iter - 1)
                else:
                    # Skip to next song (Automatic)
                    ...

            elif i < self.__iter:
                # Removed previous song -> Fix current song position
                self.set_iter(self.__iter - 1)

            else:
                # Nothing to do
                ...
            return item

    async def clear(self):
        async with self.__lock:
            self.set_iter(-1)
            self.__items = []

    # ================================================================================================================ #
    #   Queue location manipulation
    # ---------------------------------------------------------------------------------------------------------------- #

    async def finish(self):
        async with self.__lock:
            self.set_iter(-1)

    async def next(self):

        i = self.__iter + (0 if self.__start_zero else 1)
        await self.goto(i + 1)

    async def previous(self):

        i = self.__iter + (0 if self.__start_zero else 1)
        await self.goto(i - 1)

    async def goto(self, pos: int):

        async with self.__lock:
            self.set_iter(self.__check_index(pos))

    def set_iter(self, i):
        self.__iter = i
        if i > -1:
            self.__waiter.set()

    # ================================================================================================================ #
