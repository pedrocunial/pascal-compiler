class Token:
    plus = '+'
    minus = '-'
    int_ = 'int'
    operators = [plus, minus]

    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value


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
        if curr_token in Token.operators:
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


    def _read_operator(self):
        current_token = self.src[self.pos]
        self.pos +=1
        if current_token == '+':
            return Token(Token.plus, None)
        elif current_token == '-':
            return Token(Token.minus, None)
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

        return Token(Token.int_, val)


class Parser:
    def __init__(self, src):
        self.tokens = Tokenizer(src)

    def analyse_exp(self):
        val = self.tokens.get_next()
        if val is None:
            return 0
        res = val.value
        val = self.tokens.get_next()
        while val is not None:
            if val.type_ == Token.plus:
                val = self.tokens.get_next()
                if val.type_ == Token.int_:
                    res += val.value
                else:
                    raise ValueError('Unexpected token type, expected int, got {}'
                                     .format(val.type_))
            elif val.type_ == Token.minus:
                val = self.tokens.get_next()
                if val.type_ == Token.int_:
                    res -= val.value
                else:
                    raise ValueError('Unexpected token type, expected int, got {}'
                                     .format(val.type_))
            else:
                print(res)
                raise ValueError('Unexpected token type, expected operator, got {}'
                                 .format(val.type_))
            val = self.tokens.get_next()
        return res

if __name__ == '__main__':
    # for debugging
    while True:
        val = input()
        if val == 'exit':
            break
        parser = Parser(val)
        print('result: {}'.format(parser.analyse_exp()))
