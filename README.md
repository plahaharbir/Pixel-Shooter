# Pixel Shooter

A 2D side-scrolling run-and-gun platformer built in Python with Pygame. Originally developed as my A Level Computer Science programming project (Unit 3), built up over three prototypes.

![Screenshot](screenshots/gameplay.png)
<!-- Add a screenshot or GIF of the game running at screenshots/gameplay.png -->

## Features

- Tile-based levels loaded from CSV files, with 3 playable levels
- Scrolling camera with parallax backgrounds
- Player movement, jumping and gravity with tile collision detection
- Shooting and grenades (with blast radius damage), limited ammo
- Enemy AI: patrols platforms, turns at edges, idles at random, and shoots when the player is in its line of sight
- Collectibles: health packs, ammo boxes and grenade boxes
- Hazards (water) and level exit posts
- Sprite animations (idle, run, jump, death) and explosion effects
- Sound effects and background music
- Main menu, pause menu, death screen, win screen and screen transitions
- Custom level editor (`map_maker.py`) with save/load, scrolling and a tile palette

## Development history

The project was built in stages, and all three prototypes are included so the progression can be seen:

| File | What it added |
|------|---------------|
| `prototype_1.py` | Window, background, player and enemy sprites, movement, jumping and gravity |
| `prototype_2.py` | CSV level loading, tile collisions, scrolling camera, enemy AI, shooting, grenades, pickups, health bar, menus and level progression |
| `prototype_3.py` | Sprite animations, sound and music, explosion effects, screen transitions, and menu, death and win screens |

## Running it

Requires Python 3 and Pygame:

```
pip install pygame
python prototype_3.py
```

Run it from the repository root so the asset folders (`TILES/`, `BACKGROUND/`, and so on) are found.

### Controls

| Key | Action |
|-----|--------|
| A / D | Move left / right |
| W | Jump |
| Space | Shoot |
| Q | Throw grenade |
| Esc | Pause |

### Level editor

```
python map_maker.py
```

Left click places a tile, right click erases. Up/Down changes the level number, Left/Right scrolls (hold Right Shift to scroll faster), and the Save/Load buttons write and read `levelN_data.csv`.

## Built with

- Python
- Pygame

## Notes

This was written while learning to program, so some of the code is repetitive (for example, the level reload logic is repeated in several places). If I rebuilt it today I would move that into a single function and split the code across modules.
