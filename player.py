from lib import *


class Player(pygame.sprite.Sprite):
    def __init__(self, viewport):

        self.name = "perso"
        self.viewport = viewport
        self.position = (viewport.rect.centerx, viewport.rect.centery)
        self.image = load_image('player.png', 0xff00ff, 'data')
        center_tile_x = (self.viewport.rect.width - 1) / 2
        center_tile_y = (self.viewport.rect.height - 1) / 2
        self.rect = pygame.Rect((center_tile_x * 32, center_tile_y * 32), (32, 32))

    def try_move(self, dungeon, move_dir):
        new_position = (self.position[0] + move_dir[0], self.position[1] + move_dir[1])
        t = dungeon.get_tile_at(new_position[0], new_position[1])
        if t.is_passable():
            self.move(move_dir)

    def move(self, move_dir):
        self.position = (self.position[0] + move_dir[0], self.position[1] + move_dir[1])
        self.viewport.move(move_dir)

    def in_proximity(self, other):
        top_left = (self.position[0] - 1, self.position[1] - 1)
        bottom_right = (self.position[0] + 1, self.position[1] + 1)
        for y in range(top_left[1], bottom_right[1] + 1):
            for x in range(top_left[0], bottom_right[0] + 1):
                if other.get_tile().position[0] == x and other.get_tile().position[1] == y:
                    return True
        return False

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # line scan algorithm to "flood fill" the visibility mask
    def calculate_visibility(self, dungeon):
        self.viewport.calculate_visibility(self, dungeon)


class Viewport(object):
    def __init__(self, world_coords, size):
        left = world_coords[0] - size[0] / 2
        top = world_coords[1] - size[1] / 2
        self.rect = pygame.Rect((left, top), size)
        self.visibility_mask = pygame.Mask(size)
        self.visibility_mask.clear()

    def move(self, move_dir):
        self.rect.move_ip(move_dir[0], move_dir[1])

    def coords(self):
        viewport_y = 0
        for y in range(self.rect.top, self.rect.bottom):
            viewport_x = 0
            for x in range(self.rect.left, self.rect.right):
                yield (x, y, viewport_x, viewport_y)
                viewport_x += 1
            viewport_y += 1

    def world_to_viewport_coord(self, world_coords):
        viewport_x = world_coords[0] - self.rect.left
        viewport_y = world_coords[1] - self.rect.top
        return viewport_x, viewport_y

    def calculate_visibility(self, player, dungeon):

        self.visibility_mask.clear()

        # Calculate initial seed point.
        x, y = player.position[0], player.position[1]
        x, y = self.find_left_boundary(x, y, dungeon)
        seed_points = [(x, y)]
        point_set = set(seed_points)

        while seed_points:
            seed_point = seed_points.pop()
            length = self.fill_scan_line(seed_point[0], seed_point[1], dungeon)

            x1 = seed_point[0]
            x2 = x1 + length - 1

            bottom_seed_points = self.find_new_seed_points(x1, x2, seed_point[1] + 1, dungeon)
            bottom_point_set = set(bottom_seed_points)
            bottom_point_set.difference_update(point_set)
            point_set.update(bottom_point_set)

            top_seed_points = self.find_new_seed_points(x1, x2, seed_point[1] - 1, dungeon)
            top_point_set = set(top_seed_points)
            top_point_set.difference_update(point_set)
            point_set.update(top_point_set)

            seed_points.extend(list(bottom_point_set))
            seed_points.extend(list(top_point_set))

        self.fill_border_line()

    def find_left_boundary(self, x, y, dungeon):

        t = dungeon.get_tile_at(x, y)

        viewport_x, viewport_y = self.world_to_viewport_coord((x, y))

        while x > 0 and viewport_x > 0 and t.is_passable():
            x -= 1
            viewport_x, viewport_y = self.world_to_viewport_coord((x, y))
            t = dungeon.get_tile_at(x, y)
        if not t.is_passable():
            x += 1
        return x, y

    def fill_scan_line(self, x, y, dungeon):

        viewport_x, viewport_y = self.world_to_viewport_coord((x, y))
        if not (0 <= viewport_x <= 14 and 0 <= viewport_y <= 14):
            return 0

        self.visibility_mask.set_at((viewport_x, viewport_y), 1)

        line_length = 1
        while 0 <= viewport_x < 14:
            x += 1
            viewport_x, viewport_y = self.world_to_viewport_coord((x, y))
            t = dungeon.get_tile_at(x, y)
            if not t.is_passable():
                break
            self.visibility_mask.set_at((viewport_x, viewport_y), 1)
            line_length += 1
        return line_length

    def find_new_seed_points(self, start_x, end_x, y, dungeon):

        seed_points = []

        t = dungeon.get_tile_at(start_x, y)
        if t.is_passable():
            start_x, y = self.find_left_boundary(start_x, y, dungeon)

        prev_is_passable = False
        for x in range(start_x, end_x + 1):
            t = dungeon.get_tile_at(x, y)
            if t.is_passable():
                if not prev_is_passable:
                    seed_points.append((x, y))
                prev_is_passable = True
            else:
                prev_is_passable = False

        return seed_points

    def fill_border_line(self):
        border_set = set()
        width, height = self.visibility_mask.get_size()
        for y in range(0, height):
            for x in range(0, width):
                viewport_x, viewport_y = x, y
                if 0 < viewport_x < 14 and 0 < viewport_y < 14 and self.visibility_mask.get_at(
                        (viewport_x, viewport_y)) == 1:
                    for nx in [viewport_x - 1, viewport_x, viewport_x + 1]:
                        for ny in [viewport_y - 1, viewport_y, viewport_y + 1]:
                            border_set.add((nx, ny))
        border_list = list(border_set)
        for b in border_list:
            self.visibility_mask.set_at(b, 1)