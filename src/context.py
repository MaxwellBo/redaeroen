class Context(object):
    pass

class Surround(Context):
    @classmethod
    def self(cls):
        return "s"

class Around(Context):
    @classmethod
    def self(cls):
        return "a"

class Inner(Context):
    @classmethod
    def self(cls):
        return "i"