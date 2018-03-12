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
            return Term(MULT, MULT)
        elif curr_token == DIV:
            return Term(DIV, DIV)
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

    def analyse_parent(self):
        res = self.analyse_exp()
        if self.val.type_ != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                             .format(self.val.type_))
        return res

    def analyse_unary(self, sign):
        if sign not in SIGNS:
            raise ValueError('Unexpected token type, expected sign, got {}'
                             .format(self.val.type_))
        return self.analyse_factor() if sign == PLUS else -self.analyse_factor()

    def analyse_factor(self):
        self.val = self.tokens.get_next()
        if self.val.type_ == OPEN_PARENT:
            return self.analyse_parent()
        elif self.val.type_ == MINUS:
            return self.analyse_unary(MINUS)
        elif self.val.type_ == PLUS:
            return self.analyse_unary(PLUS)
        elif self.val.type_ == NUM:
            return self.val.value
        else:
            raise ValueError('Unexpected token type, got {}'
                             .format(self.val.type_))

    def analyse_term(self):
        res = self.analyse_factor()
        self.val = self.tokens.get_next()

        while self.val is not None and self.val.type_ in Term.operators:
            if self.val.type_ == MULT:
                res *= self.analyse_factor()
            elif self.val.type_ == DIV:
                res //= self.analyse_factor()
            self.val = self.tokens.get_next()
        return res

    def analyse_exp(self):
        res = self.analyse_term()
        while self.val is not None and self.val.type_ in Expr.operators:
            if self.val.type_ == PLUS:
                res += self.analyse_term()
            elif self.val.type_ == MINUS:
                res -= self.analyse_term()
        return res


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
                print('{} = {}'.format(line, parser.analyse_exp()))
    except IOError as err:
        print(err)
