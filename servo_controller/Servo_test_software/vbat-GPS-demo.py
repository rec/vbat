#!/usr/bin/env python
# -*- coding: utf8 -*-

from Tkinter import *
from PIL import ImageTk
from PIL import Image
from math import atan2, degrees, pi
import math
import geopy
from geopy.distance import VincentyDistance


class SimpleApp(Toplevel):
    def __init__(self, master, filename, **kwargs):
        self.master = master
        self.filename = filename
        self.canvas = Canvas(master, width=700, height=700)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.b1down)
        self.canvas.bind("<ButtonRelease-1>", self.b1up)
        self.canvas.bind("<Motion>", self.motion)
        # on windows
        self.canvas.bind("<MouseWheel>", self.OnMouseWheel)
        # on linux
        self.canvas.bind("<Button-4>", self.OnMouseWheel)
        self.canvas.bind("<Button-5>", self.OnMouseWheel)

        self.canvas.create_line(0, 350, 700, 350, fill="#476042")
        self.canvas.create_text(355, 10, text="N")
        self.canvas.create_text(355, 690, text="S")
        self.canvas.create_line(350, 0, 350, 700, fill="#476042")
        self.canvas.create_text(10, 360, text="W")
        self.canvas.create_text(690, 360, text="E")
        self.canvas.create_oval(250,250,450,450, outline="red")
        self.canvas.create_text(470, 340, text="1 km")
        self.canvas.create_oval(150,150,550,550, outline="red")
        self.canvas.create_text(570, 340, text="2 km")
        self.canvas.create_oval(50,50,650,650, outline="red")
        self.canvas.create_text(670, 340, text="3 km")

        self.text_lat = self.canvas.create_text(35, 640, text="Latitude")
        self.text_lon = self.canvas.create_text(35, 655, text="Longitude")
        self.text_height = self.canvas.create_text(35, 670, text="Height")

        self.image = Image.open(self.filename)
        self.image2 = Image.open("plane.png")
        self.angle = 0
        self.down = False
        self.height = 0
        self.sent = Com_Sent()
        self.arrow_canvas_obj = self.canvas
        self.plane_canvas_obj = self.canvas
        self.angle = 0
        self.plane_angle = 0
        self.plane_counter = 0

        self.xold = 0
        self.yold = 0

        self.arrow_image = ImageTk.PhotoImage(self.image.rotate(self.angle))
        self.arrow_canvas_obj.create_image(350, 350, image=self.arrow_image)

        self.plane_image = ImageTk.PhotoImage(self.image2.rotate(self.plane_angle))
        self.plane_canvas_obj.create_image(350, 150, image=self.plane_image)

    def OnMouseWheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.height  -= 3
        if event.num == 4 or event.delta == 120:
            self.height  += 3
        if self.height<0:
            self.height = 0
        self.do(event)

    def motion(self, event):
        if self.down:
            self.do(event)

    def b1down(self, event):
        self.down = True
        self.do(event)

    def b1up(self, event):
        self.down = False

    def do(self, event):
        self.angle = self.get_angle(event.x, event.y)
        self.plane_angle = self.get_plane_angle(event.x, event.y)
        self.arrow_image = ImageTk.PhotoImage(self.image.rotate(self.angle))
        self.arrow_canvas_obj.create_image(350, 350, image=self.arrow_image)

        self.plane_image = ImageTk.PhotoImage(self.image2.rotate(self.plane_angle))
        self.plane_canvas_obj.create_image(event.x, event.y, image=self.plane_image)

        dist = math.sqrt( (350 - event.x)**2 + (350 - event.y)**2 )
        dist = dist/100
        lat, long = self.gps(-self.angle, dist)
        lat = int(lat*100000)/100000.0
        long = int(long*100000)/100000.0
        lat += 0.000001
        long += 0.000001

        if self.plane_counter<7:
            self.plane_counter += 1
        else:
            self.xold = event.x
            self.yold = event.y
            self.plane_counter = 0

        self.canvas.itemconfig(self.text_lat, text=str(lat))
        self.canvas.itemconfig(self.text_lon, text=str(long))
        self.canvas.itemconfig(self.text_height, text=str(self.height))


        self.sent.this(lat, long, self.height)
        self.canvas.update()

    def get_angle(self, x, y):
        dx = 350 - x
        dy = 350 - y
        rads = atan2(-dy,dx)
        rads %= 2*pi
        return degrees(rads)+90

    def get_plane_angle(self, x, y):
        dx = x - self.xold
        dy = y - self.yold
        rads = atan2(-dy,dx)
        rads %= 2*pi
        return degrees(rads)

    def gps(self, b, d):
        # b = bearing in degrees, d = distance in kilometers

        origin = geopy.Point(51.000000, 6.000000)
        destination = VincentyDistance(kilometers=d).destination(origin, b)

        lat, lon = destination.latitude, destination.longitude
        return lat, lon

class Com_Sent(object):
    def __init__(self):
        pass

    def this(self, lat, lon, height):
        print lat, lon, height

root = Tk()
app = SimpleApp(root, 'Up_Arrow_Icon.png')
root.mainloop()