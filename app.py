from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Label, Header, Button
from random import randint
from collections import deque

class Snake:
    def __init__(self, x: int = 0, y: int = 0, dir: str = "r") -> None: 
        self.body = deque([ (x, y), (x-1, y), (x-2, y) ])
        self.dir = dir
        self.score = 0
    
    def move(self, dx: int, dy: int) -> None:
        new_head_x = self.body[0][0] + dx
        new_head_y = self.body[0][1] + dy
        self.body.appendleft((new_head_x, new_head_y))
        self.body.pop()

class Food:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def power(self, snake: Snake):
        last_x, last_y = snake.body[len(snake.body)-1]
        snake.body.append((last_x, last_y))

class MyApp(App):
    CSS_PATH = "app.tcss"

    def __init__(self) -> None: 
        self.snake = Snake(randint(10, 30), randint(10, 20), 'r')
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
                    self.snake_widget = [ Label("◉", classes="snake") for _ in self.snake.body ]
                    for i, (s_w, pos) in enumerate(zip(self.snake_widget, self.snake.body)):
                        s_w.styles.offset = pos
                        if i==0:
                            s_w.styles.color = "white"
                        yield s_w
            
            with Vertical(classes="footer-container"):
                with Horizontal(classes="footer-cards"):
                    self.score_widget = Label(f"SCORE: 000", classes="footer-card", id="score")
                    yield self.score_widget

                    self.position_widget = Label(f"POSITION: {self.snake.body[0][0]} {self.snake.body[0][1]}", classes="footer-card", id="footer-card-position")
                    yield self.position_widget

                    min, sec = int(self.time//60), int(self.time) % 60
                    self.time_widget = Label(f"TIME: {min:02d}:{sec}", classes="footer-card")
                    yield self.time_widget

    # Movement -------------------------
    def on_key(self, event) -> None:
        if self.GO_status:
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

        self.game_tick()

    def on_ready(self) -> None:
        self.food_spawn()
        # self.set_interval(self.game_speed, self.game_tick)

    def game_tick(self) -> None:
        if self.GO_status:
            return

        g = self.playground_widget
        s = self.snake
        head_x = s.body[0][0]
        head_y = s.body[0][1]

        # up down
        if s.dir=="d" and head_y < g.size.height:
            s.move(0, 1)
        elif s.dir=="u" and head_y >= 0:
            s.move(0, -1)
        
        # right left 
        elif s.dir=="r" and head_x < g.size.width:
            s.move(1, 0)
        elif s.dir=="l" and head_x >= 0:
            s.move(-1, 0)

        # update position 
        self.position_widget.update(f"POSITION: {head_x} {head_y}")
        
        # move snake
        for s_w in self.snake_widget:
            s_w.remove()

        self.snake_widget = [ Label("◉", classes="snake") for _ in self.snake.body ]
        for i, (s_w, pos) in enumerate(zip(self.snake_widget, self.snake.body)):
            s_w.styles.offset = pos
            if i==0:
                s_w.styles.color = "white"
            g.mount(s_w)
        
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
        s = self.snake
        f = self.food
        
        head_x = s.body[0][0]
        head_y = s.body[0][1]

        if head_y==f.y and head_x == f.x: 
            self.food_widget.remove()
            self.food_spawn()
            s.score+=1
            self.score_widget.update(f"SCORE: {s.score}")
            f.power(s)

    def check_GO(self) -> None:
        g = self.playground_widget
        s = self.snake
        
        head_x = s.body[0][0]
        head_y = s.body[0][1]

        go_conditions = [
            head_x < 0, 
            head_y < 0, 
            head_x == g.size.width, 
            head_y == g.size.height
        ]

        if any(go_conditions):
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
        self.snake = Snake(randint(10, 30), randint(10, 20), 'r')
        self.GO_status: bool = False
        self.time: float = 0.0
        self.game_speed: float = 0.1
        
        # restart visuals
        g = self.playground_widget
        head_x = self.snake.body[0][0]
        head_y = self.snake.body[0][1]

        # redraw snake
        for s_w in self.snake_widget:
            s_w.remove()
        
        self.snake_widget = [ Label("◉", classes="snake") for _ in self.snake.body ]
        for i, (s_w, pos) in enumerate(zip(self.snake_widget, self.snake.body)):
            s_w.styles.offset = pos
            if i==0:
                s_w.styles.color = "white"
            g.mount(s_w)

        # footer cards
        self.position_widget.update(f"POSITION: {head_x} {head_y}")
        self.score_widget.update("SCORE: 000") 
        self.time_widget.update("TIME: 00:00")
    
    # footer  -------------------------
    def update_time(self) -> None: 
        self.time+=self.game_speed
        min, sec = int(self.time//60), int(self.time) % 60
        self.time_widget.update(f"TIME: {min:02d}:{sec}") 

MyApp().run()