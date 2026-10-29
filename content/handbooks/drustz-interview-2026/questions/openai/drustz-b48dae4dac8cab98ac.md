---
id: drustz-b48dae4dac8cab98ac
section: openai
order: 92
level: A
title: Numerically Stable Entropy from Logits (Batch and Streaming)
quick: >-
  original-structured-preparation-guide · Numerically Stable Entropy from Logits
  (Batch and Streaming)
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
      https://www.1point3acres.com/interview/problems/5331598d-bb6b-4e87-b2fc-db211ccf2ba2
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 从 Logits 稳定计算熵：整批与流式

> 证据边界：题面来自当前 UUID 可公开读取的 description；公式推导和测试建议为原创整理，不是会员答案。

## 完整题面

给一维 logits `z1...zk`，`p_i=exp(z_i)/Σexp(z_j)`，计算 `H=-Σp_i log p_i`。先实现 `entropy_from_logits(logits)`，在值达到 `±10^4` 时也不得溢出；再实现 `StreamingEntropy.update(z)` 与 `finalize()`，单遍处理且不保存全部 logits，额外空间 `O(1)`。例：`[0,0] -> ln 2`，三个 0 得 `ln 3`，`[10000,0]` 约为 0。

## 稳定公式与更新

利用 `H=log Z-E_p[z]`。整批取 `m=max(z)`、`s=Σexp(z-m)`、`t=Σz exp(z-m)`，结果为 `m+log s-t/s`。流式状态也是 `(m,s,t)`；读到 `z` 时令 `m'=max(m,z)`，把旧量乘 `exp(m-m')`，新项权重为 `exp(z-m')`，再更新 `s,t,m`。首次输入可初始化为 `(z,1,z)`。这一步重缩放正是 running maximum 改变时仍稳定的关键。

整批与流式均为 `O(k)` 时间；整批中间数组可能 `O(k)`，流式额外空间 `O(1)`。边界测试空输入应报错、单元素熵 0、全相同大正/负值、最大值跨 chunk 改变、逐元素与随机分块一致、float32/64 误差、NaN/正无穷的输入政策。不要先算普通 softmax 再 `log(p)`，下溢到 0 会制造 `log(0)`。

若输入按 block 到达，可先为每块计算 `(m_b,s_b,t_b)`，再与全局状态合并：取共同最大值 `m'`，分别用 `exp(m_old-m')` 和 `exp(m_b-m')` 重缩放两组三元组。这个 merge 近似满足结合律，可并行树归约，也能让类同时支持 `update` 与 `update_block`。`finalize` 不应改变状态，重复调用应得到同值；更新发生后再次 finalize 则反映新分布。

数值验证除对照 `torch.distributions.Categorical(logits=...).entropy()` 外，还可利用性质 `H(z+c)=H(z)`、`0≤H≤log k`。有限精度下结果可能出现极小负数，可在确认误差范围后夹到 0，但不能用 clamp 掩盖明显公式错误。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/5331598d-bb6b-4e87-b2fc-db211ccf2ba2)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
