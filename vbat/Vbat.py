#!/usr/bin/env python

from __future__ import absolute_import

import os
import copy
from datetime import datetime

from .CamLib import CamLib
from .FileHandler import loadconfig

class Vbat(object):
    def __init__(self, name):
        self.__field = []
        video = loadconfig("video")
        camx = int(loadconfig("camx"))
        camy = int(loadconfig("camy"))
        self.__percent = int(loadconfig("percent")) * 2
        self.__grayvalue = float(loadconfig("testwhite"))
        self.__divider = int(loadconfig("divider"))
        coofile = "saves/" + name + "/" + name + ".coo"
        self.createfield(coofile)
        self.TemplateFolder = "saves/" + name + "/" + name + ".templates"
        self.__matrix, self.__antimatrix, self.__characterdata = self.__creatematrix()
        self.__grabber = CamLib(video, int(camx), int(camy))
        self.__white = White(self.__grayvalue)

    def image_test(self, test_image):
        # run from image
        self.__grabber.load_image(test_image)
        return self.get_data()

    def run(self):
            # run from camera
            self.__grabber.take_image()
            return self.get_data()

    def createfield(self, coofile):
        f = open(coofile, "r")
        for line in f:
            line = line.replace("\n", "")
            line = line.split(";")
            temp = []
            for character in line:
                if character[0][0] != str(0):
                    temp.append((int(character.split(",")[0]), int(character.split(",")[1])))
                else:
                    temp.append((int(character.split(",")[0]), character.split(",")[1]))
            self.__field.append(temp)

    def __creatematrix(self):
        # Matrix[i] = eine komplette zahl mit Matrix[i][j] als einzelne zeile.
        # Marix wird True an stellen wo keine Null im Template stand.
        f = open(self.TemplateFolder, "r")
        temp = []
        matrix = []
        for line in f:
            line = line.replace("\n", "")
            line = line.split(",")
            if line[0] != "#":
                for i in range(len(line)):
                    if line[i] != "0":
                        line[i] = True
                    else:
                        line[i] = ""
                temp.append(line)
            else:
                matrix.append(temp)
                temp = []

        # erstelle antimatrix
        antimatrix = copy.deepcopy(matrix)
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    antimatrix[i][j][k] = ""

        # Fuelle antimatrix mit True
        for i in range(len(matrix)):
            for x in range(len(matrix[i][1:])):
                for y in range(len(matrix[i][x][1:])):
                    if matrix[i][x][y]:
                        if matrix[i][x + 1][y] == "":
                            antimatrix[i][x + 1][y] = True
                        if matrix[i][x][y + 1] == "":
                            antimatrix[i][x][y + 1] = True
                        if matrix[i][x - 1][y] == "":
                            antimatrix[i][x - 1][y] = True
                        if matrix[i][x][y - 1] == "":
                            antimatrix[i][x][y - 1] = True

        # Eine Liste mit der Anzahl der white (True) und non_white (False) stellen wird erstellt.
        characterdata = []
        # characterdata=[i][white, non_white, white-correct, non_white-correct]
        for i in range(len(matrix)):
            werte = [0, 0, 0, 0]
            for x in range(0, len(matrix[i]), self.__divider):
                for y in range(len(matrix[i][x])):
                    if matrix[i][x][y]:
                        werte[0] += 1
                    if antimatrix[i][x][y]:
                        werte[1] += 1
            characterdata.append(werte)

        # komprimiere Matrix
        antitemp = copy.deepcopy(matrix[0])
        postemp = copy.deepcopy(matrix[0])
        for i in range(len(antitemp)):
            for j in range(len(antitemp[i])):
                antitemp[i][j] = ""
                postemp[i][j] = ""

        for i in range(len(matrix)):
            for x in range(len(matrix[i])):
                for y in range(len(matrix[i][x])):
                    if matrix[i][x][y]:
                        if postemp[x][y] == "":
                            postemp[x][y] = []
                        postemp[x][y].append(i)
                    if antimatrix[i][x][y]:
                        if antitemp[x][y] == "":
                            antitemp[x][y] = []
                        antitemp[x][y].append(i)

        return postemp, antitemp, characterdata

    def this(self, xx, yy):
        best_value = 0
        best_from = 0
        for y in range(0, len(self.__matrix), self.__divider):
            for x in range(len(self.__matrix[y])):
                if self.__white.test(self.__grabber.get_at(x + xx, y + yy)):
                    for i in self.__matrix[y][x]:
                        self.__characterdata[i][2] += 100
                else:
                    for i in self.__antimatrix[y][x]:
                        self.__characterdata[i][3] += 100

        for i in range(len(self.__characterdata)):
            tempresult = ((self.__characterdata[i][2] / self.__characterdata[i][0]) + (
                self.__characterdata[i][3] / self.__characterdata[i][1]))
            if tempresult > best_value:
                best_value = tempresult
                best_from = i
            self.__characterdata[i][2] = 0
            self.__characterdata[i][3] = 0

        if best_value > self.__percent:
            if best_from < 10:
                return best_from
            elif best_from == 10:
                return "."
            elif best_from == 11:
                return "-"
        else:
            return "X"

    def get_data(self):
        result = []
        temp = []
        for term in self.__field:
            for character in term:
                if character[0] != 0:
                    temp.append(self.this(character[0], character[1]))
                else:
                    temp.append(character[1])
            result.append(temp)
            temp = []
        return result
