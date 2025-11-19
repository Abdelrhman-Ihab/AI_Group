# main.py
from menu import Menu
from     import GUI
import pygame

def main():
    # --- Show menu ---
    menu = Menu()
    depth, algorithm = menu.run()

    # if user closed menu or pressed ESC
    if depth is None or algorithm is None:
        pygame.quit()
        return

    print(f"Starting game with depth={depth}, algorithm={algorithm}")

    # --- Launch game ---
    gui = GUI(ai_depth=depth, algorithm=algorithm)
    gui.run()

if __name__ == "__main__":
    main()
