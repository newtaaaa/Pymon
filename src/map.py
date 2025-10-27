from dataclasses import dataclass
import pygame, pytmx, pyscroll
from player import NPC
import re
from pokemon import Combat


@dataclass
class Portal:
    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str


@dataclass
class Map:
    name: str
    walls: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]
    herbes: list[pygame.Rect]


def wrap_text(text, max_length=45):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines


def load_multiline_dialogues(file_path):
    dialogues = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Expression régulière pour capturer chaque bloc de dialogue
    pattern = r'(pnj\d+):((?:.|\n)*?)(?=(?:pnj\d+:)|\Z)'  # Match non-greedy jusqu'au prochain PNJ ou fin
    matches = re.findall(pattern, content)

    for speaker, text in matches:
        speaker = speaker.strip()
        text = text.strip().replace('\n', ' ')
        wrapped_lines = wrap_text(text, max_length=43)

        if speaker not in dialogues:
            dialogues[speaker] = []

        dialogues[speaker].extend(wrapped_lines)

    return dialogues


dialogues = load_multiline_dialogues("textes.txt")


def lireCoordonnees(fichier):
    with open(fichier, 'r') as f:
        lignes = f.readlines()
        city = lignes[0].strip()
        x = float(lignes[1].strip())
        y = float(lignes[2].strip())
        return [x, y, city]


def ecrireCoordonnees(fichier, city, x, y):
    with open(fichier, 'w') as f:
        f.write(f"{city}\n{x}\n{y}\n")


class MapManager:
    def __init__(self, screen, player):
        self.maps = dict()
        self.screen = screen
        self.player = player
        self.current_map = "bourg_grafiti"
        self.register_map("bourg_grafiti", portals=[Portal(from_world="bourg_grafiti", origin_point="house1",
                                                           target_world="house_1", teleport_point="player"),
                                                    Portal(from_world="bourg_grafiti", origin_point="house2",
                                                           target_world="house_2", teleport_point="player"),
                                                    Portal(from_world="bourg_grafiti", origin_point="house3",
                                                           target_world="house_3", teleport_point="player"),
                                                    Portal(from_world="bourg_grafiti", origin_point="house4",
                                                           target_world="house_4", teleport_point="player")
                                                    ], npcs=[NPC("paul", 2, dialogues.get("pnj0", []))])
        self.register_map("house_1", portals=[Portal(from_world="house_1", origin_point="exit_house",
                                                     target_world="bourg_grafiti", teleport_point="house1_enter"),
                                              Portal(from_world="house_1", origin_point="stage_entry",
                                                     target_world="etage_house1", teleport_point="player")])
        self.register_map("etage_house1", portals=[Portal(from_world="etage_house1", origin_point="exit_stage",
                                                           target_world="house_1", teleport_point="player2")])
        self.register_map("house_2", portals=[Portal(from_world="house_2", origin_point="exit_house2",
                                                          target_world="bourg_grafiti", teleport_point="player2")])
        self.register_map("house_3", portals=[Portal(from_world="house_3", origin_point="exit_house3",
                                                     target_world="bourg_grafiti", teleport_point="player3")])
        self.register_map("house_4", portals=[Portal(from_world="house_4", origin_point="exit_house4",
                                                     target_world="bourg_grafiti", teleport_point="player4")])
        self.teleport_player()
        self.teleport_npcs()
        self.combat = Combat(self.screen)

    def check_collisions(self):
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map:
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)
                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    point = self.get_object(copy_portal.teleport_point)
                    ecrireCoordonnees("position.txt", self.current_map, point.x, point.y)
                    self.teleport_player()

        for sprite in self.get_group().sprites():
            if isinstance(sprite, NPC):
                if sprite.feet.colliderect(self.player.feet):
                    if self.player.position != self.player.old_position:
                        self.player.move_back()
                    if sprite.position != sprite.old_position:
                        sprite.move_back()
                    sprite.speed = 0

                else:
                    sprite.speed = 1
            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()
            if sprite.feet.collidelist(self.get_herbes()) > -1:
                if self.player.step_count > 3:
                    self.combat.combat_encours = True
                    self.player.step_count = 0

    def check_npc_collisions(self, dialog_box):
        found = False
        for sprite in self.get_group().sprites():
            if isinstance(sprite, NPC) and sprite.feet.colliderect(self.player.rect):
                dialog_box.execute(sprite.dialog)
                found = True
                break

        if not found and dialog_box.reading:
            dialog_box.reading = False
            dialog_box.text_index = 0
            dialog_box.letter_index = 0

    def register_map(self, name, portals=[], npcs=[]):
        tmx_data = pytmx.util_pygame.load_pygame(f"map/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 3.8

        # Création du groupe de rendu
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=1)

        # Initialisation du joueur si ce n'est pas déjà fait

        group.add(self.player)

        # Détection des collisions
        walls = [pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                 for obj in tmx_data.objects if obj.type == "collision"]

        herbes = [pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                 for obj in tmx_data.objects if obj.type == "herbe"]

        for npc in npcs:
            group.add(npc)
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs, herbes)

    def get_map(self):
        return self.maps[self.current_map]

    def get_group(self):
        return self.get_map().group

    def get_walls(self):
        return self.get_map().walls

    def get_herbes(self):
        return self.get_map().herbes

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

    def update(self):
        self.get_group().update()
        self.player.update()
        self.player.update_animation()
        self.check_collisions()
        for npc in self.get_map().npcs:
            npc.move()

    def get_object(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)

    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]
            npcs = map_data.npcs
            for npc in npcs:
                npc.load_points(map_data.tmx_data)
                npc.teleport_spawn()

    def teleport_player(self):
        point = lireCoordonnees("position.txt")
        self.current_map = point[2]
        self.player.position[0] = point[0]
        self.player.position[1] = point[1]
        self.player.save_location()
