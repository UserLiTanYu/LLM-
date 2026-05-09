# 计算器模块需求

## 功能描述
实现一个命令行计算器，支持基本的四则运算。

## 详细需求

### Calculator 类
1. 创建一个 Calculator 类，支持以下方法：
   - `add(a: float, b: float) -> float` — 返回两个数的和
   - `subtract(a: float, b: float) -> float` — 返回两个数的差（a - b）
   - `multiply(a: float, b: float) -> float` — 返回两个数的积
   - `divide(a: float, b: float) -> float` — 返回两个数的商（a / b）

2. divide 方法在除数为0时抛出 `ValueError("除数不能为零")`

3. 支持方法链式调用，例如：
   ```
   calc = Calculator()
   result = calc.add(1, 2).multiply(3, 4)  # result 应该是最后一步的结果
   ```

4. 提供一个 `last_result` 属性，保存最后一次运算的结果

## 约束
- 使用 Python 标准库
- 所有方法必须有类型注解和docstring
