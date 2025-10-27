
from player import Player
from map import *
from src.dialog import DialogBox
from pokemon import OwnPokemonData, HealthBar


def lire_pseudo():
    with open("pseudo.txt", 'r') as f:
        return f.readline().strip()


class Game:
    def __init__(self):
        self.dialogue_box = DialogBox()
        self.dialogue_box.temps_ecran = 100
        self.dialogue_box.set_speed(20)
        self.screen = pygame.display.set_mode((1080, 720))
        pygame.display.set_caption("POMEKON")
        self.font = pygame.font.Font("dialogue/dialog_font.ttf", 40)
        self.font1 = pygame.font.Font("dialogue/dialog_font.ttf", 32)
        self.font2 = pygame.font.Font("dialogue/dialog_font.ttf", 30)
        self.player = Player()
        self.map_manager = MapManager(self.screen, self.player)
        self.menu = pygame.image.load("img/menus/menu.png")
        self.menu = pygame.transform.scale(self.menu, (350, 450))
        self.pokemons = OwnPokemonData()
        self.menu_on = False
        self.bar = [180, 240, 295, 350, 410, 465, 535]
        self.menu_ind = 0
        self.dialog_started = False
        self.height = 70

    def afficher_pokemons(self):
        self.pokemons.update()
        self.screen.blit(self.pokemons.menu, (0, 0))
        self.screen.blit(self.pokemons.cancel, (800, 550))
        self.screen.blit(self.pokemons.first_po, (0, 60))
        healthBar = HealthBar(148, 274, self.pokemons.own_pokemon[0]["hp_act"],  self.pokemons.own_pokemon[0]["hp"], 220,
                              15, self.screen, False)
        for i in range(self.pokemons.nb_pokemons - 1):
            self.screen.blit(self.pokemons.other_po, (390, self.pokemons.emplacements[i]))
        if self.pokemons.menu_ind == 0:
            self.screen.blit(self.pokemons.first_po_s, (0, 58))
        elif self.pokemons.menu_ind == 6:
            self.screen.blit(self.pokemons.cancel_s, (820, 570))
        else:
            try:
                self.screen.blit(self.pokemons.other_po_s, (352, self.pokemons.update_selected()[self.pokemons.menu_ind-1]))
            except IndexError:
                if self.pokemons.remonter:
                    self.pokemons.menu_ind = 6
                else:
                    self.pokemons.menu_ind = self.pokemons.nb_pokemons - 1

        for i in range(self.pokemons.nb_pokemons - 1):
            self.screen.blit(self.pokemons.sprites[i + 1], (360, self.pokemons.emplacements[i] - 20))
            level = self.font.render(f"{self.pokemons.own_pokemon[i+1]['level']}", False, (255, 255, 255))
            self.screen.blit(level, (620, self.pokemons.emplacements[i]+78))
            surname = self.font2.render(f"{self.pokemons.own_pokemon[i+1]['surname']}", False, (255, 255, 255))
            self.screen.blit(surname, (520, self.pokemons.emplacements[i]+40))
            if len(list(str(self.pokemons.own_pokemon[i+1]['hp_act']))) == 3:
                hp_act = self.font1.render(f"{self.pokemons.own_pokemon[i+1]['hp_act']}",
                                           False, (255, 255, 255))
                self.screen.blit(hp_act, (890, self.pokemons.emplacements[i]+80))
            else:
                hp_act = self.font1.render(f"{self.pokemons.own_pokemon[i+1]['hp_act']}",
                                           False, (255, 255, 255))
                self.screen.blit(hp_act, (910, self.pokemons.emplacements[i]+80))
            hp = self.font1.render(
                f"{self.pokemons.own_pokemon[i+1]['hp']}",
                False, (255, 255, 255))
            self.screen.blit(hp, (990, self.pokemons.emplacements[i]+80))
            temp_healthBar = HealthBar(835, self.pokemons.emplacements[i]+53, self.pokemons.own_pokemon[i+1]["hp_act"], self.pokemons.own_pokemon[i+1]["hp"],
                                  220,
                                  15, self.screen, False)
            temp_healthBar.draw()

        self.screen.blit(self.pokemons.sprites[0], (5, 100))
        healthBar.draw()
        if len(list(str(self.pokemons.own_pokemon[0]['hp_act']))) == 3:
            hp_act = self.font1.render(f"{self.pokemons.own_pokemon[0]['hp_act']}",
                                     False, (255, 255, 255))
            self.screen.blit(hp_act, (200, 300))
        else:
            hp_act = self.font1.render(f"{self.pokemons.own_pokemon[0]['hp_act']}",
                                       False, (255, 255, 255))
            self.screen.blit(hp_act, (223, 300))
        hp = self.font1.render(
            f"{self.pokemons.own_pokemon[0]['hp']}",
            False, (255, 255, 255))
        self.screen.blit(hp, (305, 300))
        level = self.font.render(f"{self.pokemons.own_pokemon[0]['level']}", False, (255, 255, 255))
        self.screen.blit(level, (230, 215))
        surname = self.font2.render(f"{self.pokemons.own_pokemon[0]['surname']}", False, (255, 255, 255))
        self.screen.blit(surname, (150, 175))

    def defiler_menu(self, aug):
        if aug == 1:
            if self.menu_ind < 6:
                self.menu_ind += 1
            else:
                self.menu_ind = 0
        else:
            if self.menu_ind > 0:
                self.menu_ind -= 1
            else:
                self.menu_ind = 6
        if self.menu_ind == 6:
            self.height = 50
        else:
            self.height = 70

    def update(self):
        self.map_manager.update()

    def afficher_menu(self):
        self.menu_on = not self.menu_on
        self.menu_ind = 0

    def actualiser(self, left, right, down, up):
        self.player.save_location()
        self.player.move(left, right, down, up)
        self.map_manager.draw()
        self.update()
        if self.menu_on:
            self.screen.blit(self.menu, (650, 150))
            text2 = self.font.render(lire_pseudo(), False, (0, 0, 0))
            self.screen.blit(text2, (720, 360))
            pygame.draw.rect(self.screen, (0, 0, 0), (705, self.bar[self.menu_ind], 270, self.height), width=5)
        if self.pokemons.menu_po:
            self.afficher_pokemons()
        if self.map_manager.combat.combat_encours:
            self.map_manager.combat.update()
            self.map_manager.combat.update_begining()
            if not self.dialog_started and self.map_manager.combat.finalbegin:
                self.dialogue_box.execute([f"Un {self.map_manager.combat.sauvage.name} sauvage apparait !"])
                self.dialog_started = True
            if self.map_manager.combat.finalbegin:
                self.map_manager.combat.update_pokemon_entry(self.dialogue_box)
        if self.map_manager.combat.combat_encours and self.pokemons.menu_po:
            self.afficher_pokemons()
