"""
Word by punctuation: aw/iw
Word by whitespace: aW/iW (see :help WORD)
Sentence: as/is
Paragraph: ap/ip
Quotes: a“/i“
Parentheses: a)/i)
Brackets: a]/i]
Braces: a}/i}
Angle Brackets: a>/i>
Tags (e.g. <html>inner</html>): at/it
"""

class TextObject(object):
    pass

class Word(TextObject):
    INNABLE = True    

    @classmethod
    def self(cls):
        return "w"

    @classmethod
    def previous(cls):
        return "e"

    @classmethod
    def next(cls):
        return "w"

class Line(TextObject):
    INNABLE = False

    @classmethod
    def start(cls):
        return "0"
    
    def end(cls):
        return "$"

    @classmethod
    def previous(cls):
        return "k"

    @classmethod
    def next(cls):
        return "j"


class File(TextObject):
    INNABLE = False
    @classmethod
    def start(cls):
        return "gg"

    @classmethod
    def end(cls):
        return "G"