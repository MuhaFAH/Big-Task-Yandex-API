import os
import pygame
import requests
import sys


class MAP:
    def __init__(self, position):
        self.name = "map.png"
        self.pos = position
        self.lon, self.lat = map(float,
                                 requests.get(f'https://geocode-maps.yandex.ru/1.x/',
                                              params={
                                                  'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                                                  'geocode': f'{self.pos}',
                                                  'format': 'json'
                                              }).json()[
                                     "response"][
                                     "GeoObjectCollection"][
                                     "featureMember"][0][
                                     "GeoObject"][
                                     "Point"][
                                     'pos'].split())
        self.type = 'map'
        self.spn = 0.01
        self.diff = 1.5
        self.response = None

    def update(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.lon},{self.lat}&" \
                       f"spn={self.spn},{self.spn}&" \
                       f"l={self.type}&geocode={self.pos}"
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.response = response

    def change_spn(self, diff):
        self.spn = self.spn / self.diff if diff == -1 else self.spn * self.diff
        self.spn = 40 if self.spn >= 40 else round(self.spn, 3)
        self.update()

    def change_lon(self, diff):
        self.lon += diff * 0.1
        self.update()

    def change_lat(self, diff):
        self.lat += diff * 0.1
        self.update()

    def change_type(self):
        types = ['map', 'sat', 'sat,skl']
        self.type = types[(types.index(self.type) + 1) % 3]
        self.update()

    def save(self):
        with open(self.name, "wb") as file:
            file.write(self.response.content)


map_resp = MAP(input('Введите адрес: '))
map_resp.change_spn(1)
map_resp.save()

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
            if event.key == pygame.K_PAGEUP:
                map_resp.change_spn(1)
                map_resp.save()
            if event.key == pygame.K_PAGEDOWN:
                map_resp.change_spn(-1)
                map_resp.save()
            if event.key == pygame.K_UP:
                map_resp.change_lat(1)
                map_resp.save()
            if event.key == pygame.K_DOWN:
                map_resp.change_lat(-1)
                map_resp.save()
            if event.key == pygame.K_RIGHT:
                map_resp.change_lon(1)
                map_resp.save()
            if event.key == pygame.K_LEFT:
                map_resp.change_lon(-1)
                map_resp.save()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                map_resp.change_type()
                map_resp.save()

    screen.fill((0, 0, 0))
    screen.blit(pygame.image.load(map_resp.name), (0, 0))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
os.remove('map.png')
