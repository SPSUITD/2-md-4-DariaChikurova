import arcade
import math
import os
import time
import subprocess
import sys
from PIL import Image


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Frog Adventures 2"

PLAYER_SCALING = 0.20
PLAYER_SPEED = 5
PLAYER_JUMP = 15
PLAYER_DOUBLE_JUMP = 8
GRAVITY = 0.5

TILE_SCALING = 0.5
COIN_SCALING = 0.45

INTERACT_DISTANCE = 150
GRID_SPACING = 64

BREATHING_ANIMATION_SPEED = 0.08

ENEMY_SCALING = 0.3
ENEMY_SPEED = 2.5
ENEMY_BOUNCE_FORCE = 8



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


# МЕНЮ ПАУЗЫ
class PauseMenuView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        
        
        self.buttons = []
        button_width = 250
        button_height = 60
        button_spacing = 80
        center_x = WINDOW_WIDTH // 2
        start_y = WINDOW_HEIGHT // 2 + 50
        
        self.buttons.append(Button(
            "Продолжить игру", 
            center_x, 
            start_y, 
            button_width, 
            button_height, 
            (50, 150, 50, 255)
        ))
        
        self.buttons.append(Button(
            "Перезапустить", 
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
            WINDOW_WIDTH, 0,
            0, WINDOW_HEIGHT,
            (0, 0, 0, 128)
        )
        arcade.draw_triangle_filled(
            WINDOW_WIDTH, 0,
            WINDOW_WIDTH, WINDOW_HEIGHT,
            0, WINDOW_HEIGHT,
            (0, 0, 0, 128)
        )
        
        arcade.draw_text(
            "ПАУЗА", 
            WINDOW_WIDTH // 2, 
            WINDOW_HEIGHT // 2 + 150, 
            arcade.color.WHITE, 
            font_size=48, 
            anchor_x="center"
        )
        
        for button in self.buttons:
            button.draw()
        
        arcade.draw_text(
            "Нажмите ESC для возврата в игру", 
            WINDOW_WIDTH // 2, 
            WINDOW_HEIGHT // 2 - 200, 
            arcade.color.LIGHT_GRAY, 
            font_size=16, 
            anchor_x="center"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        
        for button in self.buttons:
            button.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        
        for btn in self.buttons:
            if btn.contains_point(x, y):
                if btn.text == "Продолжить игру":
                    self.window.show_view(self.game_view)
                elif btn.text == "Перезапустить":
                    
                    if hasattr(self.game_view, 'music_player') and self.game_view.music_player:
                        self.game_view.music_player.pause()
                        self.game_view.music_player = None
                
                    new_game_view = GameView()
                    self.window.show_view(new_game_view)
                elif btn.text == "Главное меню":
                    self.return_to_menu()
                break

    def on_key_press(self, key, modifiers):
       
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

    def return_to_menu(self):
        
        if hasattr(self.game_view, 'music_player') and self.game_view.music_player:
            self.game_view.music_player.pause()
            self.game_view.music_player = None
        
        self.window.close()
        try:
            subprocess.call([sys.executable, "menu.py"])
        except Exception as e:
            print(f"Ошибка запуска меню: {e}")
            sys.exit()


#  ЭКРАН ЗАВЕРШЕНИЯ ИГРЫ 
class GameCompleteView(arcade.View):
    def __init__(self, total_time, game_view=None):
        super().__init__()
        self.total_time = total_time
        self.game_view = game_view
        self.music_player = None
        
        
        self.buttons = []
        button_width = 200
        button_height = 50
        
        self.buttons.append(Button(
            "Играть заново", 
            WINDOW_WIDTH // 2 - 120, 
            250, 
            button_width, 
            button_height, 
            (50, 150, 50, 255)
        ))
        
        self.buttons.append(Button(
            "Главное меню", 
            WINDOW_WIDTH // 2 + 120, 
            250, 
            button_width, 
            button_height, 
            (150, 50, 150, 255)
        ))

    def on_show_view(self):
        arcade.set_background_color((20, 20, 60))

    def on_draw(self):
        self.clear()
        
        
        arcade.draw_text(
            "ПОЗДРАВЛЯЕМ!", 
            WINDOW_WIDTH // 2, 
            450, 
            arcade.color.GOLD, 
            font_size=48, 
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Вы успешно прошли все уровни!", 
            WINDOW_WIDTH // 2, 
            400, 
            arcade.color.WHITE, 
            font_size=24, 
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"Общее время прохождения: {self.total_time:.1f} секунд", 
            WINDOW_WIDTH // 2, 
            350, 
            arcade.color.LIGHT_BLUE, 
            font_size=20, 
            anchor_x="center"
        )
        
        # Система оценки результата
        if self.total_time < 60:
            arcade.draw_text(
                "🏆 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! 🏆", 
                WINDOW_WIDTH // 2, 
                320, 
                arcade.color.YELLOW, 
                font_size=18, 
                anchor_x="center"
            )
        elif self.total_time < 120:
            arcade.draw_text(
                "⭐ ХОРОШИЙ РЕЗУЛЬТАТ! ⭐", 
                WINDOW_WIDTH // 2, 
                320, 
                arcade.color.LIGHT_GREEN, 
                font_size=18, 
                anchor_x="center"
            )
        
        for button in self.buttons:
            button.draw()
        
        arcade.draw_text(
            "Нажмите ESC для возврата в главное меню или R для перезапуска", 
            WINDOW_WIDTH // 2, 
            150, 
            arcade.color.LIGHT_GRAY, 
            font_size=16, 
            anchor_x="center"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        
        for button in self.buttons:
            button.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        
        for btn in self.buttons:
            if btn.contains_point(x, y):
                if btn.text == "Играть заново":
                    
                    if self.game_view and hasattr(self.game_view, 'music_player') and self.game_view.music_player:
                        self.game_view.music_player.pause()
                        self.game_view.music_player = None
                
                    game_view = GameView()
                    self.window.show_view(game_view)
                elif btn.text == "Главное меню":
                    self.return_to_menu()
                break

    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.ESCAPE:
            self.return_to_menu()
        elif key == arcade.key.R:
            
            if self.game_view and hasattr(self.game_view, 'music_player') and self.game_view.music_player:
                self.game_view.music_player.pause()
                self.game_view.music_player = None
            
            game_view = GameView()
            self.window.show_view(game_view)

    def return_to_menu(self):
        
        if self.game_view and hasattr(self.game_view, 'music_player') and self.game_view.music_player:
            self.game_view.music_player.pause()
            self.game_view.music_player = None
        
        if hasattr(self, 'music_player') and self.music_player:
            self.music_player.pause()
            self.music_player = None
        
        self.window.close()
        try:
            subprocess.call([sys.executable, "menu.py"])
        except Exception as e:
            print(f"Ошибка запуска меню: {e}")
            sys.exit()


# СПРАЙТЫ И ИИ 
class Enemy(arcade.Sprite):
    def __init__(self, image_path, scale, patrol_start_x, patrol_end_x, center_y):
        super().__init__(image_path, scale)
        
        self.patrol_start_x = patrol_start_x
        self.patrol_end_x = patrol_end_x
        self.center_y = center_y
        self.center_x = patrol_start_x
        self.direction = 1
        self.speed = ENEMY_SPEED
        
    def update(self, delta_time=None):
        
        self.center_x += self.speed * self.direction
        
        if self.center_x <= self.patrol_start_x:
            self.center_x = self.patrol_start_x
            self.direction = 1
        elif self.center_x >= self.patrol_end_x:
            self.center_x = self.patrol_end_x
            self.direction = -1


# ОСНОВНАЯ ИГРА 
class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        
        self.player_list = self.wall_list = self.coin_list = None
        self.portal_list = self.lava_list = None
        self.background_list = self.gui_sprite_list = None
        self.enemy_list = None

        self.player_sprite = self.bone_icon_sprite = None
        self.camera = self.gui_camera = None

        
        self.level = 1
        self.coins_required = 0
        self.coin_count = 0
        self.portal_active = False

        
        self.dx = self.dy = 0
        self.on_ground = False
        self.double_jumped = False

        
        self.show_hitboxes = False
        self.show_coordinates = False
        self.show_interact_prompt = False
        self.current_interact_obj = None
        self.message = ""
        self.message_time = 0

        self.start_time = time.time()

        
        self.sound_jump = None
        self.sound_coin = None
        self.sound_portal = None
        self.music_main = None
        self.music_minigame = None
        self.portal_sound_playing = False
        self.music_player = None
        
        try:
            self.sound_jump = arcade.load_sound("jump3.wav")
        except:
            print("Не удалось загрузить jump3.wav")
        
        try:
            self.sound_coin = arcade.load_sound("bonus.wav")
        except:
            print("Не удалось загрузить bonus.wav")
        
        try:
            self.sound_portal = arcade.load_sound("lose.wav")
        except:
            print("Не удалось загрузить lose.wav")
        
        try:
            self.music_main = arcade.load_sound("music-1.wav")
        except:
            print("Не удалось загрузить music-1.wav")
        
        try:
            self.music_minigame = arcade.load_sound("b19fd19cd041148.wav")
        except:
            print("Не удалось загрузить b19fd19cd041148.wav")

        # Анимации 
        self.frog_textures_right = []
        self.frog_textures_left = []
        
        for i in range(1, 10):
            try:
                right_tex = arcade.load_texture(f"frogg/frog{i}.png")
                self.frog_textures_right.append(right_tex)
                
                flipped_pil = right_tex.image.transpose(Image.FLIP_LEFT_RIGHT)
                left_tex = arcade.Texture(name=f"frog{i}_left", image=flipped_pil)
                self.frog_textures_left.append(left_tex)
            except:
                right_tex = arcade.load_texture("frog.png")
                self.frog_textures_right.append(right_tex)
                flipped_pil = right_tex.image.transpose(Image.FLIP_LEFT_RIGHT)
                left_tex = arcade.Texture(name=f"frog_backup{i}_left", image=flipped_pil)
                self.frog_textures_left.append(left_tex)

        
        self.animation_frame = 0
        self.animation_direction = 1
        self.last_animation_time = time.time()
        self.facing_right = True

        self.base_texture = self.frog_textures_right[0]
        
        self.setup()

    def setup(self):
        
        self.coin_count = 0
        self.portal_active = False
        self.portal_sound_playing = False
        
        if not hasattr(self, '_game_started'):
            self.start_time = time.time()
            self._game_started = True
        
        self.build_level()
        
        
        if self.music_player:
            self.music_player.pause()
            self.music_player = None
        
        if self.music_main and not self.music_player:
            self.music_player = arcade.play_sound(self.music_main, volume=0.3)

    def build_level(self):
        lvl = self.level
        plat_prefix = f"{lvl}plat"
        coin_file = f"iscra{lvl}.png"
        portal_off = f"port{lvl}.png"
        portal_on = f"1port{lvl}.png"
        back_file = f"back{lvl}.png"

        
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.portal_list = arcade.SpriteList()
        self.lava_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.gui_sprite_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Фон
        if os.path.isfile(back_file):
            bg = arcade.Sprite(
                back_file, center_x=WINDOW_WIDTH/2, center_y=WINDOW_HEIGHT/2
            )
            bg.width, bg.height = WINDOW_WIDTH*1.5, WINDOW_HEIGHT*1.5
            self.background_list.append(bg)

        # создание игрока
        self.player_sprite = arcade.Sprite(scale=PLAYER_SCALING)
        self.player_sprite.texture = self.frog_textures_right[0]
        self.player_sprite.center_x, self.player_sprite.center_y = 64, 128
        self.player_sprite.sync_hit_box_to_texture()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # Создание платформ пола
        if lvl == 1:
            manual_floor_specs = [
                ("1plat1.png", 100, 50, TILE_SCALING*0.35),
                ("1plat2.png", 600, 128, TILE_SCALING*0.35),
                ("1plat3.png", 1860, 240, TILE_SCALING*0.30),
            ]
        elif lvl == 2:
            manual_floor_specs = [
                ("2plat.png", 140, 40, TILE_SCALING*0.30),
                ("2plat.png", 768, 40, TILE_SCALING*0.30),
            ]
        else:
            manual_floor_specs = [
                ("3plat1.png", 300, 60, TILE_SCALING*0.45),
                ("3plat.png", -690, 60, TILE_SCALING*0.45),
            ]
        
        for tex, cx, cy, sc in manual_floor_specs:
            p = arcade.Sprite(tex, scale=sc)
            p.center_x, p.center_y = cx, cy
            self.wall_list.append(p)

        # Лава для уровня 2
        if lvl == 2:
            lava = arcade.Sprite("image-Photoroom (12).png", scale=2)
            # lava.top = self.wall_list[-1].top
            lava.center_x = 500
            lava.center_y = -130
            self.lava_list.append(lava)

        
        
        
        
        
        if lvl == 1:
            coin_specs = [(1504,907),
                        (1860, 330),
                        (-320, 320)]
        elif lvl == 2:
            coin_specs = [(128,340),
                           (500,380)]
        else:
            coin_specs = [(300,400),
                          (100, 640),
                        (100, 800),
                        (-128, 128)]
        for cx,cy in coin_specs:
            c = arcade.Sprite(coin_file, scale=COIN_SCALING*0.3)
            c.center_x, c.center_y = cx, cy
            self.coin_list.append(c)
        self.coins_required = len(self.coin_list)


        #  координаты портала для каждого уровня:
        if lvl == 1:
            portal_x, portal_y = 1500, 130   
        elif lvl == 2:
            portal_x, portal_y = 580, 896   
        else:
            portal_x, portal_y = 1927, 320    
        portal = arcade.Sprite(portal_off, scale=0.3)
        
        portal.center_x, portal.center_y = portal_x, portal_y
        portal.active_tex = arcade.load_texture(portal_on)
        portal.active = False
        self.portal_list.append(portal)

        # Платформа под порталом
        if lvl == 1:
            plat_tex = "1plat1.png"
        elif lvl == 2:
            plat_tex = "2plat.png"
        else:
            plat_tex = "3plat.png"
        plat = arcade.Sprite(plat_tex, scale=TILE_SCALING*0.20)
        plat.center_x = portal.center_x
        
        if lvl == 1:
            offset = 140
        elif lvl == 2:
            offset = 50
        else:
            offset = 140
        plat.center_y = portal.center_y - offset
        self.wall_list.append(plat)

        
        
        
        
        
        if lvl == 1:
            platform_specs = [
                ("1plat1.png", -320, 200, 0.1),
                ("1plat1.png", 832, 350, 0.1),
                
                ("1plat2.png", 1100, 500, 0.2),
                ("1plat3.png", 1500, 740, 0.2),
            ]
        elif lvl == 2:
            platform_specs = [
                ("2plat.png", 500, 256, 0.15),
                ("2plat.png", 900, 450, 0.15),
                ("2plat.png", -128, 192, 0.15),
                ("2plat.png", 704, 700, 0.15),
            ]
        else:
            platform_specs = [
                ("3plat3.png", 360, 196, 0.3),
                ("3plat1.png", 700, 0, 0.40),
                ("3plat2.png", 100, 450, 0.5),
                ("3plat3.png", 1200, 20, 0.55),
                ("image-Photoroom (13).png", 1700, 0, 0.6),
                ("3plat2.png", -128, -128, 0.6),
                ("3plat2.png", 64, -64, 0.4),
            ]
        for tex, cx, cy, sc in platform_specs:
            p = arcade.Sprite(tex, scale=sc)
            p.center_x, p.center_y = cx, cy
            self.wall_list.append(p)

        self.bone_icon_sprite = arcade.Sprite(coin_file, scale=16/32,
                                              center_x=10+16, center_y=WINDOW_HEIGHT-44)
        self.gui_sprite_list.append(self.bone_icon_sprite)

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.dx = self.dy = 0
        self.on_ground = False
        self.double_jumped = False

        # Создание врагов 
        
        if lvl == 1:
            enemy_specs = [
                (250, 450, 160),    
                (1600, 1900, 1000),    
            ]
        elif lvl == 2:
            enemy_specs = [
                (350, 700, 400)       
            ]
        else:  
            enemy_specs = [
                (200, 700, 410),    
                ]
        
        
        for start_x, end_x, y in enemy_specs:
            enemy = Enemy("image-Photoroom (14).png", ENEMY_SCALING, start_x, end_x, y)
            self.enemy_list.append(enemy)

    def hits(self, sprite, group):
        return [s for s in group if (
            sprite.right > s.left and sprite.left < s.right and
            sprite.top > s.bottom and sprite.bottom < s.top)]

    def on_draw(self):
        self.clear()
        if self.background_list:
            self.background_list.draw()
        self.camera.use()
        self.wall_list.draw()
        self.coin_list.draw()
        self.portal_list.draw()
        self.lava_list.draw()
        self.enemy_list.draw()  
        self.player_list.draw()
        
        if self.show_hitboxes:
            for lst,color in ((self.wall_list,arcade.color.GREEN),
                              (self.coin_list,arcade.color.YELLOW),
                              (self.portal_list,arcade.color.ORANGE),
                              (self.lava_list,arcade.color.RED),
                              (self.enemy_list,arcade.color.PURPLE),  # Добавляем врагов в отображение хитбоксов
                              (self.player_list,arcade.color.BLUE)):
                for s in lst:
                    s.draw_hit_box(color)
                    
        if self.show_coordinates:
            cam_l = self.camera.position[0]-WINDOW_WIDTH//2
            cam_b = self.camera.position[1]-WINDOW_HEIGHT//2
            cam_r, cam_t = cam_l+WINDOW_WIDTH, cam_b+WINDOW_HEIGHT
            sx = int(cam_l-(cam_l%GRID_SPACING))
            for x in range(sx, int(cam_r)+GRID_SPACING, GRID_SPACING):
                arcade.draw_line(x,cam_b,x,cam_t,arcade.color.LIGHT_GRAY,1)
            sy = int(cam_b-(cam_b%GRID_SPACING))
            for y in range(sy, int(cam_t)+GRID_SPACING, GRID_SPACING):
                arcade.draw_line(cam_l,y,cam_r,y,arcade.color.LIGHT_GRAY,1)

            for x in range(sx, int(cam_r) + GRID_SPACING, GRID_SPACING):
                arcade.draw_text(
                    f"{x}",
                    x + 2,
                    cam_b + 2,
                    arcade.color.YELLOW,
                    10,
                    anchor_x="left"
                )

            for y in range(sy, int(cam_t) + GRID_SPACING, GRID_SPACING):
                arcade.draw_text(
                    f"{y}",
                    cam_l + 2,
                    y + 2,
                    arcade.color.YELLOW,
                    10,
                    anchor_x="left"
                )

            for lst in (
                self.player_list,
                self.wall_list,
                self.coin_list,
                self.portal_list,
                self.lava_list,
            ):
                for spr in lst:
                    arcade.draw_point(
                        spr.center_x,
                        spr.center_y,
                        arcade.color.RED,
                        5,
                    )
                    arcade.draw_text(
                        f"{int(spr.center_x)}, {int(spr.center_y)}",
                        spr.center_x + 5,
                        spr.center_y + 5,
                        arcade.color.YELLOW,
                        12,
                        anchor_x="left",
                    )
        
        self.gui_camera.use()
        self.gui_sprite_list.draw()
        arcade.draw_text(f"Coins: {self.coin_count}/{self.coins_required}",
                         10+32+5, WINDOW_HEIGHT-60, arcade.color.WHITE, 20)
        
        
        arcade.draw_text(f"Уровень: {self.level}/3", 
                         10, WINDOW_HEIGHT-100, arcade.color.WHITE, 18)
        
        
        current_time = time.time() - self.start_time
        arcade.draw_text(f"Время: {current_time:.1f}с", 
                         10, WINDOW_HEIGHT-125, arcade.color.LIGHT_BLUE, 16)
        
        # Инструкции по управлению
        arcade.draw_text("WASD/Стрелки - движение, F - взаимодействие, ESC - меню", 
                         WINDOW_WIDTH // 2, 20, arcade.color.LIGHT_GRAY, 14, anchor_x="center")
        if self.show_interact_prompt:
            arcade.draw_text("Нажмите F для взаимодействия",
                             WINDOW_WIDTH/2,80, arcade.color.WHITE,20,anchor_x="center")
        if self.message:
            arcade.draw_text(self.message, WINDOW_WIDTH/2, WINDOW_HEIGHT/2,
                             arcade.color.YELLOW,24,anchor_x="center")

    def on_update(self, dt):
        # Обновляем анимацию 
        current_time = time.time()
        if current_time - self.last_animation_time >= BREATHING_ANIMATION_SPEED:
            self.last_animation_time = current_time
            
            
            self.animation_frame += self.animation_direction
            
            
            if self.animation_frame >= len(self.frog_textures_right) - 1:
                self.animation_direction = -1
            elif self.animation_frame <= 0:
                self.animation_direction = 1
            
            
            if self.facing_right:
                self.player_sprite.texture = self.frog_textures_right[self.animation_frame]
            else:
                self.player_sprite.texture = self.frog_textures_left[self.animation_frame]

        if self.message and time.time()>self.message_time:
            self.message=""

        self.show_interact_prompt=False
        self.current_interact_obj=None
        for p in self.portal_list:
            if math.hypot(p.center_x-self.player_sprite.center_x,
                          p.center_y-self.player_sprite.center_y)<=INTERACT_DISTANCE:
                self.show_interact_prompt=True
                self.current_interact_obj=p
                break

        # Обновляем врагов
        self.enemy_list.update()

        self.dy -= GRAVITY

        self.player_sprite.center_x += self.dx
        if self.hits(self.player_sprite, self.wall_list):
            self.player_sprite.center_x -= self.dx

        self.player_sprite.center_y += self.dy
        hy = self.hits(self.player_sprite, self.wall_list)
        if hy:
            if self.dy>0:
                self.player_sprite.top = min(s.bottom for s in hy)
            else:
                self.player_sprite.bottom = max(s.top for s in hy)
                self.on_ground=True
                self.double_jumped=False
            self.dy=0
        else:
            self.on_ground=False

        
        enemy_hits = self.hits(self.player_sprite, self.enemy_list)
        for enemy in enemy_hits:
            # Проверяем, атакует ли игрок сверху
            if (self.dy < 0 and 
                self.player_sprite.center_y > enemy.center_y + enemy.height/3):
                
                enemy.remove_from_sprite_lists()
                # Отскок игрока вверх
                self.dy = ENEMY_BOUNCE_FORCE
                
                self.message = "Враг повержен!"
                self.message_time = time.time() + 1
            else:
                
                self.message = "Вы погибли! Уровень перезапускается..."
                self.message_time = time.time() + 1.5
                # Перезапускаем текущий уровень 
                arcade.unschedule(self.restart_level)
                arcade.schedule(self.restart_level, 0.5)
                return

        for coin in self.hits(self.player_sprite, self.coin_list):
            coin.remove_from_sprite_lists()
            self.coin_count+=1
            
            if self.sound_coin:
                arcade.play_sound(self.sound_coin, volume=0.5)

        if not self.portal_active and self.coin_count>=self.coins_required:
            for p in self.portal_list:
                p.texture=p.active_tex
                p.active=True
            self.portal_active=True
            self.portal_sound_playing = False  

        # Обработка звука портала
        if self.portal_active and not self.portal_sound_playing:
            if self.sound_portal:
                arcade.play_sound(self.sound_portal, volume=0.4)
                self.portal_sound_playing = True
        elif not self.portal_active and self.portal_sound_playing:
            
            self.portal_sound_playing = False

        if self.level==2 and self.hits(self.player_sprite, self.lava_list):
            self.level=1
            self.setup()
            return

        tx,ty=self.player_sprite.position
        cx,cy=self.camera.position
        self.camera.position=(cx+(tx-cx)*0.1, cy+(ty-cy)*0.1)

    def restart_level(self, delta_time):
        """Перезапускает текущий уровень"""
        arcade.unschedule(self.restart_level)
        self.setup()

    def on_key_press(self, key, mods):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.dx=-PLAYER_SPEED
            self.facing_right = False
            # кадр анимации для левого направления
            self.player_sprite.texture = self.frog_textures_left[self.animation_frame]
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.dx=PLAYER_SPEED
            self.facing_right = True
            # кадр анимации для правого направления
            self.player_sprite.texture = self.frog_textures_right[self.animation_frame]
        elif key in (arcade.key.UP, arcade.key.W):
            if self.on_ground:
                self.dy=PLAYER_JUMP
                #  звук прыжка
                if self.sound_jump:
                    arcade.play_sound(self.sound_jump, volume=0.4)
            elif not self.double_jumped:
                self.dy=PLAYER_DOUBLE_JUMP
                self.double_jumped=True
               
                if self.sound_jump:
                    arcade.play_sound(self.sound_jump, volume=0.4)
        elif key==arcade.key.Q:
            self.show_hitboxes=not self.show_hitboxes
        elif key==arcade.key.E:
            self.show_coordinates=not self.show_coordinates
        elif key==arcade.key.ESCAPE:
            
            pause_menu = PauseMenuView(self)
            self.window.show_view(pause_menu)
        elif key==arcade.key.F and self.current_interact_obj:
            p=self.current_interact_obj
            if self.portal_active:
                if self.level<3:
                    self.level+=1
                    self.setup()
                else:
                   
                    total_time = time.time() - self.start_time
                    complete_view = GameCompleteView(total_time, self) 
                    self.window.show_view(complete_view)
            else:
                missing=self.coins_required-self.coin_count
                self.message=f"Не хватает ещё {missing} монет"
                self.message_time=time.time()+2

    def on_key_release(self, key, mods):
        if key in (arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D):
            self.dx=0

    def return_to_menu(self):
        """Возврат в главное меню"""
        
        if self.music_player:
            self.music_player.pause()
            self.music_player = None
        
        self.window.close()
        try:
            subprocess.call([sys.executable, "menu.py"])
        except Exception as e:
            print(f"Ошибка запуска меню: {e}")
            sys.exit()

def main():
    """Основная функция"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__=="__main__":
    main()