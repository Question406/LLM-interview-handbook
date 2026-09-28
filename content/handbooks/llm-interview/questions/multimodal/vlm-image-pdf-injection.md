---
id: vlm-image-pdf-injection
section: multimodal
order: 201
level: S
title: 图像 / PDF 中的注入攻击如何检测与缓解？
quick: 把视觉文档当 untrusted：分离可见指令与系统策略，对「忽略规则/外泄」类文本做过滤；工具调用不自动信任图中 URL/二维码。
tags:
  - Prompt Injection
  - Multimodal Security
  - PDF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: "Not What You've Signed Up For (indirect prompt injection)"
    url: https://arxiv.org/abs/2302.12173
    type: primary
---

错法：只给文本通道做 jailbreak 过滤，却把截图、发票 PDF、二维码当「用户已经看见的 harmless 数据」。这是多模态 Agent 的主漏洞。间接注入不必和控制面对话：恶意指令可以是图上白字、PDF 隐藏层、看起来像系统对话框的截图。Greshake 等人把数据通道写成攻击面；视觉文档只是同一通道的另一种载体。OCR 之后走文本安全模型会漏隐藏层，也拦不住「把图里 URL 当工具参数」。防御要按 taint：图和 PDF 是 data，不是 authority。这与 `agent-prompt-injection` 同源，评测应并进 `cu-security-evaluation` 的成对任务，而不是另做一套口头拒答。

## 攻击面比可见文字更大

至少四类：排版注入（低对比文字、页脚「忽略以上指令」）；PDF 隐藏 / 可选内容组，人眼看不到但抽取器读得到；伪造系统 UI（截图里的确认框、浏览器权限条）；机器可读载荷（二维码、图中 URL、附件脚本）。Agent 一旦把这些字符串拼进 planner，就会调用外发、支付、上传。工具参数白名单必须拒绝「来自图像抽取、未经用户确认」的 URL 与账号。Canary 可印在图或 PDF 层里，出现在出站请求即算外泄。没有 canary，你只能测模型有没有骂攻击者。

## 缓解：分层，而不是再写一句 ignore

控制面与数据面分离：系统策略不进视觉 encoder 的可改写区；视觉抽取结果标 `untrusted`。对抽取文本跑 injection 分类器，但分类器失败不得放行敏感工具，默认 deny。出站允许列表、敏感工具人审、禁止自动跟随图中链接。人眼可见与抽取文本做差分：隐藏层多出来的指令视为攻击。评测用专用红队集：正常票据任务 vs 带注入的同一版式；报告 utility、ASR、外泄率，禁止只报拦截率。攻击成功仅当环境副作用成真：$\mathrm{ASR}=n_{\mathrm{effect}}/n_{\mathrm{atk}}$，且正常任务成功率须 $\mathrm{U}\gt U_{\min}$，否则拒答一切也能刷拦截。能刷的点：只用直球「忽略之前的指令」印在图上；不测隐藏层；把 OCR 清洗当充分条件；模型说「我拒绝」但已请求图中 URL。

图像 / PDF 与网页、邮件一样是不可信数据；可见指令不能升级权限。落地清单：taint 标记、隐藏层差分、出站 allowlist、敏感工具确认、canary、成对评测。缺隐藏层差分，你在测排版而不是测 PDF。产品上要盯「二维码里的 URL 会不会直接变成 `http` 参数」。

和文本间接注入相比，视觉通道多了「用户以为自己看见了全文」的错觉。产品文案不能写「已展示给用户因此安全」；用户没看见隐藏层，Agent 却读到了。把这条写进威胁模型，比再训练一个拒答头更重要。

## 追问

- **OCR 后再做文本过滤够吗？** 不够。隐藏层、二维码和伪造 UI 不会稳定进 OCR；工具参数仍可能直接吃图中 URL。
- **和 `agent-prompt-injection`？** 那题是 tool / RAG / memory 数据通道；本题是视觉文档如何成为同一通道。
- **和 `cu-security-evaluation`？** 用成对任务与 canary 衡量视觉注入是否在环境里得逞，而不是看拒答话术。
- **用户说「按图里的做」怎么办？** 仍不能自动授图中 URL / 账号；高风险参数要系统确认，图只提供建议。
