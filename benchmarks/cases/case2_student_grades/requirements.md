# 学生成绩管理系统

## 功能概述

实现一个学生成绩管理系统，支持学生信息的增删查改，以及各科目成绩的录入、统计和排名功能。系统面向教师用户，帮助管理班级学生的多科目成绩。

## 详细需求

### 核心实体/类

#### Student 类
- `student_id: str` — 学号，唯一标识
- `name: str` — 姓名
- `grades: dict[str, float]` — 科目→成绩映射，如 `{"语文": 90.0, "数学": 85.5}`

方法：
- `add_grade(subject: str, score: float) -> None` — 添加或更新某科成绩
- `get_grade(subject: str) -> float | None` — 获取某科成绩，未录入返回 None
- `get_average() -> float` — 计算所有科目的平均分

#### GradeManager 类
管理所有学生，提供班级级别的查询和统计功能。内部维护学生列表。

方法：
- `add_student(student_id: str, name: str) -> Student` — 添加学生，学号重复时抛出 `ValueError("学号已存在")`
- `remove_student(student_id: str) -> None` — 删除学生，学号不存在时抛出 `ValueError("学生不存在")`
- `get_student(student_id: str) -> Student` — 查询学生，学号不存在时抛出 `ValueError("学生不存在")`
- `get_all_students() -> list[Student]` — 返回所有学生列表
- `record_grade(student_id: str, subject: str, score: float) -> None` — 录入成绩，成绩不在 0-100 范围内抛出 `ValueError("成绩必须在0-100之间")`
- `get_class_average(subject: str | None = None) -> float` — 全班平均分；若指定科目则计算该科平均分，否则计算总平均；无学生时返回 0.0
- `get_top_students(n: int = 3) -> list[Student]` — 按平均分降序返回前 n 名学生；学生数不足 n 时返回所有学生
- `get_subject_stats(subject: str) -> dict` — 返回该科目的统计信息，格式为 `{"max": float, "min": float, "avg": float, "count": int}`；无成绩时 `count=0`，其余为 0.0

### 业务流程

1. 教师创建班级 → 逐个添加学生（add_student）
2. 考试后教师录入成绩（record_grade），可逐科录入
3. 查询班级整体情况（get_class_average）
4. 查看排名（get_top_students）和各科统计（get_subject_stats）

### 接口/方法说明

| 方法 | 输入 | 输出 | 异常 |
|------|------|------|------|
| `Student.add_grade` | subject(str), score(float) | None | score 不在 0-100 抛 ValueError |
| `GradeManager.add_student` | student_id(str), name(str) | Student | 学号重复抛 ValueError |
| `GradeManager.remove_student` | student_id(str) | None | 不存在抛 ValueError |
| `GradeManager.get_student` | student_id(str) | Student | 不存在抛 ValueError |
| `GradeManager.record_grade` | student_id, subject, score | None | 学生不存在或成绩无效抛 ValueError |
| `GradeManager.get_class_average` | subject(str\|None) | float | 无 |
| `GradeManager.get_top_students` | n(int) | list[Student] | 无 |
| `GradeManager.get_subject_stats` | subject(str) | dict | 无 |

## 约束条件

- 使用 Python 标准库
- 所有方法必须有类型注解和 docstring
- 成绩范围为 [0, 100] 的 float
- `get_class_average` 在无学生时返回 0.0，不是抛异常
- `get_top_students` 返回的列表按平均分降序排列

## 验收条件

- [ ] 可以正常添加、查询、删除学生
- [ ] 可以录入和更新成绩
- [ ] 平均分计算正确（含浮点精度）
- [ ] 排名功能返回正确的顺序
- [ ] 科目统计 max/min/avg/count 正确
- [ ] 重复学号添加抛出 ValueError
- [ ] 不存在的学生操作抛出 ValueError
- [ ] 无效成绩（负数或超100）抛出 ValueError
- [ ] 空班级时 get_class_average 返回 0.0
- [ ] 空班级时 get_top_students 返回空列表
