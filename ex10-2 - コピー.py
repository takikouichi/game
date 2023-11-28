import pygame
from pygame.locals import *
import requests
import os
import csv
import math
#ここにAppクラスを配置
class App():
    def __init__(self):
        self.w, self.h = 250, 250
        self.fps, self.v, self.f = 20, 4, True
        self.p, self.m = Player(), Map()
        self.m.getfile()
        pygame.init()
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('CSVと緯度経度の利用')
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load(self.m.file_name)
        self.bgr = self.bg.get_rect()
        self.font = pygame.font.SysFont("yumincho", 10)
        self.main()
    def main(self):
        while self.f:
            self.up()
            self.draw()
            self.ev()
    def up(self):
        if(0 < self.p.r.x < self.w and 0 < self.p.r.y < self.h): return;
        if(self.p.r.x >= self.w):
            self.m.move(1, 0)
            self.p.r.x = self.v
        if(self.p.r.x <= 0):
            self.m.move(-1, 0)
            self.p.r.x = self.w - self.v
        if(self.p.r.y >= self.h):
            self.m.move(0, 1)
            self.p.r.y = self.v
        if(self.p.r.y <= 0):
            self.m.move(0, -1)
            self.p.r.y = self.h - self.v
        self.bg = pygame.image.load(self.m.file_name)
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg, self.bgr)
        self.screen.blit(self.p.img, self.p.r)
        pygame.draw.rect(self.screen, (0, 0, 0), (110, 240, 140, 10))
        self.txt = self.font.render("出典：国土地理院ウェブサイト", True, (255, 255, 255))
        self.screen.blit(self.txt, (110, 240))
        for obj in self.m.showlist:
            self.screen.blit(self.m.simg, (obj["r"]))
        pygame.display.update()
        self.clock.tick(self.fps)
    def ev(self):
        pressed_key = pygame.key.get_pressed()
        if(pressed_key[K_LEFT]): self.p.move(-self.v, 0)
        if(pressed_key[K_RIGHT]): self.p.move(self.v, 0)
        if(pressed_key[K_UP]): self.p.move(0, -self.v)
        if(pressed_key[K_DOWN]): self.p.move(0, self.v)
        for event in pygame.event.get():
            if event.type == QUIT:
                self.f = False
            if(event.type == KEYDOWN and event.key == K_ESCAPE):
                self.f = False
            if(event.type == KEYDOWN and event.key == K_m):
                self.m.type *= -1
                self.m.getfile()
                self.bg = pygame.image.load(self.m.file_name)
class Player():
    def __init__(self):
        w, h = 20, 20
        self.r = Rect(150, 150, w, h)
        path = os.path.dirname(__file__)
        self.img = pygame.image.load(path + "/p.png")
    def move(self, x, y):
        self.r.move_ip(x, y)
#ここにMapクラスを配置
class Map():
    def __init__(self):
        self.x, self.y, self.z, self.type = 116296, 51752, 17, 1
        self.objlist, self.showlist = [], []
        self.path = os.path.dirname(__file__)
        self.simg = pygame.image.load(self.path + "shelter.png")
        self.getcsv()
    def geturl(self):
        if self.type == 1:
            url = "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/"
            url += str(self.z)+"/"+str(self.x)+"/"+str(self.y)+".jpg"
        elif self.type == -1:
            url = "https://cyberjapandata.gsi.go.jp/xyz/pale/"
            url += str(self.z)+"/"+str(self.x)+"/"+str(self.y)+".png"
        return(url)
    def move(self, offsetX, offsetY):
        self.x += offsetX
        self.y += offsetY
        self.getfile()
def getfile(self):
    self.file_name = self.path + "/bg/" + str(self.x) + "_" + str(self.y) + "_" + str(self.z)
    self.file_name += ".jpg" if self.type == 1 else ".png"
    response = requests.get(self.geturl())
    image = response.content
    with open(self.file_name, "wb") as ff:
        ff.write(image)
        self.getobj()
    def latlon2tile(self, lat, lon):
        n = 2.0**self.z
        rad = math.radians(lat)
        xt = ((lon + 180.0) / 360.0 * n)
        yt = ((1.0 - math.log(math.tan(rad) + (1 / math.cos(rad))) / math.pi) / 2.0 * n)
        xp = int((xt - int(xt)) * 256)
        yp = int((yt - int(yt)) * 256)
        return(int(xt), int(yt), xp, yp)
    def getcsv(self):
        url = "https://www.city.chigasaki.kanagawa.jp/_res/projects/"
        url += "default_project/_page_/001/045/144/bousai/R5tsunami.csv"
        with requests.Session() as s:
            res = s.get(url)
            res.encoding = res.apparent_encoding
            data = res.content.decode(res.encoding)
            cr = csv.reader(data.splitlines(), delimiter=',')
            tmp = list(cr)
            for row in tmp:
                if(row[3] != "経度" and row[3] != ""):
                    ret = list(self.latlon2tile(float(row[4]), float(row[3])))
                    ret.append(row[1])
                    self.objlist.append(ret)
    def getobj(self):
        self.showlist = []
        for item in self.objlist:
            if(self.x == item[0] and self.y == item[1]):
                self.showlist.append({"name":item[4], "r":Rect(item[2], item[3], 20, 20)})

if __name__ == '__main__': App()