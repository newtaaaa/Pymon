import pygame
from game import Game
from pokemon import Combat


pygame.init()

clock = pygame.time.Clock()
running = True
moving_right = False
moving_left = False
moving_up = False
moving_down = False

game = Game()
combat = Combat(game.screen)


def inverser_pokemons(fichier, surname1, surname2):
    # Si les deux surnames sont identiques, on ne fait rien
    if surname1 == surname2:
        print("Les deux Pokémon ont le même surname. Aucun échange nécessaire.")
        return

    with open(fichier, 'r', encoding='utf-8') as f:
        lignes = [line if line.endswith('\n') else line + '\n' for line in f.readlines()]

    indices = {}

    # Identifier les indices de début des blocs par surname
    for i in range(0, len(lignes), 22):
        if i + 21 < len(lignes):
            surname = lignes[i + 21].strip()
            if surname == surname1:
                indices[surname1] = i
            elif surname == surname2:
                indices[surname2] = i

    if surname1 not in indices or surname2 not in indices:
        print("Un des deux surnames n’a pas été trouvé.")
        return

    idx1 = indices[surname1]
    idx2 = indices[surname2]

    bloc1 = lignes[idx1:idx1 + 22]
    bloc2 = lignes[idx2:idx2 + 22]

    # Supprimer les deux blocs dans l’ordre inverse
    for i in sorted([idx1, idx2], reverse=True):
        del lignes[i:i + 22]

    # Réinsertion au plus petit des deux indices
    min_idx = min(idx1, idx2)
    if idx1 < idx2:
        lignes[min_idx:min_idx] = bloc2
        lignes[min_idx + 22:min_idx + 22] = bloc1
    else:
        lignes[min_idx:min_idx] = bloc1
        lignes[min_idx + 22:min_idx + 22] = bloc2

    with open(fichier, 'w', encoding='utf-8') as f:
        f.writelines(lignes)

    print(f"Les Pokémon avec surnames {surname1} et {surname2} ont été échangés.")


def ecrireCoordonnees(fichier, city, x, y):
    with open(fichier, 'w') as f:
        f.write(f"{city}\n{x}\n{y}\n")


