# pascal-compiler
Yep, you read it

## EBNF

```
programa = progdec, bloco, '.';
bloco = ['var', vardec], [funcdec], comandos;
progdec = 'program', identificador, ';';
vardec = {identificador, {',', identificador}, ':', tipo, ';'}
funcdec = 'function', identificador, '(', vardec, ')', ':', tipo, ';', bloco,
tipo = ('boolean' | 'integer');
comandos = 'begin', comando, {';', comando}, 'end';
comando = atribuicao | comandos | print | if | while;
if = 'if', expressao, 'then', comando, ['else', comando];
while = 'while', expressao, 'do', comando;
print = 'print', '(', expressao, ')';
atribuicao = identificador, ':=', (expressao | read);
read = 'read', '(', ')';
expressao = expressao_simples, {('<' | '>' | '='), expressao_simples};
expressao_simples = termo, {('or' | '+', '-'), termo};
termo = fator, { ('*' | '/' | 'and'), fator };
fator = ({'+' | '-' | 'not'}, fator) | numero | '(', expressao, ')' | identificador;
identificador = (letra | '_'), {letra | digito | '_'};
numero = digito, {digito};
letra = (a | ... | z | A | ... | Z);
digito = (0 | ... | 9);
```

## Diagrama Sintático

![diagrama sintatico roteiro 8](img/r8.jpeg)
