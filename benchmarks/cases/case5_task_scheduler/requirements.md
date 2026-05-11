# 优先级任务调度器

## 功能概述

实现一个基于优先级的并发任务调度器，支持提交具有不同优先级的任务，按优先级顺序并发执行，支持超时控制、结果收集和异常隔离。单个任务的失败不应影响其他任务的执行。

## 详细需求

### 核心实体/类

#### Task 类
属性：
- `task_id: str` — 任务唯一标识
- `func: Callable[..., Any]` — 要执行的函数
- `args: tuple` — 位置参数，默认空元组
- `kwargs: dict` — 关键字参数，默认空字典
- `priority: int` — 优先级，数值越小优先级越高（0 最高），默认 0
- `timeout: float | None` — 超时时间（秒），None 表示无超时

#### TaskResult（数据类）
- `task_id: str` — 对应任务 ID
- `success: bool` — 是否执行成功
- `result: Any` — 执行返回值（成功时）
- `error: str | None` — 错误信息（失败时）
- `execution_time: float` — 执行耗时（秒）

#### TaskScheduler 类
属性：
- `max_workers: int` — 最大并发线程数，默认 4
- `tasks: list[Task]` — 已提交的任务列表

方法：
- `submit(task: Task) -> None` — 提交任务到调度队列；task_id 重复抛出 `ValueError("任务ID重复")`
- `submit_all(tasks: list[Task]) -> None` — 批量提交；任一 task_id 重复则全部不提交并抛 `ValueError`
- `run() -> list[TaskResult]` — 按优先级执行所有已提交任务
  - 优先级高的（priority 值小）先执行
  - 同优先级任务并发执行（最多 max_workers 个）
  - 有超时的任务若超时则标记为失败，error 为 `"任务超时"`
  - 任务抛出异常时标记为失败，error 为异常消息
  - 单个任务失败不影响其他任务
  - 返回所有 TaskResult 列表，按提交顺序排列
- `get_pending_count() -> int` — 返回待执行任务数
- `clear() -> None` — 清空所有待执行任务

### 调度策略

1. 将所有任务按 priority 升序排列（priority 相同按提交顺序）
2. 从优先级最高的组开始，每次取最多 max_workers 个任务并发执行
3. 当前批次全部完成后，再启动下一批次
4. 超时任务在超时后立即终止（使用 `threading.Event` 或 `concurrent.futures` 的超时机制）
5. 结果按 task_id 排序后返回

### 业务流程

1. 用户创建 Task 对象（指定函数、参数、优先级、超时）
2. 调用 `submit` 或 `submit_all` 提交任务到调度器
3. 调用 `run` 执行所有任务
4. 获取 `TaskResult` 列表，检查各任务执行状态
5. 可根据结果决定是否重新提交失败任务

### 接口/方法说明

| 方法 | 输入 | 输出 | 异常 |
|------|------|------|------|
| `TaskScheduler.submit` | Task | None | task_id 重复 |
| `TaskScheduler.submit_all` | list[Task] | None | 任一重复 |
| `TaskScheduler.run` | 无 | list[TaskResult] | 无 |
| `TaskScheduler.get_pending_count` | 无 | int | 无 |
| `TaskScheduler.clear` | 无 | None | 无 |

## 约束条件

- 使用 Python 标准库（`threading`、`queue`、`concurrent.futures`）
- 使用 `dataclasses.dataclass` 定义 TaskResult
- 所有方法必须有类型注解和 docstring
- 并发执行必须线程安全
- 超时机制必须可靠，不能让超时任务无限期阻塞
- `run` 可以多次调用，每次只执行当前已提交的任务（执行完清空队列）
- 优先级数值越小越高，0 为最高优先级

## 验收条件

- [ ] 任务按优先级顺序执行（高优先级先执行）
- [ ] 同优先级任务并发执行
- [ ] 并发数不超过 max_workers
- [ ] 任务超时被正确标记为失败，不影响其他任务
- [ ] 任务异常被正确捕获，error 字段包含异常信息
- [ ] 所有 TaskResult 正确返回（成功和失败均有记录）
- [ ] execution_time 记录准确
- [ ] task_id 重复的 submit 抛出 ValueError
- [ ] submit_all 中任一重复则全部不提交
- [ ] get_pending_count 反映正确数量
- [ ] clear 清空后 run 返回空列表
- [ ] 多次调用 run 互不干扰
- [ ] 空队列 run 返回空列表
