# coding=utf-8
# Created by deserts at 1/12/17

from combinators import *
import sys

# ！给定语法规则和句子，判别该句子是否为该文法的语言，若是则给出AST
# 规定语法规则表示如下：
# S -> E;
# E -> LI(T, VT('+'));
# T -> LI(F, VT('*'));
# F -> VT('i') | VT('n')
#
# 其中大写字母为非终结符，VT('x')表示终结符x，
# 规则LI(x, 终结符VT)
# 表示一个由终结符VT分割的任意多个x形成的列表，
# 此外可通过+，|表示连接和或，括号可改变结合性
# e.g.上述第二条规则等价于 E -> E+T | T
# 其他限制要求：首条规则的非终结符必须为S，
#              规则满足"自顶向下"顺序。


def grammer_process(g):
    gramm = g.strip().replace('->', '=')
    gramm = [i.strip() for i in gramm.split('\n')]
    script = ''
    for i in gramm:
        script = i + '\n' + script
    return script


def VT(t):
    return Tag(t)


def LI(sigle, separator):
    sep = separator ^ (lambda x: lambda l, r: (x, l, r))
    return sigle * sep


def parse(script, lang):
    compiled = compile(script, 'grammer.pyc', 'exec')
    exec(compiled)
    parsed = Phrase(S)([(c, c) for c in lang], 0)
    if parsed:
        return parsed.value
    else:
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: general_parser grammer_file sentence\n')
        sys.exit(1)
    filename = sys.argv[1]
    text = open(filename).read()
    g_ = grammer_process(text)
    print "语法规则如下: \n" + text
    sentence = sys.argv[2]
    parsed = None
    parsed = parse(g_, sentence)
    try:
        parsed = parse(g_, sentence)
    except:
        print "规则错误"
        sys.exit(1)
    if parsed:
        print "解析成功：" + str(parsed)
    else:
        print "解析失败：给定内容不是给定文法的语言"