import pygame
import pygame.gfxdraw
import sys
import json
import time
import math
import random
from collections import deque
from datetime import datetime, timedelta
from pygame.locals import *
import os
pygame.init()

RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (169, 169, 169)
LIGHT_GREY = (200, 200, 200)
DARK_GREY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

square_size = 7
speed_index = 0
current_speed_index = 0
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
money = 1000
manpower = 50000
guns = 50000
BALL_COST_MANPOWER = 1000
BALL_COST_GUNS = 1000
BALL_SPEED = 2
BALL_RADIUS = 10
MIN_DISTANCE = 50
SHIFT_INTERVAL = 0.2
BLUE_BALLS_AMOUNT = 10
FPS = 30

clock_speed = [1, 5, 10, 20]
balls = [] 
city_positions_blue = []
city_positions_red = []
squares = []
cities = []
capitals = []
global_progress_bars = []
draggable_windows = []
menu_bar_buttons = []
frontline_segments = []
frontline = []
provinces = []

at_war = False
show_province_borders = True
time_paused = False
current_open_window = None
button_clicked = False
selected_team = None
game_paused = False
capital_position_blue = None
capital_position_red = None
option = None
running = True
menu_bar_visible = False
drawing_frontline = False
frontline_start = None
frontline_end = None

current_screen = "menu"

def save_progress(progress_values):
    with open("progress2.json", "w") as file:
        json.dump(progress_values, file)

def initialize_province_file():
    with open("provinces.json", "w") as file:
        json.dump([], file)

def create_cities_and_capitals():
    global cities, capitals, city_positions_blue, city_positions_red, capital_position_blue, capital_position_red
    
    city_radius = 5
    capital_radius = 10
    
    if not city_positions_blue:
        city_positions_blue = [
            (120, 450), (210, 300), (320, 600), (410, 250), (50, 700), 
            (400, 220), (290, 510), (380, 420), (430, 360), (350, 370)
        ]
        city_positions_blue += [(500, 500), (600, 550)]
            
    if not city_positions_red:
        city_positions_red = [
            (800, 450), (750, 300), (870, 600), (910, 250), (720, 700), 
            (970, 220), (790, 510), (830, 420), (930, 360), (880, 370)
        ]
        city_positions_red += [(1100, 500), (1200, 550)]
            
    if not capital_position_blue:
        capital_position_blue = (30, 450)
        
    if not capital_position_red:
        capital_position_red = (1170, 450)
    
    cities = [
        {"x": pos[0], "y": pos[1], "radius": city_radius, "owner": "blue"} 
        for pos in city_positions_blue
    ]
    cities += [
        {"x": pos[0], "y": pos[1], "radius": city_radius, "owner": "red"} 
        for pos in city_positions_red
    ]
    capitals = [
        {"x": capital_position_blue[0], "y": capital_position_blue[1], "radius": capital_radius, "owner": "blue"}
    ]
    capitals.append(
        {"x": capital_position_red[0], "y": capital_position_red[1], "radius": capital_radius, "owner": "red"}
    )
create_cities_and_capitals()

def draw_cities_and_capitals():
    for city in cities:
        pygame.draw.circle(screen, YELLOW, (city["x"], city["y"]), city["radius"])
    for capital in capitals:
        pygame.draw.circle(screen, YELLOW, (capital["x"], capital["y"]), capital["radius"])

def change_square_owner(x, y, new_owner):
    square_x = x // square_size
    square_y = y // square_size
    if 0 <= square_x < len(squares[0]) and 0 <= square_y < len(squares):
        squares[square_y][square_x]["owner"] = new_owner

def draw_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    title_text = font.render("Strategy Game", True, BLACK)

    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 74)
    quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 74)

    mouse_pos = pygame.mouse.get_pos()

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
    draw_button("Start Game", start_button_rect, mouse_pos)
    draw_button("Quit", quit_button_rect, mouse_pos)

def draw_level_selector():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    title_text = font.render("Select Level", True, BLACK)

    level1_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 74)
    level2_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 74)
    back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 74)

    mouse_pos = pygame.mouse.get_pos()

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
    draw_button("Level 1", level1_button_rect, mouse_pos)
    draw_button("Level 2", level2_button_rect, mouse_pos)
    draw_button("Back", back_button_rect, mouse_pos)

