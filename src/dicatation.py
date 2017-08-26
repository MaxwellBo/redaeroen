from pykeyboard import PyKeyboard
from textobject import *
from verb import *
from context import *

# keyboard = PyKeyboard()

class KeyboardMock(object):
    def __init__(self):
        self.buffer = []
        
    def tap_key(self, key):
        print("Tapping: " + key)
        self.buffer.append(" "+ key + " ")

    def type_string(self, string):
        print("Appending: " + string)
        self.buffer.append(string)

    escape_key = "esc"

k = PyKeyboard()

class KeyPresses(object):
    def execute(self, k): raise NotImplementedError

    def __str__():
        return "<Empty>"

    # def __repr__(self):
    #     # lord have mercy on my soul
    #     printer = KeyboardMock()
    #     self.execute(printer)
    #     return str(k.buffer)

class LiteralPress(KeyPresses):
    def __init__(self, txt):
        self.txt = txt

    def execute(self, k):
        k.type_string(self.txt)

    def __str__(self):
        return self.txt

class ControlPress(KeyPresses):
    lookup = {
        'esc': k.escape_key
    }
    def __init__(self, key):
        self.key = key

    def execute(self, k):
        key = self.lookup.get(self.key, self.key)
        k.tap_key(key)

    def __str__(self):
        return self.key

class Mode(object):
    def transform(self, txt): raise NotImplementedError

class CamelCaseMode(object):
    def transform(self, txt):
        words = txt.split(' ')
        if words:
            transformed = ''.join(words[0] + [w.title() for w in words[1:]])
        else:
            transformed = ''
        return LiteralPress(transformed)

class StandardMode(object):
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
    inp = StandardMode().transform('def hello open paren close paren colon ellipsis')
    presses = [
        ControlPress('i'),
        inp,
        ControlPress('esc')
    ]

    print([str(p) for p in presses])

    # for i in presses:
    #     i.execute(k)