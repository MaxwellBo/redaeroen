class Verb(object):
    LOOKUP = {"change", Change
             ,"delete", Delete
             }

class Change(Verb):
    SELF = "Y"

class Delete(Verb):
    SELF = "D"

class Yank(Verb):
    SELF = "Y"

class SwapCase(Verb):
    SELF = "g~"

class MakeLowercase(Verb):
    SELF = "gu"

class MakeUppercase(Verb):
    SELF = "gU"

class ROT13(Verb):
    SELF = "g?"

class ShiftLeft(Verb):
    SELF = "<"

class ShiftRight(Verb):
    SELF = ">"