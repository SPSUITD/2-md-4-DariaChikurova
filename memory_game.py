import arcade
import random
import os
import time
import subprocess
import sys
from collections import deque


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_ROWS = 4
GRID_COLS = 3
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SPACING = 20
CARD_SCALE = 0.1



class Button:
    def __init__(self, text, x, y, width, height, color):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.is_hovered = False
        
    def contains_point(self, x, y):
        return (self.x - self.width/2 <= x <= self.x + self.width/2 and
                self.y - self.height/2 <= y <= self.y + self.height/2)
    
    def update_hover(self, mouse_x, mouse_y):
        self.is_hovered = self.contains_point(mouse_x, mouse_y)
    
    def draw(self):
        
        if self.is_hovered:
            draw_color = tuple(min(255, c + 50) for c in self.color[:3])
            border_color = arcade.color.YELLOW
        else:
            draw_color = self.color[:3]
            border_color = arcade.color.WHITE
        
        left = self.x - self.width/2
        right = self.x + self.width/2
        top = self.y + self.height/2
        bottom = self.y - self.height/2
        
        arcade.draw_triangle_filled(
            left, bottom,
            right, bottom,
            left, top,
            draw_color
        )
        arcade.draw_triangle_filled(
            right, bottom,
            right, top,
            left, top,
            draw_color
        )
        
        arcade.draw_line(left, top, right, top, border_color, 3)
        arcade.draw_line(left, bottom, right, bottom, border_color, 3)
        arcade.draw_line(left, bottom, left, top, border_color, 3)
        arcade.draw_line(right, bottom, right, top, border_color, 3)
        
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center",
            anchor_y="center"
        )


# СПРАЙТЫ И КОЛЛИЗИИ 
class Card(arcade.Sprite):
    def __init__(self, image_type, back_image, scale=1):
        self.front_image = f"card{image_type}.png"
        super().__init__(self.front_image, scale, hit_box_algorithm="None")
        
        self.back_image = back_image
        self.image_type = image_type
        self.is_face_up = False
        self.locked = False

    def turn_face_down(self):
        self.texture = arcade.load_texture(self.back_image)
        self.is_face_up = False

    def turn_face_up(self):
        self.texture = arcade.load_texture(self.front_image)
        self.is_face_up = True

    def on_click(self):
        
        if not self.locked and not self.is_face_up:
            self.turn_face_up()
            return True
        return False



