import sys
from random import randint


DIV = '/'
PLUS = '+'
MULT = '*'
MINUS = '-'

TRUE = 'true'
FALSE = 'false'
AND = 'and'
OR = 'or'
NOT = 'not'
BEGIN = 'begin'
END = 'end'
PRINT = 'print'
READ = 'read'
IF = 'if'
DO = 'do'
ELSE = 'else'
THEN = 'then'
WHILE = 'while'
PROGRAM = 'program'

GT = '>'
LT = '<'
DOT = '.'
COMMA = ','
EQUALS = '='
ASSIGNER = ':='
SEMICOLON = ';'
DOUBLE_DOTS = ':'
UNDERSCORE = '_'
OPEN_PARENT = '('
CLOSE_PARENT = ')'
OPEN_COMMENT = '{'
CLOSE_COMMENT = '}'

INTEGER_TYPE = 'integer'
BOOLEAN_TYPE = 'boolean'

NUM = 'int'
VAR = 'var'
RWORD = 'rword'
STD_FILE_NAME = 'test.pas'

SIGNS = [PLUS, MINUS, NOT]
COMPARISON = [GT, LT, EQUALS]
TERMINATORS = [END, DOT]
CONDITIONALS = [IF, ELSE]


class Token:
    operators = []

    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value


class Term(Token):
    operators = [MULT, DIV, AND]


class Num(Token):
    operators = []


class Expr(Token):
    operators = [PLUS, MINUS, OR]


class Parent(Token):
    operators = [OPEN_PARENT, CLOSE_PARENT]


class Word(Token):
    pass


class RWord(Token):
    operators = [ASSIGNER, BEGIN, END, DOUBLE_DOTS,
                 SEMICOLON, PRINT, READ, AND, NOT, OR,
                 IF, THEN, DO, WHILE, DOT, COMMA, ELSE]


class Variable:
    possible_types = [INTEGER_TYPE, BOOLEAN_TYPE]

    def __init__(self, type_, value=None):
        self.type_ = type_
        self.value = value

    def set_value(self, value):
        self.value = value


class IntVar(Variable):
    possible_types = [INTEGER_TYPE]

    def __init__(self, value=None):
        self.type_ = INTEGER_TYPE
        self.value = value

    def set_value(self, value):
        try:
            value = int(value)
        except ValueError as e:
            raise ValueError('Unmatching type for int variable')
        self.value = value


class BoolVar(Variable):
    possible_types = [BOOLEAN_TYPE]

    def __init__(self, value=None):
        self.type_ = BOOLEAN_TYPE
        self.value = value

    def set_value(self, value):
        if value == FALSE:
            self.value = False
        elif value == TRUE:
            self.value = True
        else:
            self.value = bool(value)


def variable_factory(type_, value=None):
    if type_ == INTEGER_TYPE:
        return IntVar(value)
    elif type_ == BOOLEAN_TYPE:
        return BoolVar(value)
    else:
        raise ValueError(
            'Unsupported type {}, wait for the next version (maybe...)'
            .format(type_)
        )


class SymbolTable:
    def __init__(self):
        self.table = {}

    def add_identifier(self, identifier, value):
        if identifier in self.table:
            print('[WARN] identifier already in symbol table, overriding it')
        self.table[identifier] = value

    def set_identifier(self, identifier, value):
        ''' value is a variable type '''
        if identifier not in self.table:
            raise ValueError('Undefined variable {}'.format(identifier))
        self.table[identifier].set_value(value)

    def get_identifier(self, identifier):
        if identifier not in self.table:
            raise ValueError('Identifier {} not in symbol table'
                             .format(identifier))
        return self.table[identifier].value

    def clear(self):
        self.table = {}


class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children

    def evaluate(self, symbol_table):
        pass


class Program(Node):
    def evaluate(self, symbol_table):
        for child in self.children:
            child.evaluate(symbol_table)


class VarBlock(Node):
    def evaluate(self, symbol_table):
        for child in self.children:
            child.evaluate(symbol_table)


class TriOp(Node):
    def evaluate(self, symbol_table):
        if self.value == IF:
            self.eval_if(symbol_table)

    def eval_if(self, st):
        return self.children[1 if self.children[0].evaluate(st)
                             else 2].evaluate(st)


class Statements(Node):
    def evaluate(self, symbol_table):
        for child in self.children:
            child.evaluate(symbol_table)


