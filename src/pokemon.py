import pygame
import os
import random
import re


pygame.init()
bg = pygame.image.load("img/animDebutCombat/bg_fight.png")
bg = pygame.transform.scale(bg, (1080, 720))
fight_menu = pygame.image.load("img/animDebutCombat/menu_fight.png")
fight_menu = pygame.transform.scale(fight_menu, (1080, 210))
attack_menu = pygame.image.load("img/animDebutCombat/attack_menu.png")
attack_menu = pygame.transform.scale(attack_menu, (1080, 280))
type_normal = pygame.image.load("img/animDebutCombat/type_normal.png")
type_normal = pygame.transform.scale(type_normal, (530, 90))

black = (0, 0, 0)
red = (255, 0, 0)


def modifier_valeur_bloc(fichier, surname, ligne_num, valeur, operation='soustraction'):
    if not 1 <= ligne_num <= 22:
        print(f"[ERREUR] Le numéro de ligne doit être entre 1 et 22. Tu as donné : {ligne_num}")
        return

    with open(fichier, 'r', encoding='utf-8') as f:
        lignes = [line if line.endswith('\n') else line + '\n' for line in f.readlines()]

    for i in range(21, len(lignes)):
        if lignes[i].strip() == surname.strip():
            block_start = i - 21
            ligne_index = block_start + (ligne_num - 1)

            try:
                ancienne_valeur = int(lignes[ligne_index].strip())
            except ValueError:
                print(f"[ERREUR] Ligne {ligne_num} du bloc ne contient pas un entier : '{lignes[ligne_index]}'")
                return

            if operation == 'soustraction':
                nouvelle_valeur = max(0, ancienne_valeur - valeur)
            elif operation == 'addition':
                nouvelle_valeur = ancienne_valeur + valeur
            else:
                print(f"[ERREUR] Opération inconnue : '{operation}'. Utilise 'addition' ou 'soustraction'.")
                return

            lignes[ligne_index] = f"{nouvelle_valeur}\n"
            print(f"[DEBUG] Ligne {ligne_num} modifiée ({operation}) : {ancienne_valeur} → {nouvelle_valeur}")
            break
    else:
        print(f"[ERREUR] Surname '{surname}' non trouvé dans le fichier.")
        return

    with open(fichier, 'w', encoding='utf-8') as f:
        f.writelines(lignes)


def get_pokemons_by_route(file_path, route_name):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(route_name + ":"):
                # Extrait la partie entre les crochets
                match = re.search(r'\[(.*)\]', line)
                if match:
                    pokemons_raw = match.group(1)
                    # Séparer les pokémons individuellement (attention aux virgules internes)
                    pokemon_entries = re.findall(r'(\w+)\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', pokemons_raw)
                    result = []
                    for name, level, hp, hp_max in pokemon_entries:
                        result.append({
                            'name': name,
                            'level': int(level),
                            'hp': int(hp),
                            'hp_max': int(hp_max)
                        })
                    return result
    return []  # Si la route n’est pas trouvée


def recupererDonnees():
    grille = []
    file = openFile('pokemonData')
    for element in range(len(file)):
        if file[element][0].isupper():
            tempListe = [file[element]]
            for stats in range(element + 1, len(file)):
                if not file[stats][0].isupper():
                    tempListe.append(file[stats])
                else:
                    break
            grille.append(tempListe)
    return grille


def agencerDonnees():
    grilleFinale = []
    grille = recupererDonnees()
    for liste in grille:
        dicoTemp = {"name": liste[0], "level": int(liste[1]), "hp_act": int(liste[2]), "hp": int(liste[3]),
                    "attack1": liste[4], "type1": liste[5],"pp1": int(liste[6]), "pp1_r": int(liste[7]), "attack2": liste[8], "type2": liste[9],
                    "pp2": int(liste[10]), "pp2_r": int(liste[11]), "attack3": liste[12], "type3": liste[13], "pp3": int(liste[14]),
                    "pp3_r": int(liste[15]), "attack4": liste[16], "type4": liste[17], "pp4": int(liste[18]), "pp4_r": int(liste[19]),
                    "exp": int(liste[20]), "surname": liste[21]}
        grilleFinale.append(dicoTemp)
    return grilleFinale


def openFile(fichier):
    with open(fichier, "r", encoding='utf-8') as file:
        temp = file.read().splitlines()
    return temp


