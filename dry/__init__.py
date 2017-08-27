import pygame
import sys

from typing import List, Set

from threading import Thread
from queue import Queue

from src.voicerec import voice_recognition_generator
from src.nlp import process, render_tokens, get_token_by_pos

from google.cloud.language import enums

from .drawing import GameGraphics


uncounted_words = {
    'is',
    '\'s',
    'are',
    'be',
    'do',
    '\'m',
    'am'
}


def get_score(nvs: List[str]) -> int:
    score: int = 0

    for word in nvs:
        if len(word) < 3:
            continue
        formula = max([1, (len(word) - 4) * 1.5 + max([0, ((len(word) - 5) * (len(word) - 5))])])
        score += formula

    return score


class GameState(object):

    def __init__(self):
        self._used_words: Set[str] = set()
        self._used_words_ordered: List[str] = []
        self.score = 0
        self.game_finished = False
        self.failed_word = ''

    def get_reused_words(self, words: List[str]) -> List[str]:
        return [word for word in words if word in self._used_words]

    def check_words(self, words: List[str]) -> bool:
        return len(self.get_reused_words(words)) != 0

    def add_words(self, words: List[str]) -> None:
        if self.game_finished:
            return
        self._used_words.update(set(words))
        self._used_words_ordered.extend(words)
        self.score += get_score(words)


def get_nouns_and_verbs(voice_line: str) -> List[str]:
    """
    Use NLP to extract the nouns and verbs from a line

    :param voice_line: the voice line to extract from
    :return:
    """
    tokens = process(voice_line)

    nv_tokens = get_token_by_pos(tokens, enums.PartOfSpeech.Tag.VERB)
    nv_tokens.extend(get_token_by_pos(tokens, enums.PartOfSpeech.Tag.NOUN))

    result = [token.text.content for token in nv_tokens if token.text.content not in uncounted_words]

    return result



def voice_input_gen():
    """
    Generator to get voice lines, and get the nouns and verbs from them

    :return: yields tuples (line, noun_verb_list, is_line_final)
    """
    # Voice input generator will keep looping forever
    for voice_line, is_final in voice_recognition_generator():
        yield voice_line, get_nouns_and_verbs(voice_line), is_final


def vr_thread(game_state: GameState, line_queue: Queue, words_queue: Queue) -> None:
    """
    Main loop (to run in a separate thread) for voice recognition

    :param game_state: the global game state which this thread will update
    :param line_queue: the threadsafe queue to pass the voice lines around
    :param words_queue: the threadsafe queue to pass the used words around
    :return: None
    """
    for voice_line, words, is_final in voice_input_gen():
        if not is_final:
            continue

        if game_state.check_words(words):
            game_state.failed_word = game_state.get_reused_words(words)[0]
            game_state.game_finished = True
            return

        game_state.add_words(words)

        words_queue.put(words.copy())
        line_queue.put(voice_line)

        print("Line: " + voice_line)
        print("Currently used: " + str(game_state._used_words_ordered))


def main() -> int:
    game_graphics = GameGraphics()

    clock = pygame.time.Clock()

    game_state = GameState()
    line_queue = Queue()
    words_queue = Queue()

    voice_thread = Thread(target=vr_thread,
                          kwargs={'game_state': game_state, 'line_queue': line_queue, 'words_queue': words_queue})
    voice_thread.daemon = True
    voice_thread.start()

    game_running = True

    while game_running:
        # Check for game over
        if (False or game_state.game_finished) and not game_graphics.game_over:
            print("GAME ENDED")
            game_graphics.end_game(game_state.failed_word)

        # Handle voice input events
        if not line_queue.empty():
            game_graphics.set_voice_line(line_queue.get())
            game_graphics.add_to_score(game_state.score)
        if not words_queue.empty():
            game_graphics.add_many_to_cloud(words_queue.get())

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

        # Redraw
        game_graphics.tick()

        clock.tick(60)

    return 0
