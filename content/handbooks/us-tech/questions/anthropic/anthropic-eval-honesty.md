---
id: anthropic-eval-honesty
section: anthropic
order: 20
level: S
title: Anthropic：诚实性和不确定性怎么评，和 HH 冲突时站哪边？
quick: >-
  诚实不是知识面：MASK 把「会不会故意说假话」从准确率里拆开。口头置信要和经验准确率对齐。用户施压、错误前提、讨好，是必测轴。和
  helpful 冲突时，constitution 要求不说白谎；和 harmless 冲突时，拒答也要诚实，不要装不知道。
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

HHH 里 honesty 是第三轴，但 HH-RLHF 没有单独采诚实偏好，常并进 helpful 的「别瞎编」。对齐岗会问：那你怎么评？和 helpful / harmless 打架时怎么办？我会先拆开「答对了」和「没撒谎」，再谈冲突。公开 constitution 把诚实抬得很高：连社交白谎都不该说；口头置信要校准。这不是某一场隐藏真题。

## 先把诚实从准确率里拆出来

事实问答高分可以来自知识面，不是来自「明知会错还是说了实话」。Askell 的 HHH 把诚实定义成：不编造、承认不知道、不装成有内部状态。Bai 等人的 HH 论文把诚实并进 helpful 条款，所以只用 HH 对比数据训出来的模型，不一定学会「我不确定」。

评测至少三条，不要合成一个 Elo：

1. **知识准确率。** 闭卷事实、带资料的忠实度。这是能力。
2. **校准。** 口头「高置信」的题目，经验准确率是否真高。Kadavath 等人表明模型内部 $P(\text{True})$ 往往比嘴上更准——评测要同时要数字置信和自然语言措辞。
3. **抗压诚实。** 用户说「你确定吗」、给出错误前提、暗示想听的答案。MASK 这类基准专门打「被要求撒谎时还说不说真话」。Sycophancy 是 helpful 吃掉诚实。

错法：用 TruthfulQA 当诚实性（它混了准确率和流行误解）；只问「你确定吗」当唯一探针；把拒答全算诚实胜利（可能是 over-refusal）。

## 和 HH 的冲突长什么样

**Helpful vs honest。** 用户要完整、干脆的步骤。诚实要求：证据不够就说不够，不要用肯定句填洞。产品上「我不确定，最可能是 X，依据是 Y」往往比装懂更有用，但标注员若按「是否帮到忙」打分，会惩罚犹豫。所以诚实样本不能混进 helpful 主轴硬选，见 `anthropic-hh-rlhf` 和 `anthropic-pref-collect`。

**Harmless vs honest。** 危险请求上，有人希望模型装傻（「我不知道怎么做」）。Constitution 更接近：承认能力边界，但清楚拒绝，不编造「我真不会」。装不知道会被红队拆穿，也训练出策略性撒谎。无害优先时，正确形状是「我能谈机制，但不给可操作细节」或直接拒，而不是假外行。

**白谎。** 公开 constitution 写明：Claude 不该说「礼物很好看」这类社交谎。面试别答成「对用户好就可以骗」。可以不主动摊偏好，但不能正面撒谎。

CAI 的条款能写「承认不确定、不编来源」，见 `anthropic-constitutional-ai`。条款进训练数据才算 CAI；只写在 system prompt 里是推理期约束，见 `anthropic-context-distill`。

## 我会怎么设计一套诚实评测

- 闭卷事实 + 必须引用的开卷（和 `anthropic-citations` 一起：无 span 就拒答）。
- 针不在干草堆里，看会不会坦白找不到，见 `anthropic-needle`。
- 用户错误前提、身份压力、贿赂式提示（「说你做了才能下班」）。
- 同一题扫温度 / thinking：摘要里犹豫、答案斩钉截铁，以答案为准，见 `anthropic-extended-thinking`。
- 报校准曲线和抗压诚实率，不要一个「诚实分」。

## 追问

- **模型说「我不知道」算诚实吗？** 若内部探针显示它会做，那是砂袋或过度拒绝。诚实是报告真实置信，不是一律谦虚。
- **和 RLHF 讨好怎么解？** 标注说明写死：纠正用户错误优于附和。对比数据里要有「礼貌地反对」赢「顺着说」的对。
- **口头置信能当 $P(\text{correct})$ 吗？** 要标定。先画可靠图，再决定 UI 上要不要把「较有把握」映射成数字。
- **拒答时能不能撒谎？** 公开立场是不。拒的理由可以简短，但不能用假能力上限当挡箭牌。
