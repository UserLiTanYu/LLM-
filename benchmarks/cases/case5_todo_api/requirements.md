# TODO API 服务需求

## 功能描述
实现一个简单的 TODO 管理 REST API 服务。

## 详细需求

### TodoItem 数据类
属性：
- `id: int` — 自动生成的唯一标识
- `title: str` — 标题，长度 1-100
- `description: str` — 描述，可选，默认为空字符串
- `completed: bool` — 是否完成，默认为 False
- `created_at: str` — 创建时间，ISO 8601 格式

### TodoService 类（业务逻辑层）

1. `create(title: str, description: str = "") -> TodoItem` — 创建待办事项
   - title 不能为空且不超过 100 字符

2. `get(item_id: int) -> TodoItem` — 获取单个事项
   - 不存在时抛出 ValueError

3. `list_all(completed: bool = None) -> list[TodoItem]` — 列出所有事项
   - completed=True 只返回已完成的
   - completed=False 只返回未完成的
   - completed=None 返回全部

4. `update(item_id: int, title: str = None, description: str = None, completed: bool = None) -> TodoItem` — 更新事项
   - 只更新传入的非 None 字段

5. `delete(item_id: int) -> bool` — 删除事项

6. `toggle(item_id: int) -> TodoItem` — 切换完成状态

### API 路由（使用 FastAPI）

为 TodoService 创建以下 REST API 端点：

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /todos | 创建待办事项 |
| GET | /todos | 获取列表（可选 ?completed=true/false） |
| GET | /todos/{id} | 获取单个事项 |
| PUT | /todos/{id} | 更新事项 |
| DELETE | /todos/{id} | 删除事项 |
| PATCH | /todos/{id}/toggle | 切换完成状态 |

## API 规范
- 请求体为 JSON
- 返回 HTTP 状态码：200（成功）、201（创建）、404（未找到）、422（参数错误）
- 404 和 422 返回 `{"error": "消息"}` 格式

## 约束
- 使用 FastAPI + uvicorn
- 不使用数据库，TodoService 内部用字典存储
- 所有方法必须有类型注解和docstring
