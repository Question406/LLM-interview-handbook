---
id: drustz-b5c4b903ba7effd04c
section: openai
order: 32
level: A
title: Streaming Entropy
quick: locally-saved-research-summary · Streaming Entropy
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-research-summary
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
      https://www.1point3acres.com/interview/problems/company/openai/streaming-entropy
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## PracHub 2026-04-24 MLE onsite：数值稳定的流式 entropy（logits 分块）+ 向量化 1-NN 及其神经网络等价形式

Part 1：给 logits z，p=softmax(z)，计算 H(p)=−Σ  $p_{i}$  log  $p_{i}$ ；要求 (a) log-sum-exp 防溢出；(b) 流式：logits 分块到达、全量放不进内存，单 pass、O(1) 状态。关键恒等式：H = log Z −  $E_p$ [z]，Z 为配分函数；流式维护 running max M 和两个累加器  $Σe^{z_{i}−M}$ 、 $Σz_{i}$  $e^{z_{i}−M}$ ，M 更新时 rescale（online softmax 同款技巧）。Part 2： $X_{train}$ (n,d),  $y_{train}$ ,  $X_{query}$ (m,d)：(a) 全向量化 L2 1-NN（禁 Python 循环）：‖q− $x_{i}$ ‖²=‖q‖²+‖ $x_{i}$ ‖²−2q· $x_{i}$ ，一次 matmul + broadcast，argmax 时 ‖q‖² 项可丢；(b) 把 L2 1-NN 表示成 linear layer + softmax（W=2X_train, b=−‖ $x_{i}$ ‖²，argmax 恢复最近邻）；(c) L1 变体为什么仿射层不够——需要 ReLU 网络（分段线性）。Follow-ups：为何 argmax 下 softmax 单调性重要、O(1) 状态维护 logits 的 running variance、L1 网络隐层数随 n,d 如何扩展、训练集固定时的预计算。另一独立上报：'Implement 1NN with NumPy'（2026-05-19，MLE screen）。这与 2025 面经中的 KL divergence/cross-entropy 数学题一脉相承，确认 2026 年 ML 轮仍考数值稳定+向量化基本功。

### 解题与准备提示

来源含完整解法（见 detail）。

---

## Streaming Entropy（流式熵，online + block-wise 更新）——RS/RE tech screen 60min

官方题库：streaming-entropy，coding，medium，4 帖，60min tech screen，roles RS/RE，tags: numerical-stability/streaming，reported_from 2026-04-01（4 月上新），last_asked 2026-06-22。OJ 镜像标题：'Streaming Entropy with Online and Block-wise Updates'。与 thread-1173645（RS 四轮）中 'entropy calculation task' 呼应——熵计算是 research 轨 AI-coding 题池成员。

### 解题与准备提示

（我的推断）维护词频 dict + 两个累积量 N 与 S=Σc·log c，则 H=log N − S/N；单元素更新 c→c+1 时 S += (c+1)log(c+1)−c·log c，O(1)；block-wise 合并两个直方图同理可加；讨论 log-sum 数值稳定与大流量下的近似（count-min sketch）。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/streaming-entropy)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