def obtenirListePokemon(fichier):
    pokemonSprites = {}
    liste = os.listdir(f"img/pokemon/{fichier}")
    for element in liste:
        temp_list = os.listdir(f"img/pokemon/{fichier}/{element}")
        pokemonSprites[element] = temp_list
    return pokemonSprites, liste


premierePartie = obtenirListePokemon("firstHalf")[0]
secondePartie = obtenirListePokemon("secondHalf")[0]
nomsDesPokemons = obtenirListePokemon("firstHalf")[1] + obtenirListePokemon("secondHalf")[1]
liste_route1 = ["Rattata", "Pidgey"]


def moveBack(x):
    x -= 8
    return x


class HealthBar(object):
    def __init__(self, x, y, health, max_health, longueur, epaisseur, screen, rectBlack, exp=0, exp_max=100):
        self.screen = screen
        self.longueur = longueur
        self.epaisseur = epaisseur
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.rectBlack = rectBlack
        self.green = (0, 255, 0)

        # Ajout pour l'EXP
        self.exp = exp
        self.exp_max = exp_max
        self.blue = (0, 120, 255)  # Couleur de l'expérience

    def draw(self):
        # Health bar
        ratio = self.health / self.max_health
        if ratio <= 0.5:
            self.green = (255, 255, 0)
        if ratio <= 0.25:
            self.green = red
        if self.rectBlack:
            pygame.draw.rect(self.screen, black, (self.x - 2, self.y - 2, self.longueur + 4, self.epaisseur + 4))
        pygame.draw.rect(self.screen, black, (self.x, self.y, self.longueur, self.epaisseur))
        pygame.draw.rect(self.screen, self.green, (self.x, self.y, self.longueur * ratio, self.epaisseur))

        # Appel pour dessiner la barre d'expérience
    def draw_exp_bar(self):
        ratio = self.exp / self.exp_max if self.exp_max > 0 else 0
        bar_y = self.y + self.epaisseur + 5  # juste en dessous de la barre de vie
        bar_height = self.epaisseur // 2

        # Fond noir
        # Barre bleue
        pygame.draw.rect(self.screen, self.blue, (self.x, bar_y, self.longueur * ratio, bar_height))


class OwnPokemonData(object):
    def __init__(self):
        self.own_pokemon = agencerDonnees()
        self.menu = pygame.image.load("img/menus/pokemonList.png")
        self.menu = pygame.transform.scale(self.menu, (1080, 720))
        self.first_po = pygame.image.load("img/menus/firstPokemon.png")
        self.first_po = pygame.transform.scale(self.first_po, (400, 300))
        self.first_po_s = pygame.image.load("img/menus/firstPokemonSelected.png")
        self.first_po_s = pygame.transform.scale(self.first_po_s, (400, 300))
        self.other_po = pygame.image.load("img/menus/otherPokemon.png")
        self.other_po = pygame.transform.scale(self.other_po, (700, 125))
        self.other_po_s = pygame.image.load("img/menus/otherPokemonSelected.png")
        self.other_po_s = pygame.transform.scale(self.other_po_s, (760, 135))
        self.cancel = pygame.image.load("img/menus/cancel.png")
        self.cancel = pygame.transform.scale(self.cancel, (300, 200))
        self.cancel_s = pygame.image.load("img/menus/cancelSelected.png")
        self.cancel_s = pygame.transform.scale(self.cancel_s, (263, 155))
        self.emplacements = [10, 125, 240, 355, 470]
        self.menu_po = False
        self.remonter = False
        self.dim = 150
        self.noms = [d["name"] for d in self.own_pokemon if "name" in d]
        self.surnoms = [d["surname"] for d in self.own_pokemon if "surname" in d]
        self.sprites = [self.recupererSprite(noms, "") for noms in self.noms]
        self.nb_pokemons = len(self.noms)
        self.menu_ind = 0
        self.changement = False
        self.ancien_ch = ""

    def changer(self, name):
        self.changement = not self.changement
        self.ancien_ch = name

    def update(self):
        self.own_pokemon = agencerDonnees()
        self.noms = [d["name"] for d in self.own_pokemon if "name" in d]
        self.surnoms = [d["surname"] for d in self.own_pokemon if "surname" in d]
        self.sprites = [self.recupererSprite(noms, "") for noms in self.noms]
        self.nb_pokemons = len(self.noms)

    def update_selected(self):
        liste = []
        for i in range(self.nb_pokemons-1):
            liste.append(self.emplacements[i])
        return liste

    def recupererSprite(self, name, cote):
        if os.path.exists(f"img/pokemon/secondHalf/{name}/{name}{cote}.png"):
            sprite = pygame.image.load(f"img/pokemon/secondHalf/{name}/"
                                       f"{name}{cote}.png")
            sprite = pygame.transform.scale(sprite, (self.dim, self.dim))
        else:
            sprite = pygame.image.load(f"img/pokemon/firstHalf/{name}/"
                                       f"{name}{cote}.png")
            sprite = pygame.transform.scale(sprite, (self.dim, self.dim))
        return sprite

    def changer_menu(self):
        self.menu_po = not self.menu_po
        self.menu_ind = 0

    def defiler_menu(self, aug):
        if aug == 1:
            if self.menu_ind < 6:
                self.menu_ind += 1
                self.remonter = True
            else:
                self.menu_ind = 0
        else:
            if self.menu_ind > 0:
                self.menu_ind -= 1
                self.remonter = False
            else:
                self.menu_ind = 6


