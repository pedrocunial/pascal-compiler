package main

// [WIP] (!!!!)

import (
	"os"
	"fmt"
	"log"
	"bufio"
	"errors"
	"unicode"
)

const DIV = '/'
const PLUS = '+'
const MULT = '*'
const MINUS = '-'
const NUM = "int"
const OPEN_PARENT = '('
const CLOSE_PARENT = ')'
const OPEN_COMMENT = '{'
const CLOSE_COMMENT = '}'
const STD_FILE_NAME = "test.in"
var NUMS_OP = map[rune]bool{}
var TERM_OP = map[rune]bool {MULT: true, DIV: true}
var EXPR_OP = map[rune]bool {PLUS: true, MINUS: true}  // same for sign_op
var PARENT_OP = map[rune]bool {OPEN_PARENT: true, CLOSE_PARENT: true}

type Token struct {
	value int
	type_ string
}

type Tokenizer struct {
	is_comment bool
	pos int
	src string
	curr *Token
}

type Parser struct {
	tokens *Tokenizer
}

func (t *Tokenizer) GetNext() (*Token, error) {
	if t.pos < len(t.src) {
		if err := t.read(); err != nil {
			return nil, err
		}
		return t.curr, nil
	} else {
		return nil, nil
	}
}

func (t *Tokenizer) read() error {
	// tbh i dont know why i'm using both read and readany at this point...
	var err error
	t.curr, err = t.readAny()
	return err
}

func (t *Tokenizer) readAny() (*Token, error) {
	curr_token := rune(t.src[t.pos])
	if !t.is_comment {
		if _, present := TERM_OP[curr_token]; present {
			return t.readTerm(curr_token)
		} else if _, present := EXPR_OP[curr_token]; present {
			return t.readExpr(curr_token)
		} else if _, present := PARENT_OP[curr_token]; present {
			return t.readParent(curr_token)
		} else if unicode.IsDigit(curr_token) {
			return t.readInt()
		} else if unicode.IsSpace(curr_token) {
			t.pos++
			return t.readAny()
		} else if curr_token == OPEN_COMMENT {
			t.pos++
			t.is_comment = true
			return t.readAny()
		} else {
			return nil, errors.New(
				fmt.Sprintf("Unexpected token at index %d: %s", t.pos, curr_token))
		}
	} else if curr_token == CLOSE_COMMENT {
		t.pos++
		t.is_comment = false
		return t.readAny()
	} else {
		t.pos++
		return t.readAny()
	}
	return nil, errors.New("How did you even get here?")
}

func (t *Tokenizer) readParent(curr_token rune) (*Token, error) {
	t.pos++  // prolly should be incrementing position in #readAny
	return &Token{0, string(curr_token)}, nil
}

func (t *Tokenizer) readTerm(curr_token rune) (*Token, error) {
	t.pos++  // this is literally the same func as above... what have i done ;-;
	return &Token{0, string(curr_token)}, nil
}

func (t *Tokenizer) readExpr(curr_token rune) (*Token, error) {
	t.pos++ // oh not again...
	return &Token{0, string(curr_token)}, nil
}

func (t *Tokenizer) readInt() (*Token, error) {
	// actually reads an expression with * or / until it "wraps" in a + or - token
	val := 0
	for t.pos < len(t.src) && unicode.IsDigit(rune(t.src[t.pos])) {
		val = val * 10 + rtoi(rune(t.src[t.pos]))
		t.pos++
	}
	return &Token{val, NUM}, nil
}

func rtoi(r rune) int {
	return int(r) - '0'
}

func validInMap(token *Token, test_map map[rune]bool) bool {
	if token != nil {
		if _, present := test_map[rune(token.type_[0])]; present {
			return true
		}
	}
	return false
}

func InitParser(src string) Parser {
	// """""constructor""""""
	return Parser{&Tokenizer{false, 0, src, nil}}
}

func (p Parser) AnalyseExp() (int, error) {
	res := 0
	var err error
	res, err = p.analyseTerm()
	if err != nil {
		return 0, err
	}
	for validInMap(p.tokens.curr, EXPR_OP) {
		currType := rune(p.tokens.curr.type_[0])
		if currType == PLUS {
			if val, err := p.analyseTerm(); err != nil {
				res += val
			}
		} else if currType == MINUS {
			if val, err := p.analyseTerm(); err != nil {
				res -= val
			}
		}
		if err != nil {
			return 0, err
		}
	}
	return res, nil
}

func (p Parser) analyseTerm() (int, error) {
	res := 0
	var err error
	if res, err = p.analyseFactor(); err != nil {
		return 0, err
	}
	if _, err := p.tokens.GetNext(); err != nil {
		return res, err
	}
	for validInMap(p.tokens.curr, TERM_OP) {
		currType := rune(p.tokens.curr.type_[0])
		if currType == MULT {
			if val, err := p.analyseFactor(); err != nil {
				res *= val
			}
		} else if currType == DIV {
			if val, err := p.analyseFactor(); err != nil {
				res /= val
			}
		}
		if err != nil {
			return res, err
		}
		if _, err = p.tokens.GetNext(); err != nil {
			return res, err
		}
	}
	return res, nil
}

func (p Parser) analyseFactor() (int, error) {
	var err error
	if _, err = p.tokens.GetNext(); err != nil {
		return 0, err
	}
	currType := rune(p.tokens.curr.type_[0])
	if p.tokens.curr.type_ == NUM {
		return p.tokens.curr.value, nil
	} else if currType == OPEN_PARENT {
		return p.analyseParent()
	} else if currType == MINUS {
		return p.analyseUnary(MINUS)
	} else if currType == PLUS {
		return p.analyseUnary(PLUS)
	} else {
		return 0, errors.New(
			fmt.Sprintf("Unexpected token type, expected factor token, got %s",
						p.tokens.curr.type_))
	}
	return 0, errors.New("How did you even get here?!")
}

func (p Parser) analyseUnary(sign rune) (int, error) {
	if sign == PLUS {
		return p.analyseFactor()
	} else if sign == MINUS {
		res, err := p.analyseFactor()
		return -res, err
	}
	return 0, errors.New(
		fmt.Sprintf("Unexpected token type, expected sign (+ or -) token, got %s", sign))
}

func (p Parser) analyseParent() (int, error) {
	res, err := p.AnalyseExp()
	if err != nil {
		return 0, err
	}
	currType := rune(p.tokens.curr.type_[0])
	if currType != CLOSE_PARENT {
		return 0, errors.New(
			fmt.Sprintf("Unexpected token type, expected ')', got %s", currType))
	}
	return res, nil
}

func main() {
	file, err := os.Open("./test.in")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()   // guarantees this will happen at the end!
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)

	for scanner.Scan() {
		line := scanner.Text()
		parser := InitParser(line)
		res, err := parser.AnalyseExp()
		if err != nil {
			log.Fatal(err)
			return
		}
		fmt.Printf("%s = %d\n", line, res)
	}
}