import os
import pygame
import math


def world_to_screen_coords(world_coords):
    screen_x = 32 * world_coords[0]
    screen_y = 32 * world_coords[1]
    return screen_x, screen_y


def screen_to_world_coords(screen_coords):
    world_x = round(screen_coords[0] / 32)
    world_y = round(screen_coords[1] / 32)
    return world_x, world_y


def load_image(file_name, color_key=None, image_directory='data'):
    """Loads an image, file_name, from image_directory, for use in pygame"""
    file = os.path.join(image_directory, file_name)
    _image = pygame.image.load(file)
    if color_key:
        if color_key == -1:
            #print("upper left")
            # If the color key is -1, set it to color of upper left corner
            color_key = _image.get_at((0, 0))
        #print("convert")
        #print(color_key)
        #print(file_name)
        #print(image_directory)
        _image.set_colorkey(color_key)
        _image = _image.convert()
    else:  # If there is no color key, preserve the image's alpha per pixel.
        #print("preserve alpha")
        _image = _image.convert_alpha()
    return _image


def get_image_by_gid(gid, tileset):
    local_id = gid - tileset["firstgid"]
    #print(str(tileset["source"])+" "+str(tileset["firstgid"]))
    tm_image = load_image(tileset["source"], 0xff00ff, "data")
    tm_count_x = tileset["width"] / tileset["tilewidth"]
    tile_x = local_id % tm_count_x
    tile_y = (local_id - tile_x) / tm_count_x
    r = pygame.Rect((tile_x * tileset["tilewidth"], tile_y * tileset["tileheight"]),
                    (tileset["tilewidth"], tileset["tileheight"]))
    return tm_image.subsurface(r)


def get_tileset_by_gid(gid, tilesets):
    ts = None
    for name, tileset in tilesets.items():
        if int(gid) >= tileset["firstgid"]:
            ts = tileset
        else:
            break
    return ts


def get_object_images(gid, tileset):
    #print(tileset["properties"])
    object_id = tileset["properties"][gid]["objectid"]
    images = {}
    for p_gid, p_dict in tileset["properties"].items():
        if p_dict["objectid"] == object_id:
            images[p_dict["state"]] = get_image_by_gid(p_gid, tileset)
    return images


def get_direction(from_point, to_point):
    radians = math.atan2(to_point[1] - from_point[1], to_point[0] - from_point[0])
    if radians >= 0:
        if radians < (math.pi / 8):
            return Direction.EAST
        elif radians < (3 * math.pi / 8):
            return Direction.SOUTH_EAST
        elif radians < (5 * math.pi / 8):
            return Direction.SOUTH
        elif radians < (7 * math.pi / 8):
            return Direction.SOUTH_WEST
        else:
            return Direction.WEST
    else:
        if radians > (-math.pi / 8):
            return Direction.EAST
        elif radians > (-3 * math.pi / 8):
            return Direction.NORTH_EAST
        elif radians > (-5 * math.pi / 8):
            return Direction.NORTH
        elif radians > (-7 * math.pi / 8):
            return Direction.NORTH_WEST
        else:
            return Direction.WEST


def draw_green_marker(screen, rect):
    s = pygame.Surface((rect.width, rect.height))
    s.set_alpha(128)
    s.fill((0, 255, 0))
    screen.blit(s, rect)


class Direction:
    NORTH = (0, -1)
    EAST = (1, 0)
    WEST = (-1, 0)
    SOUTH = (0, 1)
    NORTH_EAST = (1, -1)
    SOUTH_EAST = (1, 1)
    SOUTH_WEST = (-1, 1)
    NORTH_WEST = (-1, -1)