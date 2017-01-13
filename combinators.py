# coding=utf-8
# Created by deserts at 1/9/17


class Result:
    def __init__(self, value, pos):
        self.value = value
        self.pos = pos

    def __repr__(self):
        return 'Result(%s, %d)' % (self.value, self.pos)


class Parser:
    def __add__(self, other):
        return Concat(self, other)

    def __mul__(self, other):
        return Exp(self, other)

    def __or__(self, other):
        return Alternate(self, other)

    def __xor__(self, function):
        return Process(self, function)


class Tag(Parser):
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None


class Reserved(Parser):
    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and \
                        tokens[pos][0] == self.value and \
                        tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None


class Concat(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                combined_value = (left_result.value, right_result.value)
                return Result(combined_value, right_result.pos)
        return None


class Exp(Parser):
    def __init__(self, parser, separator):
        '''
        解决左递归，分解成一个列表，逐个解析列表元素，并连接起来
        :param parser: 解析单个元素
        :param separator: 分隔符解析器，
            解析后还能把分隔符两边的内容进行处理（连接起来）
            i.e. separator组合子的
        '''
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        # 当前解析的所有结果，开始前先解析第一个"元素"
        # 每次解析了后边的元素，将把结果"累加"到result上
        # 最后作为返回值返回
        result = self.parser(tokens, pos)

        # next解析器 -> 分隔符 + 单个元素解析器
        # e.g. 对于复合语句(stmt;stmt;stmt;etc.)
        # next解析器 = (';'解析器 + stmt解析器) ^ process_next
        # process_next中，把已有结果与新解析到的内容进行"合并"

        def process_next(parsed):
            (sepfunc, right) = parsed
            return sepfunc(result.value, right)

        next_parser = self.separator + self.parser ^ process_next

        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result


class Alternate(Parser):
    def __init__(self, left, right):
        '''
        S -> L | R， 先试图匹配左，后匹配右，将造成回溯
        :param left:
        :param right:
        '''
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.right(tokens, pos)
            return right_result


class Opt(Parser):
    def __init__(self, parser):
        '''
        可选的语法元素
        :param parser:
        '''
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            return result
        else:
            return Result(None, pos)


class Rep(Parser):
    def __init__(self, parser):
        '''
        匹配一个列表
        list -> item item item ...
        :param parser: 匹配单个元素
        '''
        self.parser = parser

    def __call__(self, tokens, pos):
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)


class Process(Parser):
    def __init__(self, parser, function):
        '''
        用function对parse到的结果的值进行替换，主要用于构建AST
        :param parser:
        :param function: 一个函数，接收parse的结果，返回更改后的结果
        '''
        self.parser = parser
        self.function = function

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            result.value = self.function(result.value)
            return result


class Lazy(Parser):
    def __init__(self, parser_func):
        '''
        惰性求值，通过传入一个能生成parser的函数，以便在调用时才进行求值
        :param parser_func:
        '''
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens, pos):
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)


class Phrase(Parser):
    '''
    最终的语法解析器组合子用Phrase包装，确保所有单词均被使用
    '''
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        else:
            return None


if __name__ == '__main__':
    from imp_lexer import *

    x = '''
    1+2
    a := 10;
    b := 20;
    c := 30'''
    lex = imp_lexer(x)
    print lex
    print Tag('INT')(lex, 0)
    # parser = Concat(Concat(Tag(INT), Reserved("+", RESERVED)), Tag(INT))
    parser = Tag(INT) + Reserved('+', RESERVED) + Tag(INT)

    def process_func(parsed):
        ((l, _), r) = parsed
        return int(l) + int(r)


    print parser(lex, 0)
    parser = parser ^ process_func
    print parser(lex, 0)
