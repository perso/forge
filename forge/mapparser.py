import os
import base64
import zlib
import struct
import xml.etree.ElementTree as ElementTree


class MapParser(object):
    def __init__(self, file_name, level_directory):
        self._level_directory = level_directory
        self._file = os.path.join(level_directory, file_name)
        self._tree = ElementTree.parse(self._file)

    def get_map_width(self):
        _root = self._tree.getroot()
        return _root.attrib["width"]

    def get_map_height(self):
        _root = self._tree.getroot()
        return _root.attrib["height"]

    def get_map_tilewidth(self):
        _root = self._tree.getroot()
        return int(_root.attrib["tilewidth"])

    def get_map_tileheight(self):
        _root = self._tree.getroot()
        return int(_root.attrib["tileheight"])

    def get_map_properties(self):
        property_elements = self._tree.findall("properties/property")
        properties = {}
        for p in property_elements:
            properties[p.attrib["name"]] = p.attrib["value"]
        return properties

    def get_tilesets(self):
        tileset_elements = self._tree.findall("tileset")
        tilesets = {}
        for element in tileset_elements:
            firstgid = element.attrib["firstgid"]
            source = element.attrib["source"]

            tsx_file = os.path.join(self._level_directory, source)
            tree = ElementTree.parse(tsx_file)
            tileset_element = tree.getroot()
            tileset = self.parse_tileset(tileset_element, firstgid)

            tilesets[tileset["name"]] = tileset

        return tilesets

    def parse_tileset(self, tileset_element, firstgid):
        tileset = {
            "firstgid": int(firstgid),
            "name": tileset_element.attrib["name"],
            "tilewidth": int(tileset_element.attrib["tilewidth"]),
            "tileheight": int(tileset_element.attrib["tileheight"]),
            "source": tileset_element.find("image").attrib["source"],
            "trans": tileset_element.find("image").attrib["trans"],
            "width": int(tileset_element.find("image").attrib["width"]),
            "height": int(tileset_element.find("image").attrib["height"]),
            "properties": self.get_tile_properties(tileset_element, firstgid)
        }
        return tileset

    def get_tile_ids(self, layer_name=None):
        if layer_name is not None:
            pathexp = "layer[@name='" + layer_name + "']/data"
        else:
            pathexp = ".//layer/data"
        data_elements = self._tree.findall(pathexp)

        tileids = []
        for element in data_elements:
            data = base64.b64decode(element.text)
            data = zlib.decompress(data)
            for chunk in self._chunks(data, 4):
                tile_id = struct.unpack('<I', chunk)
                tileids.append(tile_id[0])
        return tileids

    def get_map_objects(self):
        object_elements = self._tree.findall("objectgroup/object")

        objects = []
        for obj in object_elements:
            if "name" not in obj.attrib:
                obj.attrib["name"] = ""
            if "type" not in obj.attrib:
                obj.attrib["type"] = ""

            properties = self.get_object_properties(obj)

            objects.append({
                "name": obj.attrib["name"],
                "type": obj.attrib["type"],
                "gid": obj.attrib["gid"],
                "x": obj.attrib["x"],
                "y": obj.attrib["y"],
                "properties": properties
            })
        return objects

    @staticmethod
    def get_tile_properties(tileset_element, firstgid):
        tile_elements = tileset_element.findall("tile")
        tiles = {}
        for t in tile_elements:
            local_id = t.attrib["id"]
            property_elements = t.findall("properties/property")
            properties = {}
            for p in property_elements:
                properties[p.attrib["name"]] = p.attrib["value"]
            index = int(local_id) + int(firstgid)
            tiles[index] = properties
        return tiles

    @staticmethod
    def get_object_properties(object_element):
        # gid = object_element.attrib["gid"]
        property_elements = object_element.findall("properties/property")
        properties = {}
        for p in property_elements:
            properties[p.attrib["name"]] = p.attrib["value"]
        return properties

    @staticmethod
    def _chunks(data, size):
        for i in range(0, len(data), size):
            yield data[i:i + size]