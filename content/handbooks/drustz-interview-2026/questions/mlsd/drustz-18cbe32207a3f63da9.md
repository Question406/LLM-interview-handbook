---
id: drustz-18cbe32207a3f63da9
section: mlsd
order: 200
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 3. Step 2：从 PR 挖候选（附完整代码）
quick: 作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 3. Step 2：从 PR 挖候选（附完整代码）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md
    type: primary
---
## 3. Step 2：从 PR 挖候选（附完整代码）

```bash
python mine.py
```



### 概念对齐：PR 的本质

> **一个 PR = 一个 base commit + 一个 diff。**
> 所以 pipeline 完全可以跑在本地 git 历史上，不需要 GitHub API。
> 配套代码就是这么做的 —— 造一个带真实 git 历史的玩具仓库，整条链路真跑。

### 关键动作：把 diff 劈成两半

```text
solution_patch = diff 里的 **非测试文件** 部分   # gold answer，训练时不给模型
test_patch     = diff 里的 **测试文件** 部分     # 验证器，评测时才打上
```



**为什么必须劈开**：如果 gold patch 里混进了测试文件，模型在训练时
**能直接看到断言** —— 这是 SWE 数据里最经典的答案泄漏。
（配套测试 `test_solution_patch_never_touches_test_files` 就是守这一条的。）

### ⚠️ 「什么是测试文件」这个小函数，是正确性的隐藏来源

SWE-rebench V2 论文用的是无锚定子串匹配：

```python
NAIVE_TEST_RE = re.compile(r"(?i)(test(?:ing|s)?|e2e)")  # 论文里的
```



它会把 `src/contest.py`、`build/latest/x.py`、`app/protests/views.py`
全部判成测试文件。后果不是「多几条噪声」，而是
**这些文件的改动被归进 test_patch，solution_patch 变空，整个实例被静默丢弃**。

加路径段边界就好了：

```python
TEST_RE = re.compile(
    r"(^|/)(tests?|testing|e2e)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$", re.I
)
```



### 便宜的过滤放在贵的验证之前

执行验证一次要几分钟到几十分钟，而下面这些是微秒级的。
**真实 pipeline 里这一步砍掉 80%+ 的候选**：

```python
if not code_files:
    reject("只改了测试或文档")
if not test_files:
    reject("没有测试改动 → 无法自动验证")
if len(code_files) > 20:
    reject("改动面过大，多半是重构/版本升级")
if patch_lines > 400:
    reject("patch 过长")
```



---

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
