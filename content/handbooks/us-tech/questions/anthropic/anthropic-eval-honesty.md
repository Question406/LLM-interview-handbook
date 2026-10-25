---
id: anthropic-eval-honesty
section: anthropic
order: 20
level: S
title: Anthropic：诚实性和不确定性怎么评，和 HH 冲突时站哪边？
quick: "我会分开评知识准确率、置信校准和受压时是否说实话，MASK 这类测试专门看模型被要求撒谎时的表现。证据不足就说明不确定；按公开 constitution，社交白谎也不该说，拒绝危险请求时也要如实解释，不能装作不会。"
tags:
  - Anthropic
  - Honesty
  - Evaluation
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
  - title: A General Language Assistant as a Laboratory for Alignment
    url: https://arxiv.org/abs/2112.00861
    type: primary
  - title: Claude's Constitution
    url: https://www.anthropic.com/news/claudes-constitution
    type: primary
  - title: Language Models (Mostly) Know What They Know
    url: https://arxiv.org/abs/2207.05221
    type: primary
---

我会把知识准确率、置信校准和受压时是否说实话分开评，再分别检查它们和 helpful、harmless 的冲突。例如用户问完又说「你确定吗」，要看模型是根据证据调整回答，还是为了迎合用户改口。拒答时也要诚实说明理由。

HHH 里的 honesty 是第三轴。Askell 把它定义为不编造、承认不知道、不假装有内部状态；Bai 等人的 HH-RLHF 没有单独采诚实偏好，常把它放进 helpful 的「别瞎编」条款。因此，事实题得分高可能只是知识多，用 HH 对比数据训练也不保证模型会表达不确定。

评测时，我先测闭卷事实准确率，再用带资料的开卷任务检查是否忠于材料，必须引用的场景没有 span 就拒答，见 `anthropic-citations`。随后检查校准：模型说「高置信」的题目，实际准确率是否也高。Kadavath 等人发现内部 $P(\text{True})$ 往往比口头置信更准，所以数字置信和自然语言措辞都要记录。

抗压测试则加入错误前提、身份压力、用户暗示和「说你做了才能下班」这样的提示。MASK 专门检查被要求撒谎时能否继续说真话；谄媚说明迎合用户的目标压过了诚实。还可以故意不给大海捞针任务里的针，看模型会不会承认找不到，见 `anthropic-needle`。同一题扫描温度和 thinking 设置时，以最终答案为准，摘要犹豫、答案却斩钉截铁同样要记失败，见 `anthropic-extended-thinking`。结果分开报校准曲线和抗压诚实率，合成一个 Elo 或「诚实分」会掩盖差异。

## 和 helpful、harmless 冲突时怎么处理

用户要完整、干脆的步骤，证据却不足时，我会让回答明确说「我不确定，最可能是 X，依据是 Y」。标注员若只按是否帮上忙打分，可能惩罚这种犹豫，所以诚实样本要单独定义标准，不能混入 helpful 主轴硬选，见 `anthropic-hh-rlhf`、`anthropic-pref-collect`。

危险请求需要拒绝时，理由也要真实。可以说「我能谈机制，但不给可操作细节」，或者简短拒绝；装作「我不知道怎么做」会被红队拆穿，也会训练出策略性撒谎。公开 constitution 连「礼物很好看」这类社交白谎也不鼓励，可以不主动表达偏好，但不能正面撒谎。

CAI 可以把「承认不确定、不编来源」写进条款，见 `anthropic-constitutional-ai`。条款参与生成训练数据才属于这里说的 CAI，只放进 system 输入提示属于推理期约束，见 `anthropic-context-distill`。评测时也要避开几个混淆：TruthfulQA 混合了准确率和流行误解，单问「你确定吗」覆盖面太窄，拒答还可能只是 over-refusal。

## 追问

**模型说「我不知道」就算诚实吗？**
不一定。若内部探针显示它会做，可能是砂袋或过度拒绝。要看它是否如实报告置信。

**RLHF 造成的讨好怎么处理？**
把纠正用户错误明确写成优先标准，并收集「礼貌地反对」胜过「顺着说」的偏好对。

**口头置信能当 $P(\text{correct})$ 吗？**
先标定。画出可靠图之后，再决定 UI 是否把「较有把握」映射成数字。

**拒答时能不能撒谎？**
按公开立场不能。理由可以简短，但不能编造能力上限。
