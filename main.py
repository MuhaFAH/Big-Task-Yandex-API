import os
import pygame
import requests
import sys


class MAP:
    def __init__(self, position):
        self.name = "map.png"
        self.pos = position
        self.spn = 0.01
        self.diff = 1.5
        self.response = None

    def update(self, diff):
        self.spn = self.spn / self.diff if diff == -1 else self.spn * self.diff
        self.spn = 40 if self.spn >= 40 else round(self.spn, 3)
        print(self.spn)
        map_request1 = f'https://geocode-maps.yandex.ru/1.x/'
        params = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'geocode': f'{self.pos}',
            'format': 'json'
        }
        lon, lat = map(str, requests.get(map_request1,
                                         params=params).json()[
            "response"][
            "GeoObjectCollection"][
            "featureMember"][0][
            "GeoObject"][
            "Point"][
            'pos'].split())
        map_request2 = f"http://static-maps.yandex.ru/1.x/?ll={lon},{lat}&" \
                       f"spn={self.spn},{self.spn}&" \
                       f"l=map&geocode={self.pos}"
        response = requests.get(map_request2)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request2)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.response = response

    def save(self):
        with open(self.name, "wb") as file:
            file.write(self.response.content)


map_resp = MAP(input('Введите адрес: '))
map_resp.update(1)
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
                map_resp.update(+1)
                map_resp.save()
            if event.key == pygame.K_PAGEDOWN:
                map_resp.update(-1)
                map_resp.save()
    screen.fill((0, 0, 0))
    screen.blit(pygame.image.load(map_resp.name), (0, 0))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
os.remove('map.png')
