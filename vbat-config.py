#!/usr/bin/env python
# -*- coding: utf8 -*-
from Tkinter import *
from PIL import Image
from tkFileDialog import askdirectory
from tkFileDialog import askopenfilename
import tkSimpleDialog
import tkMessageBox
import pygame
import pygame.camera
import datetime
import ImageTk
import math
import os
import os.path
import shutil
from lib.CamLib import *
from lib.file_handler import loadconfig


class Main(object):
    def __init__(self):
        self.__master = Tk()
        self.__master.title("vbat-config")
        self.__frame = Frame(self.__master)
        self.__frame2 = Frame(self.__master)
        self.__frame3 = Frame(self.__master)
        self.__menue()

        image = Image.open("files/background")
        # iwidth, iheight = image.size
        # self.__w.config(width=iwidth,height=iheight)
        photo = ImageTk.PhotoImage(image)
        self.__sessionname = ""
        self.__canvas_width = 800
        self.__canvas_height = 600
        self.__w = Canvas(self.__master, width=self.__canvas_width, height=self.__canvas_height)
        self.__x = self.__w.create_image(0, 0, anchor=NW, image=photo)
        iwidth, iheight = image.size
        self.__w.config(width=iwidth, height=iheight)
        self.__w.grid(row=0, column=0, columnspan=3, rowspan=3)

        self.__listbox = Listbox()
        self.__listbox.grid(row=3, column=0, sticky=N + E + S + W)

        self.__button1 = Button(self.__frame, text="Next Picture ->", command=self.__next_picture)
        self.__button1.grid(row=0, column=0, sticky=W + E)
        self.__button2 = Button(self.__frame, text="<- Previous Picture", command=self.__prev_picture)
        self.__button2.grid(row=1, column=0, sticky=W + E)
        self.__button2 = Button(self.__frame, text="Delete Picture", command=self.__delete_picture)
        self.__button2.grid(row=2, column=0, sticky=W + E)
        self.__frame.grid(row=3, column=1, sticky=W)

        self.__check_img = PhotoImage(file="files/Green_check.svg.png")
        self.__cross_img = PhotoImage(file="files/13px-Red_x.svg.png")

        self.__button_lat = Button(self.__frame2, image=self.__cross_img, text="Latitude", compound="left",
                                   state=DISABLED, command=lambda: self.__set_field("lat"))
        self.__button_lat.grid(row=0, column=0, sticky=W + E)
        self.__button_lon = Button(self.__frame2, image=self.__cross_img, text="Longitude", compound="left",
                                   state=DISABLED, command=lambda: self.__set_field("lon"))
        self.__button_lon.grid(row=1, column=0, sticky=W + E)
        self.__button_height = Button(self.__frame2, image=self.__cross_img, text="Height", compound="left",
                                      state=DISABLED, command=lambda: self.__set_field("height"))
        self.__button_height.grid(row=2, column=0, sticky=W + E)
        self.__button_cancel = Button(self.__frame2, text="Cancel", state=DISABLED, command=self.__show)
        self.__button_cancel.grid(row=3, column=0, sticky=W + E)
        self.__frame2.grid(row=3, column=2)

        self.__mouse_binding = ""
        self.__image_list = []
        self.__filename = "settings"
        self.__new_field_name = ""
        self.__new_field_x1 = ""
        self.__new_field_y1 = ""
        self.__new_field_x2 = ""
        self.__new_field_y2 = ""
        self.__rectangle = ""
        self.__fields = []
        self.__characterfield = ["", "", ""]
        self.__selected = "lat"  # "lat" "lon" "height"
        self.__mainimage = ""

        self.__w.bind("<Button-1>", self.__mouse_click)
        self.__listbox.insert(END, "Import an image,")
        self.__listbox.insert(END, "or import existing session")

        self.__master.mainloop()

    def __menue(self):
        menubar = Menu(self.__master)
        # filemenu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import Image from...File", command=self.__open_image_file)
        # filemenu.add_command(label="Import Image from...Directory", command=self.__open_image_directory)
        filemenu.add_command(label="Import Image from...Video Source", underline=1, accelerator="Ctrl+V",
                             command=self.__grab_image)
        filemenu.add_separator()
        filemenu.add_command(label="Open", command=self.__open_session)
        filemenu.add_separator()
        filemenu.add_command(label="extract number", command=self.__extract_number)
        filemenu.add_command(label="create template", command=self.__create_template)
        # filemenu.add_command(label="Save", command=self.__save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.__master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.__master.bind_all("<Control-v>", self.__grab_image)
        # Do_menue
        do_menue = Menu(menubar, tearoff=0)
        do_menue.add_command(label="Assign Characters",
                             command=self.__assign_character)
        menubar.add_cascade(label="Do", menu=do_menue)
        # helpmenu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.__about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.__master.config(menu=menubar)

    def __delete_picture(self):
        os.remove(self.__mainimage)
        self.__mainimage = ""
        self.__show()

    def __next_picture(self):
        allpictures = self.__listdir_fullpath("saves/" + self.__sessionname + "/images/")
        new = ""
        for i in range(len(allpictures)):
            if allpictures[i] == self.__mainimage:
                if i + 1 > len(allpictures) - 1:
                    new = allpictures[0]
                else:
                    new = allpictures[i + 1]
        self.__mainimage = new
        self.__show()

    def __prev_picture(self):
        allpictures = self.__listdir_fullpath("saves/" + self.__sessionname + "/images/")
        new = ""
        for i in range(len(allpictures)):
            if allpictures[i] == self.__mainimage:
                if i > 0:
                    new = allpictures[i - 1]
                else:
                    new = allpictures[-1]
        self.__mainimage = new
        self.__show()

    def __assign_character(self):
        self.__extract_number()
        if Assign_Characters(self.__master, self.__sessionname):
            if os.path.exists("saves/" + self.__sessionname + "/temp/1"):
                self.__create_template()
                self.__show()

    def __extract_number(self):
        self.__save_file()
        Extract_Number(self.__characterfield, self.__listdir_fullpath("saves/" + self.__sessionname + "/images/"),
                       self.__sessionname)
        self.__listbox.delete(0, END)
        self.__listbox.insert(END, "Sort the characters,")
        self.__listbox.insert(END, "then start \"create template\"")

    def __create_template(self):
        Create_Template(self.__sessionname)
        self.__listbox.delete(0, END)
        self.__listbox.insert(END, "Select Height")

    def __set_session_name(self):
        while self.__sessionname == "":
            self.__sessionname = tkSimpleDialog.askstring("New name", "Name")
            for checkfolder in os.listdir("saves/"):
                if self.__sessionname == checkfolder:
                    tkMessageBox.showinfo("Something Went Wrong", "The name " + self.__sessionname + "already exists")
                    self.__sessionname = ""
        os.makedirs("saves/" + self.__sessionname)
        os.makedirs("saves/" + self.__sessionname + "/images")
        # for i in range(10):
        #    os.makedirs("saves/" + self.__sessionname + "/temp/" + "/" + str(i))
        # os.makedirs("saves/" + self.__sessionname + "/temp/" + "dot")
        # os.makedirs("saves/" + self.__sessionname + "/temp/" + "minus")

    def __open_image_file(self):
        if self.__sessionname == "":
            self.__set_session_name()
        image = askopenfilename(filetypes=[("Image Files", ("*.jpg", "*.jpeg"))])
        if (image != "()") and (image != ""):
            self.__mainimage = image
            shutil.copy(image, "saves/" + self.__sessionname + "/images/")
            self.__listbox.delete(0, END)
            self.__listbox.insert(END, "Select latitude and")
            self.__listbox.insert(END, "Select longitude field")
            self.__show()

    def __open_image_directory(self):
        folder = str(askdirectory())
        if (folder != "()") and (folder != ""):
            dateien = os.listdir(folder)
            for i in range(len(dateien)):
                endung = os.path.splitext(dateien[i])
                if (endung[len(endung) - 1].lower() == ".jpg") or (endung[len(endung) - 1].lower() == ".jpeg"):
                    self.__image_list.append([folder, dateien[i]])
            self.__show()

    def __grab_image(self, event=None):
        if self.__sessionname == "":
            self.__set_session_name()
        pygame.init()
        pygame.camera.init()
        data = File_Handler()
        data.set_filename(self.__filename)
        cam = pygame.camera.Camera(data.get("video"), (int(data.get("camx")), int(data.get("camy"))))
        try:
            cam.start()
            for i in range(3):
                image = cam.get_image()
            cam.stop()
            path = str(datetime.datetime.today()).replace(":", "-").replace(".", "-") + ".jpeg"
            pygame.image.save(image, "saves/" + self.__sessionname + "/images/" + path)
            self.__mainimage = "saves/" + self.__sessionname + "/images/" + path
        except:
            tkMessageBox.showinfo("Something Went Wrong",
                                  "Check the video device, or try to change the video resolution.")
        self.__show()

    def __listdir_fullpath(self, d):
        return [os.path.join(d, f) for f in os.listdir(d)]

    def __show(self):
        if self.__sessionname == "":
            image = Image.open("files/background")
        elif self.__mainimage == "":
            last_image = self.__listdir_fullpath("saves/" + self.__sessionname + "/images/")
            image = Image.open(last_image[0])
            self.__mainimage = last_image[0]
        else:
            image = Image.open(self.__mainimage)
        self.__w.delete(ALL)
        iwidth, iheight = image.size
        self.__w.config(width=iwidth, height=iheight)
        self.__photo = ImageTk.PhotoImage(image)
        self.__x = self.__w.create_image(0, 0, anchor=NW, image=self.__photo)

        # Button stuff
        # Button Latitude
        self.__button_lat.config(text="Latitude", command=lambda: self.__set_field("lat"))
        if self.__characterfield[0] != "":
            self.__button_lat.config(image=self.__check_img)
        else:
            self.__button_lat.config(image=self.__cross_img)
        # Button Longitude
        self.__button_lon.config(text="Longitude", command=lambda: self.__set_field("lon"))
        if self.__characterfield[1] != "":
            self.__button_lon.config(image=self.__check_img)
        else:
            self.__button_lon.config(image=self.__cross_img)
        # Button Height
        self.__button_height.config(text="Height", command=lambda: self.__set_field("height"))
        if self.__characterfield[2] != "":
            self.__button_height.config(image=self.__check_img)
        else:
            self.__button_height.config(image=self.__cross_img)
        # Button all
        if self.__sessionname != "":
            self.__button_lat["state"] = "normal"
            self.__button_lon["state"] = "normal"
            if os.path.exists("saves/" + self.__sessionname + "/" + self.__sessionname + ".templates"):
                self.__button_height["state"] = "normal"
            else:
                self.__button_height["state"] = "disabled"
        else:
            self.__button_lat["state"] = "disabled"
            self.__button_lon["state"] = "disabled"
            self.__button_height["state"] = "disabled"

        self.__new_field_name = ""
        self.__new_field_x1 = ""
        self.__new_field_y1 = ""
        self.__new_field_x2 = ""
        self.__new_field_y2 = ""
        self.__w.delete(self.__mouse_binding)
        if self.__rectangle != "":
            self.__w.delete(self.__rectangle)
            self.__rectangle = ""

    def __open_session(self):
        folder = str(askdirectory(initialdir="saves/")).split("/")
        self.__sessionname = folder[-1]
        self.__characterfield = ["", "", ""]
        self.__imageindex = -1
        self.__listbox.delete(0, END)
        self.__mainimage = ""
        self.__show()

    def __save_file(self):
        f = open("saves/" + self.__sessionname + "/" + self.__sessionname + ".coo", "w")
        for i in self.__characterfield:
            f.write(i + "\n")
        f.close()

    def __manage_loaded_images(self):
        pass

    def __set_field(self, source):
        if self.__sessionname != "":
            self.__button_cancel["state"] = "normal"
            self.__show()
            self.__new_field_name = ""
            self.__new_field_x1 = ""
            self.__new_field_y1 = ""
            self.__new_field_x2 = ""
            self.__new_field_y2 = ""
            self.__mouse_binding = self.__w.bind("<B1-Motion>", self.__mouse_move)
            if source == "lat":
                self.__button_lat.config(text="Test", command=lambda: self.__test_new_field(source))
            elif source == "lon":
                self.__button_lon.config(text="Test", command=lambda: self.__test_new_field(source))
            elif source == "height":
                self.__button_height.config(text="Test", command=lambda: self.__test_new_field(source))
        else:
            tkMessageBox.showinfo("Something Went Wrong", "You Have No Images Loaded")

    def __mouse_click(self, event):
        self.__new_field_x1 = event.x
        self.__new_field_y1 = event.y
        self.__new_field_x2 = event.x
        self.__new_field_y2 = event.y
        if self.__rectangle == "":
            self.__rectangle = self.__w.create_rectangle(self.__new_field_x1, self.__new_field_y1,
                                                         self.__new_field_x1, self.__new_field_y1, outline='red')
        else:
            self.__w.coords(self.__rectangle, self.__new_field_x1, self.__new_field_y1, event.x, event.y)

    def __mouse_move(self, event):
        if self.__new_field_x1 != "":
            if self.__rectangle != "":
                self.__new_field_x2 = event.x
                self.__new_field_y2 = event.y
                self.__w.coords(self.__rectangle, self.__new_field_x1, self.__new_field_y1, event.x, event.y)

    def __test_new_field(self, source):
        if (self.__new_field_x2 == "") or (self.__new_field_x2 == self.__new_field_x1) or (
                    self.__new_field_y2 == self.__new_field_y1):
            tkMessageBox.showinfo("Something Went Wrong", "You Have To Select A Field First")
        else:
            if self.__new_field_x1 > self.__new_field_x2:
                temp = self.__new_field_x1
                self.__new_field_x1 = self.__new_field_x2
                self.__new_field_x2 = temp
            if self.__new_field_y1 > self.__new_field_y2:
                temp = self.__new_field_y1
                self.__new_field_y1 = self.__new_field_y2
                self.__new_field_y2 = temp
            self.__w.delete(self.__mouse_binding)
            self.__w.delete(self.__rectangle)
            self.__rectangle = ""
            if source != "height":
                # Analyses field from all loaded images
                data = Field_Analyser(self.__listdir_fullpath("saves/" + self.__sessionname + "/images/"),
                                      self.__new_field_x1, self.__new_field_y1, self.__new_field_x2,
                                      self.__new_field_y2)
            else:
                # Analyses filed only from current image
                data = Field_Analyser([self.__mainimage], self.__new_field_x1, self.__new_field_y1, self.__new_field_x2,
                                      self.__new_field_y2)
            self.__fields = data.analyse()
            # make field smaller
            for i in range(len(self.__fields)):
                self.__fields[i][0] += 1
                self.__fields[i][1] += 2
                self.__fields[i][3] += -1
            # Change Buttons
            if source == "lat":
                self.__button_lat.config(text="Save", command=lambda: self.__save_field(source))
            elif source == "lon":
                self.__button_lon.config(text="Save", command=lambda: self.__save_field(source))
            elif source == "height":
                self.__button_height.config(text="Extract Height Field", command=self.__extract_height_field)

            for i in range(len(self.__fields)):
                self.__w.create_rectangle(self.__fields[i][0], self.__fields[i][1], self.__fields[i][2] - 1,
                                          self.__fields[i][3] - 1, outline='blue')

    def __listbox_delete(self):
        self.__listbox.delete(0, END)

    def __extract_height_field(self):
        #
        # create new field, depending on what field[-1] is
        #
        x1 = 999999
        y1 = 999999
        x2 = 0
        y2 = 0
        width = 0
        heightc = tkSimpleDialog.askstring("What Character Is Selected?", "0-9")
        counter = 0
        y = -1
        fobj = open("saves/" + self.__sessionname + "/" + self.__sessionname + ".templates")
        for line in fobj:
            if line[0] == "#":
                counter += 1
            elif counter == int(heightc):
                y += 1
                line = line.replace("\n", "")
                line = line.split(",")
                width = len(line)
                for i in range(len(line)):
                    if line[i] != str(0):
                        if i < x1:
                            x1 = i
                        if i > x2:
                            x2 = i
                        if y < y1:
                            y1 = y
                        if y > y2:
                            y2 = y
        height = y
        fobj.close()
        self.__fields[0][0] = int(self.__fields[0][0]) - (int(x1) - 1)
        self.__fields[0][1] = int(self.__fields[0][1]) - (int(y1) - 1)
        self.__fields[0][2] = int(self.__fields[0][2]) + (int(width - x2) - 2)
        self.__fields[0][3] = int(self.__fields[0][3]) + (int(height - y2) - 1)
        # 2 linke partner einfuegen
        temp = self.__characterfield[0].split(";")
        temp2 = []
        for i in range(len(temp)):
            temp2.append(temp[i].split(","))
        distance = int(temp2[1][0]) - int(temp2[0][0])
        for i in [1, 2]:
            self.__fields.append(
                [self.__fields[0][0] - i * distance, self.__fields[0][1], self.__fields[0][2] - i * distance,
                 self.__fields[0][3]])
        self.__fields.reverse()

        self.__button_height.config(text="Save", command=lambda: self.__save_field("height"))

    def __save_field(self, source):
        # self.__fields.insert(0, self.__new_field_name)
        text2save = str(self.__fields)
        text2save = text2save.replace("['", "")
        text2save = text2save.replace("],", "")
        text2save = text2save.replace("[", ";")
        text2save = text2save.replace("]", "")
        text2save = text2save.replace("',", "")
        text2save = text2save.replace(" ", "")
        text2save = text2save.replace(";;", "")

        if source == "lat":
            self.__characterfield[0] = text2save
        elif source == "lon":
            self.__characterfield[1] = text2save
        elif source == "height":
            self.__characterfield[2] = text2save

        if (self.__characterfield[0] != "") and (self.__characterfield[1] != ""):
            self.__listbox.delete(0, END)
            self.__listbox.insert(END, "Start \"extract number\"")
        self.__save_file()
        self.__button_cancel["state"] = "disabled"
        self.__show()

    def __about(self):
        pass


