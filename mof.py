'''a simple game to learn to read partitures'''

import os
import pygame
import random

from pygame.locals import *

def load_image(name, base='imgs'):
    '''load an image from a file and return the surface
    and the rect'''

    fullname = os.path.join(base, name)

    try:
        image = pygame.image.load(fullname)

    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message

    image = image.convert_alpha()
    return image, image.get_rect()


def random_note():
    '''generate a random note'''
    return Note(random.randint(8, 20), random.randint(0, 3))


class Note(object):
    '''representation of a note'''

    (A0, B0, C0, D0, E0, F0, G0, A, B, C, D, E, F, G, A1, B1, C1, D1, E1, F1,
            G1) = range(21)
    NOTES = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'D', 'E', 'F',
                'G', 'A', 'B', 'C', 'D', 'E', 'F', 'G')
    (FLAT, NATURAL, SHARP) = range(3)
    (WHOLE, HALF, QUARTER, EIGHTH) = range(4)

    def __init__(self, note, shape, accidental=None):
        self.note   = note
        self.shape  = shape

        if accidental is None:
            self.accidental = Note.NATURAL
        else:
            self.accidental = accidental

class Staff(object):
    '''a surface that holds notes'''

    def __init__(self, signature=(4, 4), x=20, y=100, height=100,
            width=600, clef='g'):

        self.x = x
        self.y = y
        self.height = height
        self.width  = width
        self.signature = signature
        self.clef = clef

        self.notes = {}
        self.__load_resources()
        self.offset = {}

        if self.clef == 'g':
            for i in range(21):
                self.offset[i] = self.y + self.height - (
                        (i - 4) * self.height / 8)
        else:
            for i in range(21):
                self.offset[i] = self.y + self.height - (
                        (i - 6) * self.height / 8)

    def draw(self, surface):
        '''draw the staff in the surface passed as parameter'''
        x = self.x
        y = self.y
        color = (0, 0, 0)

        pygame.draw.rect(surface, color, (x, y, self.width, self.height), 1)
        ypos = y + self.height/4
        pygame.draw.line(surface, color, (x, ypos), (x + self.width, ypos))
        ypos = y + (self.height/4 * 2)
        pygame.draw.line(surface, color, (x, ypos), (x + self.width, ypos))
        ypos = y + (self.height/4 * 3)
        pygame.draw.line(surface, color, (x, ypos), (x + self.width, ypos))

        if self.clef == 'f':
            image = self.fclef[0]
            offset = 0
        else:
            image = self.gclef[0]
            offset = -40

        surface.blit(image, (self.x, self.y + offset))

    def draw_note(self, surface, note, pos=0):
        '''draw a note in the surface passed as parameter'''
        surface.blit(self.notes[note.shape][0],
                (self.x + 60 + pos * self.width / 8, self.offset[note.note]))

    def __load_resources(self):
        '''load all the resources for the object'''
        self.__load_images()

    def __load_images(self):
        '''load all images for the object'''
        self.notes[Note.WHOLE]   = load_image("whole.png")
        self.notes[Note.HALF]    = load_image("half.png")
        self.notes[Note.QUARTER] = load_image("quarter.png")
        self.notes[Note.EIGHTH]  = load_image("eighth.png")

        self.fclef = load_image("fclef.png")
        self.gclef = load_image("gclef.png")

class Game(object):
    '''the main game class, perfome the logic here'''

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Mozart on Fire!')

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

    def run(self, GameClass):
        '''loop until we have to quit on user action'''
        game = GameClass(self.screen, self.background)

        do_quit = False

        while not do_quit:
            do_quit = game.step()


class HitTheKeyGame(object):

    def __init__(self, screen, background):
        self.screen = screen
        self.background = background
        self.gstaff = Staff(y=80)
        self.fstaff = Staff(y=300, clef='f')
        self.new_note()
        self.__load_resources()

        self.count_ok = 0
        self.count_bad = 0
        self.is_ok = True

        self.font = pygame.font.Font(None, 36)

    def __load_resources(self):
        '''load all the resources for the object'''
        self.ok  = load_image("ok.png")
        self.bad = load_image("bad.png")

    def new_note(self):
        '''generate a new random note for one of the
        staffs'''

        self.staff = random.choice(['f', 'g'])
        self.last_note = random_note()
        self.last_pos  = random.randint(0, 6)

    def step(self):
        '''perform a single step in the logic of the game'''

        self.background.fill((250, 250, 250))
        self.gstaff.draw(self.background)
        self.fstaff.draw(self.background)
        self.show_count()
        self.screen.blit(self.background, (0, 0))

        for event in pygame.event.get():

            if event.type == QUIT:
                return True

            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return True

            elif event.type == KEYUP and event.key < 128:

                if Note.NOTES[self.last_note.note] == chr(event.key).upper():
                    self.is_ok = True
                    self.count_ok += 1
                else:
                    self.is_ok = False
                    self.count_bad += 1

                self.new_note()

        self.show_status()
        self.draw_note()
        pygame.display.flip()

        return False

    def draw_note(self):
        '''draw a random note on one of the staffs'''

        if self.staff == 'f':
            staff = self.fstaff
        else:
            staff = self.gstaff

        staff.draw_note(self.screen, self.last_note, self.last_pos)

    def show_status(self):
        '''show the status of the last selection'''
        if self.is_ok:
            self.screen.blit(self.ok[0], (5, 5))
        else:
            self.screen.blit(self.bad[0], (5, 5))

    def show_count(self):
        '''show the number of correct vs incorrect answers'''
        text = self.font.render(str(self.count_ok) + \
                " / " + str(self.count_bad), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=300, centery=460)
        self.background.blit(text, textpos)

if __name__ == '__main__':
    Game().run(HitTheKeyGame)
