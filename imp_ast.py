# coding=utf-8
# Created by deserts at 1/8/17
class Equality:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Statement(Equality):
    pass


class Aexp(Equality):
    pass


class Bexp(Equality):
    pass


class ListExp(Equality):
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return 'ListExp(%s)' % self.items

    def eval(self, env):
        return [item.eval(env) for item in self.items]


class PrintStatement(Statement):
    def __init__(self, exp):
        self.exp = exp

    def __repr__(self):
        return 'PrintStatement %s' % (self.exp,)

    def eval(self, env):
        result = self.exp.eval(env)
        print result


class FunctionStatement(Statement):
    def __init__(self, name, params, body):
        '''
        函数声明，作为语法树的一部分
        :param name: 名
        :param params: 参数列表
        :param body: 函数体
        '''
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return 'FunctionStatement(%s, %s, %s)' % (self.name,
                                                  self.params,
                                                  self.body)

    def eval(self, env):
        # 在env中生成一个可执行的实体
        env[self.name] = ExecFunction(self.name,
                                      self.params,
                                      self.body)


class FunctionCall(Aexp):
    def __init__(self, name, param_list):
        self.param_list = param_list
        self.name = name

    def __repr__(self):
        return 'FunctionCall(%s, %s)' % (self.name, self.param_list)

    def eval(self, env):
        callable_func = env[self.name]
        params = [p.eval(env) for p in self.param_list]
        return callable_func(env, params)


class ExecFunction(object):
    def __init__(self, name, params, body):
        self.name = name
        self.param_names = params
        self.body = body

    def __repr__(self):
        return '<function %s(%s)>' % (self.name,
                                      (str(self.param_names))[1:-1])

    def __call__(self, env, call_params):
        '''
        执行一个函数
        '''
        # 参数列表不匹配
        e = RuntimeError('parameter error: %s(%s) is expected' %
                         (self.name, (str(self.param_names))[1:-1]))
        if call_params and self.param_names:
            if len(call_params) != len(self.param_names):
                raise e
        elif not call_params and not self.param_names:
            pass
        else:
            raise e
        env_temp = env.copy()
        env_exec = dict(env_temp.items() +
                        zip(self.param_names, call_params))
        # 执行
        if self.body:
            self.body.eval(env_exec)
        # 闭包
        for k in env_exec:
            if env.has_key(k) and k not in self.param_names:
                env[k] = env_exec[k]
        return env_exec['return'] if env_exec.has_key('return') else None


class ReturnStatement(Statement):
    def __init__(self, aexp):
        self.aexp = aexp

    def __repr__(self):
        return 'ReturnStatement(%s)' % (self.aexp,)

    def eval(self, env):
        env['return'] = self.aexp.eval(env)


class AssignStatement(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp

    def __repr__(self):
        return 'AssignStatement(%s, %s)' % (self.name, self.aexp)

    def eval(self, env):
        value = self.aexp.eval(env)
        env[self.name] = value


class CompoundStatement(Statement):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __repr__(self):
        return 'CompoundStatement(%s, %s)' % (self.first, self.second)

    def eval(self, env):
        self.first.eval(env)
        self.second.eval(env)


class IfStatement(Statement):
    def __init__(self, condition, true_stmt, false_stmt):
        self.condition = condition
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt

    def __repr__(self):
        return 'IfStatement(%s, %s, %s)' % (self.condition, self.true_stmt, self.false_stmt)

    def eval(self, env):
        condition_value = self.condition.eval(env)
        if condition_value:
            self.true_stmt.eval(env)
        else:
            if self.false_stmt:
                self.false_stmt.eval(env)


class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return 'WhileStatement(%s, %s)' % (self.condition, self.body)

    def eval(self, env):
        condition_value = self.condition.eval(env)
        while condition_value:
            self.body.eval(env)
            condition_value = self.condition.eval(env)


class ForStatement(Statement):
    def __init__(self, var, list, body):
        self.var = var
        self.list = list
        self.body = body

    def __repr__(self):
        return 'ForStatement(%s, %s, %s)' % (self.var, self.list, self.body)

    def eval(self, env):
        env[self.var] = None
        l = self.list.eval(env)
        for item in l:
            env[self.var] = item
            self.body.eval(env)
        env.pop(self.var)


class IntAexp(Aexp):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'IntAexp(%d)' % self.i

    def eval(self, env):
        return self.i


class VarAexp(Aexp):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'VarAexp(%s)' % self.name

    def eval(self, env):
        if self.name in env:
            return env[self.name]
        else:
            raise RuntimeError('using the undefined variable')


class BinopAexp(Aexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'BinopAexp(%s, %s, %s)' % (self.op,
                                          self.left,
                                          self.right)

    def eval(self, env):
        left_value = self.left.eval(env)
        right_value = self.right.eval(env)
        if self.op == '+':
            value = left_value + right_value
        elif self.op == '-':
            value = left_value - right_value
        elif self.op == '*':
            value = left_value * right_value
        elif self.op == '/':
            value = left_value / right_value
        else:
            raise RuntimeError('unknown operator: ' + self.op)
        return value


class RelopBexp(Bexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'RelopBexp(%s, %s, %s)' % (self.op,
                                          self.left,
                                          self.right)

    def eval(self, env):
        left_value = self.left.eval(env)
        right_value = self.right.eval(env)
        if self.op == '<':
            value = left_value < right_value
        elif self.op == '<=':
            value = left_value <= right_value
        elif self.op == '>':
            value = left_value > right_value
        elif self.op == '>=':
            value = left_value >= right_value
        elif self.op == '=':
            value = left_value == right_value
        elif self.op == '!=':
            value = left_value != right_value
        else:
            raise RuntimeError('unknown operator: ' + self.op)
        return value


class AndBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'AndBexp(%s, %s)' % (self.left, self.right)

    def eval(self, env):
        left_value = self.left.eval(env)
        right_value = self.right.eval(env)
        return left_value and right_value


class OrBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'OrBexp(%s, %s)' % (self.left, self.right)

    def eval(self, env):
        left_value = self.left.eval(env)
        right_value = self.right.eval(env)
        return left_value or right_value


class NotBexp(Bexp):
    def __init__(self, exp):
        self.exp = exp

    def __repr__(self):
        return 'NotBexp(%s)' % self.exp

    def eval(self, env):
        value = self.exp.eval(env)
        return not value
