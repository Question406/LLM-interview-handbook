---
id: drustz-b08b9ee14bcf237e4b
section: mlsd
order: 204
level: A
title: >-
  21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 7. Step 6：curate（这一步你的 math
  经验直接迁移）
quick: >-
  作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 7. Step 6：curate（这一步你的
  math 经验直接迁移）
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
## 7. Step 6：curate（这一步你的 math 经验直接迁移）

```bash
python curate.py
```



### 去重：单位是「改动的语义」，不是文本

同一个仓库里「给 N 个函数各加一个 None 检查」的 PR 可能有几十个 ——
patch 文本高度相似，**对模型是同一道题**。

做法：normalization patch（只保留 +/- 行、去注释去空白）→ shingle → MinHash → LSH 分桶。
和你在 math 上做近重复是同一套，只是**normalization函数不同**。

> **我在这里踩了一个值得记的坑**：合成实例最初存的是**整份修改后的源码**，
> 而挖来的实例存的是 **unified diff**。`normalize_patch` 只保留 `+/-` 开头的行，
> 于是合成实例normalization后**全是空串** → MinHash 签名全相同 → 去重把它们**全判成重复**，
> 而且一声不吭。
> **两个数据源 schema 不一致，会让下游过滤静默失效。**
> 修法是加一行护栏：

```python
def assert_is_diff(patch, who=""):
    if not normalize_patch(patch).strip():
        raise ValueError(f"归一化后为空，{who} 传进来的多半不是 unified diff")
```



### 去污染：三层，缺一不可

```text
① 整仓排除    SWE-bench 的 12 个测试仓库，**整个仓库**都不能用
              （不只是那 2,294 条实例 —— 同仓库其他 PR 会泄漏代码库结构和风格）
② 精确匹配    instance_id / commit SHA
③ 近重复      patch 与 benchmark patch 的 MinHash 相似度
```



**只做 ①② 不够**：同一个 bug 可能出现在 fork 里、在别的仓库 vendored 的副本里。

**还要加时间维度**：训练数据的 commit 时间必须早于评测集的时间窗口。
（这也是 SWE-bench-Live / SWE-rebench 持续刷新的动机 —— **benchmark 会腐烂**。）

### 难度：别用 patch 行数，用 pass@k

```text
def empirical_difficulty(inst, rollout_results):
    p = sum(rollout_results) / len(rollout_results)
    return {"pass_rate": p, "keep_for_rl": 0 < p < 1, ...}
```



⭐ **这一条和你在 math/STEM 上做的自适应难度筛选是同一件事**：

```text
pass@k = 0  →  无梯度信号，GRPO 组内优势全为 0，**这一组 rollout 白跑**
pass@k = 1  →  同样无信号
0 < p < 1   →  有区分度，这才是该留的
```



`static_difficulty`（patch 行数 + 文件数）只能当**初筛和分桶**用，
**不能当结论** —— 行数和难度的相关性没有你以为的高。

---

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
