"""
ATTEMPT NUMERO DOS

We have:
    Commands (like switch mode, substitute etc)
    Movement (forward/back, up down, start-of, end-of)
    Modification (delete, change; targets a selection)
    Selection (current item (inner word), or 'til'-ish

"""

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