class PokemonSauvage:
    def __init__(self, name, sprite, hp, hp_max, level, surnom, exp=0):
        self.pokemon = random.choice(get_pokemons_by_route('routes.txt', 'Route1'))
        self.name = name
        self.exp = exp
        self.enemy = sprite
        self.enemy = pygame.transform.scale(self.enemy, (500, 500))
        self.hp = hp
        self.hp_max = hp_max
        self.level = level
        self.surnom = surnom

        self.waiting_attack = False
        self.subir = False
        self.attack_timer = 0
        self.response_delay = 1600
        self.attack_delay = 2000  # délai en millisecondes (ex: 1000 = 1 seconde)
        self.pending_damage = 0
        self.response_timer = 0
        self.fini = False
        self.fin_combat = False

    def reset(self):
        self.attack_timer = 0
        self.attack_delay = 2000
        self.pending_damage = 0

    def launch_attack(self, damage, dialog_box, attacker_name, attack_name):
        dialog_box.execute([f"{attacker_name} lance {attack_name} !"])
        self.waiting_attack = True
        self.attack_timer = pygame.time.get_ticks()
        self.pending_damage = damage

    def process_damage(self, dialog_box):
        now = pygame.time.get_ticks()
        if now - self.attack_timer >= self.attack_delay:
            self.hp -= self.pending_damage
            self.waiting_attack = False
            self.fini = True
            self.response_timer = pygame.time.get_ticks()  # Démarre le timer de réponse
            self.reset()
            if self.hp > 0:
                dialog_box.execute([f"{self.name} lance charge !"])
            self.response_delay = 1600
            self.attack_delay = 2000

    def new(self, objet):
        now = pygame.time.get_ticks()
        if now - self.response_timer >= self.response_delay:
            self.fini = False
            self.attack_timer = pygame.time.get_ticks()
            if self.hp > 0:
                objet.pokemon_ally.hp -= 10
                modifier_valeur_bloc("pokemonData", objet.pokemon_ally.surnom,  3, 10, "soustraction")

    def delay(self):
        now = pygame.time.get_ticks()
        if now - self.response_timer >= self.response_delay:
            self.fin_combat = True


