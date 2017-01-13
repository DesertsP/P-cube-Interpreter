# coding=utf-8
# Created by deserts at 1/8/17
from imp_lexer import *
from combinators import *
from imp_ast import *


def keyword(kw):
    # 保留字
    return Reserved(kw, RESERVED)


# 标识符
id = Tag(ID)
# 数字
num = Tag(INT) ^ (lambda i: int(i))


def parser():
    # 最终的语法分析器
    return Phrase(stmt_list())


def print_stmt():
    def process(parsed):
        return PrintStatement(parsed[-1])
    return keyword('print') + aexp() ^ process


def aexp_value():
    # 解析数字或标识符
    # 值 -> 函数调用 | 数字 | 标识符
    # 注意顺序
    return call_exp() | \
           (num ^ (lambda i: IntAexp(i))) | \
           (id ^ (lambda v: VarAexp(v)))


def process_group(parsed):
    # 从"(expression)"中提取expression
    ((_, p), _) = parsed
    return p


def aexp_group():
    # (expression)
    return keyword('(') + Lazy(aexp) + \
           keyword(')') ^ process_group


def aexp_term():
    # factor -> i | (expression)
    return aexp_value() | aexp_group()


def process_binop(op):
    # 用于生成AST中的二元运算
    return lambda l, r: BinopAexp(op, l, r)


def any_operator_in_list(ops):
    # Parse二元运算符
    op_parsers = [keyword(op) for op in ops]
    # reduce(function, sequence[, initial_value])
    # 先前的结果以及下一个序列的元素由function处理
    # 最后将序列reduce成单个元素
    parser = reduce(lambda l, r: l | r, op_parsers)
    return parser


aexp_precedence_levels = [
    ['*', '/'],
    ['+', '-'],
]


def precedence(value_parser, precedence_levels, combine):
    '''
    ！表达式文法更易理解的写法参见通用的语法分析器。
    一个通用的优先级处理方式：
    先构造高优先级表达式的解析器，
    然后用这个解析器作为下一优先级解析器的value_parser，
    或者说，自底向上地构造解析器，自顶向下地分析，
    自底向上地构建语法树(局部的自底向上)
    对于表达式文法：
    E0 = value_parser
    E1 = E0 * op_parser(precedence_levels[0])
    E2 = E1 * op_parser(precedence_levels[1])
    以上三个解析器，分别对应表达式文法的factor，term，expression
    :param value_parser: 读取数字，变量，group；表达式文法使用aexp_term
    :param precedence_levels: 操作符列表；表达式文法使用aexp_precedence_levels
    :param combine: 连接表达式（生成语法树）；表达式文法使用process_binop
    :return: 最终的Parser
    '''

    def op_parser(precedence_level):
        # 解析指定优先级的一组操作符，组合后作为返回值
        return any_operator_in_list(precedence_level) ^ combine

    parser = value_parser * op_parser(precedence_levels[0])
    for precedence_level in precedence_levels[1:]:
        parser = parser * op_parser(precedence_level)
    return parser


def aexp():
    # 算术表达式Parser
    return precedence(aexp_term(), aexp_precedence_levels, process_binop)


def process_relop(parsed):
    # 生成布尔关系式AST
    ((left, op), right) = parsed
    return RelopBexp(op, left, right)


def bexp_relop():
    # bool_relation_exp -> arithmetic_exp + operator + arithmetic_exp
    relops = ['<', '<=', '>', '>=', '=', '!=']
    return aexp() + any_operator_in_list(relops) + aexp() ^ process_relop


def bexp_not():
    # bool_not_exp -> not + bool_term
    # notice: not有最高优先级
    return keyword('not') + Lazy(bexp_term) ^ (lambda parsed: NotBexp(parsed[1]))


def bexp_group():
    # (bool_exp)
    return keyword('(') + Lazy(bexp) + keyword(')') ^ process_group


def bexp_term():
    # bool_term -> bool_not_exp | bool_relation_exp | (bool_exp)
    return bexp_not() | bexp_relop() | bexp_group()


# notice: and比or优先级高，处理方式同算术表达式
bexp_precedence_levels = [
    ['and'],
    ['or'],
]


def process_logic(op):
    if op == 'and':
        return lambda l, r: AndBexp(l, r)
    elif op == 'or':
        return lambda l, r: OrBexp(l, r)
    else:
        raise RuntimeError('unknown logic operator: ' + op)


