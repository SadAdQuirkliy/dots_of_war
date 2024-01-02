import pygame
import sys
import math
import random
import numpy as np
import asyncio
import os
pygame.init()
win_width = 800
win_height = 600
enemy_ball_timer = 0
enemy_balls_spawned = 0
enemy_max_balls = 15
enemy_ball_interval = 2000 
enemy_ball_count = 0 
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("map1.jpg")
background_image_path = r'C:\Users\Marlon\Documents\python\dots_of_war\map1.jpg'
background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (win_width, win_height))

white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 128, 0)

font = pygame.font.Font(None, 36)

def button(x, y, width, height, inactive_color, active_color, click_action, text, text_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(win, active_color, (x, y, width, height))
        if click[0] == 1 and callable(click_action):  # Check if click_action is callable
            click_action()
    else:
        pygame.draw.rect(win, inactive_color, (x, y, width, height))

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
    win.blit(text_surface, text_rect)

def quit_game():
    global phase
    phase = 0

def level_selector():
    global phase
    phase = 2

def Level_one():
    global phase
    global balls
    global ball_active
    global rope
    global gold

    phase = 3.1
    balls = []
    ball_active = []
    gold = 0

def Level_two():
    global phase
    phase = 3.2

def Level_three():
    global phase
    phase = 3.3

def move_rope_segment(rope, index, force):
    if force != (0, 0):
        seg_start = (rope[index][0], rope[index][1])
        seg_end = (rope[index][0] + rope[index][2], rope[index][1] + rope[index][3])

        seg_vector = (seg_end[0] - seg_start[0], seg_end[1] - seg_start[1])
        seg_length = distance(seg_start, seg_end)

        perp_vector = (-seg_vector[1], seg_vector[0])

        perp_length = distance((0, 0), perp_vector)
        if perp_length != 0:
            perp_vector = (perp_vector[0] / perp_length, perp_vector[1] / perp_length)

            rope[index] = (rope[index][0] + force[0], rope[index][1] + force[1], rope[index][2], rope[index][3], rope[index][4])
            rope[index + 1] = (
            rope[index + 1][0] + force[0], rope[index + 1][1] + force[1], rope[index + 1][2], rope[index + 1][3],
            rope[index + 1][4])

            new_seg_vector = (rope[index + 1][0] - rope[index][0], rope[index + 1][1] - rope[index][1])
            new_seg_length = distance((rope[index][0], rope[index][1]), (rope[index + 1][0], rope[index + 1][1]))
            scaling_factor = seg_length / new_seg_length

            rope[index + 1] = (
            rope[index][0] + new_seg_vector[0] * scaling_factor, rope[index][1] + new_seg_vector[1] * scaling_factor,
            rope[index + 1][2], rope[index + 1][3], rope[index + 1][4])


rope = [
    [330, 0, 2, 16, white], [332, 16, 7, 16, white], [339, 32, 4, 16, white], [343, 48, 2, 16, white],
    [345, 64, 5, 16, white], [350, 80, 0, 0, white],
    [345, 90, 0, 0, white], [345, 110, 2, 10, white], [347, 120, 0, 1, white],
    [347, 121, 0, 1, white], [348, 122, 0, 1, white], [348, 123, 0, 1, white], [348, 124, 0, 1, white],
    [349, 125, 1, 3, white], [350, 128, 0, 0, white],
    [350, 130, 8, 25, white], [358, 155, 4, 10, white], [362, 165, 3, 5, white], [365, 170, 5, 10, white],
    [370, 180, 2, 10, white],
    [372, 190, 0, 0, white], [365, 200, 0, 0, white], [365, 210, 0, 0, white], [365, 220, 5, 10, white],
    [370, 230, 0, 0, white], [370, 240, 0, 0, white], [371, 250, 0, 0, white], [372, 260, 0, 0, white],
    [373, 270, 7, 10, white],
    [380, 280, 9, 10, white], [389, 290, 9, 10, white], [398, 300, 7, 10, white], [405, 310, 10, 5, white],
    [415, 315, 0, 0, white],
    [430, 330, 10, 20, white], [440, 350, 10, 10, white], [450, 360, 0, 0, white], [450, 370, 0, 0, white],
    [450, 380, 0, 0, white], [450, 390, 0, 0, white], [450, 400, 0, 0, white], [450, 410, 0, 0, white],
    [450, 420, 0, 0, white],
    [450, 430, 0, 0, white], [450, 440, 0, 0, white], [450, 450, 0, 0, white], [450, 460, 0, 0, white],
    [450, 470, 0, 0, white], [450, 480, 0, 0, white], [450, 490, 0, 0, white], [450, 500, 0, 0, white],
    [450, 510, 0, 0, white],
    [450, 520, 0, 0, white], [450, 520, 0, 0, white], [450, 530, 0, 0, white], [450, 540, 0, 0, white],
    [450, 550, 0, 0, white], [450, 560, 0, 0, white], [450, 570, 0, 0, white], [450, 580, 0, 0, white],
    [450, 590, 0, 0, white], [450, 600, 0, 0, white]
]
rope_thickness = 5
balls = [
    {"position": [int(x), int(y)], "active": True, "group": 0,
     "attack": random.randint(1, 10), "defense": random.randint(1, 10),
     "speed": random.uniform(0.5, 2.0), "organization": 10}
    for x, y in zip(range(10, win_width - 10, 50), [random.randint(10, win_height - 10) for _ in range(5)])
]
ball_active = [True]  # Flag for each ball to indicate if it's active or stopped

def ball_line_collision(balls, rope, force_multiplier=0.1, damping=0.9, segment_distance=50):
    for ball in balls:
        for i in range(len(rope) - 1):
            line_start = tuple(rope[i][:2])
            line_end = tuple(rope[i + 1][:2])

            d = distance(line_start, line_end)
            if len(ball.get("position", [])) > 1:
                ball_position = ball["position"]
                dist_from_start = distance(line_start, ball_position)
                dist_from_end = distance(line_end, ball_position)
                ball_radius = 10  # Assuming the radius of the ball is 10

                if dist_from_start + dist_from_end - d <= ball_radius:
                    # Collision detected, calculate force based on curvature
                    perp_vector = (-force_multiplier * (line_end[1] - line_start[1]),
                                   force_multiplier * (line_end[0] - line_start[0]))

                    # Gradual change in force based on distance
                    distance_factor = max(0, 1 - (dist_from_start + dist_from_end) / (2 * ball_radius))
                    perp_vector = (perp_vector[0] * distance_factor, perp_vector[1] * distance_factor)

                    # Apply damping to the force
                    perp_vector = (perp_vector[0] * damping, perp_vector[1] * damping)

                    # Move the relevant segments based on the force
                    rope[i] = (rope[i][0] + perp_vector[0], rope[i][1] + perp_vector[1],
                               rope[i][2], rope[i][3], rope[i][4])
                    rope[i + 1] = (rope[i + 1][0] + perp_vector[0], rope[i + 1][1] + perp_vector[1],
                                   rope[i + 1][2], rope[i + 1][3], rope[i + 1][4])

    return False

def is_on_enemy_side(rope, point):
    # Modify this function to check if the point is on the "enemy side" based on your rope's structure
    return point[0] > rope[0][0]       

enemy_ball_timer = 0
enemy_ball_interval = 5000  # 5000 milliseconds = 5 seconds
enemy_balls_spawned = 0
enemy_max_balls = 5

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def generate_smooth_rope(rope_points, num_segments):#
    global gap 
    smooth_rope = []
    for i in range(len(rope_points) - 1):
        p0, p1 = rope_points[i], rope_points[i + 1]
        for t in range(num_segments):
            x = int(p0[0] * (1 - t / num_segments) + p1[0] * (t / num_segments))
            y = int(p0[1] * (1 - t / num_segments) + p1[1] * (t / num_segments))
            smooth_rope = generate_smooth_rope(rope, 100, gap = 10)   
            x = max(gap, min(x, win_width - gap))
            y = max(gap, min(y, win_height - gap))
            smooth_rope.append((x, y))
    return smooth_rope


gold = 0
gold_per_second = 0.5
division_cost = 100
spawn_cooldown = 10

clock = pygame.time.Clock()

def earn_gold():
    global gold
    gold += gold_per_second

def display_gold():
    gold_text = font.render(f"Gold: {int(gold)}", True, black)
    win.blit(gold_text, (10, 10))
    
def draw_line_once(rope):
    for i in range(len(rope) - 1):
        line_start = tuple(rope[i][:2])  # Convert to tuple (x, y)
        line_end = tuple(rope[i + 1][:2])  # Convert to tuple (x, y)
        pygame.draw.line(win, (0, 0, 0), line_start, line_end, 2)



def select_balls():
    global balls, selected_group

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            for i, ball in enumerate(balls):
                if ball["active"] and len(ball.get("position", [])) > 1:
                    ball_x, ball_y = map(int, ball["position"])
                    distance_to_ball = distance((mouse_x, mouse_y), (ball_x, ball_y))

                    if distance_to_ball < 10:  # Assuming the radius of the ball is 10
                        selected_group = ball.get("group", -1)  # Set selected_group to the ball's group
                        return
                    
def spawn_friendly_ball():
    global gold
    global balls
    global ball_active
    global rope
    global spawn_cooldown
    global friendly_ball_count
    global drawing_line
    drawing_line = False
    current_time = pygame.time.get_ticks()

    if gold >= 100 and current_time - spawn_friendly_ball.last_spawn_time > spawn_cooldown:
        x = random.randint(10, int(rope[0][0]) - 10)
        y = random.randint(10, win_height - 10)
        friendly_ball_count += 1
        new_ball = {
            "position": [x, y], 
            "active": True, 
            "group": 0,
            "division_number": friendly_ball_count,  # Assign a unique number
            "attack": random.randint(5, 10), 
            "defense": random.randint(5, 10),
            "speed": random.randint(5, 10), 
            "organization": 100
        }
        new_ball["name"] = f"{new_ball['division_number']}.Infantry Division "  # Add ". Infantry Division" to the name
        balls.append(new_ball)
        ball_active.append(True)
        gold -= 100
        spawn_friendly_ball.last_spawn_time = current_time

# Initialize the last_spawn_time and friendly_ball_count
spawn_friendly_ball.last_spawn_time = 0
friendly_ball_count = 0


# Function to spawn a new enemy ball
def spawn_enemy_ball():
    global balls
    global ball_active
    global enemy_ball_timer
    global enemy_balls_spawned
    global enemy_max_balls
    global enemy_ball_count

    current_time = pygame.time.get_ticks()
    time_since_last_spawn = current_time - enemy_ball_timer

    if time_since_last_spawn >= enemy_ball_interval and enemy_balls_spawned < enemy_max_balls:
        x = random.randint(int(rope[0][0]) + 10, win_width - 10)
        y = random.randint(10, win_height - 10)
        enemy_ball_count += 1
        new_ball = {
            "position": [x, y], 
            "active": True, 
            "group_enemy": 0,
            "division_number": enemy_ball_count,
            "attack": random.randint(5, 10), 
            "defense": random.randint(5, 10),
            "speed": random.randint(5, 10), 
            "organization": 100
        }
        new_ball["name"] = f"{new_ball['division_number']}Enemy Division"  # Add ". Enemy Division" to the name
        balls.append(new_ball)
        ball_active.append(True)
        enemy_balls_spawned += 1
        enemy_ball_timer = current_time
        
def move_balls_right():
    for ball in balls:
        ball['position'][0] = win_width - 20  # Move the balls to the right side

def display_hud(ball):
    hud_font = pygame.font.Font(None, 24)
    if ball["group"] == 0:
        # Display full stats for friendly balls
        hud_text = hud_font.render(
            f"Name: {ball['name']}\nAttack: {ball['attack']}\nDefense: {ball['defense']}\nSpeed: {ball['speed']}\nOrganization: {ball['organization']}",
            True,
            black
        )
    else:
        # Only display division name for enemy balls
        hud_text = hud_font.render(f"Enemy Division {ball['division_number']}", True, black)


    if "group" in ball and ball["group"] == 0:
        pass
    elif "enemy_group" in ball and ball["enemy_group"] == 1:
        pass
    hud_rect = hud_text.get_rect(center=(win_width // 2, win_height - 50))
    win.blit(hud_text, hud_rect)
    
capital_position = (100, 300)  # Adjust the coordinates of your capital as needed
enemy_capital_position = (550, 300)  # Adjust the coordinates of the enemy capital as needed
friendly_city1_position = (122, 456)
friendly_city2_position = (223, 234)
friendly_city3_position = (315, 511)
friendly_city4_position = (206, 100)
friendly_city5_position = (307, 300)
enemy_city1_position = (384, 108)
enemy_city2_position = (491, 95)
enemy_city3_position = (680, 397)
enemy_city4_position = (485, 412)
enemy_city5_position = (671, 210)
def draw_location(position, color, radius):
    pygame.draw.circle(win, color, position, radius)

def on_location_click(position, is_enemy, location_type):
    # Add your desired functionality when a location is clicked
    if is_enemy:
        print(f"Enemy {location_type} at {position} clicked!")
    else:
        print(f"Your {location_type} at {position} clicked!")

def normalize_vector(vector):
    length = distance((0, 0), vector)
    if length != 0:
        return (vector[0] / length, vector[1] / length)
    else:
        return (0, 0)

def calculate_direction(ball_position, closest_point):
    direction = (closest_point[0] - ball_position[0], closest_point[1] - ball_position[1])
    return normalize_vector(direction)

def find_closest_point_on_rope(point, rope):
    closest_point = rope[0][:2]
    min_distance = distance(point, closest_point)
    closest_segment_index = 0

    for i in range(len(rope) - 1):
        segment_start = rope[i][:2]
        segment_end = rope[i + 1][:2]

        # Calculate the closest point on the segment to the given point
        closest_point_on_segment = closest_point_on_line(point, segment_start, segment_end)

        # Calculate the distance between the given point and the closest point on the segment
        distance_to_segment = distance(point, closest_point_on_segment)

        # Update the closest point if the current segment is closer
        if distance_to_segment < min_distance:
            min_distance = distance_to_segment
            closest_point = closest_point_on_segment
            closest_segment_index = i

    return closest_point, closest_segment_index, min_distance

def closest_point_on_line(point, line_start, line_end):
    line_vector = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    point_vector = (point[0] - line_start[0], point[1] - line_start[1])

    line_length = distance(line_start, line_end)

    if line_length == 0:
        # Handle the case where the line has zero length to avoid division by zero
        return line_start

    dot_product = (point_vector[0] * line_vector[0] + point_vector[1] * line_vector[1]) / line_length**2

    dot_product = max(0, min(1, dot_product))

    closest_point = (
        line_start[0] + dot_product * line_vector[0],
        line_start[1] + dot_product * line_vector[1]
    )

    return closest_point

def move_balls_to_rope(balls, rope):
    buffer_distance = 10  # Adjust the buffer distance as needed

    for i in range(len(balls)):
        if balls[i]["active"] and len(balls[i].get("position", [])) > 1:
            ball_position = list(map(int, balls[i]["position"]))

            closest, seg_index, dist = find_closest_point_on_rope(ball_position, rope)

            if dist < buffer_distance:
                direction = (closest[0] - ball_position[0], closest[1] - ball_position[1])
                dist = distance(closest, ball_position)

                if dist != 0:
                    direction = (direction[0] / dist, direction[1] / dist)
                    speed = 2  # Adjust speed as needed

                    # Move the ball away from the rope with the buffer zone
                    new_position = (
                        ball_position[0] - direction[0] * (buffer_distance - dist),
                        ball_position[1] - direction[1] * (buffer_distance - dist)
                    )

                    balls[i]["position"] = new_position

async def run_game():
    global ball_position
    global i,movement_activated
    global phase
    global selected_group 
    global ball
    global current_time
    selected_group = 0
    phase = 0
    running = True
    current_time = pygame.time.get_ticks()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    select_balls() 
          
        win.blit(background_image, (0, 0))

        if phase == 0:
            button(150, 348, 150, 50, blue, red, level_selector, "Play", black)
            button(480, 348, 150, 50, blue, red, quit_game, "Quit", black)

        if phase == 2:
            button(200, 200, 150, 50, blue, red, Level_one, "Level 1", black)
            button(200, 300, 150, 50, blue, red, Level_two, "Level 2", black)
            button(200, 400, 150, 50, blue, red, Level_three, "Level 3", black)

        if phase == 3.1: 
            ball_line_collision(balls, rope, force_multiplier=0.1)  
            button(10, 10, 150, 50, (0, 200, 0), (0, 255, 0), spawn_enemy_ball, "Spawn Enemy", (0, 0, 0))
            move_balls_to_rope
            for _ in range(1):
                draw_line_once(rope)
            i = 0  # Add this line to define 'i'
            for i in range(len(balls)):
                is_enemy_side = is_on_enemy_side(rope, balls[i]["position"])

            line_drawn = True  # Set the variable here to avoid clearing attack_plan in each iteration
            movement_activated = False
            for ball in balls:
                if ball["active"] and len(ball.get("position", [])) > 1:
                    pygame.draw.circle(win, red, (int(ball["position"][0]), int(ball["position"][1])), 10)

                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    ball_x, ball_y = map(int, ball["position"])
                    distance_to_ball = distance((mouse_x, mouse_y), (ball_x, ball_y))

                    if distance_to_ball < 10:  # Assuming the radius of the ball is 10
                        display_hud(ball)
            draw_location(capital_position, (255, 255, 0), 10)  # Your capital in yellow
            draw_location(enemy_capital_position, (255, 0, 0), 10)  # Enemy capital in red
            draw_location(friendly_city1_position, (0, 255, 0), 8)  # Friendly City 1 in green
            draw_location(friendly_city2_position, (0, 255, 0), 8)
            draw_location(friendly_city3_position, (0, 255, 0), 8)
            draw_location(friendly_city4_position, (0, 255, 0), 8)
            draw_location(friendly_city5_position, (0, 255, 0), 8)
            draw_location(enemy_city1_position, (0, 0, 255), 8)  # Enemy City 1 in blue
            draw_location(enemy_city2_position, (0, 0, 255), 8)
            draw_location(enemy_city3_position, (0, 0, 255), 8) 
            draw_location(enemy_city4_position, (0, 0, 255), 8) 
            draw_location(enemy_city5_position, (0, 0, 255), 8)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if not line_drawn:
                draw_line_once(rope)
                line_drawn = True

            if ball_line_collision(balls, rope, force_multiplier=0.1):
                print("Collision detected with balls!")
            # 
            distance_to_capital = distance((mouse_x, mouse_y), capital_position)
            if distance_to_capital < 10:  # Adjust the radius of the capital
                if pygame.mouse.get_pressed()[0]:  # Check if the left mouse button is clicked
                    on_location_click(capital_position, False, "Capital")

            # Check enemy capital
            distance_to_enemy_capital = distance((mouse_x, mouse_y), enemy_capital_position)
            if distance_to_enemy_capital < 10:  # Adjust the radius of the capital
                if pygame.mouse.get_pressed()[0]:  # Check if the left mouse button is clicked
                    on_location_click(enemy_capital_position, True, "Capital")

            # ... (previo
            line_drawn = False
            if not line_drawn:
                draw_line_once(rope)
                line_drawn = True
            earn_gold()
            display_gold()
            button(600, 10, 180, 50, blue, red, spawn_friendly_ball, "Spawn Friendly Ball (100 Gold)", black)
            for i in range(len(rope) - 1):
                for j in range(len(rope) - 1):
                    line_start = rope[j]
                    line_end = rope[j + 1]
            if not isinstance(line_start, (list, tuple)):
                line_start = (0, 0)
            if not isinstance(line_end, (list, tuple)): 
                line_end = (0, 0)
            if len(line_start) != 2 or len(line_end) != 2:
                line_start = (0, 0)
                line_end = (0, 0)
                pygame.draw.line(win, (0, 0, 0), line_start, line_end, 2)
                earn_gold()
                display_gold()
                move_rope_segment(rope, i, (0, 1))
                button(600, 10, 180, 50, blue, red, spawn_friendly_ball, "Spawn Friendly Ball (100 Gold)", black)
            for ball in balls:
                if ball["active"] and len(ball.get("position", [])) > 1:
                    if "group_enemy" in ball and ball["group_enemy"] == 0:
                        pygame.draw.circle(win, red, (int(ball["position"][0]), int(ball["position"][1])), 10)  # enemy ball in red
                    else:
                        pygame.draw.circle(win, blue, (int(ball["position"][0]), int(ball["position"][1])), 10)  # friendly ball in blue
            for i in range(len(balls)):
                if balls[i]["active"] and len(balls[i].get("position", [])) > 1:
                    ball_position = list(map(int, balls[i]["position"]))
                    closest, seg_index, dist = find_closest_point_on_rope(ball_position, rope)
                
                    if is_on_enemy_side(rope, ball_position):
                        direction = calculate_direction(ball_position, closest)
                        speed = 2  # Adjust speed as needed
                        balls[i]["position"][0] += direction[0] * speed
                        balls[i]["position"][1] += direction[1] * speed
                    else:
                        if ball_position[0] < rope[0][0]:
                            direction = calculate_direction(ball_position, closest)
                            speed = 2  # Adjust speed as needed
                            balls[i]["position"][0] += direction[0] * speed
                            balls[i]["position"][1] += direction[1] * speed
# You need to loop through the balls to define 'i'
                if i < len(ball_active) and ball_active[i] and len(balls[i].get("position", [])) > 1:
                    ball_position = list(map(int, balls[i]["position"]))
                    if "group_enemy" in ball and ball["group_enemy"] == 0:
                        pygame.draw.circle(win, red, (int(ball["position"][0]), int(ball["position"][1])), 10)  # enemy ball in red
                    else:
                        pygame.draw.circle(win, blue, (int(ball["position"][0]), int(ball["position"][1])), 10)  # friendly ball in blue
                if 0 <= i < len(ball_active) and ball_active[i] and len(ball.get("position", [])) > 1:
                    ball_position = list(map(int, ball["position"]))
                    for j, other_ball in enumerate(balls):
                        if 0 <= i < len(ball_active) and ball_active[i] and len(ball.get("position", [])) > 1:
                            if "group_enemy" in ball and ball["group_enemy"] == 0:
                                pygame.draw.circle(win, red, (int(ball["position"][0]), int(ball["position"][1])), 10)  # enemy ball in red
                            else:
                                pygame.draw.circle(win, blue, (int(ball["position"][0]), int(ball["position"][1])), 10)  # friendly ball in blue

                is_enemy_side = is_on_enemy_side(rope, balls[i]["position"])
                
            button(600, 10, 180, 50, blue, red, spawn_friendly_ball, "Spawn Friendly Ball (100 Gold)", black)
            for ball in balls:

                    closest, seg_index, dist = (0, 0), 0, 0 
                    if is_on_enemy_side(rope, balls[i]["position"]):
                        direction = (closest[0] - balls[i]["position"][0], closest[1] - balls[i]["position"][1])
                        dist = distance(closest, balls[i]["position"])
                        pass
                        if dist != 0:
                            direction = (direction[0] / dist, direction[1] / dist)
                            speed = 2  # Adjust speed as needed
                    else:
                        if balls[i]["position"][0] < rope[0][0]:
                            direction = (closest[0] - balls[i]["position"][0], closest[1] - balls[i]["position"][1])
                            dist = distance(closest, balls[i]["position"])
                            pass
                            if dist != 0:
                                direction = (direction[0] / dist, direction[1] / dist)
                                speed = 2  # Adjust speed as needed
            for j in range(len(rope) - 1):
                line_start = rope[j]
                line_end = rope[j + 1]
                for j in range(len(rope) - 1):
                    line_start = rope[j]
                    line_end = rope[j + 1]
        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()

asyncio.run(run_game())
sys.exit()