import asyncio

import pygame


async def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 360))
    pygame.display.set_caption("Hello Pygame Web")
    clock = pygame.time.Clock()
    x = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill((26, 34, 52))
        pygame.draw.circle(screen, (110, 220, 255), (80 + x, 180), 22)
        pygame.display.flip()

        x = (x + 2) % 500
        await asyncio.sleep(0)
        clock.tick(60)


asyncio.run(main())
