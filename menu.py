import arcade
import subprocess
import sys
import os

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
        
        
        
        arcade.draw_line(
            left, top,
            right, top,
            border_color, 3
        )
        
        arcade.draw_line(
            left, bottom,
            right, bottom,
            border_color, 3
        )
        
        arcade.draw_line(
            left, bottom,
            left, top,
            border_color, 3
        )
        
        arcade.draw_line(
            right, bottom,
            right, top,
            border_color, 3
        )
        
        
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center",
            anchor_y="center"
        )

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        
       
        self.buttons = []
        
        
        button_width = 250
        button_height = 60
        button_spacing = 80
        
       
        center_x = 400  
        start_y = 400   
        
        
        self.buttons.append(Button(
            "Основная игра", 
            center_x, 
            start_y, 
            button_width, 
            button_height, 
            (50, 120, 200, 255)
        ))
        
        self.buttons.append(Button(
            "Мини-игра", 
            center_x, 
            start_y - button_spacing, 
            button_width, 
            button_height, 
            (50, 180, 120, 255)
        ))
        
        self.buttons.append(Button(
            "Выход", 
            center_x, 
            start_y - button_spacing * 2, 
            button_width, 
            button_height, 
            (200, 50, 50, 255)
        ))

    def on_show_view(self):
        arcade.set_background_color((20, 30, 40))

    def on_draw(self):
        self.clear()
        
        
        arcade.draw_text(
            "ИГРОВОЕ МЕНЮ", 
            400, 520, 
            arcade.color.WHITE, 
            font_size=36, 
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Выберите игру для запуска", 
            400, 470, 
            arcade.color.LIGHT_GRAY, 
            font_size=18, 
            anchor_x="center"
        )
        
        # кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши для эффектов наведения"""
        for button in self.buttons:
            button.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка кликов по кнопкам"""
        for btn in self.buttons:
            if btn.contains_point(x, y):
                if btn.text == "Основная игра":
                    self.start_game("game2.py")
                elif btn.text == "Мини-игра":
                    self.start_game("memory_game.py")
                elif btn.text == "Выход":
                    arcade.exit()
                break

    def start_game(self, script_name):
        """Запуск игры в отдельном процессе"""
        if os.path.exists(script_name):
            self.window.close()
            try:
                subprocess.call([sys.executable, script_name])
                
                main()
            except Exception as e:
                print(f"Ошибка запуска {script_name}: {e}")
        else:
            print(f"Файл {script_name} не найден!")

class GameOverView(arcade.View):
    
    def __init__(self, message="Игра окончена!"):
        super().__init__()
        self.message = message
        
        
        self.buttons = []
        
        button_width = 200
        button_height = 50
        
        
        self.buttons.append(Button(
            "Играть заново", 
            300, 
            200, 
            button_width, 
            button_height, 
            (50, 150, 50, 255)
        ))
        
        
        self.buttons.append(Button(
            "Главное меню", 
            500, 
            200, 
            button_width, 
            button_height, 
            (150, 50, 150, 255)
        ))

    def on_show_view(self):
        arcade.set_background_color((40, 40, 40))

    def on_draw(self):
        self.clear()
        
        arcade.draw_text(
            self.message, 
            400, 400, 
            arcade.color.WHITE, 
            font_size=32, 
            anchor_x="center"
        )
        
        # кнопки
        for button in self.buttons:
            button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.contains_point(x, y):
                if btn.text == "Играть заново":
                    
                    pass
                elif btn.text == "Главное меню":
                    self.window.close()
                    main()
                break

def main():
    window = arcade.Window(800, 600, "Игровое меню")
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()