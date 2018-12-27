import subprocess

class Player():
    def __init__(self):
      self.dirname = ""
      self.filename = ""
    
    def Open(self, dirname, filename):
      if dirname[-1] == "/":
        self.dirname = dirname
      else:
        self.dirname = dirname + "/"
      
      self.filename = filename
        
    def Play(self):
      subprocess.Popen(["vlc", self.dirname + self.filename])
        
vlc = Player()
vlc.Open("/home/renan/Documents/3ano/SO/Servidor/client", "my_concatenation.mkv")
vlc.Play()

# clip0 = VideoFileClip("HomemFormiga_00000.mkv")
# clip1 = VideoFileClip("HomemFormiga_00001.mkv")
# clip2 = VideoFileClip("HomemFormiga_00002.mkv")
# clip3 = VideoFileClip("HomemFormiga_00003.mkv")
# clip4 = VideoFileClip("HomemFormiga_00004.mkv")
# clip5 = VideoFileClip("HomemFormiga_00005.mkv")
# clip6 = VideoFileClip("HomemFormiga_00006.mkv")
# clip7 = VideoFileClip("HomemFormiga_00007.mkv")
# final_clip = concatenate_videoclips([clip1, clip2, clip3, clip4, clip5, clip6, clip7])
# final_clip.write_videofile("my_concatenation.mkv")


# import subprocess

# p = subprocess.Popen(["vlc","/home/renan/Documents/3ano/SO/Servidor/client/0.mp4"])