def draw_button(text, rect, mouse_pos, action=None):
    color = LIGHT_GREY if rect.collidepoint(mouse_pos) else GREY
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + (rect.height - text_surf.get_height()) // 2))
    if rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
        if action:
            action()

class ProgressBar:
    def __init__(self, x, y, width, height, progress=0, on_complete=None, window_x=0, window_y=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = progress
        self.last_update_time = time.time()
        self.on_complete = on_complete
        self.completed = False
        self.window_x = window_x
        self.window_y = window_y

    def increment_progress(self, amount):
        self.progress = min(self.progress + amount, 100)

    def update(self, speed_multiplier, paused):
        if paused or self.completed:
            return
        current_time = time.time()
        if current_time - self.last_update_time >= 1 / speed_multiplier:
            self.increment_progress(1)
            self.last_update_time = current_time
            if self.progress >= 100:
                self.completed = True
                if self.on_complete:
                    self.on_complete(self)

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 150, 150), self.rect)
        inner_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width * (self.progress / 100), self.rect.height)
        pygame.draw.rect(screen, GREEN, inner_rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

    def to_dict(self):
        return {
            "x": self.rect.x - self.window_x,
            "y": self.rect.y - self.window_y,
            "width": self.rect.width,
            "height": self.rect.height,
            "progress": self.progress
        }

class DraggableWindow:
    def __init__(self, x, y, width, height, button_label, button_action):
        global current_open_window
        if current_open_window:
            current_open_window.visible = False

        self.rect = pygame.Rect(x, y, width, height)
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.close_button_rect = pygame.Rect(self.rect.right - 30, self.rect.y, 30, 30)
        self.button_label = button_label
        self.button_action = button_action
        self.visible = True
        self.progress_bars = []

        if button_label == "Add Progress":
            self.load_progress_bars()

        current_open_window = self

    def load_progress_bars(self):
        global progress_values
        global global_progress_bars
        self.progress_bars = [
            ProgressBar(bar["x"] + self.rect.x, bar["y"] + self.rect.y, bar["width"], bar["height"], bar["progress"],
                        on_complete=self.complete_progress_bar, window_x=self.rect.x, window_y=self.rect.y)
            for bar in progress_values
        ]
        global_progress_bars = self.progress_bars

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    if self.close_button_rect.collidepoint(event.pos):
                        self.visible = False
                        return 'close'
                    elif event.pos[1] < self.rect.y + 30:
                        self.dragging = True
                        self.drag_offset_x = event.pos[0] - self.rect.x
                        self.drag_offset_y = event.pos[1] - self.rect.y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = event.pos[0] - self.drag_offset_x
                new_y = event.pos[1] - self.drag_offset_y
                dx = new_x - self.rect.x
                dy = new_y
                self.rect.x = new_x
                self.rect.y = new_y
                self.close_button_rect.topleft = (self.rect.right - 30, self.rect.y)

                for bar in self.progress_bars:
                    bar.rect.x += dx
                    bar.rect.y += dy
                    bar.window_x = self.rect.x
                    bar.window_y = self.rect.y

    def update(self, speed_multiplier, paused):
        if self.visible:
            for bar in self.progress_bars:
                bar.update(speed_multiplier, paused)
            self.progress_bars = [bar for bar in self.progress_bars if not bar.completed]
            self.adjust_progress_bar_positions()

    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), (self.rect.x, self.rect.y, self.rect.width, 30))
        pygame.draw.rect(screen, RED, self.close_button_rect)
        pygame.draw.line(screen, WHITE, 
                         (self.close_button_rect.left + 5, self.close_button_rect.top + 5), 
                         (self.close_button_rect.right - 5, self.close_button_rect.bottom - 5), 2)
        pygame.draw.line(screen, WHITE, 
                         (self.close_button_rect.right - 5, self.close_button_rect.top + 5), 
                         (self.close_button_rect.left + 5, self.close_button_rect.bottom - 5), 2)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        self.draw_button(screen)

        if self.button_label == "Add Progress":
            for bar in self.progress_bars:
                bar.draw(screen)

    def draw_button(self, screen):
        global button_clicked
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        button_rect = pygame.Rect(self.rect.x + 50, self.rect.y + 50, 100, 50)

        if button_rect.collidepoint(mouse):
            pygame.draw.rect(screen, (100, 100, 100), button_rect)
            if click[0] == 1:
                if not button_clicked:
                    button_clicked = True
                    if callable(self.button_action):
                        self.button_action()
        else:
            pygame.draw.rect(screen, (200, 200, 200), button_rect)

        if click[0] == 0:
            button_clicked = False

        text_surf = font.render(self.button_label, True, BLACK)
        text_rect = text_surf.get_rect(center=(button_rect.x + 50, button_rect.y + 25))
        screen.blit(text_surf, text_rect)

    def add_progress_bar(self, progress=0):
        if len(self.progress_bars) < 9:
            new_y = self.rect.y + 120 + len(self.progress_bars) * 30
            new_bar = ProgressBar(self.rect.x + 50, new_y, 400, 20, progress, on_complete=self.complete_progress_bar,
                                  window_x=self.rect.x, window_y=self.rect.y)
            self.progress_bars.append(new_bar)
            global_progress_bars.append(new_bar)
            global progress_values
            progress_values = [bar.to_dict() for bar in global_progress_bars]
            save_progress(progress_values)

    def complete_progress_bar(self, bar):
        print("Progress complete")
        if bar in self.progress_bars:
            self.progress_bars.remove(bar)
        if bar in global_progress_bars:
            global_progress_bars.remove(bar)
        global progress_values
        progress_values = [bar.to_dict() for bar in global_progress_bars]
        save_progress(progress_values)
        self.adjust_progress_bar_positions()

    def adjust_progress_bar_positions(self):
        for index, bar in enumerate(self.progress_bars):
            new_y = self.rect.y + 120 + index * 30
            bar.rect.y = new_y
            bar.window_y = self.rect.y

