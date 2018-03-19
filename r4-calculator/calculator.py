import sys


DIV = '/'
PLUS = '+'
MULT = '*'
MINUS = '-'
NUM = 'int'
OPEN_PARENT = '('
CLOSE_PARENT = ')'
OPEN_COMMENT = '{'
CLOSE_COMMENT = '}'
STD_FILE_NAME = 'test.in'
SIGNS = [PLUS, MINUS]

class Token:
    operators = []

    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

class Term(Token):
    operators = [MULT, DIV]

class Num(Token):
    operators = []

class Expr(Token):
    operators = [PLUS, MINUS]

class Parent(Token):
    operators = [OPEN_PARENT, CLOSE_PARENT]


class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def evaluate(self):
        pass

class BinOp(Node):
    def evaluate(self):
        # this if is unnecessary
        if len(self.children) != 2:
            raise ValueError('Unexpected children len for node, expected 2, got',
                             len(self.children))
        children_values = [c.evaluate() for c in self.children]

        # do math
        if self.value == PLUS:
            return children_values[0] + children_values[1]
        elif self.value == MINUS:
            return children_values[0] - children_values[1]
        elif self.value == DIV:
            return children_values[0] // children_values[1]
        elif self.value == MULT:
            return children_values[0] * children_values[1]
        else:
            raise ValueError('Unexpected value for BinOp, got', self.value)

class UnOp(Node):
    def evaluate(self):
        # this if is unnecessary
        if len(self.children) != 1:
            raise ValueError('Unexpected children len for node, expected 1, got',
                             len(self.children))
        child_value = self.children[0].evaluate()
        if self.value == PLUS:
            return child_value
        elif self.value == MINUS:
            return -child_value
        else:
            raise ValueError('Unexpected value for UnOp, got', self.value)


class IntVal(Node):
    def evaluate(self):
        return self.value


class NoOp(Node):
    def evaluate(self):
        pass

class Tokenizer:
    def __init__(self, src, pos=0, curr=None):
        self.src = src
        self.pos = pos
        self.curr = curr
        self.is_comment = False

    def get_next(self):
        if self.pos < len(self.src):
            self._read()
            return self.curr
        else:
            return None

    def _read(self):
        self.curr = self._read_any()

    def _read_any(self):
        curr_token = self.src[self.pos]
        if not self.is_comment:
            if curr_token in Term.operators:
                return self._read_term()
            elif curr_token in Expr.operators:
                return self._read_operator()
            elif curr_token in Parent.operators:
                return self._read_parent()
            elif curr_token.isdigit():
                return self._read_int()
            elif curr_token.isspace():
                self.pos += 1
                return self._read_any()
            elif curr_token == OPEN_COMMENT:
                self.pos += 1
                self.is_comment = True
                return self._read_any()
            else:
                raise ValueError('Unexpected token at index {id_}: {token}'
                                 .format(id_=self.pos,
                                         token=self.src[self.pos]))
        elif curr_token == CLOSE_COMMENT:
            self.pos += 1
            self.is_comment = False
            return self._read_any()
        else:
            self.pos += 1
            return self._read_any()

    def _read_parent(self):
        curr_token = self.src[self.pos]
        self.pos += 1
        if curr_token not in Parent.operators:
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))
        return Parent(curr_token, None)

    def _read_term(self):
        curr_token = self.src[self.pos]
        self.pos += 1
        if curr_token == MULT:
            return Term(MULT, None)
        elif curr_token == DIV:
            return Term(DIV, None)
        else:
            self.pos -= 1
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))

    def _read_operator(self):
        current_token = self.src[self.pos]
        self.pos +=1
        if current_token == '+':
            return Expr(PLUS, None)
        elif current_token == '-':
            return Expr(MINUS, None)
        else:
            self.pos -= 1
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))

    def _read_int(self):
        # actually reads an expression with * or / until it "wraps" in a + or -
        # token
        if not self.src[self.pos].isdigit():
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))
        val = 0
        while self.src[self.pos].isdigit():
            val = val * 10 + int(self.src[self.pos])
            self.pos += 1
            if self.pos >= len(self.src):
                break

        return Num(NUM, val)

class Parser:
    def __init__(self, src):
        self.tokens = Tokenizer(src)

    def analyze_parent(self):
        node = self.analyze_expr()
        if self.value.type_ != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                             .format(self.value.type_))
        return node

    def analyze_unary(self, value):
        return UnOp(value, [self.analyze_factor()])

    def analyze_factor(self):
        self.value = self.tokens.get_next()
        if self.value.type_ == OPEN_PARENT:
            return self.analyze_parent()
        elif self.value.type_ == MINUS:
            return self.analyze_unary(MINUS)
        elif self.value.type_ == PLUS:
            return self.analyze_unary(PLUS)
        elif self.value.type_ == NUM:
            return IntVal(self.value.value, [])
        else:
            raise ValueError('Unexpected token type, expected factor, got {}',
                             self.value.type_)

    def analyze_term(self):
        node = self.analyze_factor()
        self.value = self.tokens.get_next()
        while self.value is not None and self.value.type_ in Term.operators:
            node = BinOp(self.value.type_, [node, self.analyze_factor()])
            self.value = self.tokens.get_next()
        return node

    def analyze_expr(self):
        node = self.analyze_term()
        while self.value is not None and self.value.type_ in Expr.operators:
            node = BinOp(self.value.type_, [node, self.analyze_term()])
        return node


if __name__ == '__main__':
    # for debugging
    try:
        file_name = sys.argv[1]
    except IndexError:
        # no arg was passed
        file_name = STD_FILE_NAME

    try:
        with open(file_name, 'r') as fin:
            for line in fin:
                line = line.strip()
                parser = Parser(line)
                print(line, '=' , parser.analyze_expr().evaluate())

    except IOError as err:
        print(err)
