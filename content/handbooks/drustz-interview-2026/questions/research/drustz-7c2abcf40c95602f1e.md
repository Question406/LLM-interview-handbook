---
id: drustz-7c2abcf40c95602f1e
section: research
order: 163
level: A
title: PracHub 2026-04-03 MLE tech screen：Debug MiniGPT + 手推 matmul 反向 + KV cache 实现
quick: >-
  supplemental-research-note · PracHub 2026-04-03 MLE tech screen：Debug MiniGPT
  + 手推 matmul 反向 + KV cache 实现
companies:
  - openai
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://prachub.com/interview-questions/debug-minigpt-and-backpropagate-matmul
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

两 part，共约 1 小时（MLE technical screen，上报 2026-04-03）。Part A：decoder-only transformer 代码语法正确但autoregressivedecoding输出错误文本，要求 debug 并加 KV cache。考点：各阶段 tensor shape、causal mask 机制、attention 计算、位置编码、loss 对齐（next-token shift）、train/eval 模式、greedy/sampling。期望交付：找出并修复 bug（mask 错误/softmax 轴/√ $d_h$  缩放/位置编码/target shift/模式类 bug）、prefill 与 decode 干净分离、O(T) decode vs O( $T^{2}$ ) 重算、内存讨论（MQA/GQA/量化）。Part B：自定义 C=A@B 的 forward+backward：从  $C_{ij}$ = $Σ_r$   $A_{ir}$   $B_{rj}$  逐 index 推导 dA=dC@Bᵀ、dB=Aᵀ@dC，支持 batch/broadcast，用 torch.autograd.Function + save_for_backward，gradcheck 验证。追加 follow-up：Hillis-Steele prefix scan 的 O(n log n) work / O(log n) depth，及 scan vs reduction 何时划算；Blelloch scan 对比。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://prachub.com/interview-questions/debug-minigpt-and-backpropagate-matmul)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
