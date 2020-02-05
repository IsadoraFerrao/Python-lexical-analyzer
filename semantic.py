#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ply import yacc
from parser import parser
from lexer import lexer
import sys

scope = []
codigo = open(sys.argv[1]).read()
ast = parser.parse(codigo)
declaration = False # Flag para ser usada em caso de múltiplas declarações
function_flag = 0 # Flag para ser usada na verificação do escopo interno de funções

# Tipos que estão na mesma lista executam as mesmas operações
r1 = ['statement_list', 'print_statement', 'parameter']
r2 = ['program']


# Nós que são apenas 'containers' de outros nós
def routine1(node):
    for child in node.children:
        visit(child)
    return

# Operações que abrem um novo escopo
def routine2(node):
    # Inicia um novo escopo na lista de escopo
    scope.append(None)
    for child in node.children:
        visit(child)
    # Desmonta o escopo
    while scope.pop():
        pass
    return

def visit(node):
    global declaration, function_flag, last_function

    # Tipos pertencentes a r1
    if node.type in r1:
        routine1(node)

    # Tipos pertencentes a r2
    elif node.type in r2:
        routine2(node)

    elif node.type == 'bin_op':
        types = []
        for child in node.children:
            types.append(visit(child))
        return op_type(types, node.leaf, node.line)

    elif node.type == 'boolean_exp':
        types = []
        for child in node.children:
            types.append(visit(child))
        return op_type(types, node.leaf, node.line)

    elif node.type == 'declaration':
        # Verificar o escopo para identificar declaração duplicada
        if len(node.children) == 2: # Declaração única (com atribuição)
            # Checa para ver se o ID já existe
            check_scope(node.children[0], node.line, 1, function_flag)
            # Adiciona no escopo o ID e o tipo
            scope.append([node.children[0], node.leaf])
            exp_type = visit(node.children[1])
            check_type(node.children[0], fetch_type(node.children[0]), exp_type, node.line)
        else: # Declaração múltipla
            # Verifica no escopo para ver se a declaração é duplicada
            check_scope(node.children[0], node.line, 1, function_flag)
            scope.append([node.children[0], node.leaf])
            # Define declaração como True para visitar os nós de atribuição(node.type == 'assignment')
            declaration = True
            visit(node.children[1])
            visit(node.children[2])
            declaration = False

    elif node.type == 'null_declaration':
        if len(node.children) == 1: # Declaração nula única
            # Verifica o escopo por duplicadas
            check_scope(node.children[0], node.line, 1, function_flag)
            # Adiciona ao escopo
            scope.append([node.children[0], node.leaf])
        else: # Declaração nula de múltiplas variáveis
            # Verifica o escopo por duplicadas
            check_scope(node.children[0], node.line, 1, function_flag)
            scope.append([node.children[0], node.leaf])
            # Visita o id_list
            visit(node.children[1])

    elif node.type == 'id_list':
        scope.append([node.children[0], scope[-1][1]])
        if node.leaf == ',':
            visit(node.children[1])


    # Se o node for do tipo valor, a expressão vira um primitivo(int, float, id, etc.)
    elif node.type == 'value':
        # Verificar se o ID sendo usado na expressão existe
        if node.leaf == 'id' or node.leaf == 'increment' or node.leaf == 'decrement':
            check_scope(node.children[0], node.line, function = function_flag)
            # retorna o tipo do valor
            return fetch_type(node.children[0])
        if node.leaf == 'int' or node.leaf == 'real' or node.leaf == 'texto' or node.leaf == 'boolean':
            # Retorna o tipo
            return node.leaf


    # Se o node for um atribuição
    elif node.type == 'assignment':
        if node.leaf == '=':
            if declaration:
                # Se for uma atribuição que está dentro de uma declaração, como:
                # int x é 10, y é 5, z é 53.
                # Verifica por variáveis duplicadas no escopo
                check_scope(node.children[0], node.line, 1, function_flag)
                # Adiciona a variável no escopo
                scope.append([node.children[0], scope[-1][1]])
                # Visita a expressão
                exp_type = visit(node.children[1])
                check_type(node.children[0], fetch_type(node.children[0]), exp_type, node.line)

            else:
                # Se for uma atribuição comum e.g: ID ATRIBUICAO expression
                # Verifica se a variável existe no escopo
                check_scope(node.children[0], node.line, function = function_flag)
                # Adiciona na lista o tipo do id que recebe a expressão
                # Visita a child expression
                exp_type = visit(node.children[1])
                check_type(node.children[0], fetch_type(node.children[0]), exp_type, node.line)
        else:
            for child in node.children:
                visit(child)


    elif node.type == 'while_loop':
        scope.append(None)
        tp = visit(node.children[0])
        if tp == 'boolean':
            for child in node.children:
                visit(child)
        else:
            print ('Enquanto: Expressão incompatível na linha {}, esperava boolean mas obteve {}'.format(node.line, tp))
            raise SystemExit
        # Desmonta o escopo
        while scope.pop():
            pass
        return


    elif node.type == 'for_loop':
        scope.append(None)
        # Adiciona ao escopo a variável do loop
        # A variável do loop deve ser do mesmo tipo que o item da lista
        # o qual ela representa # Ver um jeito de pegar o tipo de cada elemento
        # Momentâneamente fica como inteiro, precisamosa acessar os valores da lista e buscar o tipo de cada um
        scope.append([node.children[0], 'int'])
        # Verifica o tipo da variável que está sendo iterada
        exp_type = visit(node.children[1])
        if exp_type != 'lista':
            print ("{}: Tentativa de iterar sobre elemento não iterável na linha {}.".format(node.children[0], node.line))
            raise SystemExit
        visit(node.children[2])
        while scope.pop():
            pass

    # Se o node é uma declaração de função
    elif node.type == 'function_declaration':
        # Verifica se a função não está duplicada no escopo
        check_scope(node.leaf, node.line, 1, function = function_flag)
        last_function = node.leaf
        # Adiciona a função ao escopo:
        if len(node.children) == 2:
            # Se há dois filhos é uma declaração com parâmetros.
            # Adiciona no escopo o nome da função e o statement_list e os argumentos
            # Inicia o tipo de retorno como None, depois que encontrar o retorno altera.
            scope.append([node.leaf, None, node.children[1], node.children[0]])
        else:
            # É uma declaração de função sem parâmetros.
            # Coloca o ID da função no escopo
            scope.append([node.leaf, None])
            # visit(node.children[0])

        # Inicia um escopo agora somente para testar a função
        scope.append(None)
        # Visita os filhos para colocar os parâmetros no escopo
        for child in node.children:
            visit(child)
        # Desmonta o escopo, que será montado novamente quando a função for chamada
        while scope.pop():
            pass
        last_function = None

    elif node.type == 'function_call':
        # Verifica o escopo para ver se a função foi declarada
        check_scope(node.leaf, node.line, function = function_flag)
        # Se a função foi declarada, adiciona ao escopo os parâmetros da função
        scope.append(None)
        function_flag = 1
        # Percorre o escopo de trás pra frente
        for var in scope[::-1]:
            # Se encontrar a função que está sendo chamada:
            if var and var[0] == node.leaf:
                if len(var) > 2: # É uma função que possui parâmetros [ID, Statement_list, Arguments]
                    # Precisamos montar o escopo da função
                    visit(var[3])
                    # Verifica o corpo da função
                    visit(var[2])
                else: # É uma função sem parâmetros
                    # Verifica o corpo da função
                    visit(var[2])

        function_flag = 0
        while scope.pop():
            pass
        tipo_retorno = fetch_type(node.leaf)
        return tipo_retorno

    elif node.type == 'args':
        if node.leaf == 'single_argument':
            scope.append([node.children[0], node.children[1]])
        else:
            for child in node.children:
                visit(child)

    elif node.type == 'index':
        # Checa se a variável que está sendo indexada existe
        check_scope(node.children[0], node.line, function = function_flag)
        # Checa se a variável que está sendo indexada é uma lista
        id_type = fetch_type(node.children[0])
        if id_type != 'lista':
            print("Linha {}: Variáveis do tipo {} não podem ser acessadas por meio de índices.".format(node.line, id_type))

    elif node.type == 'append':
        # Verifica se o ID existe no escopo
        check_scope(node.children[1], node.line, function = function_flag)
        if fetch_type(node.children[1]) != 'lista':
            print ("Linha {}: Variáveis do tipo {} não possuem o método 'bota'.".format(node.line, fetch_type(node.children[1])))
            raise SystemExit
        # Pega o tipo da expressão que está sendo colocada na lista
        exp_type = visit(node.children[0])
        if exp_type == 'lista':
            print ("Linha {}: Tipos incompatíveis para a operação 'bota', lista em lista.".format(node.line))


    elif node.type == 'read':
        check_scope(node.children[0], node.line, function = function_flag)
        tipo = fetch_type(node.children[0])
        if tipo == 'lista' or tipo == 'boolean':
            print ("Linha {}: Variáveis do tipo {} não podem ser lidas.".format(node.line, tipo))
            raise SystemExit

    elif node.type == 'iterable':
        return 'lista'


    elif node.type == 'if_statement':
        scope.append(None)

        tp = visit(node.children[0])
        if tp == 'boolean':
            for child in node.children:
                visit(child)
        else:
            print ('Se: Expressão incompatível na linha {}, esperava boolean mas obteve {}'.format(node.line, tp))
        # Desmonta o escopo
        while scope.pop():
            pass
        return

    elif node.type == 'return':
        tipo_retorno = visit(node.children[0])
        # Adicionar o tipo do retorno da função no escopo
        for index in range(len(scope)):
            if scope[index] and scope[index][0] == last_function:
                scope[index][1] = tipo_retorno
                break

