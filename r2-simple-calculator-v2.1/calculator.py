DIV = '/'
PLUS = '+'
MULT = '*'
MINUS = '-'
NUM = 'int'


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

class Tokenizer:
    def __init__(self, src, pos=0, curr=None):
        self.src = src
        self.pos = pos
        self.curr = curr

    def get_next(self):
        if self.pos < len(self.src):
            self._read()
            return self.curr
        else:
            return None

    def _read(self):
        if self.curr is None and self.pos == 0:
            self.curr = self._read_int()
        else:
            self.curr = self._read_any()


    def _read_any(self):
        curr_token = self.src[self.pos]
        if curr_token in Term.operators:
            return self._read_term()
        elif curr_token in Expr.operators:
            return self._read_operator()
        elif curr_token.isdigit():
            return self._read_int()
        elif curr_token.isspace():
            self.pos += 1
            return self._read_any()
        else:
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))

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
        if not self.src[self.pos].isdigit():
            raise ValueError('Unexpected token at index {id_}: {token}'
                             .format(id_=self.pos,
                                     token=self.src[self.pos]))
        val = 0
        while self.src[self.pos].isdigit():
            val += val * 10 + int(self.src[self.pos])
            self.pos += 1
            if self.pos >= len(self.src):
                break

        return Num(NUM, val)

class Parser:
    def __init__(self, src):
        self.tokens = Tokenizer(src)

    def analyse_term(self):
        self.val = self.tokens.get_next()
        if self.val.type_ != NUM:
            raise ValueError('Unexpected token type, expected int, got {}'
                                .format(self.val.type_))
        res = self.val.value
        self.val = self.tokens.get_next()

        while self.val is not None and self.val.type_ in Term.operators:
            if self.val.type_ == MULT:
                self.val = self.tokens.get_next()
                if self.val.type_ == NUM:
                    res *= self.val.value
                else:
                    raise ValueError('Unexpected token type, expected int, got {}'
                                        .format(self.val.type_))

            elif self.val.type_ == DIV:
                self.val = self.tokens.get_next()
                if self.val.type_ == NUM:
                    res //= self.val.value
                else:
                    raise ValueError('Unexpected token type, expected int, got {}'
                                        .format(self.val.type_))

            self.val = self.tokens.get_next()
        return res

    def analyse_exp(self):
        res = self.analyse_term()
        while self.val is not None:
            if self.val.type_ == PLUS:
                res += self.analyse_term()
            elif self.val.type_ == MINUS:
                res -= self.analyse_term()
        return res

if __name__ == '__main__':
    # for debugging
    while True:
        val = input()
        if val == 'exit':
            break
        parser = Parser(val)
        print('result: {}'.format(parser.analyse_exp()))
