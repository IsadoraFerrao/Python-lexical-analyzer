#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ply import yacc
from lexer import tokens
import sys


class Node:
    def __init__(self, type, children=None, leaf=None, line=None):
        self.type = type
        self.line = line
        if children:
            if not isinstance(children, (list, tuple)):
                children = [children]
            self.children = children
        else:
            self.children = []
        self.leaf = leaf

    def _pretty(self, prefix='| '):
        string = []
        root = '{}'.format(str(self.type))
        if self.leaf is not None:
            root += ' ({})'.format(self.leaf)
        string.append(root)
        for child in self.children:
            if isinstance(child, Node):
                for child_string in child._pretty():
                    string.append('{}{}'.format(prefix, child_string))
            else:
                string.append('{}{}'.format(prefix, child))
        return string

    def pretty(self):
        return '\n'.join(self._pretty())

    def __str__(self):
        children_string = ', '.join([str(c) for c in self.children]) if self.children else ''
        leaf_string = '{} '.format(self.leaf) if self.leaf is not None else ''
        return '({} {}[{}])'.format(self.type, leaf_string, children_string)

def p_program(p):
    ''' program : statement_list '''
    p[0] = Node('program', children = p[1], leaf = '')


def p_list(p):
    '''statement_list : statement statement_list
                      | statement '''
    if len(p) == 2:
        p[0] = p[1]
        #p[0] = Node('statement', children=p[1], leaf = ' ')
    else:
        p[0] = Node('statement_list', children=[p[1],p[2]], leaf = ' ')


def p_statement(p):
    ''' statement : expression FIM_COMANDO
                 | statement FIM_COMANDO
                 | if_statement FIM_COMANDO
                 | for_statement FIM_COMANDO
                 | while_statement FIM_COMANDO
                 | print_statement
                 | read_statement FIM_COMANDO
                 | declaration FIM_COMANDO
                 | null_declaration FIM_COMANDO
                 | assignment FIM_COMANDO
                 | boolean_exp FIM_COMANDO
                 | function_declaration FIM_COMANDO
                 | return FIM_COMANDO'''

    # Não precisa pegar o p[2], a regra é pra garantir que só sejam aceitos
    # statements que possuem um ponto final
    p[0] = p[1]


def p_binary_op(p):
    ''' expression : expression MAIS expression
                   | expression MENOS expression
                   | expression VEZES expression
                   | expression DIVIDIDO expression
                   | expression ELEVADO expression
                   | INCREMENTA ID
                   | DECREMENTA ID
                   | NUM_INTEIRO
                   | NUM_REAL
                   | TEXTO_RAW
                   | boolean
                   | ID'''

    if p.slice[1].type == 'ID':
        p[0] = Node('value', children=p[1], leaf='id', line=p.lineno(1))
    elif p.slice[1].type == 'NUM_INTEIRO':
        p[0] = Node('value', children=p[1], leaf='int', line=p.lineno(1))
    elif p.slice[1].type == 'NUM_REAL':
        p[0] = Node('value', children=p[1], leaf='real', line=p.lineno(1))
    elif p.slice[1].type == 'TEXTO_RAW':
        p[0] = Node('value', children=p[1], leaf='texto', line=p.lineno(1))
    elif p.slice[1].type == 'INCREMENTA':
        p[0] = Node('value', children=p[2], leaf='increment', line=p.lineno(2))
    elif p.slice[1].type == 'DECREMENTA':
        p[0] = Node('value', children=p[2], leaf='decrement', line=p.lineno(2))
    elif p.slice[1].type == 'boolean':
        p[0] = Node('value', children=p[1], leaf='boolean', line=p.lineno(1))
    elif p.slice[1].type == 'expression':
        p[0] = Node('bin_op', children=[p[1], p[3]], leaf=p[2], line=p.lineno(2))