class BinOp(Node):
    def evaluate(self, symbol_table):
        # this if is unnecessary
        if len(self.children) != 2:
            raise ValueError('Unexpected children len for node, expected 2,\
            got {}'.format(len(self.children)))
        if self.value == ASSIGNER:
            symbol_table.set_identifier(self.children[0].value,
                                        self.children[1].evaluate(
                                            symbol_table))
            return None
        elif self.value == WHILE:
            return self.eval_while(symbol_table)
        elif self.value == DOUBLE_DOTS:  # variable declarations
            symbol_table.add_identifier(self.children[0],
                                        variable_factory(self.children[1],
                                                         None))
            return

        children_values = [c.evaluate(symbol_table) for c in self.children]
        if self.value == PLUS:
            return children_values[0] + children_values[1]
        elif self.value == MINUS:
            return children_values[0] - children_values[1]
        elif self.value == DIV:
            return children_values[0] // children_values[1]
        elif self.value == MULT:
            return children_values[0] * children_values[1]
        elif self.value == OR:
            return children_values[0] or children_values[1]
        elif self.value == AND:
            return children_values[0] and children_values[1]
        elif self.value == LT:
            return children_values[0] < children_values[1]
        elif self.value == GT:
            return children_values[0] > children_values[1]
        elif self.value == EQUALS:
            return children_values[0] == children_values[1]
        else:  # this should NEVER happen!
            raise ValueError('Unexpected value for BinOp, got', self.value)

    def eval_while(self, st):
        expr = self.children[0]
        stmt = self.children[1]
        while expr.evaluate(st):
            stmt.evaluate(st)


class ReadOp(Node):
    def evaluate(self, symbol_table):
        return int(input())


class UnOp(Node):
    def evaluate(self, symbol_table):
        # this if is unnecessary
        if len(self.children) != 1:
            raise ValueError('Unexpected children len for node, expected 1, \
            got {}'.format(len(self.children)))
        # print('UnOp#evaluate', self.value, self.children)
        child_value = self.children[0].evaluate(symbol_table)
        if self.value == PLUS:
            return child_value
        elif self.value == MINUS:
            return -child_value
        elif self.value == PRINT:
            print(child_value)
            return None
        elif self.value == NOT:
            return not child_value
        else:
            raise ValueError('Unexpected value for UnOp, got {}'
                             .format(self.value))


class IntVal(Node):
    def evaluate(self, symbol_table):
        return self.value


