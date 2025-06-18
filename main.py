"""Entry point for the Personality Casino application."""
import sys
import pygame
from pygame import Surface

from games import Poker, Blackjack, Chinchiro, Roulette
from engine import (
    init_db,
    log_play,
    fetch_logs,
    calculate_scores,
    classify_business_type,
    generate_radar_chart,
)

WIDTH, HEIGHT = 640, 480
FONT_SIZE = 24


def draw_text(screen: Surface, lines):
    """Render a list of text lines centered on the screen."""
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, FONT_SIZE)
    y = 50
    for line in lines:
        img = font.render(line, True, (255, 255, 255))
        rect = img.get_rect(center=(WIDTH // 2, y))
        screen.blit(img, rect)
        y += FONT_SIZE + 10
    pygame.display.flip()


def get_text_input(screen: Surface, prompt: str) -> str:
    """Return string input from the user via a simple text prompt."""
    font = pygame.font.SysFont(None, FONT_SIZE)
    user_input = ""
    while True:
        screen.fill((0, 0, 0))
        prompt_img = font.render(prompt + user_input, True, (255, 255, 255))
        screen.blit(prompt_img, (50, HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_input
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode


def wait_for_key():
    """Block until the user presses any key or closes the window."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def play_game(screen: Surface, conn, game_name: str):
    """Run a single game round and record the result."""
    if game_name == "Poker":
        game = Poker()
        choice = get_text_input(screen, "Enter any text to start: ")
    elif game_name == "Blackjack":
        game = Blackjack()
        choice = get_text_input(screen, "Action hit/stand: ")
    elif game_name == "Chinchiro":
        game = Chinchiro()
        choice = get_text_input(screen, "Guess even/odd: ")
    else:
        game = Roulette()
        num_str = get_text_input(screen, "Choose number 0-36: ")
        choice = num_str if num_str.isdigit() else "0"

    bet_str = get_text_input(screen, "Bet amount: ")
    try:
        bet = int(bet_str)
    except ValueError:
        bet = 0

    result = game.play_round(bet, choice)
    log_play(conn, game_name, bet, choice, result["result"], result["time"])

    draw_text(
        screen,
        [
            f"Game: {game_name}",
            f"Result: {result['result']}",
            "Press any key to continue",
        ],
    )
    wait_for_key()


def show_final(screen: Surface, conn):
    """Display the aggregated results and radar chart."""
    logs = fetch_logs(conn)
    scores = calculate_scores(logs)
    radar_path = "radar.png"
    generate_radar_chart(scores, radar_path)
    btype = classify_business_type(scores)

    radar_img = pygame.image.load(radar_path)
    radar_rect = radar_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    draw_text(
        screen,
        [
            "Final Results",
            f"Type: {btype}",
            f"RISK: {scores['RISK']:.2f}",
            f"STRATEGY: {scores['STRATEGY']:.2f}",
            f"CHALLENGE: {scores['CHALLENGE']:.2f}",
            f"ADAPT: {scores['ADAPT']:.2f}",
        ],
    )
    screen.blit(radar_img, radar_rect)
    pygame.display.flip()
    wait_for_key()


def main() -> None:
    """Start the Pygame event loop for the casino application."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Personality Casino")

    conn = init_db()

    while True:
        draw_text(
            screen,
            [
                "Select Game:",
                "1: Poker",
                "2: Blackjack",
                "3: Chinchiro",
                "4: Roulette",
                "5: Finish",
            ],
        )
        choice = get_text_input(screen, "Enter choice: ")
        if choice == "1":
            play_game(screen, conn, "Poker")
        elif choice == "2":
            play_game(screen, conn, "Blackjack")
        elif choice == "3":
            play_game(screen, conn, "Chinchiro")
        elif choice == "4":
            play_game(screen, conn, "Roulette")
        elif choice == "5":
            break

    show_final(screen, conn)
    pygame.quit()


if __name__ == "__main__":
    main()
