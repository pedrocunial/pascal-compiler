# pascal-compiler
Yep, you read it

## EBNF
```
expr = term (('+' | '-') term)*
term = fact (('*' | '/') fact)*
fact = '(' expr ')' | num | ('-'|'+') fact
```

Nova EBNF
```
comandos = 'begin', commando, {';', comando}, 'end';
comando = atribuicao | comandos | print;
print = 'print', '(', expressao, ')';
atribuicao = identificador, ':=', expressao;
expressao = termo, { ('+' | '-'), termo};
termo = fator, { ('*' | '/'), fator };
fator = {'+' | '-'}, fator | numero | '(', expressao, ')' | identificador;
identificador = (letra | '_'), { letra | digito | '_'};
numero = digito, {digito};
letra = (a | ... | z | A | ... | Z);
digito = (0 | ... | 9);
```
