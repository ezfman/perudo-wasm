import asyncio
import math
import os
import pygame
import random

from collections import Counter
from typing import List, Optional


class Player:
    def __init__(self, id: int, hand: List[int], dice: int, total_dice: int) -> None:
        self.id = id
        self.hand = hand
        self.dice_left = dice
        self.total_dice = total_dice
        self.last_action: Optional[dict] = None  # To store the last action taken
        self.lost_last_round: bool = False
        self.last_bet: Optional[dict] = None

    def __call__(self, bet: Optional[dict], uno: bool = False) -> dict:
        if not bet:
            bet = {
                "count": 1,
                "face": 2,
            }

        match random.randint(1, 3) if not bet else 1:
            case 1:
                if uno:
                    action = {
                        "action": "BET",
                        "count": random.randint(
                            min(bet["count"] + 1, self.total_dice), self.total_dice
                        ),
                        "face": bet["face"],
                        "id": self.id,
                    }
                else:
                    action = {
                        "action": "BET",
                        "count": random.randint(bet["count"], self.total_dice),
                        "face": random.randint(bet["face"], 6),
                        "id": self.id,
                    }
                self.last_bet = action
            case 2:
                self.last_bet = None
                action = {"action": "CALL"}
            case 3:
                self.last_bet = None
                action = {"action": "EXACT"}

        self.last_action = action
        return action

    def round(self, outcome: dict, hand: List[int]) -> None:
        assert all(["loss" in outcome, "dice_lost" in outcome])
        assert isinstance(outcome["loss"], bool)
        assert isinstance(outcome["dice_lost"], int)
        assert outcome["dice_lost"] in range(1, self.total_dice + 1)

        self.hand = hand
        self.total_dice -= outcome["dice_lost"]
        self.lost_last_round = outcome["loss"]

        if outcome["loss"]:
            self.dice_left -= 1


class Perudo:
    def __init__(self, players: int = 5, dice: int = 5):
        self.total_dice = players * dice
        self.hands = []
        self.players = []
        self.player_ids = []
        for id in range(players):
            hand = self._hand(dice)
            self.hands.append(hand)
            self.players.append(Player(id, hand, dice, dice * players))
            self.player_ids.append(id)

        self.counts = Counter(sum(self.hands, []))
        self.bet = None
        self.uno = False
        self.eliminated_players = []
        self.at_bat = self.player_ids[random.randint(0, len(self.players) - 1)]

    def __call__(self) -> Optional[int]:
        """Run a round of Perudo, returning losers or the ultimate winner

        Returns:
            Optional[int]: ID of round losers or the winning player
        """
        losers = self._round()

        if len(self.players) == 1:
            return self.players[0].id
        else:
            return losers

    def _round(self):
        round_over = False
        while not round_over:
            for player in self.players[self.at_bat :] + self.players[: self.at_bat]:
                bet = player(self.bet)
                if self.bet and self.bet["face"] == 1:
                    wilds = 0
                else:
                    wilds = self.uno * self.counts[1]
                match bet["action"]:
                    case "BET":
                        # If bets are invalid, lose as punishment.
                        if self._validate_bet(bet):
                            self.bet = bet
                        else:
                            losers = [player.id]
                            round_over = True
                    case "CALL":
                        round_over = True
                        if self.bet["count"] <= self.counts[self.bet["face"]] + wilds:
                            losers = [player.id]
                        else:
                            losers = [bet["id"]]
                    case "EXACT":
                        round_over = True
                        if self.bet["count"] == self.counts[self.bet["face"]] + wilds:
                            losers = [id for id in self.player_ids if not player.id]
                        else:
                            losers = [player.id]
                    case _:
                        losers = [player.id]
                        round_over = True

        # TODO: Correct at_bat if a player is eliminated
        self.at_bat = player.id
        while self.at_bat in self.eliminated_players:
            self.at_bat += 1
            self.at_bat = self.at_bat % self.players
        self.uno = False
        self._deal(losers)
        self.bet = None
        self.total_dice -= len(losers)

        return losers

    def _deal(self, losers: List[int]) -> None:
        self.hands = []
        for player in self.players:
            hand = self._hand(player.dice_left)
            self.hands.append(hand)
            player.round({"loss": player.id in losers, "dice_lost": len(losers)}, hand)

            match player.dice_left:
                case 1:
                    self.uno = True
                case 0:
                    self.players = list(
                        filter(lambda x: x.id != player.id, self.players)
                    )
                    self.eliminated_players.append(player.id)

        self.counts = Counter(sum(self.hands, []))

    def _hand(self, num_dice: int) -> List[int]:
        return [random.randint(1, 6) for _ in range(num_dice)]

    def _validate_bet(self, bet: dict) -> bool:
        # Compare incoming bet to existing to validate that it is legal
        try:
            assert all(["face" in bet, "count" in bet])
            assert 1 <= bet["face"] <= 6
            assert 1 <= bet["count"] <= self.total_dice
        except AssertionError:
            return False

        # Allow any legal bet for the first turn of the round
        if not self.bet:
            return True

        # Face value cannot change on an uno round
        if self.uno and bet["face"] != self.bet["face"]:
            return False

        if self.bet["face"] == 1:
            if bet["face"] == 1:
                return bet["count"] > self.bet["count"]
            else:
                return bet["count"] >= 2 * self.bet["count"]
        elif bet["face"] == 1:
            return 2 * bet["count"] > self.bet["count"]
        else:
            if bet["count"] > self.bet["count"]:
                return True
            elif bet["count"] == self.bet["count"]:
                return bet["face"] > self.bet["face"]
            else:
                return False


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


async def main():
    hurt_frames = SpriteSheet()
    sit_frames = SpriteSheet("sit.png")

    num_players = 5
    num_dice = 5

    radius = 200

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
                (
                    hurt_frames.sprites[-1]
                    if idx in p.eliminated_players
                    else (
                        hurt_frames.sprites[2]
                        if idx in losers
                        else hurt_frames.sprites[0]
                    ),
                    (
                        SCREEN_WIDTH / 2
                        + radius * math.cos(math.tau * idx / len(p.player_ids))
                        - hurt_frames.sprites[-1]
                        if idx in p.eliminated_players
                        else (
                            hurt_frames.sprites[2]
                            if idx in losers
                            else hurt_frames.sprites[0]
                        ).get_width()
                        / 2,
                        SCREEN_HEIGHT / 2
                        + radius * math.sin(math.tau * idx / len(p.player_ids))
                        - hurt_frames.sprites[-1]
                        if idx in p.eliminated_players
                        else (
                            hurt_frames.sprites[2]
                            if idx in losers
                            else hurt_frames.sprites[0]
                        ).get_height()
                        / 2,
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
        screen.blit(
            sit_frames.sprites[4], (SCREEN_WIDTH / 2 - 32, SCREEN_HEIGHT / 2 - 32)
        )
        pygame.display.update()
        await asyncio.sleep(0)
        frames -= 1

    pygame.quit()


asyncio.run(main())
