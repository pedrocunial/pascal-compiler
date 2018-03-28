import sys


DIV = '/'
PLUS = '+'
MULT = '*'
MINUS = '-'
BEGIN = 'begin'
END = 'end'
PRINT = 'print'
ASIGNER = ':='
SEMICOLON = ';'
UNDERSCORE = '_'
NUM = 'int'
VAR = 'var'
RWORD = 'rword'
OPEN_PARENT = '('
CLOSE_PARENT = ')'
OPEN_COMMENT = '{'
CLOSE_COMMENT = '}'
STD_FILE_NAME = 'test.pas'
SIGNS = [PLUS, MINUS]
RESERVED_WORDS = [PRINT, BEGIN, END]
TERMINATORS = [END, SEMICOLON]

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

class Word(Token):
    operators = []

class SymbolTable:
    def __init__(self):
        self.table = {}

    def set_identifier(self, identifier, value):
        self.table[identifier] = value

    def get_identifier(self, identifier):
        if identifier not in self.table:
            raise ValueError('Identifier {} not in symbol table'
                             .format(identifier))
        return self.table[identifier]

    def clear(self):
        self.table = {}

class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def evaluate(self, symbol_table):
        pass

class BinOp(Node):
    def to_int(key, symbol_table):
        if isinstance(key, str):
            return symbol_table.get_identifier(key)
        elif isinstance(key, int) or isinstance(key, float):
            return int(key)

    def evaluate(self, symbol_table):
        # this if is unnecessary
        if len(self.children) != 2:
            raise ValueError('Unexpected children len for node, expected 2, got',
                             len(self.children))
        children_values = [c.evaluate(symbol_table) for c in self.children]

        # do math
        if self.value == PLUS:
            return self.to_int(children_values[0], symbol_table) + \
                self.to_int(children_values[1], symbol_table)
        elif self.value == MINUS:
            return self.to_int(children_values[0], symbol_table) - \
                self.to_int(children_values[1], symbol_table)
        elif self.value == DIV:
            return self.to_int(children_values[0], symbol_table) // \
                self.to_int(children_values[1], symbol_table)
        elif self.value == MULT:
            return self.to_int(children_values[0], symbol_table) * \
                self.to_int(children_values[1], symbol_table)
        elif self.value == ASIGNER:
            symbol_table.set_identifier(children_values[0],
                                        self.to_int(children_values[1],
                                                    symbol_table))
        else:  # this should NEVER happen!
            raise ValueError('Unexpected value for BinOp, got', self.value)

class UnOp(Node):
    def evaluate(self, symbol_table):
        # this if is unnecessary
        if len(self.children) != 1:
            raise ValueError('Unexpected children len for node, expected 1, got',
                             len(self.children))
        child_value = self.children[0].evaluate(symbol_table)
        if self.value == PLUS:
            return child_value
        elif self.value == MINUS:
            return -child_value
        elif self.value == PRINT:
            print(child_value)
            return None
        else:
            raise ValueError('Unexpected value for UnOp, got', self.value)

class IntVal(Node):
    def evaluate(self, symbol_table):
        return self.value

class NoOp(Node):
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
            elif curr_token.isalpha() or curr_token == UNDERSCORE:
                return self._read_word()
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

    def _read_word(self):
        word = self.src[self.pos]
        char = word
        while char.isalpha() or char == UNDERSCORE:
            self.pos += 1
            char = self.src[self.pos]
            word += char
        return Word(word, RWORD if word in RESERVED_WORDS else VAR)

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
        self.symbol_table = SymbolTable()

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

    def analyze_cmd(self):
        self.value = self.tokens.get_next()
        if self.value.type_ == VAR:
            # atribuicao
            self.analyze_attr()
        elif self.value.type_ == RWORD:
            # reserved word
            if self.value.value == PRINT:
                self.analyze_print()
            else:
                raise ValueError('Unexpected word: ', self.value.value)


    def analyze_cmds(self):
        self.value = self.tokens.get_next()
        if self.value.value != BEGIN:
            raise ValueError('Unexpected token type, expected {}, got {}'
                             .format(BEGIN, begin))
        while self.value.value != END:
            self.analyze_cmd()


if __name__ == '__main__':
    # for debugging
    try:
        file_name = sys.argv[1]
    except IndexError:
        # no arg was passed
        file_name = STD_FILE_NAME

    try:
        with open(file_name, 'r') as fin:
            src = fin.read()
            parser = Parser(src)
            print(src)
            # print(line, '=' , parser.analyze_expr().evaluate(parser.symbol_table))

    except IOError as err:
        print(err)
