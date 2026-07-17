from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Label, Header, Button
from random import randint

class Snake:
    def __init__(self, x: int = 0, y: int = 0, dir: str = "r") -> None:
            self.x, self.y, self.dir = x, y, dir
            self.score = 0
    
    def move(self, dx: int, dy: int) -> None:
            self.x += dx
            self.y += dy

class Player:
    def __init__(self, x: int, y: int, dir: str) -> None:
        self.x, self.y, self.dir = x, y, dir
        self.score: int = 0

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

class Food:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

class MyApp(App):
    CSS_PATH = "app.tcss"

    def __init__(self) -> None:
        self.player: Player = Player(randint(10, 30), randint(10, 20), 'r')
        self.GO_status: bool = False
        self.time: float = 0.0
        self.game_speed: float = 0.1
        super().__init__()

    # layout -------------------------
    def compose(self) -> ComposeResult:
        with Vertical(classes="wrapper"):
            with Vertical(classes="header-container"):
                yield Label("S N A K E", classes="header-text")

            with Vertical(classes="playground-container"):
                self.playground_widget = Container(classes="playground")
                with self.playground_widget:
                    self.snake_widget = Label("◉", classes="snake")
                    self.snake_widget.styles.offset = (self.player.x, self.player.y)
                    yield self.snake_widget
            
            with Vertical(classes="footer-container"):
                with Horizontal(classes="footer-cards"):
                    self.score_widget = Label(f"SCORE: 000", classes="footer-card", id="score")
                    yield self.score_widget

                    self.position_widget = Label(f"Position: {self.player.x} {self.player.y}", classes="footer-card", id="footer-card-position")
                    yield self.position_widget

                    min, sec = int(self.time//60), int(self.time) % 60
                    self.time_widget = Label(f"TIME: {min:02d}:{sec}", classes="footer-card")
                    yield self.time_widget

    # Movement -------------------------
    def on_key(self, event) -> None:
        if self.GO_status:
            return

        p = self.player
        
        # up down 
        if event.key in ('s', 'down') and p.dir!="u":
            p.dir = "d"
        elif event.key in ('w', 'up') and p.dir!="d":
            p.dir = "u"

        # right left 
        elif event.key in ('d', 'right') and p.dir!="l":
            p.dir = "r"
        elif event.key in ('a', 'left') and p.dir!="r":
            p.dir = "l"

        # self.game_tick()

    def on_ready(self) -> None:
        self.food_spawn()
        self.set_interval(self.game_speed, self.game_tick)

    def game_tick(self) -> None:
        if self.GO_status:
            return

        g = self.playground_widget
        p = self.player

        # up down
        if p.dir=="d" and p.y < g.size.height:
            p.move(0, 1)
        elif p.dir=="u" and p.y >= 0:
            p.move(0, -1)
        
        # right left 
        elif p.dir=="r" and p.x < g.size.width:
            p.move(1, 0)
        elif p.dir=="l" and p.x >= 0:
            p.move(-1, 0)

        # update position 
        self.position_widget.update(f"Position: {p.x} {p.y}")
        
        # move snake
        self.snake_widget.styles.offset = (p.x, p.y)
        
        # collision
        self.check_food_collision()

        # game over check
        self.check_GO()

        # update time
        self.update_time()

    # Food and collision -------------------------
    def food_spawn(self) -> None:
        g = self.playground_widget
        self.food = Food(randint(0, self.playground_widget.size.width - 1), randint(0, self.playground_widget.size.height - 1))
        f = self.food

        self.food_widget = Label(f"◉", classes="food")
        self.food_widget.styles.offset = (f.x, f.y)
        g.mount(self.food_widget)

    def check_food_collision(self) -> None:
            p = self.player
            f = self.food
    
            if p.y==f.y and p.x == f.x: 
                self.food_widget.remove()
                self.food_spawn()
                self.player.score+=1
                self.score_widget.update(f"SCORE: {self.player.score}")

    def check_GO(self) -> None:
        p: Player = self.player
        g: Container = self.playground_widget

        if any([p.x < 0, p.y < 0, p.x == g.size.width, p.y == g.size.height]):
            self.GO_status = True

            self.game_over_widget: Label = Label("G A M E  O V E R", classes="game_over")
            g.mount(self.game_over_widget)

            self.restart_widget: Button = Button("Restart", id="restart")
            g.mount(self.restart_widget)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "restart":
            self.handle_restart()

    def handle_restart(self):
        # remove overlay
        self.game_over_widget.remove()
        self.restart_widget.remove()
        
        # restart game variables
        self.player = Player(randint(10, 30), randint(10, 20), 'r')
        self.GO_status = False
        self.time = 0.0
        self.game_speed = 0.1
        
        # restart visuals
        self.snake_widget.styles.offset = (self.player.x, self.player.y)
        self.score_widget.update("SCORE: 000")
        self.position_widget.update(f"Position: {self.player.x} {self.player.y}")
        self.time_widget.update("00:00")
    
    # footer  -------------------------
    def update_time(self) -> None: 
        self.time+=self.game_speed
        min, sec = int(self.time//60), int(self.time) % 60
        self.time_widget.update(f"TIME: {min:02d}:{sec}") 

MyApp().run()