# main.py (or inside lvl1 after loop)
import tiles, lvl2

screen = None
# run level1 and request a handoff
screen = tiles.run(return_screen=True)   # you'd modify lvl1.run to optionally return the screen
lvl2.main(existing_screen=screen)