class Field_Analyser:
    def __init__(self, files, x1, y1, x2, y2):
        self.__files = files
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2

    def __weisstest(self, farbe):
        if int(math.sqrt((math.sqrt((farbe[0] ** 2) + (farbe[1] ** 2)) ** 2) + farbe[2] ** 2)) < 330:
            return False
        else:
            return True

    def analyse(self):
        easy_field = []
        for i in range(self.__x2 - self.__x1):
            easy_field.append(["", ""])
        # Fuellt eine Liste von (x2-x1) mit den Werten fuer das oberste und das unterste y,
        # wenn auf der Strecke ein weisser Pixel ist
        for i in range(len(self.__files)):
            image2 = pygame.image.load(self.__files[i])
            for x in range(self.__x2 - self.__x1):
                for y in range(self.__y2 - self.__y1):
                    if self.__weisstest(image2.get_at((self.__x1 + x, self.__y1 + y))):
                        if (easy_field[x][0] == "") or (easy_field[x][0] > y):
                            easy_field[x][0] = y
                        if (easy_field[x][1] == "") or (easy_field[x][1] < y):
                            easy_field[x][1] = y
        # Erkennt die einzelnen Felder und erstellt eine Liste mit x1,y1,x2,y2
        x1 = 0
        y1 = 0
        y2 = 0
        fields = []
        for i in range(len(easy_field) - 1):
            if (easy_field[i][0] == "") and (easy_field[i][1] == "") and (easy_field[i + 1][0] != "") and (
                        easy_field[i + 1][1] != ""):
                y1 = easy_field[i + 1][0]
                y2 = easy_field[i + 1][1]
                x1 = self.__x1 + i + 1
            if (easy_field[i][0] != "") and (x1 != 0):
                if y1 > easy_field[i][0]:
                    y1 = easy_field[i][0]
                if y2 < easy_field[i][1]:
                    y2 = easy_field[i][1]
            if (easy_field[i][0] != "") and (easy_field[i][1] != "") and (easy_field[i + 1][0] == "") and (
                        easy_field[i + 1][1] == "") and (x1 != 0):
                x2 = self.__x1 + i
                fields.append([x1, self.__y1 + y1, x2, self.__y1 + y2])
                x1 = 0
                # zu diesem punkt enthalt "fields" eine Liste mit allen
                # feldern vom ersten weisen pixel x1,y1 bis zum letzten x2,y2
        # fuege breite, abstand(L) und abstand (R) hinzu
        for i in range(len(fields)):
            fields[i].append(fields[i][2] - fields[i][0])  # breite anhaengen
            if i < 1:
                fields[i].append(0)
            else:
                fields[i].append(fields[i][0] - fields[i - 1][2])  # Abstand linker Nachbar
            if i < (len(fields) - 1):
                fields[i].append(fields[i + 1][0] - fields[i][2])  # Abstand rechter Nachbar
            else:
                fields[i].append(0)

        zaehler = [[0, 0]]
        for i in range(len(fields)):  # sucht den haeufigsten Abstand
            for j in range(2):
                gefunden = False
                for k in range(len(zaehler)):
                    if fields[i][5 + j] == zaehler[k][0]:
                        zaehler[k][1] += 1
                        gefunden = True
                if not gefunden:
                    zaehler.append([fields[i][5 + j], 1])

        zaehler[0][1] = 0
        zaehler = sorted(zaehler, reverse=True, key=lambda times: times[1])

        # ein Wert mit passendem abstand raussuchen
        result = ""
        for i in range(len(fields)):
            if fields[i][5] == zaehler[0][0] and fields[i][6] == zaehler[0][0]:
                result = [fields[i][0], fields[i][1], fields[i][2], fields[i][3], fields[i][4], fields[i][5]]
            elif result == "":
                if fields[i][5] == zaehler[0][0]:
                    result = [fields[i][0], fields[i][1], fields[i][2], fields[i][3], fields[i][4], fields[i][5]]
                elif fields[i][6] == zaehler[0][0]:
                    result = [fields[i][0], fields[i][1], fields[i][2], fields[i][3], fields[i][4], fields[i][6]]

        # resut=[x1, y1, x2, y2, breite, abstand] fuer einzelne Zeichen ins Abstand =0
        startx = result[0]
        while startx - (result[4] + result[5]) >= self.__x1:
            startx -= result[4] + result[5]
        endx = result[2]
        while endx + (result[4] + result[5]) <= self.__x2:
            endx += result[4] + result[5]
        zaehler = startx
        y1 = result[1]
        y2 = result[3]
        step = result[4] + result[5]
        back = []
        while zaehler < endx:
            back.append([zaehler, y1, zaehler + result[4], y2])
            zaehler += step
        for i in range(len(back)):
            xmehr = int((back[i][2] - back[i][0]) / 6)
            ymehr = int((back[i][3] - back[i][1]) / 6)
            back[i][0] -= xmehr
            back[i][1] -= ymehr
            back[i][2] += xmehr
            back[i][3] += ymehr
        return back