class Combat:
    def __init__(self, screen):
        self.data = OwnPokemonData()
        self.screen = screen
        self.images = []
        self.index = 0
        animation_list = ['entree', 'outOfBall']
        for animation in animation_list:
            temp_list = []
            num_frames = len(os.listdir(f"img/animDebutCombat/{animation}"))
            for num in range(num_frames):
                if animation == 'entree':
                    image = pygame.image.load(f"img/animDebutCombat/{animation}/00{num + 30}.png")
                else:
                    image = pygame.image.load(f"img/animDebutCombat/{animation}/{num}.png")
                image = pygame.transform.scale(image, (1080, 720))
                temp_list.append(image)
            self.images.append(temp_list)

        self.image = self.images[0][self.index]

        self.sprite_first = self.data.recupererSprite(self.data.noms[0], "_back")
        self.sprite_first = pygame.transform.scale(self.sprite_first, (600, 600))
        self.x_debut = -250
        self.update_time = pygame.time.get_ticks()
        self.run_entry = True
        self.begin_fight = False
        self.finalbegin = False
        self.combat_encours = False
        self.bg_displayed = False  # Pour savoir si on a affiché le fond

        self.pokemon = random.choice(get_pokemons_by_route('routes.txt', 'Route1'))
        self.sauvage = PokemonSauvage(self.pokemon["name"], self.data.recupererSprite(f"{self.pokemon['name']}", ""), self.pokemon["hp"], self.pokemon["hp_max"], self.pokemon["level"], self.pokemon["name"])

        self.x_enemy = 1200
        self.font = pygame.font.Font("dialogue/dialog_font.ttf", 40)
        self.font2 = pygame.font.Font("dialogue/dialog_font.ttf", 31)
        self.font3 = pygame.font.Font("dialogue/dialog_font.ttf", 26)
        self.current_row = 0
        self.current_col = 0
        self.liste_menu = [[530, 520], [800, 520], [530, 605], [800, 605]]
        self.attack_menu = False
        self.emplacements_attaques = [(0, 465), (550, 465), (-5, 560), (550, 560)]
        self.liste_menu_atk = [[530, 520], [1080, 520], [530, 605], [1080, 605]]
        # --- Sous-menu Attaques ---
        # positions "ancrage" utilisées pour dessiner le rectangle de sélection
        # (on soustrait 530 et 50 plus bas pour obtenir le coin sup. gauche du cadre)
        self.liste_menu_atk5 = [
            [530, 520],   # attaque 1 (haut-gauche)
            [1080, 520],  # attaque 2 (haut-droite)
            [530, 605],   # attaque 3 (bas-gauche)
            [1080, 605],  # attaque 4 (bas-droite)
            [805, 690],   # CANCEL (centré sous les 4 attaques)
        ]
        self.current_atk_idx = 0     # sélection courante dans le sous-menu attaques
        self.just_cancelled_attack = False
        self.pokemon_ally = PokemonSauvage(self.data.own_pokemon[0]["name"], self.data.recupererSprite(f"{self.data.own_pokemon[0]['name']}", "_back"), self.data.own_pokemon[0]["hp_act"], self.data.own_pokemon[0]["hp"], self.data.own_pokemon[0]["level"], self.data.own_pokemon[0]["surname"], self.data.own_pokemon[0]["exp"])
        self.timer_fin_combat = 0
        self.fin_combat_en_cours = False

    def move_focus_atk(self, key):
        """
        Déplacements dans le sous-menu attaques (4 slots + Cancel).
        Table d'adjacence = comportement façon jeux Pokémon classiques :
            - Gauche/Droite dans la même rangée basculent entre colonnes.
            - Bas depuis la rangée du haut = rangée du bas correspondante.
            - Bas depuis la rangée du bas = Cancel.
            - Haut depuis Cancel = remonte vers la dernière colonne utilisée
              (on mémorise la dernière colonne via self._atk_last_col).
        """
        # mémorise la dernière colonne "logique" (0=gauche,1=droite) utilisée
        if not hasattr(self, "_atk_last_col"):
            self._atk_last_col = 0

        idx = self.current_atk_idx

        # conversion index -> (row,col) "logiques" pour les 4 attaques
        if idx < 4:
            row = idx // 2
            col = idx % 2
        else:
            row = 2   # Cancel
            col = self._atk_last_col

        if key == "UP":
            if row == 2:            # depuis Cancel -> remonte rangée du bas
                row = 1
                col = self._atk_last_col
            elif row == 1:
                row = 0
            # row == 0 => reste en 0
        elif key == "DOWN":
            if row == 0:
                row = 1
            elif row == 1:
                # descend vers Cancel
                row = 2
            # row == 2 => reste Cancel
        elif key == "LEFT":
            if row < 2:  # dans la grille
                col = 0
            # Cancel : ignore
        elif key == "RIGHT":
            if row < 2:
                col = 1
            # Cancel : ignore

        # reconversion (row,col) -> index
        if row == 2:
            idx = 4  # Cancel
        else:
            idx = row * 2 + col
            self._atk_last_col = col  # mémorise dernière colonne atteinte

        self.current_atk_idx = idx

    def reset_combat(self):
        # Réinitialisation des booléens
        self.run_entry = True
        self.begin_fight = False
        self.finalbegin = False
        self.combat_encours = False
        self.bg_displayed = False

        # Réinitialisation des animations
        self.index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.images[0][self.index]

        # Réinitialisation de la position des sprites
        self.x_debut = -250
        self.x_enemy = 1200

        # Recharge les données du joueur
        self.data = OwnPokemonData()
        self.generate_first()

        # Réinitialisation du menu
        self.attack_menu = False
        self.current_row = 0
        self.current_col = 0
        self.current_atk_idx = 0
        self.pokemon = random.choice(get_pokemons_by_route('routes.txt', 'Route1'))
        self.sauvage = PokemonSauvage(self.pokemon["name"], self.data.recupererSprite(f"{self.pokemon['name']}", ""),
                                      self.pokemon["hp"], self.pokemon["hp_max"], self.pokemon["level"], self.pokemon["name"])
        self.pokemon_ally = PokemonSauvage(self.data.own_pokemon[0]["name"], self.data.recupererSprite(f"{self.data.own_pokemon[0]['name']}", "_back"), self.data.own_pokemon[0]["hp_act"], self.data.own_pokemon[0]["hp"], self.data.own_pokemon[0]["level"], self.data.own_pokemon[0]["surname"], self.data.own_pokemon[0]["exp"])

    def reset_ally(self):
        self.data = OwnPokemonData()
        self.pokemon_ally = PokemonSauvage(self.data.own_pokemon[0]["name"], self.data.recupererSprite(f"{self.data.own_pokemon[0]['name']}", "_back"), self.data.own_pokemon[0]["hp_act"], self.data.own_pokemon[0]["hp"], self.data.own_pokemon[0]["level"], self.data.own_pokemon[0]["surname"], self.data.own_pokemon[0]["exp"])

    def move_focus(self, key, current_row, current_col):
        if key == "UP":
            self.current_row = (current_row - 1) % 2
        elif key == "DOWN":
            self.current_row = (current_row + 1) % 2
        elif key == "LEFT":
            self.current_col = (current_col - 1) % 2
        elif key == "RIGHT":
            self.current_col = (current_col + 1) % 2

    def get_position(self, row, col, liste):
        index = row * 2 + col
        return liste[index]

    def generate_first(self):
        self.sprite_first = self.data.recupererSprite(self.data.noms[0], "_back")
        self.sprite_first = pygame.transform.scale(self.sprite_first, (600, 600))

    def update_animation_entry(self):
        self.data.update()
        self.generate_first()
        if self.run_entry:
            animation_cooldown = 30
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.update_time = pygame.time.get_ticks()
                self.index += 1
                if self.index < len(self.images[0]):
                    self.image = self.images[0][self.index]
            if self.index >= len(self.images[0]):
                self.run_entry = False
                self.begin_fight = True
                self.index = 0  # Reset pour l’animation suivante

    def update_begining(self):
        if self.begin_fight and not self.finalbegin:
            animation_cooldown = 100
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.update_time = pygame.time.get_ticks()
                self.index += 1
                if self.index < len(self.images[1]):
                    self.image = self.images[1][self.index]
            if self.index >= len(self.images[1]):
                self.finalbegin = True

            self.screen.blit(self.image, (-250, 60))

    def update(self):
        self.update_animation_entry()
        if not self.run_entry:
            if not self.bg_displayed:
                self.bg_displayed = True  # S'assurer qu'on n’affiche le fond qu’après l’entrée
            self.screen.blit(bg, (0, 0))  # Affichage du fond permanent après entrée

        if self.run_entry:
            self.screen.blit(self.image, (0, 0))  # Affiche l’animation d’entrée
        elif not self.finalbegin:
            self.update_begining()

    def update_pokemon_entry(self, dialog):
        hp_ally = HealthBar(783, 404, self.pokemon_ally.hp,  self.data.own_pokemon[0]["hp"], 225,
                              18, self.screen, False)
        exp_bar = HealthBar(713, 446, self.pokemon_ally.hp, self.data.own_pokemon[0]["hp"], 288,
                            26, self.screen, False, self.pokemon_ally.exp, (self.pokemon_ally.level**2)*10)
        hp_ennemy = HealthBar(232, 148, self.sauvage.hp,  self.sauvage.hp_max, 225,
                              18, self.screen, False)
        self.screen.blit(self.sprite_first, (self.x_debut, 130))
        self.move_pokemon()
        self.screen.blit(self.sauvage.enemy, (self.x_enemy, -100))
        self.move_enemy()
        self.screen.blit(fight_menu, (0, 500))
        texte1 = self.font.render('Que doit faire ', False, (0, 0, 0))
        texte2 = self.font.render(f'{self.pokemon_ally.surnom} ?', False, (0, 0, 0))
        hp1 = self.font2.render(f'{self.pokemon_ally.hp}', False, (0, 0, 0))
        hp2 = self.font2.render(f'{self.pokemon_ally.hp_max}', False, (0, 0, 0))
        lvl_ally = self.font2.render(f'{self.pokemon_ally.level}', False, (0, 0, 0))
        lvl_ennemy = self.font2.render(f'{self.sauvage.level}', False, (0, 0, 0))
        enemy_name = self.font.render(f'{self.sauvage.name}', False, (0, 0, 0))
        ally_name = self.font.render(f'{self.pokemon_ally.surnom}', False, (0, 0, 0))
        if len(list(str(self.pokemon_ally.hp))) == 3:
            self.screen.blit(hp1, (840, 430))
        else:
            self.screen.blit(hp1, (865, 430))
        self.screen.blit(lvl_ennemy, (400, 99))
        self.screen.blit(enemy_name, (100, 85))
        self.screen.blit(ally_name, (640, 345))
        self.screen.blit(hp2, (935, 430))
        self.screen.blit(lvl_ally, (950, 355))
        self.screen.blit(texte1, (50, 550))
        self.screen.blit(texte2, (50, 600))
        pygame.draw.rect(self.screen, (240, 195, 0), (self.get_position(self.current_row, self.current_col, self.liste_menu)[0],
                                                  self.get_position(self.current_row, self.current_col, self.liste_menu)[1], 280, 90), width=5)
        hp_ally.draw()
        hp_ennemy.draw()
        exp_bar.draw_exp_bar()
        if self.attack_menu:
            self.screen.blit(attack_menu, (0, 440))
            for i in range(4):
                if self.data.own_pokemon[0][f"attack{i+1}"] != "none":
                    if self.data.own_pokemon[0][f"type{i+1}"] == "normal":
                        self.screen.blit(type_normal, self.emplacements_attaques[i])
                        pp = self.font2.render(f'{self.data.own_pokemon[0][f"pp{i+1}"]}   {self.data.own_pokemon[0][f"pp{i+1}_r"]}',
                                              False, (0, 0, 0))
                        self.screen.blit(pp, (self.emplacements_attaques[i][0]+323, self.emplacements_attaques[i][1]+40))
                        name = self.font3.render(f'{self.data.own_pokemon[0][f"attack{i+1}"]}',
                                              False, (0, 0, 0))
                        self.screen.blit(name, (self.emplacements_attaques[i][0] + 60, self.emplacements_attaques[i][1]+15))
            # --- rectangle de sélection attaque / cancel ---
            sel_x_base, sel_y_base = self.liste_menu_atk5[self.current_atk_idx]
            sel_rect = pygame.Rect(sel_x_base - 530, sel_y_base - 50, 530, 85)
            if self.current_atk_idx != 4 and not self.sauvage.waiting_attack:
                pygame.draw.rect(self.screen, (240, 195, 0), sel_rect, width=5)
            elif not self.sauvage.waiting_attack:
                pygame.draw.rect(self.screen, (240, 195, 0), (sel_x_base - 783, sel_y_base - 35, 1034, 65), width=5)

            if self.sauvage.waiting_attack:
                self.sauvage.process_damage(dialog)

            if (self.pokemon_ally.hp <= 0 or self.sauvage.hp <= 0) and not self.fin_combat_en_cours:
                if self.sauvage.hp <= 0:
                    dialog.execute([f"Fin du combat, {self.sauvage.name} est K.O. !"])
                    if self.pokemon_ally.exp + 10 >= (self.pokemon_ally.level ** 2) * 10:
                        modifier_valeur_bloc("pokemonData", self.pokemon_ally.surnom, 2, 1, "addition")
                        modifier_valeur_bloc("pokemonData", self.pokemon_ally.surnom, 21, self.pokemon_ally.exp, "soustraction")
                    else:
                        modifier_valeur_bloc("pokemonData", self.pokemon_ally.surnom, 21, 10, "addition")
                else:
                    dialog.execute([f"{self.pokemon_ally.name} est K.O. !"])
                self.timer_fin_combat = pygame.time.get_ticks()
                self.fin_combat_en_cours = True

            if self.fin_combat_en_cours:
                if pygame.time.get_ticks() - self.timer_fin_combat >= 2500:  # 2 secondes
                    self.reset_combat()
                    self.fin_combat_en_cours = False

            if self.sauvage.fini:
                self.sauvage.new(self)

        if self.just_cancelled_attack:
            self.just_cancelled_attack = False

    def move_pokemon(self):
        if self.x_debut <= 0:
            self.x_debut += 8

    def move_enemy(self):
        if self.x_enemy >= 580:
            self.x_enemy -= 8

