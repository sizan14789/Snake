from random import randint
from collections import deque

from textual.app import App, ComposeResult
from textual.events import Key
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Label, Button

class Snake:
    icon = "██"
    head_color = "#d8ffe0"

    def __init__(self, g) -> None:
        self.prepare_body(g)

    def prepare_body(self, g):
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
        
    def move(self, dx: int, dy: int) -> None:
        new_head_x = self.body[0][0] + 2*dx
        new_head_y = self.body[0][1] + dy
        self.body.appendleft((new_head_x, new_head_y))
        self.body.pop()

    def grow(self):
        last_x, last_y = self.body[-1]
        self.body.append((last_x, last_y))

class Food:
    icon = "◆◆"
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def power(self, snake: Snake):
        snake.grow()

class MyApp(App):
    CSS_PATH = "app.tcss"

    def __init__(self) -> None:
        super().__init__()

    def on_mount(self):
        self.push_screen(MenuScreen())
        # self.push_screen(GameScreen())

class HeaderWidget(Container):
    def compose(self) -> ComposeResult:
        yield Label("S N A K E", classes="header-text")

class GameScreen(Screen):
    def __init__(self) -> None:
        self.time: float = 0.0 
        self.score = 0
        self.level = 1
    
        self.game_over: bool = False
        self.paused = False
    
        super().__init__()
    
    # layout -------------------------
    def compose(self) -> ComposeResult:
        with Vertical(classes="wrapper"):
            yield HeaderWidget(classes="header-container")
    
            with Vertical(classes="playground-container"):
                self.playground_widget = Container(classes="playground")
                yield self.playground_widget
                    
            with Vertical(classes="footer-container"): 
                with Horizontal(classes="footer-cards"):
                    self.score_widget = Label(f"SCORE: 000", classes="footer-card", id="score")
                    yield self.score_widget
    
                    # self.position_widget = Label(f"POSITION: 0 0", classes="footer-card", id="footer-card-position")
                    # yield self.position_widget
    
                    self.level_widget = Label(f"LEVEL: {self.level:02d}", classes="footer-card", id="footer-card-level")
                    yield self.level_widget
    
                    min, sec = int(self.time//60), int(self.time) % 60
                    self.time_widget = Label(f"TIME: {min:02d}:{sec}", classes="footer-card")
                    yield self.time_widget

    # Setup -------------------------
    def on_mount(self) -> None:
        self.call_after_refresh(self.setup_game)
            
    def setup_game(self): 
        self.snake = Snake(self.playground_widget)    
        self.render_snake()
        self.food_spawn()
        interval = min(0.8 , 0.16-self.level * 0.02)
        self.set_interval(interval, self.game_tick)
    
    # Movement -------------------------
    def on_key(self, event) -> None:
        if self.game_over:
            return
        if self.paused:
            if event.key in ('escape', 'space'):
                self.resume_game()
            return
    
        s = self.snake
    
        # up down 
        if event.key in ('s', 'down') and s.dir!="u":
            s.dir = "d"
    
        elif event.key in ('w', 'up') and s.dir!="d":
            s.dir = "u"
    
        # right left 
        elif event.key in ('d', 'right') and s.dir!="l":
            s.dir = "r"
        elif event.key in ('a', 'left') and s.dir!="r":
            s.dir = "l"
        elif event.key in ('escape', 'space'): 
            self.pause_game() 
      
    def game_tick(self) -> None:
        if self.game_over:
            return
    
        if self.paused:
            return
    
        s = self.snake 
    
        # up down
        if s.dir=="d":
            s.move(0, 1)
        elif s.dir=="u":
            s.move(0, -1)
    
        # right left 
        elif s.dir=="r":
            s.move(1, 0)
        elif s.dir=="l":
            s.move(-1, 0)
    
        head_x, head_y = s.body[0]
    
        # update position 
        # self.position_widget.update(f"POSITION: {head_x} {head_y}")
    
        # move snake
        self.render_snake()
    
        # collision
        self.check_food_collision()
    
        # game over check
        self.check_GO()
    
        # update time
        self.update_time()
    
    def render_snake(self):
        # if called first time
        if hasattr(self, "snake_widget"):
            for s_w in self.snake_widget:
                s_w.remove()
    
        self.snake_widget = [ Label(f"{self.snake.icon}", classes="snake") for _ in self.snake.body ]
        for i, (s_w, pos) in enumerate(zip(self.snake_widget, self.snake.body)):
            s_w.styles.offset = pos
            if i==0:
                s_w.styles.color = self.snake.head_color
            self.playground_widget.mount(s_w)
    
    # Food and collision -------------------------
    def food_spawn(self) -> None:
        g = self.playground_widget
    
        food_x = randint(0, self.playground_widget.size.width - 1)
        food_y = randint(0, self.playground_widget.size.height - 1)
    
        self.food = Food(food_x-1 if food_x&1 else food_x, food_y)
        f = self.food
    
        self.food_widget = Label(f"{self.food.icon}", classes="food")
        self.food_widget.styles.offset = (f.x, f.y)
        g.mount(self.food_widget)
    
    def check_food_collision(self) -> None:
        s = self.snake
        f = self.food
    
        head_x, head_y = s.body[0] 
    
        if (head_x, head_y) in [ (f.x, f.y) ]:
            self.food_widget.remove()
            self.food_spawn()
    
            self.score+=1
            self.score_widget.update(f"SCORE: {self.score:03d}")
    
            self.level = self.score // 5 + 1
            self.level_widget.update(f"LEVEL: {self.level:02d}")
    
            f.power(s)
    
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
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("restart-button"):
            self.restart_game()
        elif event.button.has_class("resume-button"):
            self.resume_game()
        elif event.button.has_class("menu-button"):
            self.app.pop_screen()
    
    def restart_game(self) -> None:
        # remove overlay if called from go screen
        if hasattr(self, "game_over_menu_widget"):
            self.game_over_menu_widget.remove()
    
        # restart game variables
        random_pos = randint(10, 20)
        self.snake = Snake(self.playground_widget)
        self.game_over: bool = False
        self.time: float = 0.0
        self.score = 0
        self.level = 1
    
        # restart visuals
        head_x, head_y = self.snake.body[0]
    
        # redraw snake
        self.render_snake()
    
        # re spawn food
        self.food_widget.remove()
        self.food_spawn()
    
        # footer cards
        # self.position_widget.update(f"POSITION: {head_x} {head_y}")
        self.level_widget.update(f"LEVEL: 1")
        self.score_widget.update("SCORE: 000") 
        self.time_widget.update("TIME: 00:00")
    
        # if called from pause screen
        self.paused = False
        if hasattr(self, "pause_widget"):
            self.pause_widget.remove()
    
    # footer -------------------------
    def update_time(self) -> None: 
        game_speed = 0.16 - self.level * 0.02
        self.time+= game_speed
        min, sec = int(self.time//60), int(self.time) % 60
        self.time_widget.update(f"TIME: {min:02d}:{sec}")

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

        if event.key in ("w", 'down'):    
            if s_f:
                s_f_i = buttons_list.index(s_f)
                new_focus_index = (s_f_i + 1) % len(buttons_list)
                buttons_list[new_focus_index].focus()
            else:
                buttons_list[0].focus()

        elif event.key in ('s', "up"):
            if s_f:
                s_f_i = buttons_list.index(s_f)
                new_focus_index = (s_f_i - 1 + len(buttons_list)) % len(buttons_list)
                buttons_list[new_focus_index].focus()
            else:
                buttons_list[0].focus()

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