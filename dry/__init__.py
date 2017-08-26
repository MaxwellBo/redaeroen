import pygame
import sys

from typing import List, Set

from threading import Thread
from queue import Queue

from src.voicerec import voice_recognition_generator
from src.nlp import process, render_tokens, get_token_by_pos

from google.cloud.language import enums

from . import *


class GameState(object):

    def __init__(self):
        self._used_words: Set[str] = set()
        self._used_words_ordered: List[str] = []

    def get_reused_words(self, words: List[str]) -> List[str]:
        return [word for word in words if word in self._used_words]

    def check_words(self, words: List[str]) -> bool:
        return len(self.get_reused_words(words)) != 0

    def add_words(self, words: List[str]) -> None:
        self._used_words.update(set(words))
        self._used_words_ordered.extend(words)


def get_nouns_and_verbs(voice_line: str) -> List[str]:
    """
    Use NLP to extract the nouns and verbs from a line

    :param voice_line: the voice line to extract from
    :return:
    """
    tokens = process(voice_line)

    nv_tokens = get_token_by_pos(tokens, enums.PartOfSpeech.Tag.VERB)
    nv_tokens.extend(get_token_by_pos(tokens, enums.PartOfSpeech.Tag.NOUN))

    result = [token.text.content for token in nv_tokens]

    return result


def voice_input_gen():
    """
    Generator to get voice lines, and get the nouns and verbs from them

    :return: yields tuples (line, noun_verb_list, is_line_final)
    """
    # Voice input generator will keep looping forever
    for voice_line, is_final in voice_recognition_generator():
        yield voice_line, get_nouns_and_verbs(voice_line), is_final


def vr_thread(game_state: GameState, line_queue: Queue) -> None:
    """
    Main loop (to run in a separate thread) for voice recognition

    :param game_state: the global game state which this thread will update
    :param line_queue: the threadsafe queue to pass the voice lines around
    :return: None
    """
    for voice_line, words, is_final in voice_input_gen():
        if not is_final:
            continue

        if game_state.check_words(words):
            print("You reused the following: " + str(game_state.get_reused_words(words)))

        line_queue.put(voice_line)

        game_state.add_words(words)

        print("Line: " + voice_line)
        print("Currently used: " + str(game_state._used_words_ordered))


def main():
    game_state = GameState()
    line_queue = Queue()

    voice_thread = Thread(target=vr_thread,
                          kwargs={'game_state': game_state, 'line_queue': line_queue})
    voice_thread.daemon = True
    voice_thread.start()

    pygame.init()

    clock = pygame.time.Clock()

    pygame.font.init()

    screen = pygame.display.set_mode((640, 480))
    screen.fill((255, 255, 255))
    pygame.display.update()

    font = pygame.font.Font(None, 30)

    while True:
        if not line_queue.empty():
            voice_line = line_queue.get()
            text = font.render(voice_line, 1, (0, 255, 0))
            screen.fill((255, 255, 255))
            screen.blit(text, (screen.get_rect().width / 2 - text.get_rect().width / 2, screen.get_rect().height - 5 - text.get_rect().height))

        pygame.display.update()

        ms_elapsed = clock.tick(60)
