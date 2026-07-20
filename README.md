# 🐍 Snake

A classic Snake game built from scratch in **Python** and **Textual**, bringing a complete arcade-style experience to the terminal.

> Eat. Grow. Adapt. Survive.

---

## 📸 Preview

```

*Add gameplay, menu, pause menu, and game-over screenshots here.*
```

---

## 🎮 About

**Snake** is a terminal-based arcade game where you control a continuously moving snake, collect different types of food, increase your score, and survive as the game gets faster.

The rules are simple:

- Eat food to gain points.
- Grow or shrink depending on the food you consume.
- Avoid the walls.
- Avoid colliding with your own body.
- Survive as long as possible.

Every **5 points** increases your level, making the snake move faster and increasing the challenge.

---

## ✨ Features

- Classic Snake gameplay
- Multiple food types with unique effects
- Progressive difficulty system
- Dynamic movement speed
- Buffered direction input for responsive controls
- Wall and self-collision detection
- Score, level, and time tracking
- Pause and resume functionality
- Restart functionality
- Game Over screen
- Main Menu, Controls, and About screens
- Keyboard-navigable menus
- Standalone executable support

---

## 🍎 Food

The game features multiple food types with different gameplay effects.

### 🍎 Apple

The standard food.

- Increases the score.
- Makes the snake grow.

### 🫐 Berry

A risk-reward food.

- Increases the score.
- Shrinks the snake by removing body segments.

The food system is designed to be extensible, making it easy to add new food types and gameplay effects.

---

## 📈 Progression

Every **5 points** increases the player's level.

As the level increases, the snake's movement interval decreases, causing the snake to move faster.

The game becomes progressively more challenging while remaining simple to understand.

---

## 🎮 Controls

### Movement

| Key       | Action     |
| --------- | ---------- |
| `W` / `↑` | Move Up    |
| `A` / `←` | Move Left  |
| `S` / `↓` | Move Down  |
| `D` / `→` | Move Right |

### Game

| Key     | Action         |
| ------- | -------------- |
| `ESC`   | Pause / Resume |
| `SPACE` | Pause / Resume |

### Menus

| Key       | Action        |
| --------- | ------------- |
| `W` / `↑` | Navigate Up   |
| `S` / `↓` | Navigate Down |
| `ENTER`   | Select        |

---

## 🧠 Responsive Direction Input

The game uses a small direction buffer to handle rapid input.

For example, `RIGHT → DOWN → LEFT` can be entered quickly and executed across consecutive game ticks.

At the same time, impossible instant reversals such as `RIGHT → LEFT` are prevented.

This keeps the controls responsive without allowing the snake to immediately collide with itself due to an instant 180-degree turn.

---

## 🧱 Architecture

Food mechanics use an abstract base class and polymorphism.

Each food type defines its own behavior through the `power()` method. This allows new food mechanics to be added independently without modifying the core collision system.

The result is a modular food system where adding a new food type does not require adding more food-specific logic to the main game loop.

---

## 🛠️ Built With

- Python
- Textual

### Concepts Used

- Object-Oriented Programming
- Abstract Base Classes
- Inheritance
- Polymorphism
- `deque`
- Type Hints
- Event-Driven Programming
- Timers
- Screen Navigation
- Keyboard Focus Management

---

## 🚀 Run Locally

### Clone the Repository

```
git clone https://github.com/sizan14789/Snake.git

cd Snake
```

### Install the Dependency

```
pip install textual
```

### Run the Game

```
python main.py
```

---

## 📦 Build a Standalone Executable

The game can be packaged as a standalone Windows executable using PyInstaller:

```
pyinstaller --onefile --add-data "app.tcss;." --name Snake main.py
```

The executable will be generated in:

```
dist/Snake.exe
```
