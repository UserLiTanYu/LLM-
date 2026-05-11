# TODO Web 应用

## 功能概述

实现一个完整的 TODO 待办事项管理 Web 应用，用户通过浏览器界面管理待办事项。系统分为后端业务逻辑层和前端 Web 界面层。

## 技术栈

- **后端框架**：Flask（Python Web 框架，需在 requirements.txt 中声明）
- **模板引擎**：Jinja2（Flask 内置）
- **前端**：HTML + CSS + JavaScript（不依赖前端构建工具）
- **后端业务逻辑**：Python 标准库（`uuid`, `datetime`, `dataclasses`）

## 详细需求

### 一、后端业务逻辑层 — TodoService

与 case6 一致，提供纯业务逻辑（不含 Flask 依赖）。

#### TodoItem（数据类）
- `id: str` — 唯一标识，自动生成（UUID4）
- `title: str` — 标题，非空，长度 1-200
- `description: str` — 描述，可为空，默认 ""
- `completed: bool` — 完成状态，默认 False
- `created_at: str` — 创建时间，ISO 格式字符串
- `updated_at: str` — 最后更新时间，ISO 格式字符串

#### TodoService 类
内部使用字典存储（`id → TodoItem`）。

方法：
- `create(title, description="") -> TodoItem`
  - title 为空或仅空白字符，抛出 `ValueError("标题不能为空")`
  - title 超过 200 字符，抛出 `ValueError("标题不能超过200个字符")`
- `get_by_id(todo_id) -> TodoItem` — 不存在抛出 `ValueError("TODO不存在")`
- `list_all(completed=None, page=1, page_size=10, order_by="created_at") -> dict`
  - 返回 `{"data": [...], "total": int, "page": int, "page_size": int, "total_pages": int}`
  - 非法 page/page_size 抛出 ValueError
  - 非法 order_by 抛出 ValueError("不支持的排序字段")
- `update(todo_id, title=None, description=None, completed=None) -> TodoItem` — 部分更新
- `delete(todo_id) -> None` — 不存在抛出 ValueError
- `toggle(todo_id) -> TodoItem` — 切换完成状态
- `get_stats() -> dict` — 返回 `{"total": int, "completed": int, "incomplete": int, "completion_rate": float}`

### 二、前端 Web 界面层 — Flask App

#### 页面路由

| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 首页：显示待办列表，支持状态筛选和分页 |
| `/add` | POST | 新增待办，重定向回首页 |
| `/toggle/<id>` | POST | 切换完成状态，重定向回首页 |
| `/delete/<id>` | POST | 删除待办，重定向回首页 |
| `/stats` | GET | 统计页面：总数/已完成/未完成/完成率 |

#### 首页 UI 要求
- 页面标题："TODO 待办事项"
- 顶部：新增待办表单（标题输入框 + 添加按钮）
- 中间：筛选栏（全部 / 未完成 / 已完成）
- 列表：每项显示标题、创建时间、完成状态，右侧有"完成/取消"和"删除"按钮
- 已完成项目用删除线标记
- 底部分页导航
- 样式简洁现代，居中布局，最大宽度 700px

#### 统计页 UI 要求
- 显示总数/已完成/未完成/完成率
- 完成率以进度条展示
- 返回首页链接

### 三、项目文件结构

```
app.py                          # Flask 应用入口
requirements.txt                # Flask 依赖
todo_service.py                 # TodoService + TodoItem 业务逻辑（独立于 Flask）
templates/
  ├── index.html                # 首页模板（列表 + 新增表单 + 筛选 + 分页）
  └── stats.html                # 统计页模板
static/
  └── style.css                 # 全局样式
```

## 约束条件

- 后端业务逻辑（TodoService）用 Python 标准库，不依赖 Flask
- Flask 仅用于路由和模板渲染
- HTML 模板使用 Jinja2 语法
- 前端样式可直接写在 `<style>` 标签中或独立 CSS 文件
- 所有 Python 文件必须有类型注解和 docstring
- 启动命令：`python app.py`（默认端口 5000，开启 debug 模式）

## 验收条件

### 后端验收
- [ ] create 创建 TODO 成功，返回 TodoItem 含有效 UUID
- [ ] create 空标题或超长标题抛出 ValueError
- [ ] list_all 返回正确的分页结构，过滤和排序正确
- [ ] update 部分更新正确，updated_at 被刷新
- [ ] delete 和 toggle 行为正确
- [ ] get_stats 统计数据正确

### 前端验收
- [ ] 浏览器访问 `http://localhost:5000` 可看到待办列表
- [ ] 可新增待办，新增后出现在列表中
- [ ] 可切换完成状态，已完成项显示删除线
- [ ] 可删除待办
- [ ] 筛选按钮（全部/未完成/已完成）正常工作
- [ ] 分页导航正常工作
- [ ] 统计页面显示正确的统计数据
