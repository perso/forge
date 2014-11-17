from mapparser import MapParser
from lib import *


class Dungeon(object):
    def __init__(self):

        self.width = 0
        self.height = 0
        self.tilesize = 0
        self.tiles = []
        self.tilesets = {}
        self.sloc = (0, 0)

        self._load_map()

    def get_tile_at(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            index = int(x + y * self.width)
            return self.tiles[index]

    def draw(self, screen, player):
        for x, y, viewport_x, viewport_y in player.viewport.coords():
            if x >= 0 and y >= 0:
                visible = True
                if player.viewport.visibility_mask.get_at((viewport_x, viewport_y)) == 0:
                    visible = False
                t = self.get_tile_at(x, y)
                if t is not None:
                    t.draw(screen, viewport_x, viewport_y, visible)

    def update(self):
        pass

    def _load_map(self):

        parser = MapParser("testroom.tmx", "data")

        self.width = int(parser.get_map_width())
        self.height = int(parser.get_map_height())
        self.tilesize = int(parser.get_map_tilewidth())
        self.tilesets = parser.get_tilesets()

        tileids = parser.get_tile_ids("RoomTiles")
        tileset = self.tilesets["dungeon"]
        for i in range(0, len(tileids), self.width):
            tileid_row = tileids[i:i + self.width]
            y = i / self.width
            for x, tileid in enumerate(tileid_row):
                image = get_image_by_gid(tileid, tileset)
                self.tiles.append(Tile(x, y, image, tileid, self.tilesize,
                                       tileset["properties"][tileid]))

        map_objects = parser.get_map_objects()
        tileset = self.tilesets["objects"]
        for obj in map_objects:
            gid = int(obj["gid"])
            tile_x = int(obj["x"])
            tile_y = int(obj["y"])

            images = get_object_images(gid, tileset)
            state = tileset["properties"][gid]["state"]

            tile = self.get_tile_at(tile_x / self.tilesize,
                                    tile_y / self.tilesize - 1)

            if obj["type"] == "sloc":
                self.sloc = (int(int(obj["x"]) / self.tilesize), int(int(obj["y"]) / self.tilesize))
            elif tile is not None:
                if obj["type"] == "door":
                    tile.add_entity(Door(tile, images, state))
                else:
                    tile.add_entity(Entity(tile, images, state))


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, gid, tilesize, properties):
        self.gid = gid
        self.position = (x, y)
        self.image = image
        self.tilesize = tilesize
        self.rect = pygame.Rect((x * tilesize, y * tilesize), (tilesize, tilesize))
        self.properties = properties
        self.entities = []
        self.items = []

    def is_passable(self):
        if self.properties["passable"] == "false":
            return False
        for entity in self.entities:
            if not entity.is_passable():
                return False
        return True

    def draw(self, screen, x, y, visible):
        if visible:
            self.rect.top = self.tilesize * y
            self.rect.left = self.tilesize * x
            screen.blit(self.image, self.rect)
            for entity in self.entities:
                entity.draw(screen, x, y, self.tilesize)

    def add_entity(self, entity):
        self.entities.append(entity)

    def onclick(self, originator):
        for entity in self.entities:
            entity.onclick(originator)


class Entity(pygame.sprite.Sprite):
    def __init__(self, tile, images, state):
        self.tile = tile
        self.state = state
        self.animations = images
        self.image = self.animations[state]
        self.rect = tile.rect.copy()

    def get_classname(self):
        return type(self).__name__

    def get_tile(self):
        return self.tile

    def is_passable(self):
        return True

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def draw(self, screen, x, y, tilesize):
        self.rect.top = tilesize * y
        self.rect.left = tilesize * x
        screen.blit(self.image, self.rect)

    def onclick(self, originator):
        pass


class Door(Entity):
    def __init__(self, tile, images, state):
        super().__init__(tile, images, state)

    def open(self):
        self.state = "open"
        self.image = self.animations[self.state]

    def close(self):
        self.state = "closed"
        self.image = self.animations[self.state]

    def is_passable(self):
        return self.state == "open"

    def onclick(self, originator):
        super().onclick(originator)
        if originator.in_proximity(self):
            if self.get_state() == "closed":
                self.open()
            else:
                self.close()
