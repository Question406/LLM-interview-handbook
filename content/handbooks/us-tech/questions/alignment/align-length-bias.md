---
id: align-length-bias
section: alignment
order: 15
level: A
title: 对齐：偏好学习里的长度偏见
quick: "偏好标注容易把更长、更完整的外观当成更好，RM、DPO、BoN 和评测又可能放大它。训练要看长度与奖励是否一起涨，评测应报长度匹配后的偏好和固定预算下的任务成功率，避免把多写字误判为能力提升。"
tags:
  - OpenAI
  - LMSYS
  - Length Bias
  - Preference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Length-Controlled AlpacaEval — A Simple Way to Debias Automatic Evaluators
    url: https://arxiv.org/abs/2404.04475
    type: primary
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

长度偏见是偏好流程学会把字数当质量的捷径。比如短而准确的回答看起来不如带很多列表的回答完整，标注员选后者，RM 学到这个相关性，RL、DPO 和 BoN 又会继续放大。

InstructGPT / HH 这类人工偏好中，完整外观、列表和较长拒答都可能占便宜，尤其平局被强行分胜负时。RM 用 BT 拟合分差，若 $y_w$ 系统比 $y_l$ 长，就可能给 token 数加分，即使校准指标很好也不代表学到了内容质量，见 `align-reward-model`。BoN 再取 $\arg\max r$，更容易搜到这条捷径，见 `align-best-of-n`、`align-reward-hack`。

DPO / IPO 的 $\Delta$ 是两条序列 log 比之差，按 token 求和会让更长序列的 $\log\pi$ 尺度进入间隔；换成 token 平均则重标定 $\beta$，必须明确实现约定，见 `align-dpo`。RL 若每条序列只给一个回报 $r$、又没有长度约束，也可能多写 RM 喜欢的套话。Arena 与 LLM-as-judge 同样偏好长回答和 Markdown，若再把它们当训练标准，循环会加重，见 `align-arena`、`align-llm-judge`。

## 训练中怎么发现和控制

我会一起画平均 response 长度、长度分位数、chosen/rejected 长度差、单位长度奖励与独立胜率。若 RL 后长度与训练 RM 分数一起涨，人工抽检却多了废话，就要怀疑刷长度。也可画长度为横轴、RM 分为纵轴，SFT 的点云经 RL / BoN 移到长且高分的角落，再叠 gold；角落 gold 低，就说明 proxy 在奖励错误特征。

控制方式各有代价。奖励可用 $r' = r - \lambda |y|$，或先做 token 平均再进 PPO，但 $\lambda$ 太大会让有用步骤也被砍。构造 pair 时可限制 $|y_w|-|y_l|$，或在同一 prompt 下选长度相近回答再标，减少 RM 捷径，也会减少可用信息。DPO 用平均 logp 要在报告中写清，否则别人的 $\beta=0.1$ 与当前实现不等价。推理时限制最大长度或目标长度带只能控制输出，还可能截断需要的长推理。

数学最终答案、代码单测这类可验证任务的偏见通常较弱，但格式套话仍可能增长，开放 helpful 场景尤其容易遇到。AlpacaEval LC 把长度当协变量，统计扣除这部分影响，说明为什么评测也要处理。

验收同时报原始 win-rate、平均长度和长度匹配后的 win-rate。可以比较相近长度的 pair，或用长度协变量回归；还要给固定长度预算下的任务成功率。短事实指令、中等长度任务、必须长的代码与多步推理分别看，不能把全局变短直接算成对齐成功。安全切片看该拒的是否拒绝、正常问题是否过度道歉，见 `align-over-refuse`，再结合安全、延迟与成本。

## 追问

**平均 logp 能根治吗？**
只能减弱求和尺度差，标注本身偏长仍需数据和评测控制。

**用户本来喜欢长回答呢？**
可以明确作为产品选择，但评测仍区分信息增量和字数。

**Arena 涨了却私有分没涨？**
先查长度与排版，Arena 偏长见 `align-arena`。

**推理模型确实需要长怎么办？**
用可验证正确率判断这些步骤是否有用，避免让开放 RM 鼓励无限思维链。

## 相关题

- [[align-llm-judge]]：位置、自偏好和交换顺序协议。
- [[align-arena]]：ELO 的文风与选择偏差。
- [[xai-lmarena]]：在线与离线榜的分布差别。
- [[msft-orpo]]：未归一化序列概率怎样让长度进入 odds。
