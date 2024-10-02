# This file is generated by running tools/generate_ast.py


class Visitor:
    def visit_binary(self, _expr):
        raise NotImplementedError()

    def visit_grouping(self, _expr):
        raise NotImplementedError()

    def visit_literal(self, _expr):
        raise NotImplementedError()

    def visit_unary(self, _expr):
        raise NotImplementedError()


class Expression:
    def accept(self, _visitor):
        raise NotImplementedError()


class Binary(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary(self)


class Grouping(Expression):
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping(self)


class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)


class Unary(Expression):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary(self)
