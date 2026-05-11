# 订单状态机

## 功能概述

实现一个电商订单状态管理系统，管理订单从创建到完结的完整生命周期。核心是一个有限状态机，确保订单状态只能按照预设的合法路径转换，防止出现非法状态跳转。

## 详细需求

### 核心实体/类

#### OrderStatus（枚举）
定义以下 6 种状态：
- `PENDING` — 待确认（初始状态）
- `CONFIRMED` — 已确认
- `SHIPPED` — 已发货
- `DELIVERED` — 已签收（终态）
- `CANCELED` — 已取消（终态）
- `REFUNDED` — 已退款（终态）

#### OrderItem（数据类）
- `name: str` — 商品名称
- `price: float` — 单价
- `quantity: int` — 数量
- `item_id: str` — 商品编号

#### Order 类
属性：
- `order_id: str` — 订单号，唯一
- `items: list[OrderItem]` — 订单商品列表
- `status: OrderStatus` — 当前状态，初始为 PENDING
- `total_amount: float` — 订单总金额（只读属性，自动计算 = sum(item.price * item.quantity for item in items)）
- `status_history: list[tuple[OrderStatus, str]]` — 状态变更历史，每项为 (状态, 备注)

方法：
- `add_item(item: OrderItem) -> None` — 添加商品；仅在 PENDING 状态可操作，否则抛 `ValueError("仅待确认状态可修改商品")`
- `remove_item(item_id: str) -> None` — 移除商品；仅在 PENDING 状态可操作，商品不存在抛 `ValueError("商品不存在")`
- `get_total() -> float` — 返回 total_amount

#### OrderStateMachine 类
方法：
- `confirm(order: Order) -> None` — PENDING → CONFIRMED；订单商品为空时抛 `ValueError("订单无商品，无法确认")`
- `ship(order: Order) -> None` — CONFIRMED → SHIPPED
- `deliver(order: Order) -> None` — SHIPPED → DELIVERED
- `cancel(order: Order) -> None` — PENDING 或 CONFIRMED → CANCELED；已发货后不可取消，抛 `ValueError("已发货订单不可取消")`
- `refund(order: Order) -> None` — DELIVERED → REFUNDED；仅已签收可退款，抛 `ValueError("仅已签收订单可退款")`

所有非法状态转换方法必须抛出 `ValueError`，错误消息描述具体原因。

### 状态转换规则

```
PENDING ──confirm()──▶ CONFIRMED ──ship()──▶ SHIPPED ──deliver()──▶ DELIVERED ──refund()──▶ REFUNDED
   │                      │
   └──cancel()──▶ CANCELED ◀──cancel()──┘
```

合法转换：
- PENDING → CONFIRMED（确认）
- PENDING → CANCELED（取消）
- CONFIRMED → SHIPPED（发货）
- CONFIRMED → CANCELED（取消）
- SHIPPED → DELIVERED（签收）
- DELIVERED → REFUNDED（退款）

终结态（DELIVERED、CANCELED、REFUNDED）不可再进行任何转换。

### 业务流程

1. 用户创建订单（PENDING），添加商品
2. 商家确认订单（PENDING → CONFIRMED）
3. 商家发货（CONFIRMED → SHIPPED）
4. 用户签收（SHIPPED → DELIVERED）
5. 用户可申请退款（DELIVERED → REFUNDED）
6. 用户在确认前或确认后可取消（PENDING/CONFIRMED → CANCELED）

### 接口/方法说明

| 方法 | 前置状态 | 目标状态 | 异常条件 |
|------|----------|----------|----------|
| `confirm` | PENDING | CONFIRMED | 订单无商品 |
| `ship` | CONFIRMED | SHIPPED | 状态非CONFIRMED |
| `deliver` | SHIPPED | DELIVERED | 状态非SHIPPED |
| `cancel` | PENDING/CONFIRMED | CANCELED | 已发货 |
| `refund` | DELIVERED | REFUNDED | 状态非DELIVERED |

## 约束条件

- 使用 Python 标准库
- 使用 `enum.Enum` 定义 OrderStatus
- 使用 `dataclasses.dataclass` 定义 OrderItem
- 所有方法必须有类型注解和 docstring
- 状态转换时自动记录到 `status_history`（含时间戳格式备注）
- `total_amount` 为只读属性（使用 @property）
- 终态订单不可再转换，必须抛出 ValueError

## 验收条件

- [ ] 订单创建后初始状态为 PENDING
- [ ] PENDING 状态下可添加和移除商品
- [ ] 非 PENDING 状态下修改商品抛出 ValueError
- [ ] confirm 空订单抛出 ValueError
- [ ] 所有合法状态转换正确执行
- [ ] 所有非法状态转换抛出 ValueError（带描述性消息）
- [ ] SHIPPED 后 cancel 抛出 ValueError
- [ ] 终态订单（DELIVERED/CANCELED/REFUNDED）不可再转换
- [ ] total_amount 自动计算且为只读
- [ ] status_history 记录完整的状态变更轨迹
