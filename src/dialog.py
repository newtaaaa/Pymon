import pygame


class DialogBox:

    def __init__(self):
        self.box = pygame.image.load("dialogue/dialog_box.png")
        self.box = pygame.transform.scale(self.box, (1000, 200))
        self.texts = []
        self.text_index = 0
        self.font = pygame.font.Font("dialogue/dialog_font.ttf", 30)
        self.x_pos = 70
        self.y_pos = 490
        self.letter_index = 0
        self.reading = False
        self.bloquage = False
        self.dialog_started = False
        self.temps_ecran = 70
        self.last_letter_update = pygame.time.get_ticks()
        self.delay_per_letter = 40  # en millisecondes (plus bas = plus rapide)

    def execute(self, dialog=[]):
        if self.reading:
            self.next_text()
        else:
            self.reading = True  # <--- correction ici
            self.text_index = 0
            self.letter_index = 0  # Pour recommencer à 0
            self.texts = dialog

    def render(self, screen):
        if not self.reading:
            return

        if self.text_index >= len(self.texts):
            self.reading = False
            self.text_index = 0
            self.letter_index = 0
            return

        first_text = self.texts[self.text_index]
        second_text = self.texts[self.text_index + 1] if self.text_index + 1 < len(self.texts) else ""

        # Progression dans les lettres
        # Progression dans les lettres contrôlée par le temps
        current_time = pygame.time.get_ticks()
        if current_time - self.last_letter_update > self.delay_per_letter:
            self.letter_index += 1
            self.last_letter_update = current_time

        total_length = len(first_text) + len(second_text)
        if self.letter_index >= total_length + self.temps_ecran:  # +30 pour laisser un peu de temps de lecture
            self.next_text()
            return

        # Affiche la boîte
        screen.blit(self.box, (self.x_pos, self.y_pos))

        # Affichage du premier texte
        if self.letter_index <= len(first_text):
            text1 = self.font.render(first_text[:self.letter_index], False, (0, 0, 0))
            screen.blit(text1, (self.x_pos + 78, self.y_pos + 60))
        else:
            text1 = self.font.render(first_text, False, (0, 0, 0))
            screen.blit(text1, (self.x_pos + 78, self.y_pos + 60))

            # Affichage du second texte
            second_index = self.letter_index - len(first_text)
            second_index = min(second_index, len(second_text))
            text2 = self.font.render(second_text[:second_index], False, (0, 0, 0))
            screen.blit(text2, (self.x_pos + 78, self.y_pos + 90))

    def set_speed(self, ms_per_letter):
        self.delay_per_letter = ms_per_letter

    def next_text(self):
        self.text_index += 2
        self.letter_index = 0
        if self.text_index >= len(self.texts):
            self.reading = False