class GameCompleteView(arcade.View):
    def __init__(self, attempts):
        super().__init__()
        self.attempts = attempts
        
        
        self.buttons = []
        button_width = 200
        button_height = 50
        
        self.buttons.append(Button(
            "Играть заново", 
            SCREEN_WIDTH // 2 - 120, 
            SCREEN_HEIGHT // 2 - 50, 
            button_width, 
            button_height, 
            (50, 150, 50, 255)
        ))
        
        self.buttons.append(Button(
            "Главное меню", 
            SCREEN_WIDTH // 2 + 120, 
            SCREEN_HEIGHT // 2 - 50, 
            button_width, 
            button_height, 
            (150, 50, 150, 255)
        ))

    def on_show_view(self):
        arcade.set_background_color((20, 50, 20))

    def on_draw(self):
        self.clear()
        
        
        arcade.draw_text(
            "ПОЗДРАВЛЯЕМ!", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2 + 100, 
            arcade.color.GOLD, 
            font_size=48, 
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Вы успешно собрали все пары!", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2 + 50, 
            arcade.color.WHITE, 
            font_size=24, 
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"Количество попыток: {self.attempts}", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2 + 20, 
            arcade.color.LIGHT_BLUE, 
            font_size=20, 
            anchor_x="center"
        )
        
        
        if self.attempts <= 8:
            arcade.draw_text(
                "🏆 ПРЕВОСХОДНО! 🏆", 
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2 - 10, 
                arcade.color.YELLOW, 
                font_size=18, 
                anchor_x="center"
            )
        elif self.attempts <= 12:
            arcade.draw_text(
                "⭐ ОТЛИЧНО! ⭐", 
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2 - 10, 
                arcade.color.LIGHT_GREEN, 
                font_size=18, 
                anchor_x="center"
            )
        elif self.attempts <= 16:
            arcade.draw_text(
                "✓ Хорошо!", 
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2 - 10, 
                arcade.color.LIGHT_BLUE, 
                font_size=18, 
                anchor_x="center"
            )
        
        for button in self.buttons:
            button.draw()
        
        arcade.draw_text(
            "Нажмите ESC для возврата в главное меню или R для новой игры", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2 - 120, 
            arcade.color.LIGHT_GRAY, 
            font_size=14, 
            anchor_x="center"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        
        for button in self.buttons:
            button.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        
        for btn in self.buttons:
            if btn.contains_point(x, y):
                if btn.text == "Играть заново":
                    game_view = MemoryGameView()
                    self.window.show_view(game_view)
                elif btn.text == "Главное меню":
                    self.return_to_menu()
                break

    def on_key_press(self, key, modifiers):
        # Управление клавиатурой
        if key == arcade.key.ESCAPE:
            self.return_to_menu()
        elif key == arcade.key.R:
            game_view = MemoryGameView()
            self.window.show_view(game_view)

    def return_to_menu(self):
        self.window.close()
        try:
            subprocess.call([sys.executable, "menu.py"])
        except Exception as e:
            print(f"Ошибка запуска меню: {e}")
            sys.exit()


# МЕНЮ ПАУЗЫ 
class PauseMenuView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        
        
        self.buttons = []
        button_width = 250
        button_height = 60
        button_spacing = 80
        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 + 50
        
        self.buttons.append(Button(
            "Продолжить игру", 
            center_x, 
            start_y, 
            button_width, 
            button_height, 
            (50, 150, 50, 255)
        ))
        
        self.buttons.append(Button(
            "Новая игра", 
            center_x, 
            start_y - button_spacing, 
            button_width, 
            button_height, 
            (200, 150, 50, 255)
        ))
        
        self.buttons.append(Button(
            "Главное меню", 
            center_x, 
            start_y - button_spacing * 2, 
            button_width, 
            button_height, 
            (150, 50, 150, 255)
        ))

    def on_show_view(self):
        pass

    def on_draw(self):
        
        arcade.draw_triangle_filled(
            0, 0,
            SCREEN_WIDTH, 0,
            0, SCREEN_HEIGHT,
            (0, 0, 0, 128)
        )
        arcade.draw_triangle_filled(
            SCREEN_WIDTH, 0,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            0, SCREEN_HEIGHT,
            (0, 0, 0, 128)
        )
        
        arcade.draw_text(
            "ПАУЗА", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2 + 150, 
            arcade.color.WHITE, 
            font_size=48, 
            anchor_x="center"
        )
        
        for button in self.buttons:
            button.draw()
        
        arcade.draw_text(
            "Нажмите ESC для возврата в игру", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2 - 200, 
            arcade.color.LIGHT_GRAY, 
            font_size=16, 
            anchor_x="center"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        
        for button in self.buttons:
            button.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        # Обработка коллизий с кнопками
        for btn in self.buttons:
            if btn.contains_point(x, y):
                if btn.text == "Продолжить игру":
                    self.window.show_view(self.game_view)
                elif btn.text == "Новая игра":
                    
                    if hasattr(self.game_view, 'music_player') and self.game_view.music_playing:
                        self.game_view.stop_music()
                    
                    new_game_view = MemoryGameView()
                    self.window.show_view(new_game_view)
                elif btn.text == "Главное меню":
                   
                    if hasattr(self.game_view, 'music_player') and self.game_view.music_playing:
                        self.game_view.stop_music()
                    
                    self.return_to_menu()
                break

    def on_key_press(self, key, modifiers):
        # Управление клавиатурой
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

    def return_to_menu(self):
        self.window.close()
        try:
            subprocess.call([sys.executable, "menu.py"])
        except Exception as e:
            print(f"Ошибка запуска меню: {e}")
            sys.exit()
    

# ОСНОВНАЯ ИГРА
class MemoryGameView(arcade.View):
    def __init__(self):
        super().__init__()
        
        
        self.back_image = "back.png"
        self.card_list = None
        
        
        self.selected_cards = deque(maxlen=2)
        self.game_state = "playing"
        self.attempts = 0
        self.flip_timer = 0
        
       
        self.background_music = None
        self.music_player = None
        self.music_playing = False
        
        try:
            self.background_music = arcade.load_sound("fonovaya-muzyika-dlya-detskoy-igrovoy-komnatyi-979.wav")
        except:
            print("Не удалось загрузить fonovaya-muzyika-dlya-detskoy-igrovoy-komnatyi-979.wav")
        
        self.setup()

    def setup(self):
        
        self.attempts = 0
        self.game_state = "playing"
        self.selected_cards.clear()
        self.flip_timer = 0
        
        # Генерация карт и их расположение
        card_types = list(range(1, 7)) * 2
        random.shuffle(card_types)
        
        
        self.card_list = arcade.SpriteList()
        
        
        start_x = (SCREEN_WIDTH - (GRID_COLS * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)) / 2
        start_y = (SCREEN_HEIGHT - (GRID_ROWS * (CARD_HEIGHT + CARD_SPACING) - CARD_SPACING)) / 2
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                card = Card(
                    image_type=card_types.pop(),
                    back_image=self.back_image,
                    scale=CARD_SCALE
                )
                
                card.center_x = start_x + col * (CARD_WIDTH + CARD_SPACING) + CARD_WIDTH/2
                card.center_y = start_y + row * (CARD_HEIGHT + CARD_SPACING) + CARD_HEIGHT/2
                
                card.turn_face_down()
                card.locked = False
                
                self.card_list.append(card)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)
        
        
        if self.background_music and not self.music_playing:
            self.start_music()

    def start_music(self):
        
        if self.background_music:
            self.music_player = arcade.play_sound(self.background_music, volume=0.3)
            self.music_playing = True

    def stop_music(self):
        
        if self.music_player:
            self.music_player.pause()
            self.music_player = None
            self.music_playing = False

    def on_update(self, delta_time):
       
        if self.music_playing and self.music_player:
            if not self.music_player.playing:
                self.start_music()
        
        # таймер переворота карточек
        if self.game_state == "waiting" and time.time() - self.flip_timer > 1.0:
            for card in self.selected_cards:
                card.turn_face_down()
            self.selected_cards.clear()
            self.game_state = "playing"

    def on_draw(self):
        self.clear()
        
        
        self.card_list.draw()
        
        
        arcade.draw_text(f"Попыток: {self.attempts}", 10, SCREEN_HEIGHT - 30, 
                        arcade.color.WHITE, 20)
        
        arcade.draw_text("Кликайте по карточкам для переворота. ESC - меню", 
                         SCREEN_WIDTH // 2, 20, arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        # обработка кликов по карточкам
        if self.game_state == "playing":
            cards_clicked = arcade.get_sprites_at_point((x, y), self.card_list)
            if cards_clicked:
                card = cards_clicked[0]
                if card.on_click():
                    self.selected_cards.append(card)
                    self.check_card_pair()

    def check_card_pair(self):
        # проверка совпадения карточек
        if len(self.selected_cards) == 2:
            self.attempts += 1
            card1, card2 = self.selected_cards
            
            if card1.image_type == card2.image_type:
                card1.locked = True
                card2.locked = True
                self.selected_cards.clear()
                
                # Проверка условия победы
                if all(card.locked for card in self.card_list):
                    
                    self.stop_music()
                    complete_view = GameCompleteView(self.attempts)
                    self.window.show_view(complete_view)
            else:
                
                self.game_state = "waiting"
                self.flip_timer = time.time()

    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.ESCAPE:
            pause_menu = PauseMenuView(self)
            self.window.show_view(pause_menu)



def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Memory Game")
    game_view = MemoryGameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
