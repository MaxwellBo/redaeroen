"""
ATTEMPT NUMERO DOS

We have:
    Commands (like switch mode, substitute etc)
    Movement (forward/back, up down, start-of, end-of)
    Modification (delete, change; targets a selection)
    Selection (current item (inner word), or 'til'-ish

"""

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

"""
|v_aquote|	a"		   double quoted string
|v_a'|		a'		   single quoted string
|v_a(|		a(		   same as ab
|v_a)|		a)		   same as ab
|v_a<|		a<		   "a <>" from '<' to the matching '>'
|v_a>|		a>		   same as a<
|v_aB|		aB		   "a Block" from "[{" to "]}" (with brackets)
|v_aW|		aW		   "a WORD" (with white space)
|v_a[|		a[		   "a []" from '[' to the matching ']'
|v_a]|		a]		   same as a[
|v_a`|		a`		   string in backticks
|v_ab|		ab		   "a block" from "[(" to "])" (with braces)
|v_ap|		ap		   "a paragraph" (with white space)
|v_as|		as		   "a sentence" (with white space)
|v_at|		at		   "a tag block" (with white space)
|v_aw|		aw		   "a word" (with white space)
|v_a{|		a{		   same as aB
|v_a}|		a}		   same as aB
|v_iquote|	i"		   double quoted string without the quotes
|v_i'|		i'		   single quoted string without the quotes
|v_i(|		i(		   same as ib
|v_i)|		i)		   same as ib
|v_i<|		i<		   "inner <>" from '<' to the matching '>'
|v_i>|		i>		   same as i<
|v_iB|		iB		   "inner Block" from "[{" and "]}"
|v_iW|		iW		   "inner WORD"
|v_i[|		i[		   "inner []" from '[' to the matching ']'
|v_i]|		i]		   same as i[
|v_i`|		i`		   string in backticks without the backticks
|v_ib|		ib		   "inner block" from "[(" to "])"
|v_ip|		ip		   "inner paragraph"
|v_is|		is		   "inner sentence"
|v_it|		it		   "inner tag block"
|v_iw|		iw		   "inner word"
|v_i{|		i{		   same as iB
|v_i}|		i}		   same as iB
"""

"""
|c|	c	change
|d|	d	delete
|y|	y	yank into register (does not change the text)
|~|	~	swap case (only if 'tildeop' is set)
|g~|	g~	swap case
|gu|	gu	make lowercase
|gU|	gU	make uppercase
|!|	!	filter through an external program
|=|	=	filter through 'equalprg' or C-indenting if empty
|gq|	gq	text formatting
|g?|	g?	ROT13 encoding
|>|	>	shift right
|<|	<	shift left
|zf|	zf	define a fold
|g@|	g@	call function set with the 'operatorfunc' option
"""

"""
	dj
deletes two lines >
	dvj
deletes from the cursor position until the character below the cursor >
	d<C-V>j
deletes the character under the cursor and the character below the cursor. 
"""


class Verb(object):
    pass

class Change(Verb):
    @classmethod
    def self(cls):
        return "c"

class Delete(Verb):
    @classmethod
    def self(cls):
        return "d"

class Yank(Verb):
    @classmethod
    def self(cls):
        return "y"

class SwapCase(Verb):
    @classmethod
    def self(cls):
        return "g~"

class MakeLowercase(Verb):
    @classmethod
    def self(cls):
        return "gu"

class MakeUppercase(Verb):
    @classmethod
    def self(cls):
        return "gU"

class ROT13(Verb):
    @classmethod
    def self(cls):
        return "g?"

class ShiftLeft(Verb):
    @classmethod
    def self(cls):
        return "<"

class ShiftRight(Verb):
    @classmethod
    def self(cls):
        return ">"

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

def action(repetition, verb, context, motion):
    if motion is Line:
        if verb in [ Change, Yank, Delete ]:
            return verb.self() * 2
        else:
            # FIXME: Invoke ESC
            return f"v {verb.self()} ESC"
    else:
        return f"{verb.self()}{motion.self()}"



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
    def previous(cls):
        return "k"

    def next(cls):
        return "j"


class File(TextObject):
    INNABLE = True

    @classmethod
    def self(cls):
        return "V gg G"

    @classmethod
    def start(cls):
        return "gg"

    @classmethod
    def end(cls):
        return "G"


###############################################################################

class Node(object): ...


class Meta(Node): ...

class Repeat(Meta):
    def __init__(self, count, node):
        self.count = count
        self.node = node

class Sequence(Meta):
    def __init__(self, *args):
        self.nodes = args


class Movement(Node):
    def __init__(self, forward=True):
        super()
        self.forward = forward

class Word(Movement): ...
class Line(Movement): ...


class Selection(Node): ...

class MovementSelection(Selection):
    def __init__(self, movement):
        self.movement = movement


class Operation(Node):
    def __init__(self, selection):
        self.selection = selection

class Delete(Operation): ...
class Yank(Operation): ...


class Visitor(object):
    def visit(self, node):
        fn = getattr(self, 'visit_' + node.__class__.__name__, None)
        if fn:
            return fn(node)
        return None


class Compiler(Visitor):
    def visit_Repeat(self, node):
        return ''.join(self.visit(node.node) for _ in range(node.count))

    def visit_Sequence(self, node):
        return ''.join(map(self.visit, node.nodes))

    def visit_Word(self, node):
        return 'w' if node.forward else 'b'

    def visit_Line(self, node):
        return 'j' if node.forward else 'k'

    def visit_MovementSelection(self, node):
        return 'v' + self.visit(node.movement)

    def visit_Delete(self, node):
        return self.visit(node.selection) + 'd'

    def visit_Yank(self, node):
        return self.visit(node.selection) + 'y'


ast = Sequence(
    Repeat(
        2,
        Line()
    ),
    Delete(
        MovementSelection(
            Repeat(3, Word())
        )
    )
)

c = Compiler()
print(c.visit(ast))
