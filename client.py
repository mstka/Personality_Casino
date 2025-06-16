import pygame
import requests
import sys

API_BASE = 'http://localhost:8000'

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Personality Casino')
font = pygame.font.Font(None, 32)

COLOR_BG = pygame.Color('white')
COLOR_TEXT = pygame.Color('black')

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, COLOR_TEXT)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, COLOR_TEXT)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = font.render(text, True, COLOR_TEXT)

    def draw(self, screen):
        pygame.draw.rect(screen, pygame.Color('gray'), self.rect)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

def draw_text(text, x, y):
    surface = font.render(text, True, COLOR_TEXT)
    screen.blit(surface, (x, y))

def login_screen():
    user_box = InputBox(250, 120, 140, 32)
    pass_box = InputBox(250, 170, 140, 32)
    login_btn = Button(250, 220, 80, 32, 'Login')
    reg_btn = Button(340, 220, 80, 32, 'Register')
    message = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            user_box.handle_event(event)
            pass_box.handle_event(event)
            if login_btn.is_clicked(event):
                payload = {'username': user_box.text, 'password': pass_box.text}
                try:
                    r = requests.post(f'{API_BASE}/login', json=payload)
                    if r.status_code == 200:
                        return r.json()['token']
                    else:
                        message = r.json().get('detail', 'login error')
                except Exception as e:
                    message = str(e)
            if reg_btn.is_clicked(event):
                payload = {'username': user_box.text, 'password': pass_box.text}
                try:
                    r = requests.post(f'{API_BASE}/register', json=payload)
                    message = r.json().get('message', r.json().get('detail', 'error'))
                except Exception as e:
                    message = str(e)
        user_box.update(); pass_box.update()
        screen.fill(COLOR_BG)
        draw_text('Username:', 150, 125)
        draw_text('Password:', 150, 175)
        user_box.draw(screen)
        pass_box.draw(screen)
        login_btn.draw(screen)
        reg_btn.draw(screen)
        draw_text(message, 150, 270)
        pygame.display.flip()

def menu_screen(token):
    roulette_btn = Button(220, 120, 200, 40, 'Roulette')
    balance_btn = Button(220, 180, 200, 40, 'Check Balance')
    quit_btn = Button(220, 240, 200, 40, 'Quit')
    message = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if roulette_btn.is_clicked(event):
                roulette_screen(token)
            if balance_btn.is_clicked(event):
                try:
                    r = requests.post(f'{API_BASE}/balance', json={'token': token})
                    if r.status_code == 200:
                        message = f"Coins: {r.json()['coins']}"
                    else:
                        message = r.json().get('detail', 'error')
                except Exception as e:
                    message = str(e)
            if quit_btn.is_clicked(event):
                pygame.quit(); sys.exit()
        screen.fill(COLOR_BG)
        roulette_btn.draw(screen)
        balance_btn.draw(screen)
        quit_btn.draw(screen)
        draw_text(message, 220, 300)
        pygame.display.flip()

def roulette_screen(token):
    type_box = InputBox(250, 100, 140, 32, 'number')
    value_box = InputBox(250, 150, 140, 32)
    amount_box = InputBox(250, 200, 140, 32)
    spin_btn = Button(250, 250, 80, 32, 'Spin')
    back_btn = Button(340, 250, 80, 32, 'Back')
    message = ''
    result_lines = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            type_box.handle_event(event)
            value_box.handle_event(event)
            amount_box.handle_event(event)
            if spin_btn.is_clicked(event):
                try:
                    bet = {
                        'bet_type': type_box.text,
                        'value': value_box.text,
                        'amount': float(amount_box.text or 0),
                        'token': token
                    }
                    r = requests.post(f'{API_BASE}/spin', json=bet)
                    if r.status_code == 200:
                        data = r.json()
                        result_lines = [
                            f"Number: {data['result']['number']}",
                            f"Color: {data['result']['color']}",
                            f"Parity: {data['result']['parity']}",
                            f"Outcome: {data['bet_outcome']}",
                            f"Payout: {data['payout']}",
                            f"Coins: {data['coins']}"
                        ]
                    else:
                        message = r.json().get('detail', 'error')
                except Exception as e:
                    message = str(e)
            if back_btn.is_clicked(event):
                return
        type_box.update(); value_box.update(); amount_box.update()
        screen.fill(COLOR_BG)
        draw_text('Bet Type (number/color/parity):', 20, 105)
        draw_text('Value:', 150, 155)
        draw_text('Amount:', 150, 205)
        type_box.draw(screen)
        value_box.draw(screen)
        amount_box.draw(screen)
        spin_btn.draw(screen)
        back_btn.draw(screen)
        y = 300
        for line in result_lines:
            draw_text(line, 20, y)
            y += 30
        if message:
            draw_text(message, 20, y)
        pygame.display.flip()

def main():
    token = login_screen()
    if token:
        menu_screen(token)

if __name__ == '__main__':
    main()
