---
id: align-length-bias
section: alignment
order: 15
level: A
title: 对齐：偏好学习里的长度偏见
quick: >-
  人标、RM、DPO、BoN、Arena、LLM-as-judge 都会把「更长」当成「更好」。损失若按 token 求和，长度差会进隐式奖励。
  评测要对齐长度或做长度协变量，否则 win-rate 是注水。
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

对齐岗问长度偏见，不是「回答写短一点」。InstructGPT / HH 的人标里，更完整、更有列表的回答更容易赢；RM 把这个统计写进 $r$；RL、DPO、BoN 再放大。AlpacaEval LC 后来直接把长度当协变量抠掉。我会按「偏见从哪进、训练怎么显形、评测怎么拆」答。不是某次现场逐字题。

## 偏见从哪进管道

标注。开放对话没有对错，标注员用「看起来全」当代理。长回答覆盖更多检查清单，短而准的反而像敷衍。安全数据里拒答套话也偏长。平局硬掰时，更长的那条更容易被留下。

奖励模型。BT 只看差，见 `align-reward-model`。若 $y_w$ 系统比 $y_l$ 长，$r$ 学会「token 多就加分」。校准指标可以很好，仍然在给长度打分。BoN 取 $\arg\max r$ 时，这个特征被搜到极限，见 `align-best-of-n`、`align-reward-hack`。

策略目标。DPO / IPO 的 $\Delta$ 是两条序列 log 比的差。实现若对 token 求和，更长序列的 $\log\pi$ 量级更大，长度差会进间隔；改成 token 平均等于偷偷重标定 $\beta$，见 `align-dpo`。RL 的回报若按序列给一个标量、没有长度惩罚，策略会注水到 RM 喜欢的区间。

评测。Arena 和 LLM-as-judge 同样偏长、偏 markdown，见 `align-arena`、`align-llm-judge`。你用这些当 gold，会把注水训回去。

## 训练里怎么显形，怎么压

监控不要只看 RM 和 win-rate。并列画：平均 response 长度、长度分位数、chosen/rejected 的长度差、单位长度的奖励。RL 之后长度和训练 RM 一起右移、人工抽检喊废话，就是长度 hack，不是「学得更认真」。

常用补丁，各有代价：

- **长度惩罚。** $r' = r - \lambda |y|$ 或按 token 平均再进 PPO。$\lambda$ 太大变成电报体，有用的步骤被砍。
- **配对时控长度。** 造 pair 时限制 $|y_w|-|y_l|$，或同一 prompt 下抽相近长度再标。信息变少，但 RM 少一条捷径。
- **归一 logp。** DPO 用平均 logp。要在报告里写死，否则别人的 $\beta=0.1$ 和你的不是同一个目标。
- **约束解码。** 推理设最大长度或目标长度带。治标，且会截断真正需要长推理的题。

过程可验证的任务（数学最终答案、单测）长度偏见弱一些，但格式套话仍会变长。开放 helpful 几乎一定会碰到。

白板画散点：横轴长度，纵轴 RM。SFT 是一团；RL / BoN 之后点堆到「又长又高分」的角。再叠 gold 或人工，角上 gold 低，就是偏见集群。

## 评测必须把长度拆开

报 win-rate 同时报平均长度和「长度匹配后的 win-rate」。做法：在相近长度的 pair 上只比内容；或像 AlpacaEval LC 那样把长度当回归协变量。门禁用固定长度预算下的任务成功率，不要只用开放偏好。

切片：短指令（一句话事实）、中等、必须长（代码、多步推理）分开。全局「变短了所以对齐成功」会误杀推理模型。安全切片上看的是该拒的拒、不该拒的别注水道歉，见 `align-over-refuse`。

发布闸门我会写成：长度匹配偏好 + 任务成功率 + 安全 + 延迟/成本。缺长度匹配，偏好分不可信。

## 追问

- **平均 logp 能根治吗？** 能减弱求和带来的尺度差，不能消除人标本身爱长。数据和评测还要控。
- **用户就喜欢长怎么办？** 当产品选择公开说，不要藏进 RM。评测仍要拆「信息增量」和「字数」。
- **和 Arena 分数矛盾？** 先查长度和排版。Arena 偏长是已知偏差，见 `align-arena`。
- **推理模型必须长链？** 那是任务需要，用可验证正确率门禁，不要用开放 RM 鼓励无限链。