def p_boolean_expression(p):
    ''' boolean_exp : expression MAIOR_IGUAL expression
                    | expression MENOR_IGUAL expression
                    | expression IGUAL expression
                    | expression DIFERENTE expression
                    | expression MENOR_QUE expression
                    | expression MAIOR_QUE expression
                    | expression OP_LOG_OU expression
                    | expression OP_LOG_E expression
                    | expression OP_LOG_NAO expression'''

    if p.slice[2].type == 'MAIOR_IGUAL':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='maior ou igual a', line=p.lineno(1))
    elif p.slice[2].type == 'MENOR_IGUAL':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='menor ou igual a',line=p.lineno(1))
    elif p.slice[2].type == 'IGUAL':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='igual a',line=p.lineno(1))
    elif p.slice[2].type == 'DIFERENTE':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='diferente de',line=p.lineno(1))
    elif p.slice[2].type == 'MAIOR_QUE':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='maior que',line=p.lineno(1))
    elif p.slice[2].type == 'MENOR_QUE':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='menor que',line=p.lineno(1))
    elif p.slice[2].type == 'OP_LOG_OU':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='ou',line=p.lineno(1))
    elif p.slice[2].type == 'OP_LOG_E':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='e',line=p.lineno(1))
    elif p.slice[2].type == 'OP_LOG_NAO':
        p[0] = Node('boolean_exp', children=[p[1],p[3]], leaf='nao',line=p.lineno(1))


def p_boolean(p):
    ''' boolean : VERDADEIRO
                | FALSO '''
    p[0] = p[1]


def p_assign(p):
    ''' assignment : ID ATRIBUICAO expression
                   | assignment VIRGULA assignment '''
    if p.slice[1].type == 'ID':
        p[0] = Node('assignment', children=[p[1], p[3]], leaf='=',line=p.lineno(1))
    else:
        p[0] = Node('assignment', children=[p[1], p[3]], leaf=',',line=p.lineno(1))

def p_id_list(p):
    ''' id_list : ID VIRGULA id_list
                | ID '''
    if len(p) == 4:
        p[0] = Node('id_list', children=[p[1], p[3]], leaf=',', line=p.lineno(1))
    else:
        p[0] = Node('id_list', children=p[1], leaf='id', line=p.lineno(1))

def p_null_declaration(p):
    ''' null_declaration : type ID'''
    p[0] = Node('null_declaration', children=p[2], leaf=p[1], line=p.lineno(2))

def p_multi_null_declaration(p):
    ''' null_declaration : type ID VIRGULA id_list'''
    p[0] = Node('null_declaration', children=[p[2],p[4]], leaf=p[1], line=p.lineno(2))

# Declaração única
def p_declare(p):
    ''' declaration : type ID ATRIBUICAO expression '''
    p[0] = Node('declaration', children=[p[2],p[4]], leaf=p[1], line=p.lineno(2))

# Declaração múltipla
def p_declare_many(p):
    ''' declaration : type ID ATRIBUICAO expression VIRGULA assignment'''
    p[0] = Node('declaration', children=[p[2],p[4],p[6]], leaf=p[1], line=p.lineno(2))


def p_par(p):
    'expression : ABRE_PAR expression FECHA_PAR'
    p[0] = p[2]


# Deveria ser parâmetros, argumentos são somente os passados em exec

# Essa regra está conflitando com declaração nula(type ID) Resolver se der tempo
def p_argument(p):
    ''' arguments : type ID'''
    p[0] = Node('args', children=[p[2], p[1]], leaf='single_argument', line=p.lineno(2))


def p_arguments(p):
    ''' arguments : arguments VIRGULA arguments'''
                #   | argument '''
    p[0] = Node('args', children=[p[1], p[3]], leaf='multiple_arguments')


def p_types(p):
    '''type : BOOLEAN
            | INT
            | REAL
            | TEXTO
            | LISTA '''
    p[0] = p[1]


def p_list_acess(p):
    ''' expression : ID INDICE'''
    p[0] = Node('index', children=p[1], leaf='index', line = p.lineno(1)) # Talvez children=p[1], leaf = p[2]


