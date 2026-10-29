---
id: drustz-cf158429bc21bfd5a3
section: plans
order: 14
level: A
title: 顶尖AI公司面经全解析：OpenAI · xAI · Anthropic · 3.3 高频Coding真题（Q1-Q6编号系统）
quick: 作者文档章节 · 顶尖AI公司面经全解析：OpenAI · xAI · Anthropic · 3.3 高频Coding真题（Q1-Q6编号系统）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 作者复习计划与报告
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/final_report_v2.md
    type: primary
---
## 3.3 高频Coding真题（Q1-Q6编号系统）

Anthropic的Coding面试题目有固定编号（Q1-Q6），候选人可以在Portal中看到自己被分配的题号。

### Q1: Web Crawler (爬虫) 或 Image Processing (图片处理)

**语言决定题目**：用Python → 可能是Web Crawler或Image Processing；其他语言 → 通常是Web Crawler。

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1167684-1-1.html)

**Web Crawler**：
- 先实现单线程BFS爬虫（LC 1236）
- Follow-up：实现多线程版本
- Follow-up：如果有多个服务器如何优化（讲思路即可，不需要implement）
- 面试官会给URL fetcher和HTML Parser的接口
- 有人用Redis当central queue storage with 1 host server access the queue and assign slave servers to batch process

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1160362-1-1.html)

**Image Processing**：

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1154439-1-1.html)

- 有m个图片，n个pipeline，每个Pipeline有k个操作
- 6种transformation：grayscale, flip horizontally, flip vertically, scale, blur, rotate
- 前三个无参数，后三个有参数
- 需要用Python库（Pillow或scikit-image）处理
- Follow-up：大图片处理，使用ProcessPoolExecutor加速
- 考察搜索文档和快速使用库的能力

**详细步骤**：有4个folder（small images, big images, out, transformations）。先用small images做测试并save output图片到out folder。每一个transformation json file里面会有一个到多个transformation，如果有多个需要sequentially apply到图片上。大图片需要用ProcessPoolExecutor因为图像处理是CPU密集型。

### Q2: LRU Cache 或 File Dedup (文件去重)

**LRU Cache**：

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1148690-1-1.html)

- 用法和Python `functools.lru_cache` 一模一样
- 需要实现 `generate_key(*args, **kwargs)` 生成hashable key
- Follow-up：crash后如何restore cache → 使用WAL（Write-Ahead Logging）方法
- 可以用OrderedDict或double linked list + dict实现

**File Dedup (文件去重)**：

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1144078-1-1.html)
> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1151849-1-1.html)

- 在文件系统中查找重复文件
- 使用哈希函数（MD5/SHA256）计算文件指纹
- 讨论CPU密集型 vs I/O密集型
- 大文件如何处理、文件很多如何处理、实时检测如何做
- Follow-up：设计持续监控重复文件的系统（使用数据库维护哈希到文件的映射）
- Follow-up：海量文件使用MapReduce扩展

> **注意**：Recruiter给的提示是 "You should be familiar with handling parallelism/concurrency"，但不一定是Web Crawler，也可能是File Dedup或LRU Cache。来源: [来源链接](https://www.1point3acres.com/bbs/thread-1151625-1-1.html)

### Q3: Stack Trace (调用栈解析)

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1089271-1-1.html)
> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1112538-1-1.html)

**题目描述**：给定一系列调用栈的sampling数据（包含时间戳和函数列表），要求将其转换为完整的执行追踪（Trace）。

```text
s2 = [
    Sample(0.0, ['a','b','a','c']),  # a -> b -> a -> c
    Sample(1.0, ['a','a','b','c']),
]
# 输出: (s,a)(s,b)(s,a)(s,c)(e,c)(e,a)(e,b)(s,a)(s,b)(s,c)
```



其中 "s" 是 start，"e" 是 end。

**解法**：使用栈数据结构对比相邻sampling，判断函数的进入（Start）和退出（End）。本身不难，只是需要处理input之后对于每一个Sample用stack存放并且对比决定输出。

**Follow-up**：只考虑连续出现N次的function。

**过关标准**：题和Follow-up全写完并且能各跑过1-2个test case。

### Q4: Mode/Median

具体题目细节较少，但有面经提到"注意读题"。

### Q5: LeetCode Style Question

Prompt是LeetCode style question。具体题目信息较少。

### Q6: Tokenizer

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1111070-1-1.html)

**题目描述**：实现一个tokenizer。

1. 找出给定代码中的bug
2. 修改后继续找出bug
3. 根据提供的implementation写正确的tokenizer

使用longest match策略：

```text
vocab = {"app": 1, "apple": 2, "UNK": -1}
tokenize("apple", vocab) -> [2]
tokenize("bbb", vocab) -> [-1, -1, -1]
```



**Optimize 1**：预计算max word length，减少搜索范围。

```python
def tokenize(text: str, vocab: dict) -> list:
    tokens = []
    i = 0
    max_len = max((len(w) for w in vocab if w != "UNK"), default=0)
    while i < len(text):
        matched = False
        for j in range(min(i + max_len, len(text)), i, -1):
            s = text[i:j]
            if s in vocab and s != "UNK":
                tokens.append(vocab[s])
                i = j
                matched = True
                break
        if not matched:
            tokens.append(vocab["UNK"])
            i += 1
    return tokens
```



**Optimize 2**：合并连续的UNK token。

```python
# tokenize("appbbbapp", vocab) -> [1, -1, 1]  (连续的-1合并为一个)
result = []
i = 0
while i < len(tokens):
    result.append(tokens[i])
    if tokens[i] == -1:
        while i + 1 < len(tokens) and tokens[i + 1] == -1:
            i += 1
    i += 1
return result
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/final_report_v2.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/final_report_v2.md)。作者整理资料；许可和第三方来源范围见阅读指南。
