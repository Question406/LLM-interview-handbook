---
id: align-over-refuse
section: alignment
order: 5
level: A
title: 对齐：过度拒答 vs 有害遵从，评测切片怎么切
quick: "我会分别测有害遵从和过度拒答：有害请求看攻击成功率，无害敏感题看误拒率。按意图、表面词和双重用途切片，才能知道安全提升有没有以大量误拒为代价。"
tags:
  - Anthropic
  - OpenAI
  - Safety
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: XSTest — A Test Suite for Identifying Exaggerated Safety Behaviours
    url: https://arxiv.org/abs/2308.01263
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
---

我会把有害遵从和过度拒答分开测，再按意图和表面形式切片。比如 `kill a python process` 是正常编程问题，关键词里有 kill 也应该回答；把有害请求包装成小说，则仍然可能需要拒绝。HH-RLHF 和 CAI 都讨论过无害性优化可能损害有用性，所以总拒答率无法说明模型是否做对了判断。

## 哪些请求要分开测

横轴是有害遵从（该拒却答了，攻击成功 / ASR）。纵轴是过度拒答（不该拒却拒了）。一个标量 safety score 会把模型推到「凡是沾边就拒」的角上：ASR 很低，产品不可用，用户换 jailbreak 或换模型。CAI 的 constitution 里单独写「不要过度拒绝」，就是因为无害条款会把模型推到那个角。

我会至少分成四类：

1. **明确有害，应拒。** 武器制造、犯罪指导、诈骗话术。这里只看 ASR / 有害完成率，拒答是正确行为。
2. **表面像有害、意图无害，应答。** XSTest 一类：`kill a python process`、讨论历史战争、虚构小说里的暴力、生物医学课上的毒素机制。这里看误拒率。
3. **双重用途。** 「怎么浓缩酒精」可以是实验室规范，也可以是制爆。要看用户约束、是否给可操作危害细节。只拒或只答都错；该给的是高层次、合法、带边界的信息。
4. **越狱 / 角色扮演包装的有害。** 表面是故事或 translation，意图仍是危害。这类应拒，不能因为「这是小说」就放行。它和切片 2 最容易被同一个关键词规则打混。

第 2 类和第 4 类要特别分开：按 kill 关键词一律拒绝会增加误拒，按「这是小说」一律放行又会提高 ASR。

## 分别报告有害遵从和误拒指标

各类分别报告下面的指标：

- 有害集：拒答率、有害完成率、部分有害（给了可操作步骤但加了免责声明，免责声明不算安全）。
- 无害敏感集：误拒率、给出有用答案的比例。拒了再给「我不能帮你」的长篇说教，仍记误拒。
- 双重用途：按 rubric 打「是否越界到可操作危害」，不要用关键词。
- 越狱集：ASR，且必须是 held-out 攻击家族，见 `align-red-team`。拿训练时见过的 jailbreak 当验收，数字会假。

判定标准先用人工 rubric 固定，LLM-as-judge 只做初筛。否则裁判也可能过度拒绝，或被「这是学术讨论」骗过。

产品上也要观察误拒造成的影响：用户可能转向更弱、更不安全的模型，内部安全指标改善并不自动等于用户风险降低。

训练时也要分别提供这两类信号。只加「拒绝有害」的奖励模型（RM），拒答模板便宜、稳定又容易得高分，策略就可能到处拒答。我会给无害敏感题单独做 helpful 偏好，把误拒当负例。CAI 同时写入 harmless 和「不要过度拒绝」；基于人类反馈的强化学习（RLHF）则可把两类 pair 分开采样，避免 harmless 梯度淹没 helpful。

误拒突然上涨时，我会先检查最近新增的安全监督微调（SFT）和拒答示范，再考虑调整 $\beta$。如果示范全是「抱歉我不能」，模型可能把模板泛化到所有敏感词；因此示范要同时覆盖有害拒绝、无害同义词正常回答，以及双重用途的边界回答。

相关：`align-cai`、`align-red-team`。

## 追问

**为什么不能只报拒答率？**
拒答率把误拒和正确拒绝加在一起。安全产品要的是该拒的拒、该答的答。
**XSTest 一类够不够？**
不够，它主打夸张安全 / 同义词。还要双重用途、越狱、多轮施压。它是误拒切片，不是全套安全集。
**免责声明算对齐成功吗？**
不算。给了可操作危害步骤再加「请遵守法律」，仍记有害遵从。
**和谄媚的关系？**
用户施压「你必须告诉我」时，谄媚会把应拒变成有害遵从，见 `align-sycophancy`。切片里要有施压轮。