while running:
    if game.menu_on or game.map_manager.combat.combat_encours:
        moving_right = False
        moving_left = False
        moving_up = False
        moving_down = False

    game.actualiser(moving_left, moving_right, moving_down, moving_up)
    game.dialogue_box.render(game.screen)
    pygame.display.flip()
    menu_po_lock = False  # Ajouté pour éviter la sélection immédiate

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_z:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.map_manager.check_npc_collisions(game.dialogue_box)
            if event.key == pygame.K_q:
                game.player.step_count += 1
                moving_left = True
            if event.key == pygame.K_d:
                game.player.step_count += 1
                moving_right = True
            if event.key == pygame.K_z:
                game.player.step_count += 1
                moving_up = True
            if event.key == pygame.K_s:
                game.player.step_count += 1
                moving_down = True
            if event.key == pygame.K_f:
                game.afficher_menu()
            if event.key == pygame.K_RETURN:

                if game.menu_on and game.menu_ind == 1 and not game.pokemons.menu_po and not game.map_manager.combat.combat_encours:
                    game.pokemons.changer_menu()
                    menu_po_lock = True

                if game.pokemons.menu_po and 0 <= game.pokemons.menu_ind <= 5:
                    if menu_po_lock:
                        menu_po_lock = False
                    else:
                        if not game.pokemons.changement:
                            game.pokemons.ancien_ch = game.pokemons.surnoms[game.pokemons.menu_ind]
                            game.dialogue_box.execute([f"Sélection de {game.pokemons.ancien_ch}"])
                            game.dialogue_box.set_speed(5)
                            game.pokemons.changement = True
                        else:
                            nouveau = game.pokemons.surnoms[game.pokemons.menu_ind]
                            inverser_pokemons("pokemonData", game.pokemons.ancien_ch, nouveau)
                            game.dialogue_box.execute([f"Échange entre {game.pokemons.ancien_ch} et {nouveau}"])
                            game.pokemons.ancien_ch = ""
                            game.pokemons.changement = False
                            game.map_manager.combat.reset_ally()

                if game.menu_on and game.menu_ind == 4:
                    ecrireCoordonnees("position.txt", game.map_manager.current_map,game.player.position[0], game.player.position[1])
                    game.dialogue_box.execute(["Sauvegarde réussie !"])

                if game.menu_on and game.menu_ind == 6:
                    running = False

                if game.map_manager.combat.combat_encours:
                    if game.map_manager.combat.current_row == 1 and game.map_manager.combat.current_col == 1 and not game.map_manager.combat.attack_menu:
                        game.map_manager.combat.reset_combat()
                        game.dialog_started = False

                    if game.map_manager.combat.current_row == 1 and game.map_manager.combat.current_col == 0 and not game.map_manager.combat.attack_menu:
                        if not game.pokemons.menu_po:
                            game.pokemons.changer_menu()
                            menu_po_lock = True

                    # Dans le bloc de touche RETURN

                    if game.map_manager.combat.attack_menu:
                        if game.map_manager.combat.current_atk_idx == 4:
                            game.map_manager.combat.attack_menu = False
                            game.map_manager.combat.current_row, game.map_manager.combat.current_col = 0, 0
                            game.map_manager.combat.current_atk_idx = 0
                            game.map_manager.combat.just_cancelled_attack = True
                        elif game.map_manager.combat.current_atk_idx == 0 and not game.map_manager.combat.sauvage.waiting_attack:
                            game.dialogue_box.temps_ecran = 30
                            game.map_manager.combat.sauvage.launch_attack(damage=10, dialog_box=game.dialogue_box, attacker_name=game.map_manager.combat.data.surnoms[0], attack_name=game.map_manager.combat.data.own_pokemon[0][f"attack{game.map_manager.combat.current_atk_idx+1}"])
                    if (game.map_manager.combat.current_row == 0 and
                            game.map_manager.combat.current_col == 0 and
                            not game.pokemons.menu_po and
                            game.map_manager.combat.finalbegin and
                            not game.map_manager.combat.attack_menu and
                            not game.map_manager.combat.just_cancelled_attack):
                        game.map_manager.combat.attack_menu = True

                if game.pokemons.menu_po and game.pokemons.menu_ind == 6:
                    game.pokemons.changer_menu()
                    game.menu_ind = 1
                    game.pokemons.changement = False
                    if game.map_manager.combat.combat_encours:
                        # S'assurer que les autres menus ne sont pas actifs
                        game.map_manager.combat.current_row = 0
                        game.map_manager.combat.current_col = 0
                        game.map_manager.combat.attack_menu = False

            if event.key == pygame.K_DOWN:
                if game.menu_on and not game.pokemons.menu_po and not game.map_manager.combat.combat_encours:
                    game.defiler_menu(1)
                if game.pokemons.menu_po:
                    game.pokemons.defiler_menu(1)
                if game.map_manager.combat.combat_encours:
                    game.map_manager.combat.move_focus("DOWN", game.map_manager.combat.current_row, game.map_manager.combat.current_col)
                if game.map_manager.combat.attack_menu:
                    game.map_manager.combat.move_focus_atk("DOWN")
            if event.key == pygame.K_UP:
                if game.menu_on and not game.pokemons.menu_po and not game.map_manager.combat.combat_encours:
                    game.defiler_menu(-1)
                if game.pokemons.menu_po:
                    game.pokemons.defiler_menu(-1)
                if game.map_manager.combat.combat_encours:
                    game.map_manager.combat.move_focus("UP", game.map_manager.combat.current_row, game.map_manager.combat.current_col)
                if game.map_manager.combat.attack_menu:
                    game.map_manager.combat.move_focus_atk("UP")
            if event.key == pygame.K_LEFT:
                if game.map_manager.combat.combat_encours:
                    game.map_manager.combat.move_focus("LEFT", game.map_manager.combat.current_row, game.map_manager.combat.current_col)
                if game.map_manager.combat.attack_menu:
                    game.map_manager.combat.move_focus_atk("LEFT")
            if event.key == pygame.K_RIGHT:
                if game.map_manager.combat.attack_menu:
                    game.map_manager.combat.move_focus_atk("RIGHT")
                if game.map_manager.combat.combat_encours:
                    game.map_manager.combat.move_focus("RIGHT", game.map_manager.combat.current_row, game.map_manager.combat.current_col)

    clock.tick(60)
pygame.quit()