def p_if(p):
    ''' if_statement : SE boolean_exp ENTAO statement_list DEU'''
    #p[0] = Node('if_statement', children=[p[2],p[3],p[4]], leaf=p[1])
    p[0] = Node('if_statement', children=[p[2],p[4]], leaf='if', line = p.lineno(1))


def p_if_elseif(p):
    ''' if_statement : SE boolean_exp ENTAO statement_list SENAO if_statement  '''
    p[0] = Node('if_statement', children=[p[2],p[4],p[6]], leaf='if/elseif', line = p.lineno(1))


def p_if_else(p):
    ''' if_statement : SE boolean_exp ENTAO statement_list TA_BOM ENTAO statement_list DEU'''
    p[0] = Node('if_statement', children=[p[2], p[4], p[7]], leaf='if/else', line = p.lineno(1))


def p_print(p):
    ''' print_statement : MOSTRA parameters FIM_COMANDO'''
    p[0] = Node('print_statement', children=p[2],leaf=p[1], line = p.lineno(1))


def p_read(p):
    ''' read_statement : LEIA ID '''
    p[0] = Node('read', children=p[2], leaf=p[1], line = p.lineno(1))


def p_for(p):
    ''' for_statement : PARA ID EM expression FACA statement_list DEU '''
    p[0] = Node('for_loop', children=[p[2],p[4],p[6]], leaf='for', line= p.lineno(2))


def p_while(p):
    ''' while_statement : ENQUANTO boolean_exp FACA statement_list DEU '''
    p[0] = Node('while_loop', children=[p[2],p[4]], leaf='while', line = p.lineno(1))


def p_def_function(p):
    ''' function_declaration : DEFINE ID COMO statement_list DEU '''
    p[0] = Node('function_declaration', children=p[4],leaf=p[2], line = p.lineno(1))


def p_def_function_args(p):
    '''statement : DEFINE ID COM arguments COMO statement_list DEU FIM_COMANDO '''
    p[0] = Node('function_declaration', children=[p[4],p[6]], leaf=p[2], line = p.lineno(1))

def p_function_call(p):
    ''' expression : ID COM parameters'''
    p[0] = Node('function_call', children=p[3],leaf=p[1], line = p.lineno(1))


def p_return(p):
    ''' return : RETORNA expression'''
    p[0] = Node('return', children=p[2], leaf=p[1], line = p.lineno(1))

def p_parameter(p):
    ''' parameters : expression
                   | parameters VIRGULA parameters '''
    if len(p) == 2:
        p[0] = Node('parameter', children=p[1], leaf='parameter')
    else:
        p[0] = Node('parameter', children=[p[1], p[3]], leaf='parameters')


def p_append(p):
    ''' expression : BOTA expression EM ID '''
    p[0] = Node('append', children=[p[2],p[4]], leaf='append', line = p.lineno(4))


def p_unary_operation(p):
    '''expression : MENOS expression %prec UMENOS'''
    p[0] = - p[2]

def p_range(p):
    ''' expression : NUM_INTEIRO A NUM_INTEIRO '''
    p[0] =  Node('iterable', children=[p[1], p[3]], leaf='range')

# Error rule for syntax errors
def p_error(p):
    print("Erro de sintaxe!")


precedence = (
    ('left', 'ATRIBUICAO'),
    ('left', 'MAIOR_QUE', 'MENOR_QUE', 'MAIOR_IGUAL', 'MENOR_IGUAL', 'DIFERENTE'),
    ('left', 'MAIS', 'MENOS'),
    ('left','VEZES','DIVIDIDO'),
    ('left','ABRE_PAR', 'FECHA_PAR'),
    ('left','ELEVADO'),
    ('right', 'UMENOS'),
)

parser = yacc.yacc()

if __name__ == '__main__':
# while True:
#     try:
#         codigo = input('calc> ')
#     except EOFError:
#         break
#     if not codigo:
#         continue
    codigo = open(sys.argv[1]).read()
    ast = parser.parse(codigo)
    print(ast.pretty())
