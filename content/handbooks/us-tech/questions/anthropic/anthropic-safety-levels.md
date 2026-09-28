---
id: anthropic-safety-levels
section: anthropic
order: 25
level: S
title: Anthropic：ASL / RSP 面试能公开讲到哪，不要编内部阈值
quick: >-
  只讲已发布的 Responsible Scaling Policy：能力阈值触发更严的部署和安保措施。ASL 在新版政策里更接近「措施包」而不是给模型贴永久标签。ASL-4
  及以上公开文本故意写得粗。不知道内部评分数就说不知道，不要编 CBRN 门槛。
tags:
  - Anthropic
  - ASL
  - RSP
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Announcing Anthropic's Responsible Scaling Policy
    url: https://www.anthropic.com/news/anthropics-responsible-scaling-policy
    type: primary
  - title: Responsible Scaling Policy Version 3.0
    url: https://www.anthropic.com/news/responsible-scaling-policy-v3
    type: primary
  - title: Activating ASL-3 protections
    url: https://www.anthropic.com/news/activating-asl3-protections
    type: primary
---

安全 / 政策岗会问 ASL。正确姿势是：复述公开 RSP，分清版本，拒绝发明数字。2023 年第一版借用生物安全分级：能力越高，部署和安保越严。2025 年 5 月公开激活 ASL-3 措施（配合 Opus 4），并写明是预防性的——当时还没断定一定跨过能力阈值。2026 年 RSP 3.x 把「ASL」更多说成措施簇，能力阈值和 Required Safeguards 分开写。面试不是让你背内部 eval 名称。

## 公开框架里有什么

早期公开定义的大意（以当时博文为准，不要把旧定义说成永远正确）：

- ASL-2：已有早期危险能力苗头，但还不比搜索引擎 / 教材可靠多少。当时宣称当时的 Claude 属这一档。措施接近当时的行业实践：拒危险 CBRN 请求、防机会主义偷权重。
- ASL-3：相对非 AI 基线，实质性增加灾难性误用风险，或出现低水平自主。措施更严：更强的权重安保（公开表述针对老练的非国家行为者，不是「防所有国家顶级对手」）、部署侧多层拦截。激活博文强调：拒答应落在很窄的话题上，不是全面变钝。
- ASL-4+：第一版就说尚未写细；3.0 仍强调更高档难以单方面规定，可能需要集体行动。RAND 等外部安全标准被引用为「目前做不到」的例子——用来说明单边承诺的上限，不是让你背 RAND 的内部编号当 Anthropic 政策。

If-then 结构：能力评估（或「还没能排除」）→ 上更严措施。允许宁可过严：公开说过，在尚未裁定 Opus 4 是否跨线时先上 ASL-3，并排除需要更高级别。这和「已经证明跨线」不是一句话。

3.0 / 3.1 的公开变化（面试说「政策在改」比假装只有 2023 定义更好）：ASL 一词不再当模型的永久能力标签，而当措施包；另用 Capability Thresholds。具体评测条目、分数线、内部红队手册没有作为可引用的稳定公开数字。Risk Report / system card 会写当前判断，以当时文档为准，不要记成永恒阈值。

## 明确不要编的东西

- 未公开的 benchmark 名称、分数、pass/fail 线。
- 「ASL-4 等于某某自主研发加速倍数」——3.x 讨论过 AI R&D 相关阈值的方向，但不要把新闻摘要扩写成内部操作手册。
- CBRN 的可操作细节、如何做能力 uplift 实验。面试只谈到「这类误用是公开威胁模型」为止。
- 声称你知道当前所有生产模型的 ASL 标签。3.x 后这句话可能范畴都不对。

被问到「你们内部阈值是多少」：答「我只根据公开 RSP 和 system card 讲；具体评估协议和数字不在公开材料里，我不会猜。」这比瞎编更像安全意识。被要求猜数字门槛时同样拒绝：瞎编门槛比说不知道更危险。细节指向当时的 RSP PDF / system card / Risk Report。

和产品对齐的衔接：constitution / HH / 拒答政策是日常有害内容；RSP 是灾难性风险的缩放承诺。不要把 over-refusal 评测和 ASL-3 部署标准混成一个开关。Computer use、MCP 权限是产品层 TCB，见 `anthropic-computer-use`、`anthropic-mcp`，替代不了权重安保。政策文本会改版：答「以当时公开 RSP 为准」，不要把 2023 定义背成 2026 仍有效的教条。

如果对方拿出未公开的内部 eval 名字，不要顺着编分数。可以说评测类别（自主性、CBRN 误用、网络）在公开 RSP 里出现过，细节以当时 system card 为准。

## 追问

- **ASL-3 激活是否等于模型已跨线？** 公开文本说不一定，可以是预防性部署更严措施。要把「措施已开」和「能力裁定」分开说。
- **更高 ASL 为什么留空？** 太早写死可能写错；有些安保可能单公司做不到。这是公开承认的局限，不是保密。
- **面试能谈 interpretability 保证吗？** 早期 ASL-4 设想提过机制性保证，并标明仍是未解研究。不要说「我们已经用解释性证明安全」。
- **和 CAI 的关系？** CAI 是训练期原则；RSP 是组织级 if-then。条款写进模型，替代不了部署监控和安保，见 `anthropic-constitutional-ai`。
