import asyncio
import math
import os
import pygame

from perudo import Perudo


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Perudo // Liar's Dice")

BG = pygame.transform.scale(
    pygame.image.load(os.path.join("resources", "background.png")).convert(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)

TITLE_FONT = pygame.font.Font("resources/Daydream.ttf", 36)
GAME_FONT = pygame.font.Font("resources/Daydream.ttf", 24)


class SpriteSheet:
    def __init__(
        self,
        sprite_sheet: str = "hurt.png",
        pixels: tuple[int, int] = (64, 64),
        sprite_dir: str = "resources/sprites",
    ):
        assert sprite_sheet in os.listdir(sprite_dir)
        sprite_sheet = os.path.join(sprite_dir, sprite_sheet)
        self.sheet = pygame.image.load(sprite_sheet).convert_alpha()
        self.sprite_pixels = pixels
        self.sprites = []

        sheet_width, sheet_height = self.sheet.get_size()
        cols = sheet_width // pixels[0]
        rows = sheet_height // pixels[1]

        self.sprite_count = (cols, rows)
        self.total_sprites = cols * rows

        for n in range(self.sprite_count[0] * self.sprite_count[1]):
            rect = pygame.Rect(
                (n % self.sprite_count[0]) * pixels[0],
                (n // self.sprite_count[0]) * pixels[1],
                pixels[0],
                pixels[1],
            )
            frame = self.sheet.subsurface(rect).copy()
            self.sprites.append(frame)

    def get_image(self, idx: int, color: tuple[int, int, int], scale: float = 1.0):
        image = pygame.transform.scale(
            self.sprites[idx],
            (self.sprite_pixels[0] * scale, self.sprite_pixels[1] * scale),
        )
        image.set_colorkey(color)
        return image


def menu(screen, num_players: int = 5, num_dice: int = 5) -> Perudo:
    playing = False
    exit_game = False
    while not playing:
        screen.blit(BG, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit_game = True
                elif event.key == pygame.K_SPACE:
                    playing = True
                elif event.key == pygame.K_LEFT:
                    num_players = max(2, num_players - 1)
                elif event.key == pygame.K_RIGHT:
                    num_players = min(num_players + 1, 20)
                elif event.key == pygame.K_DOWN:
                    num_dice = max(1, num_dice - 1)
                elif event.key == pygame.K_UP:
                    num_dice = min(num_dice + 1, 10)

        title = TITLE_FONT.render("PERUDO", True, (255, 0, 0))
        game_config = GAME_FONT.render(
            f"PLAYERS: {num_players}\n\nDICE: {num_dice}\n\nSPACE TO PLAY",
            True,
            (255, 0, 0),
        )
        screen.blit(
            title, (SCREEN_WIDTH / 2 - title.get_width() / 2, SCREEN_HEIGHT / 4)
        )
        screen.blit(
            game_config,
            (SCREEN_WIDTH / 2 - game_config.get_width() / 2, SCREEN_HEIGHT / 2),
        )
        screen.blit(
            game_config,
            (SCREEN_WIDTH / 2 - game_config.get_width() / 2, SCREEN_HEIGHT / 2),
        )
        pygame.display.update()

        if exit_game:
            pygame.quit()
            exit()

    return Perudo(players=num_players, dice=num_dice)


def render_player(idx: int, total_players: int, sprite, radius: int = 200) -> tuple:
    """Returns all information needed to draw a player sprite for a specific player

    Args:
        idx (int): Player ID as integer
        total_players (int): Count of all players
        sprite (_type_): Sprite to render for the player
        radius (int, optional): Radius for a circle to distribute players on. Defaults to 150.

    Returns:
        tuple: Tuple holding (sprite, coordinates) for rendering in PyGame via unpacking
    """
    return (
        sprite,
        (
            SCREEN_WIDTH / 2
            + radius * math.cos(math.tau * idx / total_players)
            - sprite.get_width() / 2,
            SCREEN_HEIGHT / 2
            + radius * math.sin(math.tau * idx / total_players)
            - sprite.get_height() / 2,
        ),
    )


def play_game(screen, p: Perudo, hurt_frames) -> tuple[str, tuple]:
    run = True
    losers = []
    players_to_render = []

    while run:
        screen.blit(BG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        losers = p()
        if isinstance(losers, list):
            players_to_render = [
                render_player(
                    idx,
                    len(p.player_ids),
                    hurt_frames.sprites[-1]
                    if idx in p.eliminated_players
                    else (
                        hurt_frames.sprites[2]
                        if idx in losers
                        else hurt_frames.sprites[0]
                    ),
                )
                for idx in p.player_ids
            ]
        elif isinstance(losers, int):
            winner = p.players[0].id
            run = False
            # elif len(losers) == 1:
            #     bowing = hurt_frames.total_sprites - 1

        for data in players_to_render:
            screen.blit(*data)

        pygame.display.update()
        pygame.time.wait(200)

    return winner, players_to_render


async def main():
    hurt_frames = SpriteSheet()
    sit_frames = SpriteSheet("sit.png")

    num_players = 5
    num_dice = 5

    playing = False
    exit_game = False
    while not playing:
        screen.blit(BG, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit_game = True
                elif event.key == pygame.K_SPACE:
                    playing = True
                elif event.key == pygame.K_LEFT:
                    num_players = max(2, num_players - 1)
                elif event.key == pygame.K_RIGHT:
                    num_players = min(num_players + 1, 20)
                elif event.key == pygame.K_DOWN:
                    num_dice = max(1, num_dice - 1)
                elif event.key == pygame.K_UP:
                    num_dice = min(num_dice + 1, 10)

        title = TITLE_FONT.render("PERUDO", True, (255, 0, 0))
        game_config = GAME_FONT.render(
            f"PLAYERS: {num_players}\n\nDICE: {num_dice}\n\nSPACE TO PLAY",
            True,
            (255, 0, 0),
        )
        screen.blit(
            title, (SCREEN_WIDTH / 2 - title.get_width() / 2, SCREEN_HEIGHT / 4)
        )
        screen.blit(
            game_config,
            (SCREEN_WIDTH / 2 - game_config.get_width() / 2, SCREEN_HEIGHT / 2),
        )
        screen.blit(
            game_config,
            (SCREEN_WIDTH / 2 - game_config.get_width() / 2, SCREEN_HEIGHT / 2),
        )
        pygame.display.update()
        await asyncio.sleep(0)

        if exit_game:
            pygame.quit()
            exit()

    p = Perudo(players=num_players, dice=num_dice)

    run = True
    losers = []
    players_to_render = []

    while run:
        screen.blit(BG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        losers = p()
        if isinstance(losers, list):
            players_to_render = [
                render_player(
                    idx,
                    len(p.player_ids),
                    hurt_frames.sprites[-1]
                    if idx in p.eliminated_players
                    else (
                        hurt_frames.sprites[2]
                        if idx in losers
                        else hurt_frames.sprites[0]
                    ),
                )
                for idx in p.player_ids
            ]
        elif isinstance(losers, int):
            winner = p.players[0].id
            run = False
            # elif len(losers) == 1:
            #     bowing = hurt_frames.total_sprites - 1

        for data in players_to_render:
            screen.blit(*data)

        pygame.display.update()
        await asyncio.sleep(0)
        pygame.time.wait(200)

    text = GAME_FONT.render(f"{winner} Victorious!", True, (255, 0, 0))

    frames = 1000
    while frames:
        screen.blit(BG, (0, 0))
        # image = pygame.transform.scale(pygame.image.load(os.path.join(BASE_PATH, image)).convert(), (SCR_W, SCR_H))

        for sprite, player_coordinates in players_to_render:
            screen.blit(sprite, player_coordinates)
        screen.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, SCREEN_HEIGHT / 3))
        screen.blit(sit_frames.sprites[4], (SCREEN_WIDTH / 2 - 32, SCREEN_HEIGHT / 2 - 32))
        pygame.display.update()
        await asyncio.sleep(0)
        frames -= 1

    pygame.quit()

asyncio.run(main)
