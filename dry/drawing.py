from typing import List, Set, Tuple

import random
import time
import math

import pygame
import pygame.freetype


class GameGraphics(object):

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        random.seed(time.time())

        self._init_settings()

        self.screen: pygame.Surface = pygame.display.set_mode((1280, 720))
        self._clear_screen()

        self._cloud = []

        self._spiral = []
        self._spiral_leeway = 15
        self._spiral_smallgap = 5
        self._spiral_rect = (0, 0, 0, 0)
        self._spiral_surface = pygame.Surface((600, 600))
        self._spiral_surface.fill((200, 200, 200))
        self._spiral_curpos = (self._spiral_surface.get_rect().width / 2, self._spiral_surface.get_rect().height / 2)

        self.voice_line = ''
        self.target_score = 0
        self.prior_score = 0
        self.score = 0

        self.time_max = 30 * 60

        self.game_over = False
        self.game_over_animstate = 0
        self.game_over_text_animstate = 0
        self.failed_word = ''


    def _init_settings(self) -> None:
        # Colours
        self.background_color = (255, 255, 255)
        self.voice_line_color = (0, 255, 0)
        self.words_color = (255, 0, 0)

        self.scores_fg = (0, 0, 255)
        self.scores_bg = (128, 128, 128)
        self.scores_anim_length = 60

        self.failed_bg = (0, 0, 0)
        self.failed_fg = (255, 0, 0)
        self.failed_anim_length = 120
        self.failed_text_anim_length = 120

        # Fonts
        self.voice_line_font = pygame.freetype.Font(None, 48)
        self.words_font = pygame.freetype.Font(None, 32)
        self.score_font = pygame.freetype.Font(None, 56)
        self.failed_font = pygame.freetype.Font(None, 82)
        self.failed_font_small = pygame.freetype.Font(None, 48)

    def _clear_screen(self) -> None:
        self.screen.fill(self.background_color)

    def set_voice_line(self, voice_line: str) -> None:
        self.voice_line = voice_line

    def add_to_score(self, new_score: int):
        self.target_score = new_score
        self.prior_score = self.score

    def end_game(self, failed_word: str):
        self.game_over_animstate = 0
        self.failed_word = failed_word
        self.game_over = True

    def add_to_spiral(self, word: str) -> None:
        # Render the raw text
        surface, srect = self.words_font.render(word, fgcolor=self.words_color)

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

        # Special case to start with (to ensure centering)
        if len(self._spiral) == 0:
            cur_x -= surface.get_rect().width/2
            cur_y -= surface.get_rect().height - 40

        # Add the drawn surface to the spiral list
        self._spiral_curpos = cur_x, cur_y

        self._spiral.append(surface)

        # Calculate the new size of the whole spiral
        (total_x, total_y, total_width, total_height) = self._spiral_rect
        if orientation == 0:
            total_x = cur_x
            total_y = cur_y
            total_width = surface.get_rect().width
            total_height = max([total_height, surface.get_rect().height])
        elif orientation == 90:
            total_width += surface.get_rect().width
            total_height = surface.get_rect().height
        elif orientation == 180:
            total_x = cur_x
            total_width = surface.get_rect().width
            total_height += surface.get_rect().height
        elif orientation == 270:
            total_x = cur_x
            total_y = cur_y
            total_width += surface.get_rect().width
            total_height = surface.get_rect().height

        self._spiral_rect = (total_x, total_y, total_width, total_height)
        print("CURPOS: " + str(self._spiral_curpos))
        # Resize the spiral surface if needed
        print("RECT: " + str(self._spiral_rect))

        if total_x < 0 or total_y < 0 or total_x + total_width > self._spiral_surface.get_rect().width or total_y + total_height > self._spiral_surface.get_rect().height:
            new_surface = pygame.surface((self._spiral_surface.get_width(), self._spiral_surface.get_height()))
            new_surface.fill((200, 200, 200))
            scaled_down = pygame.transform.smoothscale(self._spiral_surface, (300, 300))
            self._spiral_surface = new_surface()

        # if total_x <= self._spiral_surface.get_rect().width / 8 or total_y <= self._spiral_surface.get_rect().height / 8 or total_x + total_width >= 7 * (self._spiral_surface.get_rect().width / 8) or total_y + total_height >= 7 * (self._spiral_surface.get_rect().height / 8):
        #     new_surface = pygame.Surface((total_width * 2, total_height * 2))
        #     new_surface.fill((0, 0, 0))
        #     # r = new_surface.blit(self._spiral_surface, (new_surface.get_rect().width/2 - total_width/2, new_surface.get_rect().height/2 - total_height/2))
        #     # print("AFFECTED: " + str(r))
        #     self._spiral_surface = new_surface
        #     print(f"NEW SURFACE: ({self._spiral_surface.get_rect().width}, {self._spiral_surface.get_rect().height})")

        self._spiral_surface.blit(surface, self._spiral_curpos)

    def add_many_to_spiral(self, words: List[str]) -> None:
        for word in words:
            self.add_to_spiral(word)

    def add_to_cloud(self, word: str) -> None:
        # Choose size
        size_scale = random.uniform(0.6, 1.4)
        size_lengthbased = 32 + max([0, len(word) - 3]) * 8
        size = int(size_scale * size_lengthbased)
        # Choose angle
        angle = random.randrange(-40, 40)
        # Choose color
        amount_nonred = random.randrange(0, 50)

        col = (255, amount_nonred, amount_nonred)

        text_surf, _ = self.words_font.render(word, fgcolor=col, rotation=angle, size=size)

        laplac_surf = pygame.transform.laplacian(text_surf)

        text_surf.blit(laplac_surf, (0, 0))

        outline_surf = pygame.transform.smoothscale(text_surf, (int(text_surf.get_width() * 1.1), int(text_surf.get_height() * 1.1)))
        arr = pygame.PixelArray(outline_surf)
        arr.replace(col, (0, 0, 0), distance=0.2)
        del arr

        outline_surf.blit(text_surf, (outline_surf.get_width()/2 - text_surf.get_width()/2, outline_surf.get_height()/2 - text_surf.get_height()/2))

        # outline_surf = pygame.transform.rotate(outline_surf, angle)

        # Choose position
        x = random.randrange(10, self.screen.get_width() - outline_surf.get_width() - 10)
        y = random.randrange(10, self.screen.get_height() - outline_surf.get_height() - 80 - 10)

        self._cloud.append((outline_surf, x, y))

    def add_many_to_cloud(self, words: List[str]) -> None:
        for word in words:
            self.add_to_cloud(word)

    def _draw_voice_line(self, surface: pygame.Surface) -> None:
        sz = self.voice_line_font.size
        text, trect = self.voice_line_font.render(self.voice_line, fgcolor=self.voice_line_color, size=sz)

        while trect.width > surface.get_width() - 5 and sz >= 10:
            sz -= 2
            text, trect = self.voice_line_font.render(self.voice_line, fgcolor=self.voice_line_color, size=sz)

        xpos = surface.get_rect().width/2 - trect.width/2
        ypos = surface.get_rect().height - 15 - trect.height
        surface.blit(text, (xpos, ypos))

    def _render_spiral(self, surface: pygame.Surface) -> None:
        if self._spiral_surface.get_rect().width > 600:
            scaled_spiral = pygame.transform.smoothscale(self._spiral_surface, (600, 600))
        else:
            scaled_spiral = self._spiral_surface
        surface.blit(scaled_spiral, (surface.get_rect().width/2 - scaled_spiral.get_rect().width/2, surface.get_rect().height/2 - scaled_spiral.get_rect().height/2))

    def _render_cloud(self, surface: pygame.Surface) -> None:
        for word_surf, x, y in self._cloud:
            surface.blit(word_surf, (x, y))

    def _render_score(self, surface: pygame.Surface) -> None:
        text, _ = self.score_font.render(str(int(self.score)), fgcolor=self.scores_fg)

        pygame.draw.circle(surface, self.scores_bg, (int(surface.get_width() - text.get_width()/2 - 20), int(20 + text.get_height()/2)), int(max([text.get_width()/2 + 10, text.get_height()/2 + 10])))
        surface.blit(text, (surface.get_width() - text.get_width() - 20, 20))

    def _render_gameover(self, surface: pygame.Surface) -> None:
        top_box_y = int((surface.get_height()/2) * self.game_over_animstate)
        bottom_box_y = int(surface.get_height() - (surface.get_height()/2) * self.game_over_animstate)

        surface.fill(self.failed_bg, rect=(-1, -1, surface.get_width() + 1, top_box_y + 1))
        surface.fill(self.failed_bg, rect=(-1, bottom_box_y, surface.get_width() + 1, surface.get_height() + 1 - bottom_box_y))

        if self.game_over_text_animstate > 0:
            t_surf = pygame.Surface((surface.get_width(), surface.get_height()))

            text, _ = self.failed_font.render('You Lost!', self.failed_fg)
            if self.failed_word == '':
                fw_text, _ = self.failed_font_small.render('You ran out of time!', self.failed_fg)
            else:
                fw_text, _ = self.failed_font_small.render('You reused: ' + self.failed_word, self.failed_fg)

            text_left, _ = self.failed_font.render('You Lost!', (64, 64, 64), rotation=-15)
            text_right, _ = self.failed_font.render('You Lost!', (64, 64, 64), rotation=15)

            t_surf.blit(text_left, (surface.get_width()/2 - text_left.get_width()/2, surface.get_height()/2 - text_left.get_height()/2 - 20))
            t_surf.blit(text_right, (surface.get_width()/2 - text_right.get_width()/2, surface.get_height()/2 - text_right.get_height()/2 - 20))
            t_surf.blit(text, (surface.get_width()/2 - text.get_width()/2, surface.get_height()/2 - text.get_height()/2 - 20))
            t_surf.blit(fw_text, (surface.get_width()/2 - fw_text.get_width()/2, surface.get_height()/2 + 150))

            # Scaling
            t_surf = pygame.transform.smoothscale(t_surf,
                                                  (int(surface.get_width() * self.game_over_text_animstate), int(surface.get_height() * self.game_over_text_animstate)))
            surface.blit(t_surf, (surface.get_width()/2 - t_surf.get_width()/2, surface.get_height()/2 - t_surf.get_height()/2))

    def _render_time_left(self, time_left: int, surface: pygame.Surface):
        cx, cy, r = (75, 75, 50)

        # Draw circle
        pygame.draw.circle(surface, (0, 0, 0), (cx, cy), r)
        angle = (float(time_left)/self.time_max) * 360 - 90

        points = [(cx, cy)]
        for n in range(-90, int(angle)):
            x_cur = cx + int((r - 2) * math.cos(n * math.pi / 180))
            y_cur = cy + int((r - 2) * math.sin(n * math.pi / 180))
            points.append((x_cur, y_cur))
        points.append((cx, cy))

        # Draw segment
        if len(points) > 2:
            if time_left < 10 * 60:
                col = (255, 0, 0)
            else:
                col = (255, 255, 0)
            pygame.draw.polygon(surface, col, points)

    def _redraw_screen(self, time_left: int) -> None:
        self._clear_screen()
        self._render_cloud(self.screen)
        self._draw_voice_line(self.screen)

        if self.game_over:
            self._render_gameover(self.screen)

        self._render_time_left(time_left, self.screen)
        self._render_score(self.screen)

        pygame.display.update()

    def tick(self, time_left: int) -> None:
        if self.score != self.target_score:
            self.score = min([self.target_score, self.score + (float(self.target_score - self.prior_score) / self.scores_anim_length)])
        if self.game_over and self.game_over_animstate < 1:
            self.game_over_animstate = min([1, self.game_over_animstate + float(1)/self.failed_anim_length])
        if self.game_over and self.game_over_animstate >= 1 and self.game_over_text_animstate < 1:
            self.game_over_text_animstate = min([1, self.game_over_text_animstate + float(1) / self.failed_text_anim_length])
        self._redraw_screen(time_left)
