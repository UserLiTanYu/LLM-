# TODO REST API 服务

## 功能概述

实现一个 TODO 待办事项管理的 REST API 服务模块，提供完整的 CRUD 操作，支持分页查询、按状态过滤、排序和输入验证。本模块聚焦于核心业务逻辑层，不依赖特定 Web 框架，但接口设计需符合 RESTful 规范。

## 详细需求

### 核心实体/类

#### TodoItem（数据类）
- `id: str` — 唯一标识，自动生成（UUID4）
- `title: str` — 标题，非空，长度 1-200
- `description: str` — 描述，可为空，默认 ""
- `completed: bool` — 完成状态，默认 False
- `created_at: str` — 创建时间，ISO 格式字符串
- `updated_at: str` — 最后更新时间，ISO 格式字符串

#### TodoService 类
内部使用字典存储 TodoItem（`id → TodoItem`），提供业务逻辑。

方法：
- `create(title: str, description: str = "") -> TodoItem` — 创建新待办
  - title 为空或仅空白字符，抛出 `ValueError("标题不能为空")`
  - title 超过 200 字符，抛出 `ValueError("标题不能超过200个字符")`
  - 自动设置 created_at 和 updated_at 为当前时间
- `get_by_id(todo_id: str) -> TodoItem` — 根据 ID 查询
  - 不存在抛出 `ValueError("TODO不存在")`
- `list_all(completed: bool | None = None, page: int = 1, page_size: int = 10, order_by: str = "created_at") -> dict` — 列表查询
  - completed=None 返回全部，True 返回已完成，False 返回未完成
  - 返回格式：`{"data": list[TodoItem], "total": int, "page": int, "page_size": int, "total_pages": int}`
  - page 从 1 开始，page 超出范围时返回空列表
  - page 或 page_size 非法（<=0）时抛出 `ValueError`
  - order_by 支持 "created_at"（默认降序）和 "updated_at"（默认降序）；非法值抛出 `ValueError("不支持的排序字段")`
- `update(todo_id: str, title: str | None = None, description: str | None = None, completed: bool | None = None) -> TodoItem` — 更新待办
  - 只更新传入的非 None 字段
  - 不存在抛出 `ValueError("TODO不存在")`
  - title 校验同 create
  - 更新后自动刷新 updated_at
- `delete(todo_id: str) -> None` — 删除待办
  - 不存在抛出 `ValueError("TODO不存在")`
- `toggle(todo_id: str) -> TodoItem` — 切换完成状态，返回更新后的 TodoItem
  - 不存在抛出 `ValueError("TODO不存在")`
- `get_stats() -> dict` — 获取统计信息
  - 返回格式：`{"total": int, "completed": int, "incomplete": int, "completion_rate": float}`

### API 端点映射（供后续 Web 层参考）

| HTTP方法 | 路径 | 对应 Service 方法 |
|----------|------|-------------------|
| POST | /todos | create(title, description) |
| GET | /todos?completed=&page=&page_size=&order_by= | list_all(...) |
| GET | /todos/{id} | get_by_id(id) |
| PUT | /todos/{id} | update(id, title, description, completed) |
| DELETE | /todos/{id} | delete(id) |
| PATCH | /todos/{id}/toggle | toggle(id) |
| GET | /todos/stats | get_stats() |

### 业务流程

1. 用户创建待办（POST /todos）→ 返回 TodoItem 含 ID
2. 用户查看列表（GET /todos）→ 支持过滤和分页
3. 用户修改待办（PUT /todos/{id}）→ 部分更新
4. 用户切换完成状态（PATCH /todos/{id}/toggle）
5. 用户删除待办（DELETE /todos/{id}）
6. 用户查看统计（GET /todos/stats）

### 接口/方法说明

| 方法 | 异常条件 | 返回 |
|------|----------|------|
| `create` | title 为空/超长 | TodoItem |
| `get_by_id` | ID 不存在 | TodoItem |
| `list_all` | page/page_size<=0, order_by 非法 | 分页字典 |
| `update` | ID 不存在, title 非法 | TodoItem |
| `delete` | ID 不存在 | None |
| `toggle` | ID 不存在 | TodoItem |
| `get_stats` | 无 | dict |

## 约束条件

- 使用 Python 标准库（`uuid`, `datetime`, `dataclasses`）
- 不依赖任何 Web 框架（Flask/FastAPI），仅实现核心业务逻辑层
- 使用 `dataclasses.dataclass` 定义 TodoItem
- 所有方法必须有类型注解和 docstring
- created_at 和 updated_at 使用 ISO 8601 格式字符串（`datetime.datetime.now().isoformat()`）
- `list_all` 的分页从第 1 页开始
- 排序默认降序（最新的在前）

## 验收条件

- [ ] create 创建 TODO 成功，返回 TodoItem 含有效 UUID
- [ ] create 空标题或超长标题抛出 ValueError
- [ ] get_by_id 返回正确的 TodoItem
- [ ] get_by_id 不存在的 ID 抛出 ValueError("TODO不存在")
- [ ] list_all 返回正确的分页结构
- [ ] list_all completed 过滤正确
- [ ] list_all page 超出范围返回空列表
- [ ] list_all 非法 page/page_size 抛出 ValueError
- [ ] list_all 非法 order_by 抛出 ValueError
- [ ] update 部分更新正确，只修改传入字段
- [ ] update 后 updated_at 被刷新
- [ ] update 不存在 ID 抛出 ValueError
- [ ] delete 删除成功，之后 get_by_id 抛异常
- [ ] delete 不存在 ID 抛出 ValueError
- [ ] toggle 正确切换 completed 状态
- [ ] get_stats 统计数据正确
- [ ] 多次操作后数据一致性保持