class File_Handler:  # reparieren
    def __init__(self):
        self.__filename = "settings"

    def get(self, word):
        send = ""
        fobj = open("files/vbat.config", "r")
        for line in fobj:
            line = line.replace("\n", "")
            daten = line.split(";")
            if daten[0] == word:
                send = daten[1]
        fobj.close()
        return send

    def set_filename(self, filename):
        self.__filename = filename


class Create_Template:
    def __init__(self, name):
        sign = []

        def weisstest(farbe):
            # weiss=441
            # print int(math.sqrt((math.sqrt((255**2)+(255**2))**2)+255**2))
            #
            # hell grau bis 290
            if int(math.sqrt((math.sqrt((farbe[0] ** 2) + (farbe[1] ** 2)) ** 2) + farbe[2] ** 2)) < 330:
                return False
            else:
                return True

        for dirs in os.walk("saves/" + name + "/temp/"):
            sign.append(dirs[0])
        del sign[0]
        sign.sort()

        picture = os.listdir(sign[0])
        image = pygame.image.load(sign[0] + "/" + picture[0])
        image_size_x, image_size_y = image.get_rect().size

        f = open("saves/" + name + "/" + name + ".templates", 'w')

        for i in range(len(sign)):
            picture = os.listdir(sign[i])
            if "template.jpg" in picture:
                picture.remove("template.jpg")
            template = []  # create matrix
            for j in range(image_size_y):
                template.append([])
            for j in range(len(template)):
                for k in range(image_size_x):
                    template[j].append(0)

            for j in range(len(picture)):
                image = pygame.image.load(sign[i] + "/" + picture[j])
                for k in range(image_size_y):
                    for l in range(image_size_x):
                        if weisstest(image.get_at((l, k))):
                            template[k][l] += 1
            for k in range(image_size_y):
                for l in range(image_size_x):
                    if template[k][l] >= len(picture) / 10:
                        image.set_at((l, k), (255, 255, 255))
                    else:
                        image.set_at((l, k), (0, 0, 0))
                        pygame.image.save(image, sign[i] + "/template.jpg")
                        print sign[i] + "/template.jpg"
                        template[k][l] = 0

            for t in range(len(template)):
                temp = str(template[t])
                temp = temp.replace(" ", "")
                temp = temp.replace("[", "")
                temp = temp.replace("]", "")
                f.write(temp + "\n")
            temp = sign[i]
            temp = temp.split("/")
            temp = temp[len(temp) - 1]
            f.write("#," + temp + "\n")

        f.close()


