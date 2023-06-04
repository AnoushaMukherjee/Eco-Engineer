# imports
import pygame
import pygame_widgets
import sys
import random as r
import math
from pygame.locals import *

pygame.init()

# setting up screen
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Transport Game")
FPS = 30

# colors
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
BLUE = (64, 139, 171)
RED = (249, 33, 33)
VIOLET = (138, 43, 226)
FORESTGREEN = (34, 139, 34)
GRAY = (165, 165, 165)
ALICE = (240, 248, 255)
YELLOW = (255, 255, 0)
DARK =  (72, 61, 139)

# variables
clock = pygame.time.Clock()
best_score = 0

# font
pygame.font.init()
font = pygame.font.Font(None, 20)


# random variables
x1, x2, y1, y2, ys, xs = 0, 0, 0, 0, 0, 0
connected = []

def format_money(amount):
    return "$" + str(amount)

# save bus picture
bus_pic = pygame.image.load('bus_pic.png')
bus_pic = pygame.transform.scale(bus_pic, (600, 600))

# nodes
def generate_nodes():
    nodes = {}
    grid_size = 601
    node_spacing = 50
    num_nodes = grid_size // node_spacing

    for i in range(num_nodes + 1):
        for j in range(num_nodes + 1):
            x = i * node_spacing
            y = j * node_spacing

            num_of_people = r.randint(0, 15)
            connections = 0
            nodes[(x, y)] = (i, j, num_of_people)

    return nodes

# Generate the nodes dictionary
nodes_dict = generate_nodes()


# random functions
def in_line(start, end):
    return start[0] == end[0] or start[1] == end[1]


def coord_round(coords):
    x = round(int(coords[0] * 2), -2) // 2
    y = round(int(coords[1] * 2), -2) // 2
    x = x if x > 50 else 50
    x = x if x < 650 else 650
    y = y if y > 50 else 50
    y = y if y < 650 else 650
    return x, y


def draw_city(WIN, additional_lines):
    global total_money
    pygame.draw.line(WIN, BLUE, (0, 600), (600, 600), 100)
    for node_pos, node_data in nodes_dict.items():
        x, y = node_pos
        num_of_people = node_data[2]
        text = pygame.font.SysFont(None, 24).render(
            str(num_of_people), True, VIOLET)
        text_rect = text.get_rect(center=(x + 10, y + 10))
        WIN.blit(text, text_rect)
    pygame.draw.line(WIN, BLUE, (0, 0), (0, 600), 100)
    pygame.draw.line(WIN, BLUE, (0, 0), (600, 0), 100)
    pygame.draw.line(WIN, BLUE, (600, 0), (600, 600), 100)
    for x in range(50, 750, 50):
        pygame.draw.line(WIN, BLACK, (x, 50), (x, 550), 2)
        pygame.draw.line(WIN, BLACK, (50, x), (550, x), 2)

    t = pygame.font.SysFont(None, 24).render(
        format_money(total_money), True, BLACK)
    t_rect = t.get_rect(center=(490, 40))

    WIN.blit(t, t_rect)

    if len(additional_lines) > 0:
        for s in additional_lines:
            x1, y1 = s[0][0], s[0][1]
            x2, y2 = s[1][0], s[1][1]
            pygame.draw.line(WIN, FORESTGREEN, (x1, y1), (x2, y2), 10)

    pygame.draw.circle(WIN, RED, (300, 300), 10)


def dfs(node, visited):
    x, y, num_of_people = node
    visited.add((x, y))
    total_people = num_of_people

    for connected_node in connected:
        if (x, y) in connected_node:
            other_node = connected_node[0] if connected_node[1] == (
                x, y) else connected_node[1]
            if other_node not in visited:
                total_people += dfs(other_node, visited)
    return total_people

def calc_carbon(lines):
    if len(lines) == 0:
        return 0
    tot = 0
    for l in lines:
        distance = (abs(l[0][0] - l[1][0]) + abs(l[0][1] - l[1][1])) / 50
        if distance > 0:
           tot += math.log2(distance)
    return round(tot)

