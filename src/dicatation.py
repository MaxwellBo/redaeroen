from nlp import process, render_tokens, to_ir
from voicerec import voice_command_generator
from nlp_to_vim import extract_command
from pykeyboard import PyKeyboard
from textobject import *
from verb import *
from context import *

###############
# GLOBALS #
###########

k = PyKeyboard()
current_form = StandardForm
current_mode = Command

#########
# MODES #
#########

class Dictation(Mode):
    @classmethod
    def to_presses(cls, command):
        text = current_mode.transform(command)
        return LiteralPress(text)

class Command(Mode):
    @classmethod
    def to_presses(cls, command):
        tokens = process(command)
        render_tokens(tokens)
        return extract_command(tokens)

def interpret_meta(meta):
    if new is Dictation:
        k.execute(ControlPress("i"))
        current_mode = new
    elif new is Command:
        k.execute(ControlPress("esc"))
        current_mode = new

    # AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHh

#########
# FORMS #
#########

class Form(object):
    def transform(self, txt): raise NotImplementedError

class StandardForm(Form):
    def transform(self, txt):
        subs = [
            ('open paren', '('),
            ('close paren', ')'),
            ('colon', ':'),
            ('ellipsis', '...')
        ]
        for orig, rep in subs:
            txt = txt.replace(orig, rep)

        return LiteralPress(txt)

class CamelCaseForm(Form):
    def transform(self, txt):
        words = txt.split(' ')
        if words:
            transformed = ''.join(words[0] + [w.title() for w in words[1:]])
        else:
            transformed = ''
        return LiteralPress(transformed)

###########
# PRESSES #
###########
 
class KeyPresses(object):
    def execute(self): raise NotImplementedError

    def __str__():
        return "<Empty>"

class LiteralPress(KeyPresses):
    def __init__(self, txt):
        self.txt = txt

    def execute(self):
        k.type_string(self.txt)

    def __str__(self):
        return self.txt

class ControlPress(KeyPresses):
    lookup = {
        'esc': k.escape_key
    }
    def __init__(self, key):
        self.key = key

    def execute(self):
        key = self.lookup.get(self.key, self.key)
        k.tap_key(key)

    def __str__(self):
        return self.key

########
# NLP ##
########


def ctrl(xs):
    return [ ControlPress(i) for i in xs ]

def action(repetition, verb, context, motion):
    if motion is Line:
        if verb in [ Change, Yank, Delete ]:
            return ctrl(verb.self()) * 2
        else:
            return [ ControlPress("v")
                   , ControlPress(motion.start())
                   , ControlPress(motion.finish())
                   , ControlPress(verb.SELF)
            ]
    if context is Inner:
        return []

if __name__ == "__main__":
    for command in voice_command_generator('hey google'):
        presses = current_mode.to_presses(command)
         
        for press in presses:
            p.execute()