class Extract_Number:
    def __init__(self, field, images, sessionname):
        pygame.init()

        name = sessionname
        fields = field
        namecounter = 0
        if not os.path.exists("saves/" + name + "/temp"):
            os.mkdir("saves/" + name + "/temp")

        for k in range(len(images)):
            image = pygame.image.load(images[k])
            for i in fields:
                i2 = i
                i2 = i2.split(";")
                if i2[0] != "":
                    for l in i2:
                        l = l.split(",")
                        x1 = int(l[0])
                        y1 = int(l[1])
                        x2 = int(l[2])
                        y2 = int(l[3])
                        cropped = pygame.Surface((x2 - x1, y2 - y1))
                        cropped.blit(image, (0, 0), (x1, y1, x2, y2))
                        namecounter += 1
                        pygame.image.save(cropped, "saves/" + name + "/temp/" + str(namecounter) + ".jpeg")


class Assign_Characters(Frame):
    def __init__(self, parent, name):

        self.__name = name

        Frame.__init__(self, parent)
        self.root = Toplevel(parent)

        # first row
        self.label_pixel_range = Label(self.root,
                                       text="Pixel-range:").grid(row=0, column=0, columnspan=3)

        self.entry_pixel_range = Entry(self.root, width=10, bg="white")
        self.entry_pixel_range.grid(row=0, column=3, columnspan=3, sticky=W)
        self.entry_pixel_range.insert(0, "2")

        self.button_pixel_range = Button(self.root,
                                         text="Find",
                                         command=lambda: self.find(int(self.entry_pixel_range.get()))).grid(row=0, column=6, columnspan=3, sticky=W)

        image = Image.open("files/black.jpeg")
        photo = ImageTk.PhotoImage(image)

        # pictures column 1
        self.__character = []
        for image_column in range(20):
            self.__character.append([])
            for image_row in range(5):
                self.__one_image = Label(self.root, image=photo)
                self.__one_image.grid(row=image_row + 2, column=image_column)
                self.__character[image_column].append(self.__one_image)

        self.__entry_list = []
        for i in range(20):
            self.__entry_character = Entry(self.root, width=3, bg="white")
            self.__entry_character.grid(row=7, column=i, sticky=W)
            self.__entry_list.append(self.__entry_character)

        self.button_save = Button(self.root, text="Save", command=self.__save)
        self.button_save.grid(row=8, column=0, columnspan=6, sticky=W)

        self.root.focus_set()
        self.root.grab_set()
        self.root.wait_window()

    def pxl_range(self):
        pass

    def __save(self):
        for case in range(len(self.__sorted_images)):
            if case<20:
                character = self.__entry_list[case].get()
                if character == ".":
                    character = "dot"
                elif character == "-":
                    character = "minus"
                if character != "":
                    if not os.path.exists("saves/" + self.__name + "/temp/" + character):
                            os.mkdir("saves/" + self.__name + "/temp/" + character)
                    for i in range(len(self.__sorted_images[case][1])):
                        if i <5:
                            shutil.copy(self.__sorted_images[case][1][i], "saves/" + self.__name + "/temp/" + character + "/")
        self.close()




    def find(self, pixel_similarity):
        path = "saves/" + self.__name + "/temp/"
        character_images = (file for file in os.listdir(path)
                            if os.path.isfile(os.path.join(path, file)))

        self.__sorted_images = []
        white_test = White(float(loadconfig("testwhite")))
        image = pygame.image.load(path + character_images.next())
        width, height = image.get_rect().size

        for column in range(20):
            for row in range(5):
                image = Image.open("files/black.jpeg")
                photo = ImageTk.PhotoImage(image)
                self.__character[column][row].config(image=photo)
                self.__character[column][row].image = photo

        for image_name in character_images:
            full_path = path + image_name
            white_counter = [0, 0, 0, 0]
            found = False
            image = pygame.image.load(full_path)
            for x in range(width):
                for y in range(height):
                    if white_test.test(image.get_at((x, y))):
                        if y < int(height / 4):
                            white_counter[0] += 1
                        elif y < int(height / 4 * 2):
                            white_counter[1] += 1
                        elif y < int(height / 4 * 3):
                            white_counter[2] += 1
                        else:
                            white_counter[3] += 1

            for case in range(len(self.__sorted_images)):
                #print sorted_images[case][0],
                if self.__sorted_images[case][0][0] <= white_counter[0] + pixel_similarity and \
                   self.__sorted_images[case][0][0] >= white_counter[0] - pixel_similarity and \
                   self.__sorted_images[case][0][1] <= white_counter[1] + pixel_similarity and \
                   self.__sorted_images[case][0][1] >= white_counter[1] - pixel_similarity and \
                   self.__sorted_images[case][0][2] <= white_counter[2] + pixel_similarity and \
                   self.__sorted_images[case][0][2] >= white_counter[2] - pixel_similarity and \
                   self.__sorted_images[case][0][3] <= white_counter[3] + pixel_similarity and \
                   self.__sorted_images[case][0][3] >= white_counter[3] - pixel_similarity:
                    self.__sorted_images[case][1].append(full_path)
                    found = True
            if not found:
                self.__sorted_images.append([white_counter, [full_path]])

        for image_column in range(len(self.__sorted_images)):
            for image_row in range(len(self.__sorted_images[image_column][1])):
                if image_row < 5 and image_column < 20:
                    image = Image.open(self.__sorted_images[image_column][1][image_row])
                    photo = ImageTk.PhotoImage(image)
                    self.__character[image_column][image_row].config(image=photo)
                    self.__character[image_column][image_row].image = photo

    def close(self):
        self.root.destroy()


if __name__ == "__main__":
    Main()
