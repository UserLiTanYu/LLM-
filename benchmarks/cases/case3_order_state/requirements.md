# 订单状态机需求

## 功能描述
实现一个订单状态机，管理订单从创建到完成的生命周期。

## 详细需求

### OrderStatus 枚举
定义以下订单状态：
- `PENDING` — 待支付
- `PAID` — 已支付
- `SHIPPED` — 已发货
- `DELIVERED` — 已签收
- `CANCELLED` — 已取消
- `REFUNDED` — 已退款

### Order 类

属性：
- `order_id: str` — 订单编号
- `status: OrderStatus` — 当前状态，初始为 PENDING
- `amount: float` — 订单金额，必须大于 0
- `items: list[str]` — 商品列表，不能为空
- `status_history: list[tuple[OrderStatus, OrderStatus]]` — 状态变更历史

方法：
1. `pay() -> None` — 支付订单，PENDING → PAID
2. `ship() -> None` — 发货，PAID → SHIPPED
3. `deliver() -> None` — 签收，SHIPPED → DELIVERED
4. `cancel() -> None` — 取消订单，PENDING 或 PAID → CANCELLED
5. `refund() -> None` — 退款，PAID、SHIPPED 或 DELIVERED → REFUNDED

所有状态转换不符合规则时抛出 `ValueError`，错误消息说明当前状态和目标状态。
每次成功状态转换时记录到 `status_history`。

## 合法状态转换表
| 当前状态 | 可转换到 |
|----------|----------|
| PENDING | PAID, CANCELLED |
| PAID | SHIPPED, CANCELLED, REFUNDED |
| SHIPPED | DELIVERED, REFUNDED |
| DELIVERED | REFUNDED |
| CANCELLED | (终态，不可转换) |
| REFUNDED | (终态，不可转换) |

## 约束
- 使用 Python 标准库 + enum 模块
- 所有方法必须有类型注解和docstring
