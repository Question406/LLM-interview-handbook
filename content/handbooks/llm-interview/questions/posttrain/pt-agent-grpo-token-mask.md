---
id: pt-agent-grpo-token-mask
section: posttrain
order: 256
level: S
title: Agent GRPO 里，思维、工具调用、工具返回哪些 token 该进梯度？
quick: >-
  和 SFT 同一条边界：policy 自己生成的 action（思维、tool call JSON）进 $\log\pi$ 和优势；环境 observation（工具返回、网页、sandbox
  输出）只当条件，不算 loss。终局奖励仍会广播到所有未 mask 的 token，所以 mask 错了是在把环境当策略训，或把关键调用洗掉。
tags:
  - Agent RL
  - GRPO
  - Loss Mask
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: veRL Agent documentation
    url: https://verl.readthedocs.io/
    type: secondary
---

单轮数学 GRPO 只 mask prompt、训 response，见 `sys-rl-response-mask`。Agent 轨迹里夹着工具返回，边界变成三条：思维、调用、观察。SFT 版见 `pt-tool-mask`。本题是带组相对优势的 RL：mask 不仅改 likelihood，还改「结局 $0/1$ 摊到谁头上」。

## 三条带

$$
\tau=(o_0,a_0,o_1,a_1,\ldots),\qquad
a_t\sim\pi_\theta(\cdot\mid o_{\le t},a_{<t}).
$$

- **$a_t$ 文本 / JSON：** 模型的动作。进 $\nabla\log\pi$，吃 $\hat A$。格式错、参数错、该停不停，都该被结局奖惩到。
- **$o_t$ 工具返回：** 环境。进 context，不进 policy loss。对它做 CE 等于在学模拟器，RL 里还会让优势灌进「预测 API」这种不可控行为。
- **隐藏思维：** 若部署时模型自己生成、也算策略内部动作，就进梯度。若只在 teacher 轨迹里出现、线上没有，监督它会造成 train-serve 缺口。

多轮里每步都要套同一规则，不要只 mask 第一段 prompt。slime / veRL 的 Agent 路径通常按 message role 或 special token 切；自己写 reward 时最常见的 bug 是把 `tool` role 整段留在 `response_mask` 里。

## 结局奖励仍然很粗

即使 observation 已经 mask 掉，一条失败轨迹上所有 tool call token 仍共享同一个负 $\hat A$。关键的对调用和最后一步胡调用一起挨打。这是 Agent 还要逐步信用的原因，见 `arl-credit`、`arl-gigpo`。Mask 只解决「别训环境」，不解决「哪一步该挨打」。

格式奖励（JSON 可解析、schema 合法）可以只加在 call token 上；任务成功仍用结局。两套信号不要都变成「整段平均」。

现场口令：观察当条件，调用当动作，思维看部署接不接口。GRPO 的组均值在轨迹级算完，再按 mask 广播。

## 追问

- **确定性工具返回训了会怎样？** 短期像多了一点 imitation，长期模型会少调用、靠背结果。动态搜索 / 代码执行上立刻露馅。
- **和 Keep Routing？** 路由是 MoE 专家；mask 是 token 角色。两层都可以错，别用一个词概括。
- **partial rollout 半截工具调用？** 不完整 JSON 不要当正样本。mask 掉或等这步完成再进组，见 `slime-dynamic-partial`。
