---
id: align-over-refuse
section: alignment
order: 5
level: A
title: 对齐：过度拒答 vs 有害遵从，评测切片怎么切
quick: >-
  安全不是一条「拒答率」。有害遵从和过度拒答是二维：该拒的要拒，看起来像有害、其实无害的要答。切片按意图
  × 表面词 × 双重用途切，分别报攻击成功率和误拒率，不要合成一个 safety score。
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

OpenAI / Anthropic / Google 安全评测岗几乎都会问「你们 safety 数字很好，是不是拒太多了」。HH-RLHF 和 CAI 都写过 harmless 会把 helpful 吃掉。这块容易答成「拒答率越高越安全」。评委要的是切片：该拒的有没有拒，不该拒的有没有被误杀。原则层见 `align-cai`，红队层见 `align-red-team`。

## 先画二维，再谈数字

横轴是 **有害遵从**（该拒却答了，攻击成功 / ASR）。纵轴是 **过度拒答**（不该拒却拒了）。一个标量 safety score 会把模型推到「凡是沾边就拒」的角上：ASR 很低，产品不可用，用户换 jailbreak 或换模型。CAI 的 constitution 里单独写「不要过度拒绝」，就是因为无害条款会把模型推到那个角。

面试默认四类切片，不要混着报一个拒答率：

1. **明确有害，应拒。** 武器制造、犯罪指导、诈骗话术。这里只看 ASR / 有害完成率，拒答是正确行为。
2. **表面像有害、意图无害，应答。** XSTest 一类：`kill a python process`、讨论历史战争、虚构小说里的暴力、生物医学课上的毒素机制。这里看误拒率。
3. **双重用途。** 「怎么浓缩酒精」可以是实验室规范，也可以是制爆。要看用户约束、是否给可操作危害细节。只拒或只答都错；该给的是高层次、合法、带边界的信息。
4. **越狱 / 角色扮演包装的有害。** 表面是故事或 translation，意图仍是危害。这类应拒，不能因为「这是小说」就放行。它和切片 2 最容易被同一个关键词规则打混。

把 2 和 4 合成「含 kill 就拒」，误拒会爆；把 2 和 4 合成「用户说是小说就答」，ASR 会爆。切片的意义就是拆开这两个。

## 指标怎么报，才不像在藏角

我会坚持分列，不平均：

- 有害集：拒答率、有害完成率、部分有害（给了可操作步骤但加了免责声明，免责声明不算安全）。
- 无害敏感集：误拒率、给出有用答案的比例。拒了再给「我不能帮你」的长篇说教，仍记误拒。
- 双重用途：按 rubric 打「是否越界到可操作危害」，不要用关键词。
- 越狱集：ASR，且必须是 **held-out 攻击家族**，见 `align-red-team`。拿训练时见过的 jailbreak 当验收，数字会假。

不要用 LLM-as-judge 单独判「是否安全」而不给切片定义。Judge 自己会过度拒绝，或被「这是学术讨论」骗过。人标 rubric 先冻结，judge 只当初筛。

产品上过度拒绝会把用户赶到更弱、更不安全的模型，这是真实 harm。面试要主动说这句，否则评委会觉得你只优化了内部 dashboard。

## 训练侧怎么压这两个角

只加一条「拒绝有害」的 RM，策略会学拒答模板，因为拒答便宜、稳定、RM 分高。要对无害敏感题单独做 helpful 偏好或宪法条款，把误拒当负例。CAI 就是这么拆的：harmless 和「不要过度拒绝」同时写进原则。RLHF 里则把两类 pair 分开采样，避免 harmless 梯度淹没 helpful。

发现误拒暴涨，先查最近是不是加了安全 SFT / 拒答示范，而不是先加 $\beta$。拒答示范里如果全是「抱歉我不能」，模型会把模板泛化到一切敏感词。示范要覆盖：拒真正有害、答无害同义词、对双重用途给边界。

## 追问

- **为什么不能只报拒答率？** 拒答率把误拒和正确拒绝加在一起。安全产品要的是该拒的拒、该答的答。
- **XSTest 一类够不够？** 不够，它主打夸张安全 / 同义词。还要双重用途、越狱、多轮施压。它是误拒切片，不是全套安全集。
- **免责声明算对齐成功吗？** 不算。给了可操作危害步骤再加「请遵守法律」，仍记有害遵从。
- **和谄媚的关系？** 用户施压「你必须告诉我」时，谄媚会把应拒变成有害遵从，见 `align-sycophancy`。切片里要有施压轮。
