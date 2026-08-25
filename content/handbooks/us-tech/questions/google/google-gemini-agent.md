---
id: google-gemini-agent
section: google
order: 28
level: A
title: Google：Gemini 工具调用、计算机使用（公开层）和搜索接地
quick: >-
  公开层就三件事：自定义 function calling、内置 Google 搜索接地、computer use 的截图-动作环。原生多模态能看见屏幕，不等于会点；搜索接地给引用，不等于让模型自己开浏览器。副作用工具要确认和沙箱。
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

Gemini 应用 / 研究岗问 agent，要你停在 **公开 API 能看见的循环**，不要编内部编排器。自定义工具、搜索接地、计算机使用是三条不同的工具面：一个填 JSON 参数，一个检索并带引用，一个对截图吐 UI 动作。评测切片见 `google-agent-eval`。看见像素不等于取消工具，见 `google-gemini-mm`。不是某次逐字真题。

## 自定义工具：模型出调用，客户端执行

Function calling 公开路径：你把工具 schema 塞进请求，模型决定是否发出 function call，你执行，把观察塞回下一轮，直到模型出自然语言或再调。这和「让模型在 token 里假装调用」不同：参数要能校验，失败要能回灌，步数和墙钟要有顶。

我会主动钉的不变量：

- 工具输出当数据，不当系统指令。网页、PDF、用户粘贴都可能带注入。
- 不可逆动作（付款、删数据、发邮件）不要一次 call 直接打生产。公开 computer use 文档里还有需要用户确认或直接拦截，同一思想。
- Schema 描述的是类型，不是权限。限额、身份、幂等键在你这边。

和搜索接地别混：自定义工具是你的 API；Google Search grounding 是平台检索，模型自己决定要不要搜、搜什么，回答带 URL 引用一类标注。接地降低的是知识截止日期和胡编；它不给你点按钮的能力。延迟上多一轮检索会打首 token。面试说「接地不是免费上下文」即可。

Agent 这里的指标是 **引用是否撑得住句子、该搜的时候有没有搜**，不是把搜索 ranker 接到生成上。本轮不做广告 / 视频排序。

## 计算机使用：截图进，动作出，环在你进程里

公开 computer use：请求里带目标、当前截图、可选历史；模型返回规范化坐标上的 click / type / scroll 一类调用。客户端在沙箱（浏览器自动化、云 VM）里执行，再截一张图喂回去。文档写明安全层可以把动作标成允许、要用户确认、或直接挡。2.5 的 Computer Use 模型公开叙事是 **浏览器优先**，桌面 OS 级控制不是当时优化目标——评测别拿 OSWorld 桌面任务当唯一 KPI，见 `google-agent-eval`。

和原生多模态的分界：模型可以描述「现在是结账页」，这是视觉；点「提交订单」是动作，坐标错了就点到广告。分辨率和视觉 token 预算见 `google-vit-patch`。环的每一步都是一次前向加一次 UI 往返，步数爆炸时贵的是墙钟和误点击，不是 MMLU。

失败模式我按层说：看错控件（视觉）、计划错步骤（推理）、环境变了还按旧坐标点（状态）、网页内容当指令（注入）。每层的补丁不同，不要只加系统提示。

## 什么时候用哪条工具面

- 要精确算术、查内部库、写代码：自定义工具或代码执行。
- 要过知识截止日期、给用户看出处：搜索接地。
- 没有 API 的网页流程、填表：computer use，且必须沙箱。
- 长文档已经在窗口里：先读像素 / 文本，见 `google-gemini-longctx`，不要为了「显得 agent」每句都去搜。

错法：把三条合成「Gemini 会用电脑所以不用检索」；说原生多模态替代了 function calling；在无沙箱的本机桌面跑 computer use 当演示。公开层把执行权留在客户端，是产品责任边界，不是实现偷懒。

轨迹、截图、检索摘要都占 $T$。环要截断旧截图、摘要旧步骤，否则 KV 先爆。每步新截图也是离散视频，旧帧策略见 `google-video-token`。

## 追问

- **搜索接地和让 agent 自己浏览差在哪？** 接地是检索-综合-引用，动作空间是查询。Computer use 动作空间是像素坐标。前者好审计出处，后者能走没有 API 的流程，也更好注入。
- **确认框谁做？** 模型可以请求确认；真正弹窗和记录同意是客户端。没日志的确认等于没确认。
- **多工具并行？** 公开文档允许内置工具和自定义工具组合（视模型代际）。并行调用要处理部分失败，不要假定全成功再生成。
- **和长上下文怎么叠？** 轨迹和截图占窗口。环要截断旧帧、摘要旧步骤，见 `google-gemini-longctx`。
