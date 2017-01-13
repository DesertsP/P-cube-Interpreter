# coding=utf-8
# Created by deserts at 1/13/17
import sys
from imp_parser import *
from imp_lexer import *


def usage():
    sys.stderr.write('Usage: imp filename [-m verbose | less]\n')
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    filename = sys.argv[1]
    text = open(filename).read()
    tokens = imp_lexer(text)
    parser = parser()
    parse_result = parser(tokens, 0)
    if not parse_result:
        sys.stderr.write('Parse error!\n')
        sys.exit(1)
    ast = parse_result.value
    env = {}
    ast.eval(env)
    if '-m' in sys.argv and sys.argv[-1] == 'verbose':
        sys.stdout.write(u'Final global variable values:\n')
        for name in env:
            sys.stdout.write('%s: %s\n' % (name, env[name]))