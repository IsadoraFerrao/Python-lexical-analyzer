#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Analisador lexico
"""

from ply import lex

# Lista de palavras reservadas da linguagem
reserved = {
# Tipos de dados
'boolean':'BOOLEAN',
'int':'INT',
'real':'REAL',
'texto':'TEXTO',
'lista':'LISTA',
'verdadeiro':'VERDADEIRO',
'falso':'FALSO',

# Operações aritméticas
'mais':'MAIS', #ok
'menos':'MENOS', #ok
'vezes':'VEZES', #ok
'incrementa':'INCREMENTA', #ok
'decrementa':'DECREMENTA', #ok

# Comparação entre variáveis
'é' : 'ATRIBUICAO', #ok
'não' : 'OP_LOG_NAO', #ok
'ou' : 'OP_LOG_OU', #ok
'e':'OP_LOG_E', #ok

#Estruturas de controle
'se':'SE',
'senão':'SENAO',
'então':'ENTAO',
'para':'PARA',
'enquanto':'ENQUANTO',
'faça':'FACA',
'a':'A',
'em':'EM',

# Input/Ouput
'mostra':'MOSTRA',
'leia':'LEIA',

# Funções
'como':'COMO',
'define':'DEFINE',
'com':'COM',
'bota':'BOTA',
'retorna':'RETORNA',
}

tokens = [
    'FIM_COMANDO', #End of statement
    'ID',
    'DEU',
    'NUM_INTEIRO',
    'NUM_REAL',
    'TEXTO_RAW',
    'ABRE_PAR',
    'FECHA_PAR',
    'VIRGULA',
    'DIVIDIDO',
    'ELEVADO',
    'DIFERENTE',
    'MENOR_QUE',
    'MAIOR_QUE',
    'MENOR_IGUAL',
    'MAIOR_IGUAL',
    'IGUAL',
    'TA_BOM',
    'INDICE',
] + list(reserved.values())

t_ABRE_PAR = r'\('
t_FECHA_PAR = r'\)'
t_VIRGULA = r'\,'


def t_DIVIDIDO(t):
    r'dividido\s+por'
    t.value = str(t.value)
    return t

def t_DEU(t):
    r'e\sdeu'
    return t

def t_ELEVADO(t):
    r'na'
    t.value = str(t.value)
    return t

def t_DIFERENTE(t):
    r'é\s+diferente\s+de'
    t.value = str(t.value)
    return t

def t_MAIOR_IGUAL(t):
    r'é\s+maior\s+ou\s+igual\s+a'
    t.value = str(t.value)
    return t

def t_MENOR_IGUAL(t):
    r'é\s+menor\s+ou\s+igual\s+a'
    t.value = str(t.value)
    return t

def t_IGUAL(t):
    r'é\s+igual\s+a'
    t.value = str(t.value)
    return t

def t_MAIOR_QUE(t):
    r'é\s+maior\s+que'
    t.value = str(t.value)
    return t

def t_MENOR_QUE(t):
    r'é\s+menor\s+que'
    t.value = str(t.value)
    return t

# def t_SENAO_SE(t):
    # r'senão\s+se'
    # t.value = str(t.value)
    # return t

def t_TA_BOM(t):
    r'tá\s+bom'
    t.value = str(t.value)
    return t

def t_NUM_REAL(t):
    r'\d+,\d+ | \,\d+'
    t.value = t.value.replace(',', '.')
    t.value = float(t.value)
    return t

def t_NUM_INTEIRO(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_TEXTO_RAW(t):
    r'\"[A-Za-z !#,$%&*+-~|:@¨¬\w]*"'
    return t

def t_INDICE(t):
    r'\[[a-zA-Z_\w*][a-zA-Z_0-9\w*]*\]|\[[0-9]+\]'
    return t

def t_ID(t):
    r'[a-zA-Z_\w*][a-zA-Z_0-9\w*]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t


def t_FIM_COMANDO(t):
    r'\.'
    return t

# def t_COMENTARIO(t):
#     r'\#.*'
#     pass

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n'
    t.lexer.lineno += 1
#     t.lexer.linepos = 0

def t_error(t):
    print('Caractere ilegal na linha {}: {}'.format(lexer.lineno, t.value[0]))
    t.lexer.skip(1)

t_ignore = ' \r\t'

t_ignore_COMMENT='\#.*'

lexer = lex.lex()

if __name__ == '__main__':
    import sys

    # dados = input('Digite uma expressao: ')

    dados = open(sys.argv[1]).read()

# with open(arq) as file:
    # Junta a lista das linhas
    # dados = ('').join(file.readlines())

    lexer.input(dados)

    token = lexer.token()
    while token:
        print(token)
        token = lexer.token()
