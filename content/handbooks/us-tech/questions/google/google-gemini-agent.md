---
id: google-gemini-agent
section: google
order: 28
level: A
title: Google：Gemini 工具调用、计算机使用（公开层）和搜索接地
quick: "Gemini 公开工具能力包括 function calling、Google Search grounding 和 computer use。自定义工具由模型生成参数、客户端执行；搜索 grounding 负责检索和引用；computer use 则不断读取截图、返回动作。能看懂屏幕和能安全执行操作需要分别验证，有副作用的工具要加确认和沙箱。"
tags:
  - Google
  - Gemini
  - Agents
  - Tool use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini API — Function calling
    url: https://ai.google.dev/gemini-api/docs/function-calling
    type: primary
  - title: Gemini API — Grounding with Google Search
    url: https://ai.google.dev/gemini-api/docs/grounding
    type: primary
  - title: Gemini API — Computer use
    url: https://ai.google.dev/gemini-api/docs/computer-use
    type: primary
  - title: Introducing the Gemini 2.5 Computer Use model
    url: https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-computer-use-model/
    type: primary
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: secondary
---

Gemini 的公开 agent 能力可以按执行方式来解释：自定义工具让模型填 JSON 参数，搜索 grounding 负责检索并给出引用，computer use 则根据截图返回 UI 动作。比如模型能认出结账页，还需要客户端执行点击，才能继续流程。下面只讨论公开 API 能看到的循环；评测见 `google-agent-eval`，视觉能力见 `google-gemini-mm`。

Function calling 公开路径：你把工具 字段和类型规范（schema） 塞进请求，模型决定是否发出 function call，你执行，把观察塞回下一轮，直到模型出自然语言或再调。这和「让模型在 token 里假装调用」不同：参数要能校验，失败要能回灌，步数和实际耗时要有顶。

执行工具时，我会保留几条边界：

- 工具输出当数据，不当系统指令。网页、PDF、用户粘贴都可能带注入。
- 不可逆动作（付款、删数据、发邮件）不要一次 call 直接打生产。公开 computer use 文档里还有需要用户确认或直接拦截，同一思想。
- Schema 描述的是类型，不是权限。限额、身份、幂等键在你这边。

和搜索 grounding别混：自定义工具是你的 API；Google Search grounding 是平台检索，模型自己决定要不要搜、搜什么，回答带 URL 引用一类标注。grounding 减少知识过时和无依据编造；它不给你点按钮的能力。延迟上多一轮检索会打首 token。所以评估搜索 grounding 时，要把新增检索耗时计入首 token 延迟。

Agent 这里的指标是引用是否撑得住句子、该搜的时候有没有搜，不是把搜索 ranker 接到生成上。这里评估的是回答与证据的关系，广告和视频排序属于另一类任务。

公开 computer use：请求里带目标、当前截图、可选历史；模型返回规范化坐标上的 click / type / scroll 一类调用。客户端在沙箱（浏览器自动化、云 VM）里执行，再截一张图喂回去。文档写明安全层可以把动作标成允许、要用户确认、或直接挡。2.5 的 Computer Use 模型公开叙事是浏览器优先，桌面 OS 级控制不是当时优化目标；评测别拿 OSWorld 桌面任务当唯一 KPI，见 `google-agent-eval`。

和原生多模态的分界：模型可以描述「现在是结账页」，这是视觉；点「提交订单」是动作，坐标错了就点到广告。分辨率和视觉 token 预算见 `google-vit-patch`。环的每一步都是一次前向加一次 UI 往返，步数爆炸时贵的是实际耗时和误点击，不是 MMLU。

失败模式我按层说：看错控件（视觉）、计划错步骤（推理）、环境变了还按旧坐标点（状态）、网页内容当指令（注入）。每层的补丁不同，不要只加系统提示。

- 要精确算术、查内部库、写代码：自定义工具或代码执行。
- 要过知识截止日期、给用户看出处：搜索 grounding。
- 没有 API 的网页流程、填表：computer use，且必须沙箱。
- 长文档已经在窗口里：先读像素 / 文本，见 `google-gemini-longctx`，不要为了「显得 agent」每句都去搜。

常见误区是：把三条合成「Gemini 会用电脑所以不用检索」；说原生多模态替代了 function calling；在无沙箱的本机桌面跑 computer use 当演示。公开层把执行权留在客户端，是产品责任边界。

轨迹、截图、检索摘要都占 $T$。环要截断旧截图、摘要旧步骤，否则 KV 先爆。每步新截图也是离散视频，旧帧策略见 `google-video-token`。

## 追问

**搜索 grounding和让 agent 自己浏览差在哪？**
grounding 是检索、综合与引用，动作空间是查询。Computer use 动作空间是像素坐标。前者好审计出处，后者能走没有 API 的流程，也更好注入。

**确认框谁做？**
模型可以请求确认；真正弹窗和记录同意是客户端。没日志的确认等于没确认。

**多工具并行？**
公开文档允许内置工具和自定义工具组合（视模型代际）。并行调用要处理部分失败，不要假定全成功再生成。

**和长上下文怎么叠？**
轨迹和截图占窗口。环要截断旧帧、摘要旧步骤，见 `google-gemini-longctx`。
