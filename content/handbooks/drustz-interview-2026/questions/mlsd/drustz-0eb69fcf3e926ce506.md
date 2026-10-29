---
id: drustz-0eb69fcf3e926ce506
section: mlsd
order: 202
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 5. Step 4：执行验证（F2P / P2P）—— 核心中的核心
quick: >-
  作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 5. Step 4：执行验证（F2P /
  P2P）—— 核心中的核心
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
## 5. Step 4：执行验证（F2P / P2P）—— 核心中的核心

```bash
python mine.py # 会真的跑 pytest，看得到每一步
```



### 三步验证，缺一不可

```text
① 在 parent commit 上跑全套测试   → 必须全过    （证明环境是好的）
② 打上 test_patch 再跑            → 新测试必须 FAIL（证明 bug 真存在）
③ 再打上 solution_patch 跑        → 必须全过    （证明这个 fix 真管用）

F2P = ②失败 且 ③通过  ← 奖励信号
P2P = ②通过 且 ③通过  ← 防回归护栏
```



**这三步是 SWE-bench 的原始定义，后续所有工作都沿用。**
配套代码 `mine.validate()` 一比一实现了它。跑出来长这样：

```text
挖到 8 个 commit（不含 initial）
  便宜过滤后剩 5 个进入执行验证
  ✅ 0f2d65e fix: mean() crashes with ZeroDivisionError    F2P=1 P2P=1
  ✅ 4eaae11 fix: median() wrong for even-length input     F2P=1 P2P=2
  ✅ 8e69ade fix: slugify keeps punctuation in the slug    F2P=1 P2P=3
  ✅ f101760 fix: truncate() should append an ellipsis     F2P=1 P2P=4
  ✅ a223d01 fix: clamp silently returns garbage           F2P=1 P2P=5
  ❌ 1331dd3 docs: add install section        只改了测试或文档
  ❌ 8af8f41 test: add idempotence check      只改了测试或文档
  ❌ 63ff97d chore: clarify mean() docstring  没有测试改动 → 无法自动验证

最终 5 个可用实例（产出率 62%）
```



### ⭐ 为什么 P2P 不能省

**只用 F2P 当 reward，模型可以把不相关的代码删光**，只要新测试过就行。
这是 SWE 里最直接的 reward hacking 路径。P2P 是「别把别的弄坏」的约束。

对应到你熟悉的 math 场景：F2P 是「答案对不对」，
P2P 是「你没有为了答对而把题目改了」。

### 两个实践细节

**跑全量测试还是只跑相关的？**
> SWE-rebench V2：**始终跑全套**，不做子集选择 ——
> 覆盖更全，而且能发现意料之外的副作用。代价是慢。

**flaky 怎么办？**
> SWE-rebench V2：**每个候选跑 3 次**，只保留三次结构化结果完全一致的实例。
> 这一条很贵但很必要 —— flaky 测试进了训练集，就是持续注入的 reward 噪声。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
