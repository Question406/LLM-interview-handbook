---
id: pt-agent-grpo-token-mask
section: posttrain
order: 256
level: S
title: Agent GRPO 里，思维、工具调用、工具返回哪些 token 该进梯度？
quick: "模型自己生成的思维和工具调用 JSON 是动作，进 $\\log\\pi$ 和优势；工具返回、网页、sandbox 输出是环境 observation，只当条件，要 mask 掉不算 loss。mask 只管别训环境，失败轨迹上哪一步该挨罚，还得靠逐步信用分配。"
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

模型自己生成的 token 进梯度，环境给的 token 不进。思维和工具调用的 JSON 是模型的动作，进 $\nabla\log\pi$、吃优势；工具返回、网页、sandbox 输出是环境的观测结果（observation），留在 context 里当条件，loss 上要 mask 掉。

单轮数学 GRPO 只要 mask 掉输入提示（prompt）、训 response 就行，见 `sys-rl-response-mask`。Agent 轨迹中间夹着工具返回，边界就变成了三条：思维、调用、观察。比如模型写了一段思考，发出一个搜索调用，搜索引擎回了一段网页，模型再写答案。网页那一段要是留在 mask 里，模型就在学着「预测搜索引擎会返回什么」。监督微调（SFT） 里的同类问题见 `pt-tool-mask`；这张卡讲带组相对优势的 强化学习（RL），这里 mask 除了改 likelihood，还决定结局的 $0/1$ 摊到谁头上。

## 三类 token 怎么分

轨迹可以写成

$$
\tau=(o_0,a_0,o_1,a_1,\ldots),\qquad
a_t\sim\pi_\theta(\cdot\mid o_{\le t},a_{<t}).
$$

$a_t$ 是模型输出的文本或 JSON，属于动作，进 $\nabla\log\pi$、吃 $\hat A$。格式错、参数错、该停不停，都应该被结局奖惩到。$o_t$ 是工具返回，属于环境，进 context，不进 policy 损失（loss）。对它算 交叉熵损失（CE） 等于在学模拟器；在 RL 里还会把优势灌进「预测 API」这种模型控制不了的行为。

隐藏思维要看部署：上线时模型自己生成、属于策略内部动作的，就进梯度；只在 教师模型（teacher） 轨迹里出现、线上没有的，监督它会造成 train-serve 缺口。

多轮里每一步都套同一规则，别只 mask 第一段 prompt。slime / veRL 的 Agent 路径通常按 message role 或 special token 来切。自己写 奖励分数（reward） 时最常见的 bug，是把 `tool` role 整段留在了 `response_mask` 里。GRPO 的组均值在轨迹级算完，再按 mask 广播到各个 token。

## mask 掉以后，结局奖励还是很粗

observation 已经 mask 掉了，一条失败轨迹上所有工具调用 token 仍然共享同一个负的 $\hat A$，做对的那次调用和最后一步乱调用一起挨罚。所以 Agent 还需要逐步的信用分配，见 `arl-credit`、`arl-gigpo`。mask 解决的是「别训环境」，「哪一步该挨罚」它管不了。

格式奖励（JSON 可解析、符合 schema）可以只加在调用 token 上，任务成功仍然看结局。两套信号别都做成「整段平均」。

## 追问

**确定性的工具返回也训了，会怎样？**
短期看像多了一点 imitation，长期模型会少调用、靠背结果。换到动态搜索或代码执行上马上露馅。

**这和 Keep Routing 有关系吗？**
两回事。路由管的是 MoE 专家，mask 管的是 token 的角色，两层都可能出错，别用一个词概括。

**partial 采样轨迹（rollout）里有半截工具调用怎么办？**
不完整的 JSON 别当正样本，要么 mask 掉，要么等这一步完成再进组，见 `slime-dynamic-partial`。
