# 基于解析器组合子的简单解释器

一个玩具级解释器，包含词法分析、语法分析、抽象语法树生成以及解释执行等模块；此外，基于解析器组合子，实现一个通用的不确定自顶向下语法分析器。使用Python语言。

### 通用语法分析器
为了简明的表达解析器组合子的设计思想，同时与编译原理课程理论结合，设计了一个较为通用的不确定的自顶向下语法分析器。（general_parser.py，50行代码不到，有作弊之嫌）
文法规则的书写与编译原理课程中类似，下面是对表达式文法的描述：

```S -> E;E -> LI(T, VT('+'));T -> LI(F, VT('*'));F -> VT('i') | VT('n')
```
其中大写字母为非终结符，VT('x')表示终结符x， 规则LI(x, 终结符VT) 表示一个由终结符VT分割的任意多个x形成的列表，此外可用+，|表示“连接”和“或”，括号可改变结合性。e.g.上述第二条规则等价于 E -> E+T | T。
对于含左递归的文法，不需要手工消除左递归；对于含左公因子的文法，由于解析器本身支持回溯，也不需要手工处理。

```
> python general_parser.py grammer 'i+i*n+i*n'
语法规则如下: 
S -> E;
E -> LI(T, VT('+'));
T -> LI(F, VT('*'));
F -> VT('i') | VT('n')
解析成功：('+', ('+', 'i', ('*', 'i', 'n')), ('*', 'i', 'n'))

```

### 语言解释器

语法规则结合了Python和Pascal，语法分析生成语法树，直接计算其节点，实现了函数、流程控制、列表、输出等简单功能。具体请看下面的代码示例。

测试:

```
> python imp.py factorial.imp 
120

> python imp.py fib.imp
13

> python imp.py hello.imp -m verbose 
15
Final global variable values:
list: [1, 2, 3, 4, 5]
sum_of_list: <function sum_of_list('list')>

```
代码示例：

```
# 求和
list = [1, 2, 3, 4, 5];
def sum_of_list(list):
    sum = 0;
    for i in list do
        sum = sum + i
    end;
    return sum
end;
print sum_of_list(list)

# 斐波那契
def fib(n):
    if n <= 2 then
        return 1
    else
        return fib(n-1) + fib(n-2)
    end
end;
print fib(7)

# 阶乘
foo = 5;
p = 1;
n = 1000;
def factorial(n):
    while n > 0 do
      p = p * n;
      n = n - 1
    end
end;
x = factorial(foo);
print p
```

文件说明：

```
├── README.md
├── combinators.py		组合子库
├── factorial.imp			测试用例，阶乘
├── fib.imp				测试用例，斐波那契数列
├── general_parser.py		通用语法分析器
├── grammer				通用语法分析器测试用文法规则
├── hello.imp				测试用例，列表（数组）值累加
├── imp.py				解释器入口
├── imp_ast.py			抽象语法树及解释执行
├── imp_lexer.py			词法分析
├── imp_parser.py			语法分析
├── imp_test.py			一些单元测试内容
```

感谢以下几位博主所做的工作：

https://jayconrod.com/tags/imp

http://www.cnblogs.com/Ninputer/archive/2011/06/26/2090645.html

http://www.cnblogs.com/huxi/archive/2011/06/18/2084316.html