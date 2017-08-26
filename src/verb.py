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

class Verb(object):
    pass

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