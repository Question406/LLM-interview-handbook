---
id: drustz-819bea477a018bdfb8
section: openai
order: 93
level: A
title: >-
  Balanced Sequence Generation for (AI, Human, Task) Tags with Prefix
  Constraints
quick: >-
  original-structured-preparation-guide · Balanced Sequence Generation for (AI,
  Human, Task) Tags with Prefix Constraints
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/6c63f46e-8897-4039-b189-0fed5e159bf7
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# AI / Human / Task 标签的前缀平衡序列

> 内容定位：公开标题中的 prefix constraints 与本地真实面经吻合。下文是对该信息的中文重述和原创证明，不复制会员页正文。

## 题意与接口

给定 `t` 个 task、`m` 个 model、`h` 个 human 和目标 `k`，返回 `(task, model, human)` 序列。每个 human 至少出现 `k` 次，且同一 `(task, human)` 至多一次；对任意输出前缀和固定 task，各 model 的出现次数最大值减最小值不超过 1，各 human 的对应计数也不超过 1。

```python
def build_balanced(
    t: int, m: int, h: int, k: int
) -> list[tuple[int, int, int]] | None: ...
```



若 `k > t`，某个 human 不可能获得 `k` 个互异 task，应返回失败。`k == 0` 返回空序列；正任务还要求 `t,m,h > 0`。

## 构造算法

按 `k` 轮输出，每轮给所有 human 一个任务。第 `r` 轮、human `u` 选择 `task=(u+r) mod t`；为每个 task 保存已出现次数 `seen[task]`，选择 `model=seen[task] mod m` 后递增计数。

例如 `t=3,m=2,h=4,k=2` 的前四项可为 `(0,0,0),(1,0,1),(2,0,2),(0,1,3)`。固定 human 在 `k<=t` 时依次拿到 `k` 个不同 task；固定 task 的 model 按 `0..m-1` 循环，所以任意前缀中的计数只能相差 1。每个 `(task,human)` 计数只可能是 0 或 1，因此 human 维度的前缀条件自动成立。

验证时不要只检查最终计数：应逐项扩展前缀，重新统计每个 task 下所有 model 与 human 的次数，才能真正覆盖题目最容易漏掉的约束。

## 复杂度与边界

输出恰好 `h·k` 项，这是满足每人至少 k 项的最短长度。时间为 `O(hk)`，除输出外用 `O(t)` 空间。测试应包含 `k=0`、`k=t`、`m=1`、`h>t`、非法零维度，以及在**每个前缀**上重新统计验证，而不能只检查最终总数。还应确认题目所谓 `(task, model)` 均衡是“固定 task 下不同 model 的计数”这一常见定义。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/6c63f46e-8897-4039-b189-0fed5e159bf7)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
