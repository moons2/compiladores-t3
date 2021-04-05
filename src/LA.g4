// titulo:
//    Gramatica regular da Linguagem Algoritmica (LA)
//    TRABALHO 3 - COMPILADORES 1
//
// autores:
//    Luan V. Moraes da Silva - 744342
//    Guilherme Servidoni - 727339
//    Alisson Roberto Gomes - 725721
    
grammar LA;

fragment
LETRA: 'A'..'Z' | 'a'..'z';

fragment
DIGITO: '0'..'9';

// definicao de erro de comentario
// ERR_COMENT: ('{' ~('}')* '\n');

COMENTARIO: '{' ~('\n'|'\r'|'{'|'}')* '}' -> skip;

// definicao de erro de cadeia
// ERR_CADEIA: '"' ~('"')* '\n';


PALAVRA_RESERVADA: 'algoritmo' | 'fim_algoritmo' | 'declare' | 'constante' | 'tipo' | 'literal' 
   | 'inteiro' | 'real' | 'logico' | 'verdadeiro' | 'falso' | 'registro' | 'fim_registro'
   | 'procedimento' | 'fim_procedimento' | 'funcao' | 'fim_funcao' | 'leia' | 'escreva'
   | 'se' | 'entao' | 'senao' | 'fim_se' | 'caso' | 'fim_caso' | 'seja' | 'para' | 'fim_para'
   | 'ate' | 'faca' | 'enquanto' | 'fim_enquanto' | 'retorne' | 'var' ;

// endereco e concatenacao
OP_UNARIO: '&' | ',';

OP_RELACIONAL: '>' | '>=' | '<' | '<=' | '<>' | '=';

OP_ARIT: '+' | '-' | '*' | '/' | '%' | '^';

OP_LOGICO: 'nao' | 'ou' | 'e';

OUTRO_OP: '.' | '..';

DECLARADOR: ':';

ATRIBUIDOR: '<-';

DELIMITADOR: '(' | ')' | '[' | ']';

NUM_INT: (DIGITO)+;

NUM_REAL: (DIGITO)+ '.' (DIGITO)+;

IDENT: (LETRA | '_') (LETRA | DIGITO | '_')*;

// definição anterior de cadei apresentou erros na interpretação
// CADEIA: '"' ( '\\"' | ~('"' | '\\' | '\n') )* '"';
CADEIA: '"' ( '\\"' | ~('"') )*? '"';

WS: (' ' | '\t' | '\n' | '\r') -> skip;

// simbolo nao identificado
// ERR_SIMBOLO: . ;

// definicoes da gramatica conforme fornecido

programa: declaracoes 'algoritmo' corpo 'fim_algoritmo';
declaracoes: (decl_local_global)*;
decl_local_global: declaracao_local | declaracao_global;
declaracao_local: 'declare' variavel | 'constante' IDENT ':' tipo_basico '=' valor_constante | 'tipo' IDENT ':' tipo;
variavel: identificador (',' identificador)* ':' tipo;

identificador: IDENT ('.' IDENT)* dimensao;
dimensao: ('[' exp_aritmetica ']')*;
tipo: registro | tipo_estendido;
tipo_basico: 'literal' | 'inteiro' | 'real' | 'logico';
tipo_basico_ident: tipo_basico | IDENT;
tipo_estendido: '^'? tipo_basico_ident;
valor_constante: CADEIA | NUM_INT | NUM_REAL | 'verdadeiro' | 'falso';

registro: 'registro' variavel* 'fim_registro';
declaracao_global: 'procedimento' IDENT '(' parametros? ')' declaracao_local* (cmd)* 'fim_procedimento' | 'funcao' IDENT '(' (parametros)? ')' ':' tipo_estendido (declaracao_local)* (cmd)* 'fim_funcao';
parametro: 'var'? identificador (',' identificador)* ':' tipo_estendido;
parametros: parametro (',' parametro)*;
corpo: (declaracao_local)* (cmd)*;


// sera util usar a notacao com primeira letra maiuscula na geração dos metodos
cmd: cmdLeia | cmdEscreva | cmdSe | cmdCaso | cmdPara | cmdEnquanto | cmdFaca | cmdAtribuicao | cmdChamada | cmdRetorne;

cmdLeia: 'leia' '(' '^'? identificador (',' '^'? identificador)* ')';

cmdEscreva: 'escreva' '(' expressao (',' expressao)* ')';

cmdSe: 'se' expressao 'entao' (se+=cmd)* ('senao' (senao+=cmd)*)? 'fim_se';

cmdCaso: 'caso' exp_aritmetica 'seja' selecao ('senao' (cmd)*)? 'fim_caso';

cmdPara: 'para' IDENT '<-' exp_aritmetica 'ate' exp_aritmetica 'faca' (cmd)* 'fim_para';

cmdEnquanto: 'enquanto' expressao 'faca' (cmd)* 'fim_enquanto';

cmdFaca: 'faca' (cmd)* 'ate' expressao;

cmdAtribuicao: (valor='^')? identificador '<-' expressao;

cmdChamada: IDENT '(' (expressao (',' expressao)*)? ')';

cmdRetorne: 'retorne' expressao;

selecao: (item_selecao)*;
item_selecao: constantes ':' (cmd)*;
constantes: numero_intervalo (',' numero_intervalo)*;
numero_intervalo: (op_unario)? NUM_INT ('..' (op_unario)? NUM_INT)?;

op_unario: '-';

exp_aritmetica: termo (op1 termo)*;
termo: fator (op2 fator)*;
fator: parcela (op3 parcela)*;

// operadores aritméticos
op1: '+' | '-';
op2: '*' | '/';
op3: '%';

parcela: (op_unario)? parcela_unario | parcela_nao_unario;
parcela_unario: (valor='^')? identificador 
                           | cmdChamada 
                           | NUM_INT 
                           | NUM_REAL 
                           | '(' expressao ')';

parcela_nao_unario: (endereco='&') identificador | CADEIA;
exp_relacional: exp_aritmetica (op_relacional exp_aritmetica)?;

// define os operadores relacionais

op_relacional: '=' | '<>' | '>=' | '<=' | '>' | '<';

expressao: termo_logico (op_logico_1 termo_logico)*;
termo_logico: fator_logico (op_logico_2 fator_logico)*;
fator_logico: 'nao'? parcela_logica;
parcela_logica: ('verdadeiro' | 'falso') | exp_relacional;

// define os operadores lógicos

op_logico_1: 'ou';
op_logico_2: 'e';