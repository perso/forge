import sys

import configparser

from pygame.locals import *

from dungeon import Dungeon
from player import Player, Viewport
from lib import *


class Application(object):
    def __init__(self):

        # Initialize ConfigParser and read settings.
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._width = int(config['Window'].get('Width', 480))
        self._height = int(config['Window'].get('Height', 480))

        # Initialize Pygame.
        pygame.init()
        pygame.display.set_caption("Forge")
        self._screen = pygame.display.set_mode((self._width, self._height))
        self._font = pygame.font.SysFont("Courier New", 16)

        # Initialize the dungeon.
        self._quit = False
        self._dungeon = Dungeon()

        # Initialize the Player and assign viewport.
        start_x = 6
        start_y = 5
        viewport_size = screen_to_world_coords((self._width, self._height))
        viewport = Viewport((start_x, start_y), viewport_size)
        self._player = Player(viewport)

    def start(self):

        screen_center = self._screen.get_rect().center

        time_step = 150
        accumulated_time = 0
        clock = pygame.time.Clock()

        while not self._quit:

            try:

                dt = clock.tick(60)
                accumulated_time += dt

                self._screen.fill((0, 0, 0))

                self._dungeon.update()
                self._player.update()

                self._player.calculate_visibility(self._dungeon)

                self._dungeon.draw(self._screen, self._player)
                self._player.draw(self._screen)

                self._display_fps(int(round(clock.get_fps())))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == QUIT:
                        self._quit = True

                    elif event.type == KEYDOWN:
                        if event.key in [K_ESCAPE]:
                            self._quit = True
                        if event.key in [K_UP, K_w]:
                            self._player.try_move(self._dungeon, Direction.NORTH)
                        if event.key in [K_DOWN, K_s]:
                            self._player.try_move(self._dungeon, Direction.SOUTH)
                        if event.key in [K_LEFT, K_a]:
                            self._player.try_move(self._dungeon, Direction.WEST)
                        if event.key in [K_RIGHT, K_d]:
                            self._player.try_move(self._dungeon, Direction.EAST)

                    elif event.type == MOUSEBUTTONDOWN:
                        b1, b2, b3 = pygame.mouse.get_pressed()
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        mouse_pos = (mouse_x, mouse_y)
                        if True in [b3]:
                            d = get_direction(screen_center, mouse_pos)
                            self._player.try_move(self._dungeon, d)
                        if True in [b2]:
                            tilesize = self._dungeon.tilesize
                            dungeon_x = math.floor(mouse_x / tilesize) + self._player.viewport.rect.left
                            dungeon_y = math.floor(mouse_y / tilesize) + self._player.viewport.rect.top
                            t = self._dungeon.get_tile_at(dungeon_x, dungeon_y)
                            if t is not None:
                                t.onclick(self._player)

                if accumulated_time >= time_step:

                    pk = pygame.key.get_pressed()
                    if True in [pk[K_RIGHT], pk[K_LEFT], pk[K_UP], pk[K_DOWN],
                                pk[K_d], pk[K_a], pk[K_w], pk[K_s]]:
                        if True in [pk[K_RIGHT], pk[K_d]]:
                            self._player.try_move(self._dungeon, Direction.EAST)
                        if True in [pk[K_LEFT], pk[K_a]]:
                            self._player.try_move(self._dungeon, Direction.WEST)
                        if True in [pk[K_UP], pk[K_w]]:
                            self._player.try_move(self._dungeon, Direction.NORTH)
                        if True in [pk[K_DOWN], pk[K_s]]:
                            self._player.try_move(self._dungeon, Direction.SOUTH)
                    else:
                        b1, b2, b3 = pygame.mouse.get_pressed()
                        if True in [b3]:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            mouse_pos = (mouse_x, mouse_y)
                            d = get_direction(screen_center, mouse_pos)
                            self._player.try_move(self._dungeon, d)

                    accumulated_time = 0

            except:
                print("Unexpected error: {0}".format(sys.exc_info()))
                raise

        pygame.quit()
        return

    def _display_fps(self, fps):
        ren = self._font.render("FPS:" + str(fps), 0, (255, 25, 25))
        self._screen.blit(ren, (5, 5))