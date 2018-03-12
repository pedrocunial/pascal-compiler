# pascal-compiler
Yep, you read it

## EBNF
```
expr = term (('+' | '-') term)*
term = fact (('*' | '/') fact)*
fact = '(' expr ')' | num | ('-'|'+') fact
```
