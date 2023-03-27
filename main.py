import os
import pygame
import pygame_gui
import pygame_textinput
import requests
import sys
import math


LON_STEP, LAT_STEP = 0.02, 0.008
CONVERT_X, CONVERT_Y = 0.0000428, 0.0000428


def lonlat_distance(a, b):
    a = [float(x) for x in a.split(',')] if type(a) == str else a
    b = [float(y) for y in b.split(',')] if type(b) == str else b
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def close_business(coordinates):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": 'организация',
        "lang": 'ru_RU',
        "spn": '0.001,0.001',
        "ll": coordinates,
        "type": "biz"
    }
    response = requests.get(search_api_server, params=search_params)
    try:
        return list(filter(lambda x: lonlat_distance(x['geometry']['coordinates'], map(float, coordinates.split(','))) < 500, response.json()["features"]))[0]
    except IndexError:
        return None


def degeocode(coords):
    request = 'http://geocode-maps.yandex.ru/1.x/'
    params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': f'{coords}',
        'format': 'json'
    }
    response = requests.get(request, params=params)
    if not response:
        print(f"ОШИБКА: {request}")
        print("HTTP-СТАТУС:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    features = response.json()["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def change_loc(location):
    try:
        lon, lat = map(float, requests.get(f'https://geocode-maps.yandex.ru/1.x/',
                                           params={
                                               'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                                               'geocode': f'{location}',
                                               'format': 'json'
                                           }).json()[
            "response"][
            "GeoObjectCollection"][
            "featureMember"][0][
            "GeoObject"][
            "Point"][
            'pos'].split())
        return lon, lat
    except (IndexError, KeyError):
        pass


class MAP:
    def __init__(self, position):
        self.name = 'map.png'
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
        self.point = (self.lon, self.lat)
        address = requests.get('https://geocode-maps.yandex.ru/1.x/',
                               params={'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                                       'geocode': f'{self.lon},{self.lat}',
                                       'format': 'json'}).json()[
            'response'][
            'GeoObjectCollection'][
            'featureMember'][0][
            'GeoObject'][
            'metaDataProperty'][
            'GeocoderMetaData'][
            'text']
        self.business = pygame.font.SysFont('Impact', 19).render(f"1", False, (0, 0, 0))
        self.address = pygame.font.SysFont('Impact', 19).render(f"Адрес: {address}", False, (0, 0, 0))
        self.index = pygame.font.SysFont('Impact', 19).render(f"Индекс: ", False, (255, 0, 0))
        self.show_business = False
        self.show_index = False
        self.zoom = 15

    def move(self, event_list):
        if event_list.key == pygame.K_PAGEUP and self.zoom < 19:
            self.zoom += 1
            update(self)
        elif event_list.key == pygame.K_PAGEDOWN and self.zoom > 2:
            self.zoom -= 1
            update(self)
        elif event_list.key == pygame.K_LEFT:
            self.lon -= LON_STEP * math.pow(2, 13 - self.zoom)
            update(self)
        elif event_list.key == pygame.K_RIGHT:
            self.lon += LON_STEP * math.pow(2, 13 - self.zoom)
            update(self)
        elif event_list.key == pygame.K_UP and self.lat < 85:
            self.lat += LAT_STEP * math.pow(2, 13 - self.zoom)
            update(self)
        elif event_list.key == pygame.K_DOWN and self.lat > -85:
            self.lat -= LAT_STEP * math.pow(2, 13 - self.zoom)
            update(self)
        elif event_list.key == pygame.K_RETURN:
            self.search(change_loc(text.manager.value), mouse=False)
            self.show_business = False
            update(self)
        elif event_list.key == pygame.K_RSHIFT:
            self.change_type()
            update(self)
        if self.lon > 180:
            self.lon -= 360
            update(self)
        if self.lon < -180:
            self.lon += 360
            update(self)

    def recoords(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.lon + dx * CONVERT_X * math.pow(2, 15 - self.zoom)
        ly = self.lat + dy * CONVERT_Y * math.cos(math.radians(self.lat)) * math.pow(2,
                                                                                     15 - self.zoom)
        return lx, ly

    def search(self, pos, mouse=False):
        if pos:
            self.point = self.recoords(pos) if mouse else pos
            address = degeocode(f'{self.point[0]},{self.point[1]}')
            self.address = pygame.font.SysFont('Impact', 19).render(
                f"Адрес: "
                f"{address['metaDataProperty']['GeocoderMetaData']['text'] if address else 'нет'}", False, (0, 0, 0))
            self.index = pygame.font.SysFont('Impact', 19).render(
                f"Индекс: {address['metaDataProperty']['GeocoderMetaData']['Address'].get('postal_code') if address else 'нет'}",
                False, (255, 0, 0))
            if not mouse:
                self.lon, self.lat = self.point[0], self.point[1]
        else:
            self.address = pygame.font.SysFont('Impact', 19).render(
                f"Адрес: НЕ НАЙДЕНО", False, (0, 0, 0))
            self.index = pygame.font.SysFont('Impact', 19).render(
                f"Индекс: НЕ НАЙДЕНО",
                False, (255, 0, 0))

    def search_business(self, pos):
        self.point = self.recoords(pos)
        address = close_business(f'{self.point[0]},{self.point[1]}')
        if address:
            self.point = tuple(address['geometry']['coordinates'])
            self.business = pygame.font.SysFont('Impact', 19).render(
                f"Название: {address['properties']['CompanyMetaData']['name']}", False, (0, 0, 0))
            self.address = pygame.font.SysFont('Impact', 19).render(
                f"Адрес: {address['properties']['CompanyMetaData']['address'] if address else 'нет'}", False, (0, 0, 0))
        else:
            self.business = pygame.font.SysFont('Impact', 19).render(
                f"Название: НЕ НАЙДЕНО", False, (0, 0, 0))
            self.address = pygame.font.SysFont('Impact', 19).render(
                f"Адрес: НЕ НАЙДЕНО", False, (0, 0, 0))

    def change_type(self):
        types = ['map', 'sat', 'sat,skl']
        self.type = types[(types.index(self.type) + 1) % 3]


def update(yan_map: MAP, business=False):
    map_request = 'http://static-maps.yandex.ru/1.x/'
    params = {
        'll': f'{yan_map.lon},{yan_map.lat}',
        'z': yan_map.zoom,
        'l': yan_map.type,
        'pt': f'{yan_map.point[0]},{yan_map.point[1]},pm2grm'
    }
    if business:
        params['pt'] = f'{yan_map.point[0]},{yan_map.point[1]},pm2rdm'
    response = requests.get(map_request, params=params)
    if not response:
        print(f"ОШИБКА: {map_request}")
        print("HTTP-СТАТУС:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    with open('map.png', 'wb') as file:
        file.write(response.content)
    return 'map.png'


try:
    self = MAP(input('Введите адрес: '))
except KeyError:
    self = MAP('Москва')

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((600, 450))
pygame.display.set_caption('Большая задача по Maps API')
text = pygame_textinput.TextInputVisualizer()
manager = pygame_gui.UIManager((600, 450))
button, btn_text, btn_weight, btn_height = [], [['искать', 'сброс', 'индекс']], 100, 50
for i in range(len(btn_text)):
    for j in range(len(btn_text[i])):
        button.append([])
        button[i].append(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((i * btn_weight + 1, (j + 1) * btn_height),
                                      (btn_weight - 2, btn_height - 2)),
            text=btn_text[i][j],
            manager=manager)
        )
running = True
clock = pygame.time.Clock()
update(self)
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            m_pressed = True
            for i in range(len(button)):
                for j in range(len(button[i])):
                    if event.ui_element == button[i][j]:
                        if button[i][j].text == 'искать' and text.manager.value:
                            self.search(change_loc(text.manager.value), mouse=False)
                            self.show_business = False
                            update(self)
                        elif button[i][j].text == 'сброс':
                            self.search(change_loc('Москва'), mouse=False)
                            self.show_business = False
                            update(self)
                            text.manager.value = ''
                        elif button[i][j].text == 'индекс':
                            self.show_index = True if not self.show_index else False
                            update(self)
        elif event.type == pygame.KEYUP:
            self.move(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.search(event.pos, mouse=True)
                self.show_business = False
                update(self)
            if event.button == 3:
                self.search_business(event.pos)
                self.show_business = True
                self.show_index = False
                update(self, business=True)
        manager.process_events(event)
    manager.update(clock.tick(60) / 1000.0)
    text.update(events)
    screen.fill((0, 0, 0))
    screen.blit(pygame.image.load(self.name), (0, 0))
    screen.blit(text.surface, (10, 10))
    screen.blit(self.address, (10, 420))
    if self.show_business:
        screen.blit(self.business, (10, 380))
    if self.show_index:
        screen.blit(self.index, (10, 400))
    manager.draw_ui(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
os.remove('map.png')
