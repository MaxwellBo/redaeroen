from typing import List, Set

import pygame
import pygame.freetype


class GameGraphics(object):

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()

        self._init_settings()

        self.screen: pygame.Surface = pygame.display.set_mode((1280, 720))
        self._clear_screen()

        self._spiral = []
        self._spiral_leeway = 15
        self._spiral_smallgap = 5
        self._spiral_surface = pygame.Surface((1000, 1000))
        self._spiral_surface.fill(self.background_color)
        self._spiral_curpos = (self._spiral_surface.get_rect().width / 2, self._spiral_surface.get_rect().height / 2)

        self.voice_line = ''

    def _init_settings(self) -> None:
        # Colours
        self.background_color = (255, 255, 255)
        self.voice_line_color = (0, 255, 0)
        self.spiral_color = (255, 0, 0)

        # Fonts
        self.voice_line_font = pygame.freetype.Font(None, 52)
        self.spiral_font = pygame.freetype.Font(None, 32)

    def _clear_screen(self) -> None:
        self.screen.fill(self.background_color)

    def set_voice_line(self, voice_line: str) -> None:
        self.voice_line = voice_line

    def add_to_spiral(self, word: str) -> None:
        # Render the raw text
        surface, srect = self.spiral_font.render(word, fgcolor=self.spiral_color)

        raw_text_height = srect.height + 2

        # Determine the orientation
        orientation = ((len(self._spiral)) % 4) * 90
        # Angles are the wrong way :'(
        o = orientation
        if orientation == 90:
            o = 270
        elif orientation == 270:
            o = 90
        surface = pygame.transform.rotate(surface, o)

        # Ensure the spiral gets larger
        req_dim = 0
        if len(self._spiral) >= 2:
            if orientation == 0 or orientation == 180:
                # Need to be width of last + width of 2nd last + leeway
                required_size = self._spiral[-1].get_rect().width + self._spiral_smallgap + self._spiral[-2].get_rect().width  + self._spiral_smallgap + self._spiral_leeway
                req_dim = 0
            elif orientation == 90 or orientation == 270:
                # Need to be height of last + height of 2nd last + leeway
                required_size = self._spiral[-1].get_rect().height + self._spiral_smallgap + self._spiral[-2].get_rect().height + self._spiral_smallgap + self._spiral_leeway
                req_dim = 1

            # Scale the surface to ensure the right size text
            aspect_ratio = surface.get_rect().width / surface.get_rect().height
            if req_dim == 0:
                # width
                surface = pygame.transform.smoothscale(surface,
                                                       (required_size, int(required_size / aspect_ratio)))
            else:
                #height
                surface = pygame.transform.smoothscale(surface, (int(required_size * aspect_ratio), required_size))


        # Find spiral position based on last text position
        cur_x, cur_y = self._spiral_curpos

        # Calculate the current position
        if orientation == 0:
            # Last one was orientation 270
            # So just move up by the height of this text
            cur_y -= surface.get_rect().height - self._spiral_smallgap
        elif orientation == 90:
            # Last one was orientation 0
            # So just move right by the width of the last text
            cur_x += self._spiral[-1].get_rect().width + self._spiral_smallgap
        elif orientation == 180:
            # Last one was orientation 90
            # So move left by the width of the new text minus the width of the last text
            cur_x -= (surface.get_rect().width - self._spiral[-1].get_rect().width) - self._spiral_smallgap
            # So move down by the height of the last text
            cur_y += self._spiral[-1].get_rect().height + self._spiral_smallgap
            pass
        elif orientation == 270:
            # Last one was orientation 180
            # So move left by the width of this text
            cur_x -= surface.get_rect().width - self._spiral_smallgap
            # So move up by the height of this text minus the height of the last text
            cur_y -= (surface.get_rect().height - self._spiral[-1].get_rect().height) - self._spiral_smallgap

        # Add the drawn surface to the spiral list
        self._spiral_curpos = cur_x, cur_y

        self._spiral.append(surface)
        self._spiral_surface.blit(surface, self._spiral_curpos)

    def add_many_to_spiral(self, words: List[str]) -> None:
        for word in words:
            self.add_to_spiral(word)

    def _draw_voice_line(self, surface: pygame.Surface) -> None:
        text, trect = self.voice_line_font.render(self.voice_line, fgcolor=self.voice_line_color)
        xpos = surface.get_rect().width/2 - trect.width/2
        ypos = surface.get_rect().height - 15 - trect.height
        surface.blit(text, (xpos, ypos))

    def _render_spiral(self, surface: pygame.Surface) -> None:
        surface.blit(self._spiral_surface, (0, 0))

    def _redraw_screen(self) -> None:
        self._clear_screen()
        self._render_spiral(self.screen)
        self._draw_voice_line(self.screen)
        pygame.display.update()

    def tick(self) -> None:
        self._redraw_screen()