def end_screen(additional_lines, total_money):
    display = True
    while display:
        clock.tick(FPS)
        WIN.fill(GRAY)

        score = calculate_efficacy_score(nodes_dict, total_money, additional_lines)
        score_txt = font.render("Score: " + str(score), True, DARK)
        WIN.blit(bus_pic, (0, 0))
        WIN.blit(score_txt, [WIDTH / 2 - 30, HEIGHT / 2+220])
        carbon = calc_carbon(additional_lines * 100) * 10
        carbon_txt = font.render("Carbon Footprint: " + str(carbon) + " Metric Tonnes per Year", True, DARK)
        WIN.blit(carbon_txt, (160, 550))

        impact1 = "This program helps to spread awareness of your carbon footprint when traveling." 
        impact2 = "In our game, you become a city planner and create a bus route with the goal of "
        impact3 = "releasing the least carbon and transporting the most people."
        impact_txt1 = font.render(impact1, True, DARK)
        impact_txt2 = font.render(impact2, True, DARK)
        impact_txt3 = font.render(impact3, True, DARK)
        WIN.blit(impact_txt1, (55, 30))
        WIN.blit(impact_txt2, (55, 50))
        WIN.blit(impact_txt3, (55, 70))

        # blit bus picture
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main()
            if event.type == pygame.QUIT:
                display = False
    return False

def calculate_people_in_center():
    visited = set()
    total_people = 0

    for nodes in connected:
        # Convert the nodes list to a set to remove duplicates
        nodes = set(nodes)
        for node in nodes:
            total_people += dfs(node, visited)

    return total_people

MAX_CENTER_SCORE = 1000  # Maximum possible center score
# Maximum possible speed score (adjust according to your system)
MAX_SPEED_SCORE = 10

CENTER_WEIGHT = 0.5
BUDGET_WEIGHT = 0.1
SPEED_WEIGHT = 0.2


def calculate_max_people_in_area(nodes_dict):
    max_people = max(node[2] for node in nodes_dict.values())
    return max_people


def calculate_efficacy_score(nodes_dict, money_left, al):
    # 1. Movement to the center
    people_in_center = calculate_people_in_center()
    center_score = people_in_center

    # Normalize the center score between 0 and 100
    normalized_center_score = (center_score / MAX_CENTER_SCORE) * 100

    # 2. Remaining budget
    if total_money==0:
        budget_score = 0
    else:
        budget_score = (money_left / 1000000) * 100

    # 3. Speed of movement
    if len(al) > 0:
        total_distance = 0
        for line in al:
            x1, y1 = line[0]
            x2, y2 = line[1]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            total_distance += distance
        average_distance = total_distance / len(al)
        speed_score = MAX_SPEED_SCORE - \
            (average_distance * (MAX_SPEED_SCORE / 100))
    else:
        speed_score = 0

    # Normalize the speed score between 0 and 100
    normalized_speed_score = (speed_score / MAX_SPEED_SCORE) * 10000

    # Calculate overall efficacy score
    efficacy_score = (normalized_center_score * CENTER_WEIGHT) + (budget_score * BUDGET_WEIGHT) + \
        (normalized_speed_score * SPEED_WEIGHT) + \
        (calculate_max_people_in_area(nodes_dict)*0.2)

    # Scale the efficacy score to make it harder to reach 100
    scaled_score = 100 - (100 - efficacy_score) * 0.2

    # Ensure the efficacy score is within the range of 1 to 100
    efficacy_score = max(min(scaled_score, 100), 1)

    return round(efficacy_score, 2)

def main():
    global total_money
    run = True
    drawing = False
    start_pos = None
    end_pos = None
    down = False
    additional_lines = []
    total_money = 1000000

    while run:
        clock.tick(FPS)
        WIN.fill(WHITE)
        for event in pygame.event.get():
            if total_money < 0:
                total_money = 0
                run = end_screen(additional_lines, total_money)
            if not down and event.type == pygame.MOUSEBUTTONDOWN:
                start_pos = pygame.mouse.get_pos()
                down = True
            if down and event.type == pygame.MOUSEBUTTONUP:
                end_pos = pygame.mouse.get_pos()
                down = False
                x1, y1 = start_pos
                x2, y2 = end_pos
            if event.type == pygame.QUIT:
                run = False
            if event.type == KEYDOWN and event.key == pygame.K_RETURN:
                run = end_screen(additional_lines, total_money)

       
            


        if start_pos and end_pos:
            start_pos = coord_round(start_pos)
            end_pos = coord_round(end_pos)
            if in_line(start_pos, end_pos):
                additional_lines.append((start_pos, end_pos))
                total_money = round(
                    total_money - math.sqrt((x2 - x1) ** 2 + (y2 - y1) **2)*500)
                connected.append([
                    nodes_dict[(round(x1, -2), round(y1, -2))],
                    nodes_dict[(round(x2, -2), round(y2, -2))]
                ])
            start_pos, end_pos = None, None

        
        draw_city(WIN, additional_lines)

        score = calculate_efficacy_score(nodes_dict, total_money, additional_lines)
        #print("Efficacy Score:", score)
        
        pygame.display.update()

if __name__ == "__main__":
    main()

pygame.quit()
sys.exit() 