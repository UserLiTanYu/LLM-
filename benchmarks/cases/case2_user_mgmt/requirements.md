# 用户管理系统需求

## 功能描述
实现一个简单的用户管理系统，支持用户的增删改查（CRUD）操作。

## 详细需求

### User 类
创建一个 User 类，包含以下属性：
- `id: int` — 用户唯一标识，创建时自动生成（自增）
- `username: str` — 用户名，长度3-20字符
- `email: str` — 邮箱，必须包含 @
- `age: int` — 年龄，范围 0-150

### UserService 类
创建一个 UserService 类，管理用户列表：

1. `add_user(username: str, email: str, age: int) -> User` — 添加用户
   - 用户名不能为空
   - 邮箱格式必须正确（包含 @）
   - 年龄必须在 0-150 之间
   - 不满足条件时抛出 ValueError

2. `get_user(user_id: int) -> User` — 根据 ID 获取用户
   - 用户不存在时抛出 ValueError("用户不存在")

3. `get_all_users() -> list[User]` — 返回所有用户列表

4. `update_user(user_id: int, username: str = None, email: str = None, age: int = None) -> User` — 更新用户
   - 只更新传入的非 None 字段
   - 用户不存在时抛出 ValueError

5. `delete_user(user_id: int) -> bool` — 删除用户
   - 用户不存在时抛出 ValueError
   - 删除成功返回 True

6. `search_by_username(keyword: str) -> list[User]` — 根据用户名关键词模糊搜索

### User 类额外方法
- `__eq__(self, other)` — 根据 id 判断相等
- `__repr__(self)` — 返回可读的字符串表示

## 约束
- 使用 Python 标准库
- 所有方法必须有类型注解和docstring
- UserService 内部使用字典存储用户（以 id 为键）