class Identifier(Node):
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
            elif curr_token in Expr.operators or curr_token in COMPARISON:
                return self._read_operator()
            elif curr_token in Parent.operators:
                return self._read_parent()
            elif curr_token.isdigit():
                return self._read_int()
            elif curr_token.isspace():
                self.pos += 1
                return self._read_any()
            elif curr_token == SEMICOLON or curr_token == COMMA:
                self.pos += 1
                print('#read_any', curr_token)
                return RWord(RWORD, curr_token)
            elif curr_token == OPEN_COMMENT:
                self.pos += 1
                self.is_comment = True
                return self._read_any()
            elif (curr_token.isalpha() or curr_token == UNDERSCORE or
                  curr_token in RWord.operators):
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
            if word.strip() != ASSIGNER:
                return Word(RWORD, DOUBLE_DOTS)
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
        return Term(curr_token, curr_token)

    def _read_operator(self):
        current_token = self.src[self.pos]
        self.pos += 1
        return Expr(current_token, current_token)

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
        self.value = self.tokens.get_next()

    def analyze_parent(self):
        node = self.analyze_expr()
        if self.value.type_ != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                             .format(self.value.type_))
        return node

    def analyze_unary(self, value):
        return UnOp(value, [self.analyze_factor()])

    def analyze_not(self):
        print('#analyze_not')
        return UnOp(NOT, [self.analyze_factor()])

    def analyze_factor(self):
        self.value = self.tokens.get_next()
        print('#analyze_factor:', self.value.value)
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
            return Identifier(self.value.value, [])
        elif self.value.type_ == RWORD and self.value.value == READ:
            return self.analyze_read()
        elif self.value.type_ == RWORD and self.value.value == NOT:
            return self.analyze_not()
        else:
            raise ValueError('Unexpected token type, expected factor, got {}'
                             .format(self.value.type_))

    def analyze_read(self):
        self.value = self.tokens.get_next()
        if self.value is not None and self.value.type_ != OPEN_PARENT:
            raise ValueError('Unexpected token type, expected (, got {}'
                             .format(self.value.type_))

        self.value = self.tokens.get_next()
        if self.value is not None and self.value.type_ != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                             .format(self.value.type_))

        return ReadOp(RWORD, [])

    def analyze_term(self):
        print('#analyze_term start:', self.value.value)
        node = self.analyze_factor()
        print('#analyze_term', node.value)
        self.value = self.tokens.get_next()
        print('#analyze_term value', self.value.value)
        while self.value is not None and self.value.value in Term.operators:
            print('#analyze_term -- in loop,', self.value.value)
            node = BinOp(self.value.value, [node, self.analyze_factor()])
            self.value = self.tokens.get_next()
        print('#analyze_term -- exit', self.value.value)
        return node

    def analyze_expr(self):
        print('#analyze_expr', self.value.value)
        node = self.analyze_simple_expr()
        while self.value is not None and self.value.type_ in COMPARISON:
            print('#analyze_expr -- in loop', self.value.value)
            node = BinOp(self.value.value, [node, self.analyze_simple_expr()])
        print('#analyze_expr -- exit', self.value.value)
        return node

    def analyze_simple_expr(self):
        print('#analyze_simple_expr begin:', self.value.value)
        node = self.analyze_term()
        print('#analyze_simple_expr node:', node.value)
        print('#analyze_simple_expr value:', self.value.value)
        while self.value is not None and self.value.value in Expr.operators:
            print('#analyze_simple_expr -- in loop::', self.value.value)
            node = BinOp(self.value.value, [node, self.analyze_term()])
        print('#analyze_simple_expr -- exit:', self.value.value)
        return node

    def analyze_print(self):
        self.value = self.tokens.get_next()
        print('print = ', self.value.value)
        if self.value.type_ != OPEN_PARENT:
            raise ValueError('Unexpected token type, expected (, got {}'
                             .format(self.value.type_))
        node = self.analyze_expr()
        # self.value = self.tokens.get_next()
        if self.value.value != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                             .format(self.value.value))
        res = UnOp(PRINT, [node])
        print('#analyze_print, result::', res)
        # self.value = self.tokens.get_next()
        return res

    def analyze_attr(self):
        var = self.value.value
        print('var =', var)
        print('var_type =', self.value.type_)
        self.value = self.tokens.get_next()
        print('#analyze_attr', self.value.value)
        if self.value.value != ASSIGNER:
            raise ValueError('Unexpected token type, expected \':=\' got "{}"'
                             .format(self.value.value))
        return BinOp(ASSIGNER, [Identifier(var, []), self.analyze_expr()])

    def analyze_while(self):
        print('#analyze_while')
        # self.value = self.tokens.get_next()
        has_parentesis = self.value.type_ == OPEN_PARENT
        expr_node = self.analyze_expr()
        if has_parentesis and self.value.type_ != CLOSE_PARENT:
            raise ValueError('Unexpected token type, expected ), got {}'
                             .format(self.value.value))
        print('#analyze_while -- read expr, reading do...', self.value.value)
        # self.value = self.tokens.get_next()
        if self.value.value != DO:
            raise ValueError('Unexpected token type, expected "do", got {}'
                             .format(self.value.value))
        print('#analyze_while, read do! yay')
        self.value = self.tokens.get_next()  # for the analyze_stmts bellow
        return BinOp(WHILE, [expr_node, self.analyze_stmts()])

    def analyze_if(self):
        print('#analyze_if -- begin:', self.value.value)
        expr_node = self.analyze_expr()
        print('#analyze_if -- after expr:', self.value.value)
        if self.value.value != THEN:
            raise ValueError('Unexpected token type, expected "then", got {}'
                             .format(self.value.value))
        self.value = self.tokens.get_next()
        print('#analyze_if -- before true branch', self.value.value)
        true_branch = self.analyze_stmt()
        print('#analyze_if -- after true branch', self.value.value)

        self.value = self.tokens.get_next()
        if self.value.value == ELSE:
            print('#analyze_if -- found else')
            self.value = self.tokens.get_next()
            false_branch = self.analyze_stmt()
        else:
            print('#analyze_if -- no else')
            false_branch = NoOp(None, None)

        print('#analyze_if -- EXITING')
        return TriOp(IF, [expr_node, true_branch, false_branch])

    def analyze_stmt(self):
        # analyze statement
        print('stmt =', self.value.value)
        if self.value.type_ == VAR:
            # atribuicao
            return self.analyze_attr()
        elif self.value.type_ == RWORD:
            # reserved word
            if self.value.value == PRINT:
                return self.analyze_print()
            elif self.value.value == BEGIN:
                return self.analyze_stmts()
            elif self.value.value == WHILE:
                return self.analyze_while()
            elif self.value.value == IF:
                return self.analyze_if()
            else:
                raise ValueError('Unexpected word {}, expected a reserved word'
                                 .format(self.value.value))
        else:
            raise ValueError('Unexpected word {}, expected begin, print or a \
            variable name'.format(self.value.value))

    def analyze_stmts(self):
        # analyze statements
        _id = randint(0, 10000)  # for identifing inner stmts (debug)
        print('#analyze_stmts -- begin #{}'.format(_id))
        if self.value.value != BEGIN:
            raise ValueError('Unexpected token type, expected {}, got {}'
                             .format(BEGIN, self.value.value))

        nodes = []
        self.value = self.tokens.get_next()
        while self.value is not None and self.value.value not in TERMINATORS:
            print('#analyze_stmts#{}:'.format(_id), self.value.value)
            nodes.append(self.analyze_stmt())
            self.value = self.tokens.get_next()
            print('#analyze_stmts#{} -- next value: {}'
                  .format(_id, self.value.value))
            while self.value is not None and self.value.value == SEMICOLON:
                # allows for infinite ; tokens
                print('#analyze_stmts, got semicolon')
                self.value = self.tokens.get_next()

        return Statements(None, nodes)

    def analyze_program(self):
        if self.value.value != PROGRAM:
            raise ValueError('Unexpected token value {}, expected "program" \
            keyword'.value.value)

        # get program name
        self.value = self.tokens.get_next()
        if self.value.type_ == RWORD:
            raise ValueError('Program name cannot be a reserved word!')
        elif self.value.type_ != VAR:
            raise ValueError('Unexpected type {}, expected a variable-like\
            name'.format(self.value.type_))
        prog_name = self.value.value

        self.value = self.tokens.get_next()  # should be ;
        if self.value.value == DOT:
            return prog_name  # end of the program
        elif self.value.value != SEMICOLON:
            raise ValueError('Expected ";", got {}'.format(self.value.value))

        # get next token (standard)
        self.value = self.tokens.get_next()
        return prog_name

    def has_ended(self):
        return self.value.value == DOT

    def analyze_variable_declarations(self):
        if self.value.value != VAR:
            print('[WARN] No variable declaration block found')
            return
        self.value = self.tokens.get_next()  # first get variable name
        var_names = []
        var_nodes = []
        while self.value.type_ == VAR:
            var_names.append(self.value.value)
            self.value = self.tokens.get_next()
            if self.value.value == COMMA:
                print('#analyze_var_dec inside loop, got comma')
                self.value = self.tokens.get_next()
            if self.value.value == DOUBLE_DOTS:
                # get vars type
                self.value = self.tokens.get_next()
                var_type = self.value.value
                if var_type not in Variable.possible_types:
                    raise ValueError('Unsupported variable type {}'
                                     .format(self.value.value))
                # add variables to symbol table
                for var in var_names:
                    var_nodes.append(BinOp(DOUBLE_DOTS, [var, var_type]))
                var_names = []
                self.value = self.tokens.get_next()
                if self.value.value != SEMICOLON:
                    raise ValueError('Excpected semicolon, got {}'
                                     .format(self.value.value))
                self.value = self.tokens.get_next()
        return var_nodes

    def run(self):
        program_name = self.analyze_program()
        if self.has_ended():
            # program end
            return NoOp(None, None)
        print('#run -- before var_nodes', self.value.value)
        var_nodes = self.analyze_variable_declarations()
        body_nodes = self.analyze_stmts()
        return Program(program_name, [
            VarBlock(None, var_nodes),
            body_nodes
        ])


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
            result = parser.run()
            print('\n\n================== result ====================\n\n')
            result.evaluate(st)

    except IOError as err:
        print(err)
