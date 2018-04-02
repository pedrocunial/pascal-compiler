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
DOUBLE_DOTS = ':'
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
RESERVED_WORDS = [PRINT, BEGIN, END, ASIGNER]
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
    pass

class RWord(Token):
    operators = [ASIGNER, BEGIN, END, DOUBLE_DOTS, SEMICOLON, PRINT]

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

class Statements(Node):
    def evaluate(self, symbol_table):
        print("\n\n====== starting =======\n\n")
        for child in self.children: child.evaluate(symbol_table)

class BinOp(Node):

    def evaluate(self, symbol_table):
        # this if is unnecessary
        if len(self.children) != 2:
            raise ValueError('Unexpected children len for node, expected 2, got',
                             len(self.children))
        if self.value == ASIGNER:
            print('doing asigner', self.children[0], self.children[1])
            symbol_table.set_identifier(self.children[0].value,
                                        self.children[1].evaluate(symbol_table))
            print(symbol_table.table)
            return None

        print('not doing asigner', [c for c in self.children])
        children_values = [c.evaluate(symbol_table) for c in self.children]
        if self.value == PLUS:
            return children_values[0] + children_values[1]
        elif self.value == MINUS:
            return children_values[0] - children_values[1]
        elif self.value == DIV:
            return children_values[0] // children_values[1]
        elif self.value == MULT:
            return children_values[0] * children_values[1]
        else:  # this should NEVER happen!
            raise ValueError('Unexpected value for BinOp, got', self.value)

class UnOp(Node):
    def evaluate(self, symbol_table):
        # this if is unnecessary
        if len(self.children) != 1:
            raise ValueError('Unexpected children len for node, expected 1, got',
                             len(self.children))
        print('UnOp#evaluate', self.value, self.children)
        child_value = self.children[0].evaluate(symbol_table)
        if self.value == PLUS:
            return child_value
        elif self.value == MINUS:
            return -child_value
        elif self.value == PRINT:
            print('#evaluate print', child_value)
            return None
        else:
            raise ValueError('Unexpected value for UnOp, got', self.value)

class IntVal(Node):
    def evaluate(self, symbol_table):
        return self.value

class VarOp(Node):
    def evaluate(self, symbol_table):
        return symbol_table.get_identifier(self.value)

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
        if self.pos >= len(self.src):
            return None
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
            elif curr_token == SEMICOLON:
                self.pos += 1
                print('#read_any', curr_token)
                return RWord(RWORD, SEMICOLON)
            elif curr_token == OPEN_COMMENT:
                self.pos += 1
                self.is_comment = True
                return self._read_any()
            elif curr_token.isalpha() or curr_token == UNDERSCORE or \
                 curr_token in RWord.operators:
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
        char = self.src[self.pos]
        word = ''
        if char == DOUBLE_DOTS:
            self.pos += 1
            word += char + self.src[self.pos]
            if word.strip() != ASIGNER:
                print('beep', word)
                raise ValueError ('Unexpected token, expected =, got {}'\
                                    .format(word[-1]))
            self.pos += 1
            char = ''

        while char.isalpha() or char == UNDERSCORE:
            word += char
            self.pos += 1
            char = self.src[self.pos]
        word = word.strip() if word != '' else char
        print('#read_word', word)
        return Word(RWORD if word in RWord.operators else VAR, word)

    def _read_parent(self):
        curr_token = self.src[self.pos]
        print('#read_parent', curr_token)
        self.pos += 1
        if curr_token not in Parent.operators:
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))
        return Parent(curr_token, curr_token)

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
        self.value = self.tokens.get_next()

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
        # print(self.value.value)
        if self.value.type_ == OPEN_PARENT:
            return self.analyze_parent()
        elif self.value.type_ == MINUS:
            return self.analyze_unary(MINUS)
        elif self.value.type_ == PLUS:
            return self.analyze_unary(PLUS)
        elif self.value.type_ == NUM:
            # print('ni hao')
            return IntVal(self.value.value, [])
        elif self.value.type_ == VAR:
            # print('ohai')
            return VarOp(self.value.value, [])
        else:
            raise ValueError('Unexpected token type, expected factor, got {}',
                             self.value.type_)

    def analyze_term(self):
        node = self.analyze_factor()
        print('#analyze_term', node.value)
        self.value = self.tokens.get_next()
        print('#analyze_term value', self.value.value)
        while self.value is not None and self.value.type_ in Term.operators:
            node = BinOp(self.value.type_, [node, self.analyze_factor()])
            self.value = self.tokens.get_next()
        return node

    def analyze_expr(self):
        node = self.analyze_term()
        print('#analyze_expr', node.value)
        while self.value is not None and self.value.type_ in Expr.operators:
            node = BinOp(self.value.type_, [node, self.analyze_term()])
        print('#analyze_expr value', self.value.value)
        return node

    def analyze_print(self):
        self.value = self.tokens.get_next()
        print('print = ', self.value.value)
        if self.value.type_ != OPEN_PARENT:
            raise ValueError('Unexpected token type, expected (, got', self.value.type_)
        node = self.analyze_expr()
        # self.value = self.tokens.get_next()
        if self.value.value != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                                .format(self.value.value))
        res = UnOp(PRINT, [node])
        print(UnOp)
        self.value = self.tokens.get_next()
        return res

    def analyze_attr(self):
        var = self.value.value
        print('var =', var)
        print('var_type =', self.value.type_)
        self.value = self.tokens.get_next()
        print('#analyze_attr', self.value.value)
        if self.value.value != ASIGNER:
            raise ValueError('Unexpected token type, expected \':=\' got "{}"'
                                .format(self.value.value))
        return BinOp(ASIGNER, [VarOp(var, []), self.analyze_expr()])

    def analyze_cmd(self):
        print('cmd =', self.value.value)
        if self.value.type_ == VAR:
            # atribuicao
            return self.analyze_attr()
        elif self.value.type_ == RWORD:
            # reserved word
            if self.value.value == PRINT:
                return self.analyze_print()
            elif self.value.value == BEGIN:
                return self.analyze_cmds()
            else:
                raise ValueError('Unexpected word {}, expected print'
                                 .format(self.value.value))
        else:
            raise ValueError('Unexpected word {}, expected begin, print or a variable name'
                            .format(self.value.value))

    def analyze_cmds(self):
        if self.value.value != BEGIN:
            raise ValueError('Unexpected token type, expected {}, got {}'
                             .format(BEGIN, self.value.value))

        nodes = []
        self.value = self.tokens.get_next()
        while self.value is not None and self.value.value not in TERMINATORS:
            nodes.append(self.analyze_cmd())
            self.value = self.tokens.get_next()
        return Statements(None, nodes)


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
            st = SymbolTable()
            print(src)
            parser.analyze_cmds().evaluate(st)

    except IOError as err:
        print(err)
