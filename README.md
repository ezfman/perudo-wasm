# Perudo

This repository implements Perudo (also known as Liar's Dice) with a simple PyGame interface.

## Running

To install the project, use:

```bash
# With pipx
pipx install .

# With uv
uv sync
```

To run the game, simply use the `game` entrypoint:

```bash
# With pipx
game

# With uv
uv run game
```

To simulate a game:

```bash
# With pipx
sim

# With uv
sim
```

## TODO

The game rules are currently not accurate; rounds are also represented in a single frame, and the option for turn-based animation should be added.

Additionally, the game only runs once; to simulate many trials, it could be beneficial to allow parallel simulations or rapid sequential runs.

Finally, it will be important to allow player customization; specifically, enabling the use of multiple subclasses of `perudo.Player` would enable testing multiple AI against one another, and potentially the allowance for a manual player to compete with lobbies of bots.

## Resources

The sprites used are from [LPC](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator), which are subject to their own license.
The font used is from [dafont](https://www.dafont.com/daydream-3.font) and is permitted for personal use only.
The background was generated via [this generator](https://deep-fold.itch.io/space-background-generator), which allows permissive use.
