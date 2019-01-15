from os.path import abspath

class MusicQueue:

    def __init__(self):
        self.path = abspath('queue.txt')
        self._load_queue()

    def _load_queue(self):
        with open(self.path, 'r') as queue:
            self.queue_list = [line for line in queue.readlines() if line != '' or line != '\n']

    def add_music(self, song:str):
        print("ADD")
        with open(self.path, 'r+') as queue:
            queue_list = queue.readlines()
            queue_list.append(song)
            queue.seek(0)
            queue.write('\n'.join(queue_list))
            queue.truncate()
        self._load_queue()

    #TODO: remover por index
    def remove_music(self, song='', index=9999):
        with open(self.path, 'r+') as queue:
            queue_list = queue.readlines()
            queue_list.remove(song,1)
            queue.seek(0)
            queue.write('\n'.join(queue_list))
            queue.truncate()
        self._load_queue()

    def skip_music(self):
        print('SKIP')
        with open(self.path, 'r+') as queue:
            queue_list = queue.readlines()[1:]
            queue.seek(0)
            queue.write('\n'.join(queue_list))
            queue.truncate()
        self._load_queue()

    def jump_to(self, song='', index=9999):
        if song != '':
            with open(self.path, 'r+') as queue:
                n_song = 9999
                for index, value in self.queue_list:
                    if value == song:
                        n_song = index
                        break
                if n_song == 9999:
                    print("Erro na seleção de música para pular no queue")
                    return
                queue.seek(0)
                queue.write('\n'.join(self.queue_list[n_song:]))
                queue.truncate()
            self._load_queue()

    def get_queue(self):
        return self.queue_list

    #TODO: Clear queue pra qdo o bot boota