def check_scope(identifier, lineno, duplicate = 0, function = 0):
    if duplicate == 1:
        # Se for checar por duplicadas, checa somente no escopo atual.
        for var in scope[::-1]:
            if var and var[0] == identifier:
                print("{}: Declaração de variável duplicada na linha {}.".format(identifier, lineno))
                raise SystemExit
            # Para quando chegar no fim do último escopo
            elif var == None:
                break
    else:
        if function == 1:
            for var in scope[::-1]:
                if var and var[0] == identifier:
                    break
                elif var == None:
                    print ("{}: Variável não declarada na linha {}.".format(identifier, lineno))
                    raise SystemExit
        else:
            for var in scope[::-1]:
                if var and var[0] == identifier:
                    break
            else:
                print ("{}: Variável não declarada na linha {}.".format(identifier, lineno))
                raise SystemExit

def check_type(var, left_hand_type, right_hand_type, line):
    if left_hand_type != right_hand_type:
        print ("Tipos incompatíveis ao atribuir valor a variável {} na linha {}.".format(var, line)
        + " Esperava {} mas obteve {}.".format(left_hand_type, right_hand_type))
        raise SystemExit

def fetch_type(identifier):
    # Percorre o escopo de trás pra frente
    for var in scope[::-1]:
        # Quando encontrar a variável em questão
        if var and var[0] == identifier:
            return var[1] # Retorna o tipo

