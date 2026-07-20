from __future__ import annotations 
from random import randint
from collections import deque
from abc import ABC, abstractmethod

from textual.app import App, ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Label, Button

# CLasses -----------------------------------
class Snake:
    icon = "██"
    head_color = "#d8ffe0"
    body_color ="#22c55e" 
    dx_dy = { 'r': (2, 0), 'l': (-2, 0), 'u': (0, -1), 'd': (0, 1) }
    min_length = 3

    def __init__(self, g: Container) -> None:
        self.prepare_body(g)

    def prepare_body(self, g: Container):
        x_offset, y_offset = 16, 10
        head_x = (randint(x_offset, g.size.width - x_offset) // 2) * 2
        head_y = randint(y_offset, g.size.height - y_offset)

        self.body = deque([ (head_x, head_y) ]) 
        self.dir = ('r', 'l', 'u', 'd')[randint(0, 3)]

        if self.dir=='r':
            self.body.extend((head_x - i, head_y) for i in range(2, 7, 2))
        elif self.dir=='l':
            self.body.extend((head_x + i, head_y) for i in range(2, 7, 2))
        elif self.dir=='u':
            self.body.extend((head_x, head_y+i) for i in range(1, 4))
        elif self.dir=='d':
            self.body.extend((head_x, head_y-i) for i in range(1, 4))
        
    def move(self, game: GameScreen) -> None:
        new_head_x = self.body[0][0] + self.dx_dy[self.dir][0]
        new_head_y = self.body[0][1] + self.dx_dy[self.dir][1]

        # set new head
        self.body.appendleft((new_head_x, new_head_y))
        new_head = Label(f"{self.icon}", classes="snake")
        new_head.styles.offset = (new_head_x, new_head_y)
        new_head.styles.color = self.head_color
        game.snake_widget.appendleft(new_head)
        game.playground_widget.mount(new_head)

        # remove the old head (color)
        game.snake_widget[1].styles.color = self.body_color

        # remove old tail
        self.body.pop()
        game.snake_widget.pop().remove()

    def grow(self, game: GameScreen):
        last_x, last_y = self.body[-1]
        self.body.append((last_x, last_y))

        tail = Label(f"{self.icon}", classes="snake")
        tail.styles.offset = self.body[-1]
        game.snake_widget.append(tail)
        game.playground_widget.mount(tail)

    def shrink(self, game: GameScreen, amount: int):
        shrink_by = amount if len(self.body) - amount >= self.min_length else 0

        for _ in range(shrink_by):
            self.body.pop()
            game.snake_widget.pop().remove()
    
class Food(ABC):
    def __init__(self, icon = "◆◆", color = "#fb7185") -> None:
        self.height = 1
        self.width = 2
        self.icon = icon
        self.color = color

    @abstractmethod
    def power(self, snake: Snake, game: GameScreen):
        pass

class AppleFood(Food):
    def __init__(self) -> None:
        super().__init__("◆◆", "#fb7185") 

    def power(self, snake: Snake, game: GameScreen):
        game.score+=1
        snake.grow(game)
        
class BerryFood(Food):
    def __init__(self) -> None:
        super().__init__("○○", "#a954ff") 

    def power(self, snake: Snake, game: GameScreen):
        game.score+=1
        snake.shrink(game, 2)

# game --------------------------------------
class MyApp(App):
    CSS_PATH = "app.tcss"

    def __init__(self) -> None:
        super().__init__()

    def on_mount(self):
        self.push_screen(MenuScreen())

class HeaderWidget(Container):
    def compose(self) -> ComposeResult:
        yield Label("S N A K E", classes="header-text")

class GameScreen(Screen):
    def __init__(self) -> None:
        self.base_speed = 0.15
        self.min_speed = 0.07
        super().__init__() 
    
    # layout -------------------------
    def compose(self) -> ComposeResult:
        with Vertical(classes="wrapper"):
            yield HeaderWidget(classes="header-container")
    
            with Vertical(classes="playground-container"):
                self.playground_widget = Container(classes="playground")
                yield self.playground_widget
                    
            yield Horizontal(classes="footer-container")
            
    # Setup -------------------------
    def on_mount(self) -> None:
        self.call_after_refresh(self.setup_game) 
    
    def setup_game(self):
        # Initialize game variables
        self.time: float = 0.0 
        self.score = 0
        self.level = 1

        self.game_over: bool = False
        self.paused = False 

        self.next_dir = deque() 

        # setup food
        if hasattr(self, "food_widget_dict"): # if previous food exists
            for food in self.food_widget_dict.values():
                food.remove()

        self.food_widget_dict = {}
        self.food_dict = {}
        self.spawn_one_food()
        self.spawn_one_food()
        self.spawn_one_food()
        
        # setup snake
        self.snake = Snake(self.playground_widget)

        if hasattr(self, "snake_widget"): # if previous snake exists
            for s_w in self.snake_widget:
                s_w.remove()
        
        self.snake_widget = deque([ Label(f"{self.snake.icon}", classes="snake") for _ in self.snake.body ])
        for i, (s_w, pos) in enumerate(zip(self.snake_widget, self.snake.body)):
            s_w.styles.offset = pos
            if i==0:
                s_w.styles.color = self.snake.head_color
            self.playground_widget.mount(s_w)

        # setup timer
        if hasattr(self, "timer"): # if previous timer exists
            self.timer.stop()
        self.timer = self.set_interval(self.base_speed, self.game_tick)

        # setup_footer  
        if hasattr(self, 'score_widget'): # remove footers if exist 
            self.score_widget.remove()
            self.level_widget.remove()
            self.time_widget.remove()

        a = self.query_one(".footer-container", Horizontal)
        self.score_widget = Label(f"SCORE: 000", classes="footer-card")
        a.mount(self.score_widget)
        self.level_widget = Label(f"LEVEL: 01", classes="footer-card")
        a.mount(self.level_widget)
        self.time_widget = Label(f"TIME: 00:00", classes="footer-card")
        a.mount(self.time_widget)
    
    # Movement -------------------------
    def on_key(self, event: Key) -> None:
        if self.game_over:
            self.navigation_for_pause_game_over(event.key)            
            return
        if self.paused:
            self.navigation_for_pause_game_over(event.key)
            return 
        
        # up down left right
        if event.key in ('s', 'down'):
            if len(self.next_dir) == 2:
                self.next_dir.pop()
            self.next_dir.append("d")

        elif event.key in ('w', 'up'):
            if len(self.next_dir) == 2:
                self.next_dir.pop()
            self.next_dir.append("u")
        
        elif event.key in ('d', 'right'):
            if len(self.next_dir) == 2:
                self.next_dir.pop()
            self.next_dir.append("r")

        elif event.key in ('a', 'left'):
            if len(self.next_dir) == 2:
                self.next_dir.pop()
            self.next_dir.append("l")

        elif event.key in ('escape', 'space'): # Pause
            self.pause_game() 

    def navigation_for_pause_game_over(self, key: str) -> None:
            options_list = list(self.query(".pause-go-button"))

            current_focus = self.app.focused            
            current_focus_index = len(options_list) - 1

            if current_focus:
                current_focus_index = options_list.index(current_focus)

            if key in ('escape', 'space'):
                self.resume_game()

            elif key in ('s', 'down'):
                options_list[(current_focus_index + 1) % len(options_list)].focus()
            elif key in ('w', 'up'):
                options_list[(current_focus_index - 1 + len(options_list)) % len(options_list)].focus()
    
    def game_tick(self) -> None:
        if self.game_over:
            return
    
        if self.paused:
            return

        # provide direction to snake
        last_dir = self.snake.dir
        if(self.next_dir):
            last_dir = self.next_dir.popleft()

        if not any([
            self.snake.dir in ('r', 'l') and last_dir in ('r', 'l'),
            self.snake.dir in ('u', 'd') and last_dir in ('u', 'd') 
        ]):
            self.snake.dir = last_dir

        # move snake
        self.snake.move(self) 

        # collision
        self.check_food_collision()
    
        # game over check
        self.check_GO()
    
        # update time
        self.update_time()

    # Food and collision ------------------------- 
    def spawn_one_food(self):
        food_classes = [ AppleFood, BerryFood, AppleFood, AppleFood ]
        cur_food = food_classes[randint(0, len(food_classes)-1)]()

        # generating random location and adding to list
        f_x = (randint(0, self.playground_widget.size.width - cur_food.width) // 2)*2
        f_y = randint(0, self.playground_widget.size.height - cur_food.height)
        self.food_dict[(f_x, f_y)] = cur_food

        # creating food widget
        c_f = Label(f"{cur_food.icon}", classes="food")
        c_f.styles.color = cur_food.color
        c_f.styles.offset = (f_x, f_y)

        self.food_widget_dict[(f_x, f_y)] = c_f
        self.playground_widget.mount(c_f)
    
    def remove_one_food(self, x: int, y: int):
        self.food_dict.pop((x, y))
        self.food_widget_dict.pop((x, y)).remove()
      
    def check_food_collision(self) -> None:
        prev_level = self.level
        head_x, head_y = self.snake.body[0] 
    
        if (head_x, head_y) in self.food_dict:
            self.food_dict[(head_x, head_y)].power(self.snake, self)
            self.remove_one_food(head_x, head_y)
            self.spawn_one_food()

            self.score_widget.update(f"SCORE: {self.score:03d}")
            self.level = self.score // 5 + 1
            self.level_widget.update(f"LEVEL: {self.level:02d}")

        if self.level > prev_level: 
            self.timer.stop()
            self.timer = self.set_interval(max(self.min_speed, self.base_speed - self.level * 0.02), self.game_tick)
    
    # Pause Resume -------------------------
    def pause_game(self):
        self.paused = True
    
        g = self.playground_widget
        self.pause_widget = Container(classes="pause-menu")
        g.mount(self.pause_widget)
    
        self.pause_widget.mount(Label("P A U S E D", classes='pause-title'))
        self.pause_widget.mount(Button("Resume", classes='pause-go-button resume-button' ))
        self.pause_widget.mount(Button("Restart", classes='pause-go-button restart-button' ))
        self.pause_widget.mount(Button("Main Menu", classes='pause-go-button menu-button' ))

        self.pause_widget.query_one(".resume-button").focus()
    
    def resume_game(self):
        self.paused = False
        self.pause_widget.remove()
    
    # game over and restart -------------------------
    def check_GO(self) -> None:
        g = self.playground_widget
        s = self.snake
    
        head_x, head_y = s.body[0] 
    
        go_conditions = [
            head_x < 0, 
            head_y < 0, 
            head_x == g.size.width, 
            head_y == g.size.height,
            (head_x, head_y) in list(s.body)[1:]
        ]
    
        if any(go_conditions):
            self.game_over = True 
    
            self.game_over_menu_widget = Container(classes="game-over-menu")
            self.playground_widget.mount(self.game_over_menu_widget)
    
            self.game_over_menu_widget.mount(Label("G A M E  O V E R", classes="game-over-title"))
            self.game_over_menu_widget.mount(Button("Restart", classes="pause-go-button restart-button"))
            self.game_over_menu_widget.mount(Button("Main Menu", classes='pause-go-button menu-button' ))

            self.game_over_menu_widget.query_one(".restart-button").focus()

    def restart_game(self) -> None:
        # remove overlay if called from game over screen
        if hasattr(self, "game_over_menu_widget"):
            self.game_over_menu_widget.remove()

        # remove overlay if called from pause screen
        self.paused = False
        if hasattr(self, "pause_widget"):
            self.pause_widget.remove()

        self.setup_game() 

    # Button handling ----------------------     
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("restart-button"):
            self.restart_game()
        elif event.button.has_class("resume-button"):
            self.resume_game()
        elif event.button.has_class("menu-button"):
            self.app.pop_screen()
    
    # footer -------------------------
    def update_time(self) -> None:  
        self.time+= self.timer._interval 
        min, sec = int(self.time//60), int(self.time) % 60
        self.time_widget.update(f"TIME: {min:02d}:{sec:02d}")

class MenuScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.state = "home"

    # Setup -------------------------
    def compose(self) -> ComposeResult:
        with Vertical(classes="wrapper"):
            yield HeaderWidget(classes="header-container")

            self.menu_container_widget =  Vertical(classes="menu-container")
            with self.menu_container_widget:
                yield Button("Start Game", classes="main-menu-button start-game-button")
                yield Button("Controls", classes="main-menu-button control-button")
                yield Button("About", classes="main-menu-button about-button")
                yield Button("Exit", classes="main-menu-button exit-button")
            
            yield Label("© 2026 Sizan. All rights reserved.", classes="menu-footer")

    # key presses -------------------
    def on_key(self, event: Key) -> None:
        buttons_list = list(self.query('.main-menu-button'))
        s_f = self.app.focused
        s_f_i = 0
        if s_f and s_f.has_class("main-menu-button"):
            s_f_i = buttons_list.index(s_f)

        if event.key in ("s", 'down'):
            buttons_list[(s_f_i + 1) % len(buttons_list)].focus()
        elif event.key in ('w', "up"): 
            buttons_list[(s_f_i - 1 + len(buttons_list)) % len(buttons_list)].focus()
        
    # button actions --------------------
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.has_class("start-game-button") and self.state=='home':
            self.app.push_screen(GameScreen())

        elif event.button.has_class("control-button") and self.state=='home':
            self.summon_controls()
        elif event.button.has_class("control-main-menu-button"):
            self.controls_container_widget.remove()
            self.state = 'home'

        elif event.button.has_class("about-button") and self.state=='home':
            self.summon_about()
        elif event.button.has_class("about-main-menu-button"):
            self.about_container_widget.remove()
            self.state = 'home'
       
        elif event.button.has_class("exit-button") and self.state=='home':
            self.app.exit()

    def summon_controls(self):
        m = self.menu_container_widget
        self.state = "controls"

        self.controls_container_widget = Container(classes="controls-container")
        sccw = self.controls_container_widget

        m.mount(sccw)
        sccw.mount(Label("     C O N T R O L S", classes="control-title"))
        sccw.mount(Label("W / ↑               Move Up", classes="control-text"))
        sccw.mount(Label("A / ←             Move Left", classes="control-text"))
        sccw.mount(Label("S / ↓             Move Down", classes="control-text"))
        sccw.mount(Label("D / →            Move Right", classes="control-text"))
        sccw.mount(Label("ESC / SPACE  Pause / Resume", classes="control-text"))
        sccw.mount(Button("Back to Main Menu", classes="control-text control-main-menu-button")) 

    def summon_about(self):
        m = self.menu_container_widget
        self.state = "about"

        self.about_container_widget = Container(classes="about-container")
        m.mount(self.about_container_widget)

        acw = self.about_container_widget

        acw.mount(Label("A B O U T", classes="about-title"))

        acw.mount(Label(
            "SNAKE is a classic arcade game where you grow your snake\n"
            "by eating food while avoiding the walls and your own body.",
            classes="about-text"
        ))

        acw.mount(Label(
            "RULES\n"
            "• Eat food to grow and increase your score.\n"
            "• Avoid the walls and your own body.\n"
            "• Colliding with either ends the game.",
            classes="about-text"
        ))

        acw.mount(Label(
            "PROGRESSION\n"
            "Every 5 points increases your level.\n"
            "Higher levels make the snake move faster.",
            classes="about-text"
        ))

        acw.mount(Label("Created by Sizan", classes="about-credit" ))
        acw.mount(Button( "Back to Main Menu", classes="about-text about-main-menu-button" ))

MyApp().run()