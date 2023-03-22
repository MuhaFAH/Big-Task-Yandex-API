import os
import pygame
import requests

x, y, spn = input('Введите координаты и масштаб (через пробел): ').split()
map_request = f"http://static-maps.yandex.ru/1.x/?ll={x},{y}&spn={spn},0.002&l=map"
resp = requests.get(map_request)
map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(resp.content)
pygame.init()
screen = pygame.display.set_mode((600, 450))
pygame.display.set_caption('Большая задача по Maps API')
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pass
    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
os.remove('map.png')
