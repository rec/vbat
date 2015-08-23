__author__ = 'testcaseone'


class CamLib(object):
    def __init__(self, source, x, y):
        self.__source = source
        self.__x = x
        self.__y = y
        self.__image = []
        import pygame.camera
        pygame.init()
        pygame.camera.init()
        self.__cam = pygame.camera.Camera(self.__source, (self.__x, self.__y))
        self.__cam.start()

    def load_image(self, path):
        import pygame
        self.__image = pygame.image.load(path)

    def take_image(self):
        self.__image = self.__cam.get_image()

    def get_at(self, px, py):
        return self.__image.get_at((px, py))

class White(object):
    def __init__(self, value):
        self.__value = value

    def test(self, color):
            if color[0] * .3 + color[1] * 0.6 + color[2] * 0.1 < self.__value:
                return False
            else:
                return True