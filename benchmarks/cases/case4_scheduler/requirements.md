# 任务调度器需求

## 功能描述
实现一个简单的并发任务调度器，支持任务的提交、调度和执行。

## 详细需求

### Task 类
属性：
- `task_id: int` — 任务唯一标识
- `name: str` — 任务名称
- `func: callable` — 要执行的函数（无参数的可调用对象）
- `status: str` — 任务状态：pending/running/completed/failed
- `result: any` — 执行结果（初始为 None）
- `error: str | None` — 错误信息（初始为 None）

### TaskScheduler 类

1. `submit(name: str, func: callable) -> Task` — 提交任务，返回 Task 对象，状态为 pending

2. `run_all(max_workers: int = 3) -> list[Task]` — 并发执行所有 pending 任务
   - 使用 `concurrent.futures.ThreadPoolExecutor`
   - 每个任务执行后更新其 status、result 或 error
   - 返回所有已执行的任务列表

3. `run_one(task_id: int) -> Task` — 执行单个任务
   - 如果任务不存在抛出 ValueError
   - 如果任务已完成或正在运行抛出 RuntimeError
   - 返回执行后的 Task

4. `get_task(task_id: int) -> Task` — 获取任务状态
   - 任务不存在时抛出 ValueError

5. `get_all_tasks() -> list[Task]` — 获取所有任务

6. `get_stats() -> dict` — 返回统计信息：`{pending, running, completed, failed}` 各状态数量

## 异常处理
- 任务函数抛出异常时，Task.status 设为 "failed"，Task.error 记录错误信息
- 调度器本身不应因单个任务失败而崩溃

## 约束
- 使用 Python 标准库（threading、concurrent.futures）
- 所有方法必须有类型注解和docstring
- 操作共享数据时必须线程安全（使用 threading.Lock）
