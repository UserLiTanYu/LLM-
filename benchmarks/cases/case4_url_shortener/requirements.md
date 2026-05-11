# 短链接服务

## 功能概述

实现一个 URL 短链接服务，将长 URL 转换为短码，并通过短码重定向回原始 URL。支持自定义短码、访问统计、短码过期管理。这是一个后端服务模块，不涉及 HTTP 服务器，仅提供核心业务逻辑。

## 详细需求

### 核心实体/类

#### URLValidator 类
方法：
- `validate(url: str) -> bool` — 验证 URL 格式是否合法（必须以 http:// 或 https:// 开头，且包含有效域名）
- `normalize(url: str) -> str` — 标准化 URL（去除尾部斜杠、转小写协议和域名部分）

#### URLShortener 类
属性：
- `store: dict[str, dict]` — 内部存储，短码 → {"url": str, "created_at": float, "access_count": int, "expires_at": float | None}

方法：
- `shorten(url: str, custom_code: str | None = None, ttl: int | None = None) -> str` — 将长URL生成短码
  - 若 custom_code 为 None，自动生成 6 位短码（base62 编码）
  - 若 custom_code 不为 None，使用该自定义短码（如已被占用抛出 `ValueError("短码已被占用")`）
  - ttl 为过期时间（秒），None 表示永不过期
  - url 不合法时抛出 `ValueError("无效的URL")`
  - 同一个 URL（标准化后）返回相同短码（已有映射则复用，不重复创建）
- `resolve(code: str) -> str` — 解析短码，返回原始URL
  - 短码不存在抛出 `ValueError("短码不存在")`
  - 短码已过期抛出 `ValueError("短码已过期")`
  - 每次解析时 access_count + 1
- `get_stats(code: str) -> dict` — 获取短码统计信息，返回格式：
  `{"url": str, "access_count": int, "created_at": float, "expires_at": float | None, "is_expired": bool}`
  - 短码不存在抛出 `ValueError("短码不存在")`
- `delete(code: str) -> None` — 删除短码映射；短码不存在抛出 `ValueError("短码不存在")`
- `cleanup_expired() -> int` — 清理所有已过期的短码，返回清理数量
- `list_all() -> list[dict]` — 列出所有有效短码及其统计信息

### 短码生成规则

- 自动生成：对 "原始URL + 时间戳" 取 SHA256，取前 8 字节转为整数，base62 编码取前 6 位
- base62 字符集：`0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`
- 若生成的短码已存在且指向不同 URL，则在时间戳上加 1 重试（最多 5 次）
- 自定义短码：用户提供 4-10 位字母数字组合字符串，验证通过则直接使用

### 业务流程

1. 用户输入长 URL → `validate` 验证 → `normalize` 标准化 → `shorten` 生成短码
2. 用户访问短码 → `resolve` 查找原始 URL → access_count + 1 → 返回原始 URL
3. 定期调用 `cleanup_expired` 清理过期短码
4. 管理员调用 `get_stats` 和 `list_all` 查看服务状态

### 接口/方法说明

| 方法 | 输入 | 输出 | 异常 |
|------|------|------|------|
| `URLValidator.validate` | url(str) | bool | 无 |
| `URLValidator.normalize` | url(str) | str | 无 |
| `URLShortener.shorten` | url, custom_code, ttl | str(短码) | 无效URL、短码占用 |
| `URLShortener.resolve` | code(str) | str(原始URL) | 不存在、已过期 |
| `URLShortener.get_stats` | code(str) | dict | 不存在 |
| `URLShortener.delete` | code(str) | None | 不存在 |
| `URLShortener.cleanup_expired` | 无 | int | 无 |
| `URLShortener.list_all` | 无 | list[dict] | 无 |

## 约束条件

- 使用 Python 标准库（hashlib, time, re）
- 所有方法必须有类型注解和 docstring
- `shorten` 对相同 URL 应返回同一短码（幂等）
- 自动生成的短码长度固定为 6 位
- 自定义短码必须由 4-10 位字母数字组成，否则抛 `ValueError("自定义短码格式无效")`
- 过期判断使用 `time.time()`
- 线程安全不在本次需求范围内

## 验收条件

- [ ] 合法 URL 能成功生成短码
- [ ] 无效 URL（无协议、无域名）抛出 ValueError
- [ ] 相同 URL 多次 shorten 返回相同短码
- [ ] 自定义短码能正常使用
- [ ] 自定义短码冲突抛出 ValueError
- [ ] 自定义短码格式不符抛出 ValueError
- [ ] resolve 正确返回原始 URL
- [ ] resolve 不存在的短码抛出 ValueError
- [ ] resolve 过期短码抛出 ValueError
- [ ] access_count 随 resolve 递增
- [ ] cleanup_expired 正确清理且返回清理数量
- [ ] delete 后 resolve 抛出 ValueError
- [ ] URL 标准化正确（尾部斜杠、大小写）