def bexp():
    # 布尔表达式文法
    # bool_exp -> bool_exp + or + bool_and_exp | bool_and_exp
    # bool_and_exp -> bool_and_exp + and + bool_term | bool_term
    # bool_term -> bool_not_exp | bool_relation_exp | (bool_exp)
    # bool_not_exp -> not + bool_term
    # bool_relation_exp -> arithmetic_exp + relation_operator + arithmetic_exp
    # !notice: 以上bool_term文法要惰性求值防止无限递归
    return precedence(bexp_term(),
                      bexp_precedence_levels,
                      process_logic)


def assign_stmt():
    # 赋值语句 -> 标识符 = (算术表达式 | 列表)
    def process(parsed):
        ((name, _), exp) = parsed
        return AssignStatement(name, exp)

    return id + keyword('=') + \
           (aexp() | list_exp()) ^ process


def if_stmt():
    def process(parsed):
        # process之前parse到的内容（与下面的解包对应）：
        # ((((('if', 条件), 'then'), 表达式列表), ('else', 表达式列表)), 'end')
        (((((_, condition), _), true_stmt), false_parsed), _) = parsed
        if false_parsed:
            (_, false_stmt) = false_parsed
        else:
            false_stmt = None
        return IfStatement(condition, true_stmt, false_stmt)

    # !notice: else和之后的语句optional
    return keyword('if') + bexp() + keyword('then') + Lazy(stmt_list) + \
           Opt(keyword('else') + Lazy(stmt_list)) + \
           keyword('end') ^ process


def while_stmt():
    def process(parsed):
        # (((('while', 条件), 'do'), 语句列表), 'end')
        ((((_, condition), _), body), _) = parsed
        return WhileStatement(condition, body)

    return keyword('while') + bexp() + keyword('do') + \
           Lazy(stmt_list) + keyword('end') ^ process


def process_list_items(parsed):
    '''
    处理连续嵌套的"列表"，
    将形如((_,_),_)的多层嵌套元组内的元素提取到一个列表中
    :param parsed:
    :return:
    '''
    result_list = []
    items = parsed
    if items:
        while True:
            if type(items) is not tuple:
                result_list.append(items)
                break
            left, right = items
            result_list.append(right)
            items = left
        result_list.reverse()
    return result_list


list_item_separator = keyword(',') ^ (
    lambda x: lambda l, r: (l, r))


def list_exp():
    def process(parsed):
        ((_, items), _) = parsed
        return ListExp(items)

    return keyword('[') + \
           Opt(aexp() * list_item_separator ^ process_list_items) + \
           keyword(']') ^ process


def for_stmt():
    # for each loop
    # 类似python的for 语句，或者其他语言中的for each
    # for_statement -> for + id + in + (list_exp | id) + do + statements + end
    def process(parsed):
        ((((((_, var_name), _), list_or_id), _), body), _) = parsed
        return ForStatement(var_name, list_or_id, body)

    # 注意list变量id的解析方法，需要用VarAexp作为节点
    return keyword('for') + id + keyword('in') + \
           (list_exp() | (id ^ (lambda l: VarAexp(l)))) + \
           keyword('do') + Lazy(stmt_list) + \
           keyword('end') ^ process


def stmt():
    # 语句 -> 赋值语句 | if语句 | while语句
    #       | for语句 | 函数声明 | 函数调用
    return assign_stmt() | print_stmt() | \
           if_stmt() | while_stmt() | for_stmt() | \
           func_stmt() | return_stmt()


def stmt_list():
    '''
    stmt_list -> stmt_list ; stmt | stmt
    ！左递归
    '''
    separator = keyword(';') ^ (
        lambda x: lambda l, r: CompoundStatement(l, r))
    return stmt() * separator


def func_stmt():
    '''
    func_stmt -> def name (param_list): stmt_list end
    stmt_list -> stmt_list ; stmt | stmt
    stmt -> func_stmt | assign_stmt | ……
    param_list -> param_list, param | param
    func_stmt和stmt互相调用，必须延迟求值
    '''
    def process(parsed):
        (((((((_, name), _), params), _), _), body), _) = parsed
        return FunctionStatement(name, params, body)

    return keyword('def') + id + keyword('(') + \
           Opt((id * list_item_separator) ^
               process_list_items) + \
           keyword(')') + keyword(':') + \
           Lazy(stmt_list) + keyword('end') ^ process


def call_exp():
    # 调用函数表达式
    def process(parsed):
        (((name, _), params), _) = parsed
        return FunctionCall(name, params)
    return id + keyword('(') + \
           Opt((Lazy(aexp) * list_item_separator) ^
               process_list_items) + \
           keyword(')') ^ process


def return_stmt():
    def process(parsed):
        return ReturnStatement(parsed[-1])
    return keyword('return') + aexp() ^ process


if __name__ == '__main__':
    pass
