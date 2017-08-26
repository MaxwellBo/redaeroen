from pykeyboard import PyKeyboard

k = PyKeyboard()


class KeyPresses(object):
    def execute(self): raise NotImplementedError

class CombinedPress(KeyPresses):
    def __init__(self, *args):
        self.presses = args

    def execute(self):
        for p in self.presses:
            p.execute()

class LiteralPress(KeyPresses):
    def __init__(self, txt):
        self.txt = txt

    def execute(self):
        k.type_string(self.txt)

class ControlPress(KeyPresses):
    lookup = {
        'esc': k.escape_key
    }
    def __init__(self, key):
        self.key = key

    def execute(self):
        key = self.lookup.get(self.key, self.key)
        k.tap_key(key)

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

inp = StandardMode().transform('def hello open paren close paren colon ellipsis')
presses = CombinedPress(
    ControlPress('i'),
    inp,
    ControlPress('esc')
)
presses.execute()