class TwoButtonWindow(DraggableWindow):
    def __init__(self, x, y, width, height, button1_label, button1_action, button2_label, button2_action):
        super().__init__(x, y, width, height, button1_label, button1_action)
        self.button2_label = button2_label
        self.button2_action = button2_action

    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), (self.rect.x, self.rect.y, self.rect.width, 30))
        pygame.draw.rect(screen, RED, self.close_button_rect)
        pygame.draw.line(screen, WHITE,
                         (self.close_button_rect.left + 5, self.close_button_rect.top + 5),
                         (self.close_button_rect.right - 5, self.close_button_rect.bottom - 5), 2)
        pygame.draw.line(screen, WHITE,
                         (self.close_button_rect.right - 5, self.close_button_rect.top + 5),
                         (self.close_button_rect.left + 5, self.close_button_rect.bottom - 5), 2)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        self.draw_button(screen, 50, self.button_label, self.button_action)
        self.draw_button(screen, 110, self.button2_label, self.button2_action)

        for bar in self.progress_bars:
            bar.draw(screen)

    def draw_button(self, screen, y_offset, label, action):
        global button_clicked
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        button_rect = pygame.Rect(self.rect.x + 50, self.rect.y + y_offset, 100, 50)

        if button_rect.collidepoint(mouse):
            pygame.draw.rect(screen, (100, 100, 100), button_rect)
            if click[0] == 1:
                if not button_clicked:
                    button_clicked = True
                    if callable(action):
                        action()
        else:
            pygame.draw.rect(screen, (200, 200, 200), button_rect)

        if click[0] == 0:
            button_clicked = False

        text_surf = font.render(label, True, BLACK)
        text_rect = text_surf.get_rect(center=(button_rect.x + 50, button_rect.y + 25))
        screen.blit(text_surf, text_rect)

