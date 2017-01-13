# coding=utf-8
# Created by deserts at 1/8/17

import sys
import re


def lex(characters, token_exprs):
    pos = 0
    tokens = []
    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            sys.stderr.write('Illegal characters: %s at %d' % (characters[pos], pos))
            sys.exit(1)
        else:
            pos = match.end(0)
    return tokens


def imp_lexer(characters):
    return lex(characters, token_exprs)


RESERVED = 'RESERVED'
INT = 'INT'
ID = 'ID'

token_exprs = [
    (r'[ \n\t]+', None),
    (r'#[^\n]*', None),
    (r':', RESERVED),
    (r'=', RESERVED),
    (r'\(', RESERVED),
    (r'\)', RESERVED),
    (r'\[', RESERVED),
    (r'\]', RESERVED),
    (r',', RESERVED),
    (r';', RESERVED),
    (r'\+', RESERVED),
    (r'-', RESERVED),
    (r'\*', RESERVED),
    (r'/', RESERVED),
    (r'<=', RESERVED),
    (r'<', RESERVED),
    (r'>=', RESERVED),
    (r'>', RESERVED),
    (r'==', RESERVED),
    (r'!=', RESERVED),
    (r'and', RESERVED),
    (r'or', RESERVED),
    (r'not', RESERVED),
    (r'if', RESERVED),
    (r'then', RESERVED),
    (r'else', RESERVED),
    (r'while', RESERVED),
    (r'do', RESERVED),
    (r'for', RESERVED),
    (r'in', RESERVED),
    (r'end', RESERVED),
    (r'def', RESERVED),
    (r'return', RESERVED),
    (r'print', RESERVED),
    (r'[0-9]+', INT),
    (r'[A-Za-z_][\w_]*', ID),
]