def op_type(types, operation, line):
    if len(set(types)) == 1:
        # Cai aqui: [str str] [int int] [real real] [boolean boolean] [lista lista]
        # As operações envolvem somente um tipo - OK
        if types[0] == 'boolean':
            if operation in ['mais', 'menos', 'dividido por', 'vezes', 'na']:
                print ("Operação inválida para o tipo {} na linha {}: {}.".format(types[0], line, operation))
                raise SystemExit

        elif types[0] == 'texto' or types[0] == 'lista':
            if operation in ['menos', 'dividido por', 'vezes', 'na', 'menor que', 'maior que', 'menor ou igual a', 'maior ou igual a',
            'ou', 'e', 'nao']:
                print ("Operação inválida para o tipo {} na linha {}: {}.".format(types[0], line, operation))
                raise SystemExit

        elif types[0] == 'int' or types[0] == 'real':
            if operation in ['e', 'ou', 'nao']:
                print ("Operação inválida para o tipo {} na linha {}: {}.".format(types[0], line, operation))
                raise SystemExit

        if operation in ['maior que', 'menor que', 'diferente de', 'igual a', 'maior ou igual a', 'menor ou igual a', 'e', 'ou', 'nao']:
            return 'boolean'

        return types[0]

    # Se for uma operação entre dois tipos diferentes
    if len(set(types)) == 2:
        # Se os tipos da operação forem real e inteiro
        if 'real' in types and 'int' in types:
            if operation in ['maior que', 'menor que', 'diferente de', 'igual a', 'maior ou igual a', 'menor ou igual a', 'e', 'ou', 'nao']:
                # Se for uma operação booleana retorna boolean
                return 'boolean'
            else:
                # Se for uma operação aritmética retorna real
                return 'real'

        else:
            print ("Linha {}: Tipos incompatíveis para a operação '{}', {} e {}.".format(line, operation, types[0], types[1]))
            raise SystemExit


print (ast.pretty())
visit(ast)
print ("[+] Verificação concluída. Nenhum erro encontrado")
