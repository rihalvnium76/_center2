# 游戏规则：
# 1. 每局在 `[1, 100]` 中随机选择一个整数作为 **炸弹数字**
#     - 轮到玩家行动时，必须选择一个数字进行排除
#     - 如果玩家选到炸弹数字，则其他玩家分数+100，并结束该局游戏
#     - 每次选择非炸弹数字后，会自动排除不包含炸弹数字的小于等于，或大于等于选择数字的数字（例如：炸弹数字50，选择25，则自动排除1至25；选择60，则排除60至100）
# 2. 每局生成一个作为提示的随机算式，其结果为 **炸弹数字**
#     - 算式结构为：`整数1 运算符1 整数2 运算符2 整数3 运算符3 整数4`
#     - 运算符号包括 `+ - * /`
#     - 初始3个运算符号隐藏，随着数字排除会逐步解锁其中的 **2个** 运算符号
# 
# 请你根据游戏规则，用 Python 编写一个交互式 CLI 辅助程序，每次输入`<整数1><运算符1><整数2><运算符2><整数3><运算符3><整数4> <最小数字>-<最大数字>`，未知运算符用 `.`表示（例如 `28.9/4-35 28-33`），输出可能的炸弹数字
# 
# 未知运算符抽取为常量，方便自定义

import re
import itertools
from fractions import Fraction

UNKNOWN_OP = '.'

def evaluate(nums, ops):
    """
    计算表达式 nums[0] ops[0] nums[1] ops[1] nums[2] ops[2] nums[3]
    按照标准四则运算优先级（先乘除后加减，同级从左到右），返回 Fraction 结果。
    """
    # 构建中缀 token 列表：数字用 Fraction 表示
    tokens = []
    for i in range(4):
        tokens.append(Fraction(nums[i], 1))
        if i < 3:
            tokens.append(ops[i])

    # 运算符优先级
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    # 调车场算法转后缀表达式
    output = []
    op_stack = []
    for token in tokens:
        if isinstance(token, Fraction):
            output.append(token)
        elif token in precedence:
            while (op_stack and op_stack[-1] in precedence and
                   precedence[op_stack[-1]] >= precedence[token]):
                output.append(op_stack.pop())
            op_stack.append(token)
    while op_stack:
        output.append(op_stack.pop())

    # 计算后缀表达式
    stack = []
    for token in output:
        if isinstance(token, Fraction):
            stack.append(token)
        else:
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                stack.append(a / b)   # Fraction 除法
    return stack[0]

def solve(expr_str, range_str):
    """解析输入并返回所有可能的炸弹数字（已排序、去重）"""
    # 解析表达式
    op_chars = f'+\\-*/{UNKNOWN_OP}'
    expr_pattern = re.compile(r'^(\d+)([{}])(\d+)([{}])(\d+)([{}])(\d+)$'.format(op_chars, op_chars, op_chars))
    m = expr_pattern.match(expr_str)
    if not m:
        raise ValueError("无效的表达式格式，应为 整数1运算符1整数2运算符2整数3运算符3整数4")

    nums = [int(m.group(1)), int(m.group(3)), int(m.group(5)), int(m.group(7))]
    ops = [m.group(2), m.group(4), m.group(6)]

    # 解析范围
    parts = range_str.split('-')
    if len(parts) != 2:
        raise ValueError("范围格式错误，应为 min-max")
    try:
        min_val = int(parts[0])
        max_val = int(parts[1])
    except ValueError:
        raise ValueError("范围必须为整数")

    # 枚举未知运算符
    all_ops = ['+', '-', '*', '/']
    unknown_indices = [i for i, op in enumerate(ops) if op == UNKNOWN_OP]
    possible_results = set()

    for combo in itertools.product(all_ops, repeat=len(unknown_indices)):
        cur_ops = ops[:]
        for idx, op in zip(unknown_indices, combo):
            cur_ops[idx] = op

        result = evaluate(nums, cur_ops)
        # 结果必须为整数
        if result.denominator == 1:
            val = result.numerator
            if min_val <= val <= max_val and 1 <= val <= 100:
                possible_results.add(val)

    return sorted(possible_results)

def main():
    print(f"炸弹数字辅助程序 (表达式 范围 举例 45-46{UNKNOWN_OP}10*9 1-100，输入 quit 退出)")
    while True:
        try:
            line = input("\n>>> 请输入 表达式 范围: ").strip()
        except EOFError:
            break
        if not line:
            continue
        if line.lower() == 'quit':
            break

        parts = line.split()
        if len(parts) != 2:
            print("格式错误：需要两个部分，用空格分隔")
            continue

        expr_str, range_str = parts[0], parts[1]
        try:
            results = solve(expr_str, range_str)
            if results:
                print("可能的炸弹数字:", ' '.join(map(str, results)))
            else:
                print("没有可能的炸弹数字")
        except Exception as e:
            print("错误:", e)

if __name__ == "__main__":
    main()
