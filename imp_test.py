# coding=utf-8
# Created by deserts at 1/11/17

from imp_lexer import *
from imp_ast import *
from imp_parser import *


def eval_ast(code, lexer, parser):
    ast = parser(lexer(code), 0).value
    env = {}
    ast.eval(env)
    return ast, env


def test_case1():
    code = '''
    list = [1, 2, 3, 4, 5];
    def sum_of_list(list):
        sum = 0;
        for i in list do
            sum = sum + i
        end;
        return sum
    end;
    print sum_of_list(list)
    '''
    p = parser()
    ast, env = eval_ast(code, imp_lexer, p)
    # print ast
    print env

def test_case2():
    code = '''
    def fib(n):
        if n <= 2 then
            return 1
        else
            return fib(n-1) + fib(n-2)
        end
    end;
    print fib(7)
    '''
    p = parser()
    ast, env = eval_ast(code, imp_lexer, p)
    # print ast
    print env


def test_case3():
    code = '''
    foo = 5;
    p = 1;
    def factorial(n):
        while n > 0 do
          p = p * n;
          n = n - 1
        end
    end;
    print factorial(foo);
    print p
    '''
    p = parser()
    ast, env = eval_ast(code, imp_lexer, p)
    # print ast
    print env

def test_func():
    example = '''
    def fun():
        x = 1
    end
    '''
    p = func_stmt()
    ast, env = eval_ast(example, imp_lexer, p)
    print ast
    print env


def test_func2():
    example = '''
    x = 1;
    def fun(a, b, c):
        x = 1;
        y = 4
    end
    '''
    p = parser()
    ast, env = eval_ast(example, imp_lexer, p)
    print ast
    print env


def test_call():
    example = '''
    def multiply(foo, bar):
        return foo * bar
    end;
    def factorial(n):
        p = 1;
        while n > 0 do
          p = p * n;
          n = n - 1
        end;
        return p
    end;
    n = 1;
    print factorial(3)
    '''
    p = parser()
    ast, env = eval_ast(example, imp_lexer, p)
    print ast
    print env


def test_list():
    list_example = '''
    [2, 1, 0, 9]
    '''
    p = list_exp()
    print imp_lexer(list_example)
    print p(imp_lexer(list_example), 0)


def test_print():
    example = '''
    a = 2;
    b = 1;
    print a + b;
    print b - a
    '''
    ast, env = eval_ast(example, imp_lexer, stmt_list())
    print ast
    # print env


def test_something():
    s = '''
    s = 1 ; y = 22
    '''
    tokens = imp_lexer(s)

    ### 算术表达式测试

    def op_parser(precedence_level):
        return any_operator_in_list(precedence_level) ^ process_binop

    factor = aexp_term()
    term = factor * op_parser(aexp_precedence_levels[0])
    expression = term * op_parser(aexp_precedence_levels[1])
    # print expression(tokens, 0)
    ### 布尔表达式测试
    bool_exp = bexp()

    # print bool_exp(tokens, 0)
    ### 语句测试
    # stmt = stmt()
    # print (bool_exp + stmt)(tokens, 0)
    def stmt_list():
        # 解析复合语句：e.g. stmt; stmt; stmt; etc.
        def process(parsed):
            def AST(l, r):
                # print l, r
                return CompoundStatement(l, r)

            return AST

        separator = keyword(';') ^ process
        # print separator
        return Exp(stmt(), separator)

    stmts = stmt_list()
    # print stmts(tokens, 0)
    # if statement
    if_s = """
    if 3 > 2 then s = 2
    else w = f end
    """
    p = if_stmt()
    # print p(imp_lexer(if_s), 0).value
    # while
    while_s = """
    while 3 < 2 do s = 2 end
    """
    p = while_stmt()
    # print p(imp_lexer(while_s), 0).value
    ### List
    list_example = '''
    [2,1,0,9, ]
    '''
    p = list_exp()
    print p(imp_lexer(list_example), 0)
    ### for
    for_example = '''
    x = 0;
    list = [3 * x, 4, 5, 1, ];
    for i in list do x = x + i end;
    while x > 1 do x = x - 1 end
    '''
    p = parser()
    # print imp_lexer(for_example)
    foo = p(imp_lexer(for_example), 0)
    env = {}
    foo.value.eval(env)
    print env


def test_parser():
    example = '''
    n = 3;
    p = 1;
    while n > 0 do
      p = p * n;
      if n > 0 then n = n - 1
        else n = 0
      end
    end
    '''
    p = parser()
    ast = p(imp_lexer(example), 0).value


if __name__ == '__main__':
    test_case3()