class PauseMenu:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.buttons = []
        self.create_buttons()
        self.button_clicked = False

    def create_buttons(self):
        labels = ["Resume", "Option 2", "Option 3", "Option 4", "Quit"]
        actions = [self.resume_game, None, None, None, self.quit_game]
        y_offset = 20
        for label, action in zip(labels, actions):
            self.buttons.append((label, action, y_offset))
            y_offset += 60

    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        for label, action, y_offset in self.buttons:
            self.draw_button(screen, y_offset, label, action)

    def draw_button(self, screen, y_offset, label, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        button_rect = pygame.Rect(self.rect.x + (self.rect.width - 200) // 2, self.rect.y + y_offset, 200, 50)

        if button_rect.collidepoint(mouse):
            pygame.draw.rect(screen, (200, 200, 200), button_rect)
            if click[0] == 1 and not self.button_clicked:
                self.button_clicked = True
                if callable(action):
                    action()
        else:
            pygame.draw.rect(screen, WHITE, button_rect)

        if click[0] == 0:
            self.button_clicked = False

        text_surf = small_text.render(label, True, BLACK)
        text_rect = text_surf.get_rect(center=(button_rect.x + 100, button_rect.y + 25))
        screen.blit(text_surf, text_rect)

    def resume_game(self):
        global game_paused
        self.visible = False
        game_paused = False

    def quit_game(self):
        pygame.quit()
        sys.exit()

def open_law_window():
    TwoButtonWindow(200, 150, 500, 400, "Action 1", lambda: print("Action 1 clicked!"), "Action 2", lambda: print("Action 2 clicked!"))

def start_progress():
    if window.can_afford_resources():
        window.reduce_resources()
        window.add_progress_bar()

def draw_clock_and_controls(screen, current_time, speed_index):
    global clock_rect, minus_rect, plus_rect, pause_button_rect, game_paused
    
    font = pygame.font.Font(None, 36)
    clock_rect = pygame.Rect(screen.get_width() - 250, 10, 240, 100)
    minus_rect = pygame.Rect(clock_rect.x + 10, clock_rect.y + 10, 30, 30)
    plus_rect = pygame.Rect(clock_rect.right - 40, clock_rect.y + 10, 30, 30)
    speed_bar_rect = pygame.Rect(clock_rect.x + 10, clock_rect.bottom - 30, 220, 20)
    pause_button_rect = pygame.Rect(clock_rect.right - 70, clock_rect.y + 10, 30, 30)
    
    pygame.draw.rect(screen, GREY, clock_rect)
    pygame.draw.rect(screen, BLACK, clock_rect, 2)

    pygame.draw.rect(screen, WHITE, minus_rect)
    pygame.draw.rect(screen, WHITE, plus_rect)
    pygame.draw.rect(screen, WHITE, pause_button_rect)
    
    screen.blit(font.render("-", True, BLACK), (minus_rect.x + 8, minus_rect.y + 2))
    screen.blit(font.render("+", True, BLACK), (plus_rect.x + 8, plus_rect.y + 2))
    screen.blit(font.render("||" if not game_paused else ">", True, BLACK), (pause_button_rect.x + 4, pause_button_rect.y + 2))

    time_control_text = font.render("Time", True, BLACK)
    screen.blit(time_control_text, (minus_rect.right + 10, minus_rect.y + 2))

    time_text = current_time.strftime("%H:%M %d %m %Y")
    time_surf = font.render(time_text, True, BLACK)
    screen.blit(time_surf, (clock_rect.x + (clock_rect.width - time_surf.get_width()) // 2, clock_rect.y + 50))
    
    for i in range(4):
        segment_rect = pygame.Rect(speed_bar_rect.x + i * 55, speed_bar_rect.y, 55, 20)
        if i < speed_index:
            color = RED if i == 3 else GREEN
            pygame.draw.rect(screen, color, segment_rect)
        else:
            pygame.draw.rect(screen, BLACK, segment_rect)

def handle_clock_controls(event):
    global speed_index, game_paused, button_clicked, show_province_borders

    if event.type == pygame.MOUSEBUTTONDOWN:
        if not button_clicked:
            mouse_x, mouse_y = event.pos
            if minus_rect.collidepoint(mouse_x, mouse_y):
                speed_index = max(0, speed_index - 1)
                button_clicked = True
            elif plus_rect.collidepoint(mouse_x, mouse_y):
                speed_index = min(3, speed_index + 1)
                button_clicked = True
            elif pause_button_rect.collidepoint(mouse_x, mouse_y):
                game_paused = not game_paused
                button_clicked = True

    if event.type == pygame.MOUSEBUTTONUP:
        button_clicked = False

def open_window_production():
    TwoButtonWindow(200, 150, 500, 400, "Action 1", lambda: print("Action 1 clicked!"), "Action 2", lambda: print("Action 2 clicked!"))

def open_window_politics():
    TwoButtonWindow(200, 150, 500, 400, "Action 1", lambda: print("Action 1 clicked!"), "Action 2", lambda: print("Action 2 clicked!"))

def open_pause_menu():
    global pause_menu
    pause_menu.visible = True
    global game_paused
    game_paused = True
    
def open_single_button_window():
    global current_open_window
    if current_open_window:
        if current_open_window in draggable_windows:
            current_open_window.visible = False
            draggable_windows.remove(current_open_window)
    new_window = DraggableWindow(100, 100, 500, 400, "Add Progress", lambda: new_window.add_progress_bar())
    current_open_window = new_window
    draggable_windows.append(new_window)
    
def create_menu_bar_buttons():
    global menu_bar_buttons
    x_start = 70
    y_position = SCREEN_HEIGHT - 90
    button_width = 50
    button_height = 40
    spacing = 20

    menu_bar_buttons = []
    for i in range(5):
        button_rect = pygame.Rect(x_start + i * (button_width + spacing), y_position, button_width, button_height)
        menu_bar_buttons.append(button_rect)

def draw_arrow_button(screen):
    color = LIGHT_GREY if arrow_button_rect.collidepoint(pygame.mouse.get_pos()) else GREY
    pygame.draw.rect(screen, color, arrow_button_rect)
    pygame.draw.rect(screen, BLACK, arrow_button_rect, 2)
    pygame.draw.polygon(screen, BLACK, [
        (arrow_button_rect.centerx - 10, arrow_button_rect.centery + 5),
        (arrow_button_rect.centerx + 10, arrow_button_rect.centery + 5),
        (arrow_button_rect.centerx, arrow_button_rect.centery - 5)
    ])

def draw_close_button(screen):
    color = LIGHT_GREY if close_button_rect.collidepoint(pygame.mouse.get_pos()) else GREY
    pygame.draw.rect(screen, color, close_button_rect)
    pygame.draw.rect(screen, BLACK, close_button_rect, 2)
    pygame.draw.polygon(screen, BLACK, [
        (close_button_rect.centerx - 10, close_button_rect.centery - 5),
        (close_button_rect.centerx + 10, close_button_rect.centery - 5),
        (close_button_rect.centerx, close_button_rect.centery + 5)
    ])

def draw_menu_bar(screen):
    pygame.draw.rect(screen, DARK_GREY, pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
    draw_close_button(screen)
    for button_rect in menu_bar_buttons:
        color = LIGHT_GREY if button_rect.collidepoint(pygame.mouse.get_pos()) else GREY
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)

def handle_arrow_button_click():
    global menu_bar_visible
    if arrow_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        menu_bar_visible = not menu_bar_visible

def handle_close_button_click():
    global menu_bar_visible
    if close_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        menu_bar_visible = False

def handle_menu_bar_buttons():
    for button_rect in menu_bar_buttons:
        if button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            print(f"Button at {button_rect.topleft} clicked")
            
def create_squares():
    global squares
    province_map = {}
    for province in provinces:
        for square in province["squares"]:
            x, y = square["x"], square["y"]
            province_map[(x, y)] = province

    squares = []
    for y in range(0, SCREEN_HEIGHT, square_size):
        row = []
        for x in range(0, SCREEN_WIDTH, square_size):
            square_key = (x // square_size, y // square_size)
            province = province_map.get(square_key)
            if province:
                owner = province["owner"]
            else:
                owner = "blue" if x < SCREEN_WIDTH // 2 else "red"
            square = {"rect": pygame.Rect(x, y, square_size, square_size), "owner": owner, "province": province}
            row.append(square)
        squares.append(row)
    print("Grid created with squares populated from provinces.")

def draw_squares():
    for row in squares:
        for square in row:
            color = BLUE if square["owner"] == "blue" else RED
            pygame.draw.rect(screen, color, square["rect"])

def draw_frontline():
    frontline = []
    for y in range(len(squares)):
        for x in range(len(squares[y])):
            if squares[y][x]["owner"] is not None:
                if x < len(squares[y]) - 1 and squares[y][x]["owner"] != squares[y][x + 1]["owner"]:
                    if squares[y][x + 1]["owner"] is not None:
                        pygame.draw.line(screen, BLACK, (squares[y][x]["rect"].right, squares[y][x]["rect"].top), (squares[y][x]["rect"].right, squares[y][x]["rect"].bottom), 5)
                        frontline.append(((squares[y][x]["rect"].right, squares[y][x]["rect"].top), (squares[y][x]["rect"].right, squares[y][x]["rect"].bottom)))
                if y < len(squares) - 1 and squares[y][x]["owner"] != squares[y + 1][x]["owner"]:
                    if squares[y + 1][x]["owner"] is not None:
                        pygame.draw.line(screen, BLACK, (squares[y][x]["rect"].left, squares[y][x]["rect"].bottom), (squares[y][x]["rect"].right, squares[y][x]["rect"].bottom), 5)
                        frontline.append(((squares[y][x]["rect"].left, squares[y][x]["rect"].bottom), (squares[y][x]["rect"].right, squares[y][x]["rect"].bottom)))
    return frontline

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = BLACK
        self.radius = 10
        self.speed = 2
        self.attack = random.uniform(8, 12)
        self.defense = random.uniform(8, 12)

    def move_towards_frontline(self, frontline):
        closest_point = self.get_closest_point_on_line(frontline)
        if closest_point is None:
            return

        direction_x, direction_y = closest_point[0] - self.x, closest_point[1] - self.y
        distance = math.hypot(direction_x, direction_y)

        if distance == 0:
            return

        if distance < MIN_DISTANCE:
            self.x -= direction_x * (MIN_DISTANCE - distance) / distance
            self.y -= direction_y * (MIN_DISTANCE - distance) / distance
        else:
            direction_x, direction_y = direction_x / distance, direction_y / distance
            self.x += direction_x * self.speed
            self.y += direction_y * self.speed

    def get_closest_point_on_line(self, line):
        closest_point = None
        min_distance = float('inf')

        for segment in line:
            for point in segment:
                distance = math.hypot(self.x - point[0], self.y - point[1])
                if distance < min_distance:
                    min_distance = distance
                    closest_point = point

        return closest_point

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def spawn_balls(num_balls, region):
    balls = []
    spacing = SCREEN_HEIGHT // num_balls
    for i in range(num_balls):
        y = spacing * i + spacing // 2
        if region == "left":
            x = random.randint(0, SCREEN_WIDTH // 2 - 1)
        elif region == "right":
            x = random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH)
        balls.append(Ball(x, y))
    return balls

def calculate_combined_attack(balls, frontline):
    combined_attack = 0
    for ball in balls:
        closest_point = ball.get_closest_point_on_line(frontline)
        if closest_point is None:
            continue

        distance = math.hypot(ball.x - closest_point[0], ball.y - closest_point[1])
        if distance < 60:
            combined_attack += ball.attack
    return combined_attack

def identify_strips():
    strip_1, strip_2, strip_3 = [], [], []

    for y in range(len(squares)):
        for x in range(len(squares[y])):
            if squares[y][x]["owner"] is not None:
                if x < len(squares[y]) - 1 and squares[y][x]["owner"] != squares[y][x + 1]["owner"]:
                    if squares[y][x + 1]["owner"] is not None:
                        strip_1.append((y, x))
                        if x + 1 < len(squares[y]) - 1:
                            strip_2.append((y, x + 1))
                            if x + 2 < len(squares[y]) - 1:
                                strip_3.append((y, x + 2))
                if y < len(squares) - 1 and squares[y][x]["owner"] != squares[y + 1][x]["owner"]:
                    if squares[y + 1][x]["owner"] is not None:
                        strip_1.append((y, x))
                        if y + 1 < len(squares) - 1:
                            strip_2.append((y + 1, x))
                            if y + 2 < len(squares) - 1:
                                strip_3.append((y + 2, x))
                if x > 0 and squares[y][x]["owner"] != squares[y][x - 1]["owner"]:
                    if squares[y][x - 1]["owner"] is not None:
                        strip_1.append((y, x))
                        if x - 1 > 0:
                            strip_2.append((y, x - 1))
                            if x - 2 > 0:
                                strip_3.append((y, x - 2))
                if y > 0 and squares[y][x]["owner"] != squares[y - 1][x]["owner"]:
                    if squares[y - 1][x]["owner"] is not None:
                        strip_1.append((y, x))
                        if y - 1 > 0:
                            strip_2.append((y - 1, x))
                            if y - 2 > 0:
                                strip_3.append((y - 2, x))

    return strip_1, strip_2, strip_3

def shift_frontline(combined_attack_red, combined_attack_blue):
    global last_shift_time, squares

    if not at_war:
        return

    current_time = time.time()
    if current_time - last_shift_time >= SHIFT_INTERVAL:
        strip_1, strip_2, strip_3 = identify_strips()
        
        if combined_attack_blue > combined_attack_red:
            target_strip = strip_1 if strip_1 else (strip_2 if strip_2 else strip_3)
        else:
            target_strip = strip_1 if strip_1 else (strip_2 if strip_2 else strip_3)

        if not target_strip:
            return

        new_squares = [row[:] for row in squares]  # Create a copy of current squares

        max_changes = 60  # Maximum number of squares to change per interval
        changes_made = 0
        random.shuffle(target_strip)

        for y, x in target_strip:
            if changes_made >= max_changes:
                break
            if combined_attack_blue > combined_attack_red and squares[y][x]["owner"] == "red":
                new_squares[y][x]["owner"] = "blue"
                changes_made += 1
            elif combined_attack_red > combined_attack_blue and squares[y][x]["owner"] == "blue":
                new_squares[y][x]["owner"] = "red"
                changes_made += 1

        squares[:] = new_squares
        last_shift_time = current_time

def draw_province_borders():
    for y in range(len(squares)):
        for x in range(len(squares[y])):
            if x < len(squares[y]) - 1 and squares[y][x]["province"] != squares[y][x + 1]["province"]:
                pygame.draw.line(screen, BLACK, (squares[y][x]["rect"].right, squares[y][x]["rect"].top), 
                                 (squares[y][x]["rect"].right, squares[y][x]["rect"].bottom), 1)
            if y < len(squares) - 1 and squares[y][x]["province"] != squares[y + 1][x]["province"]:
                pygame.draw.line(screen, BLACK, (squares[y][x]["rect"].left, squares[y][x]["rect"].bottom), 
                                 (squares[y][x]["rect"].right, squares[y][x]["rect"].bottom), 1)

def load_province_data():
    global provinces
    try:
        for filename in os.listdir(province_dir):
            if filename.endswith('.json'):
                with open(os.path.join(province_dir, filename), 'r') as f:
                    province_data = json.load(f)
                    provinces.append(province_data)
                    print(f"Loaded province: {filename} with {len(province_data['squares'])} squares.")
        print(f"Loaded {len(provinces)} provinces in total.")
    except FileNotFoundError:
        print(f"Directory {province_dir} not found. Ensure the directory path is correct.")
    except json.JSONDecodeError:
        print("Error decoding JSON from a province file.")

last_shift_time = time.time()
close_button_rect = pygame.Rect(10, SCREEN_HEIGHT - 90, 40, 40)
arrow_button_rect = pygame.Rect(570, SCREEN_HEIGHT - 50, 60, 40)
clock_rect = pygame.Rect(0, 0, 0, 0)
minus_rect = pygame.Rect(0, 0, 0, 0)
plus_rect = pygame.Rect(0, 0, 0, 0)
pause_button_rect = pygame.Rect(0, 0, 0, 0)
toggle_borders_button_rect = pygame.Rect(10, 70, 200, 50)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Strategy Game")
province_dir = 'dots of war/provinces'
selected_squares = set()
current_time = datetime.now()
last_time_update = time.time()
small_text = pygame.font.Font("freesansbold.ttf", 20)
pause_menu = PauseMenu((SCREEN_WIDTH - 400) // 2, (SCREEN_HEIGHT - 500) // 2, 400, 500)
last_save_time = time.time()
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

create_cities_and_capitals()
create_menu_bar_buttons()
load_province_data()
create_squares()

def draw_map():
    screen.fill(WHITE)
    draw_squares()
    draw_frontline()  # Pass the screen argument here
    draw_cities_and_capitals()
    if show_province_borders:
            draw_province_borders()

def draw_ui():
    draw_clock_and_controls(screen, current_time, speed_index + 1)
    draw_button("mobilize", pygame.Rect(70, 50, 100, 50), pygame.mouse.get_pos(), open_single_button_window)
    draw_button("laws", pygame.Rect(70, 120, 100, 50), pygame.mouse.get_pos(), open_law_window)
    draw_button("politics", pygame.Rect(70, 190, 100, 50), pygame.mouse.get_pos(), open_window_politics)
    draw_button("production", pygame.Rect(70, 260, 100, 50), pygame.mouse.get_pos(), open_window_production)
    draw_button("Pause", pygame.Rect(10, 10, 50, 50), pygame.mouse.get_pos(), open_pause_menu)
    if pause_menu.visible:
        pause_menu.draw(screen)
    if current_open_window:
        current_open_window.update(clock_speed[speed_index], game_paused)
        current_open_window.draw(screen)
    draw_arrow_button(screen)
    handle_arrow_button_click()
    if menu_bar_visible:
        draw_menu_bar(screen)
        handle_close_button_click()
        handle_menu_bar_buttons()

red_balls = spawn_balls(15, "right")
blue_balls = spawn_balls(BLUE_BALLS_AMOUNT, "left")
 
running = True
while running:
    now = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                at_war = not at_war
        handle_clock_controls(event)
        if current_open_window:
            current_open_window.handle_event(event)
        for window in draggable_windows[:]:
            result = window.handle_event(event)
            if result == 'close':
                draggable_windows.remove(window)
        if current_screen == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 74).collidepoint(mouse_x, mouse_y):
                    current_screen = "level_selector"
                elif pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 74).collidepoint(mouse_x, mouse_y):
                    running = False
        elif current_screen == "level_selector":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 74).collidepoint(mouse_x, mouse_y):
                    selected_level = 1
                    create_cities_and_capitals()
                    current_screen = "game"
                elif pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 74).collidepoint(mouse_x, mouse_y):
                    selected_level = 2
                    create_squares()
                    create_cities_and_capitals()
                    current_screen = "game"
                elif pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 74).collidepoint(mouse_x, mouse_y):
                    current_screen = "menu"
        elif current_screen == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    selected_team = "blue"
                elif event.key == pygame.K_r:
                    selected_team = "red"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if selected_team:
                    x, y = event.pos
                    change_square_owner(x, y, selected_team)
                    selected_team = None

    elapsed_time = now - last_time_update
    if not game_paused and elapsed_time >= 1 / clock_speed[speed_index]:
        current_time += timedelta(seconds=elapsed_time * 60 * clock_speed[speed_index])
        last_time_update = now

    if now - last_save_time >= 1:
        last_save_time = now
        progress_values = [bar.to_dict() for bar in global_progress_bars]
        save_progress(progress_values)
    for bar in global_progress_bars:
        bar.update(clock_speed[speed_index], game_paused)

    screen.fill((255, 255, 255))  # Clear screen with white color

    if current_screen == "menu":
        draw_menu()
    elif current_screen == "level_selector":
        draw_level_selector()
    elif current_screen == "game":
        draw_map()
        frontline = draw_frontline()
        for ball in red_balls + blue_balls:
            ball.move_towards_frontline(frontline)
            ball.draw(screen)
        draw_ui()
        combined_attack_red = calculate_combined_attack(red_balls, frontline)
        combined_attack_blue = calculate_combined_attack(blue_balls, frontline)

        shift_frontline(combined_attack_red, combined_attack_blue)
        

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()









"""the things I need you to do:
1. reduce lags so that is runs 30 FPS properly
2. add "attack arrows" like seen in this video https://www.youtube.com/watch?v=2OR9IdAUiFQ
3. make the game revolve more around tactics and less around army szie 
4. add the ability to spawn balls after the game started
5. also add, if possible, a whole controll system for future artificial intelligence
thanks"""