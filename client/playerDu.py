import vlc
from os import listdir

class Player():
    def __init__(self):
        self.dirname = ""
        self.filename = ""

    def setPath(self, path):
        if path[-1] == "/":
            self.dirname = path
        else:
            self.dirname = path + "/"

    def listar_arquivos(self):
        lista_arqs = [arq for arq in listdir(self.dirname)]
        return lista_arqs

if __name__ == '__main__':
    obj = Player()
    # print("Digite o diretório dos arquivos: ")
    # path = input()
    # obj.setPath(path)
    # movies = obj.listar_arquivos()
    # playlist = ['./0.mkv', './1.mkv', './2.mkv']

    # for song in playlist:
    # pl = vlc.Instance("")
    Instance = vlc.Instance()
    # player = vlc.MediaPlayer("./0.mkv")
    # player.play()