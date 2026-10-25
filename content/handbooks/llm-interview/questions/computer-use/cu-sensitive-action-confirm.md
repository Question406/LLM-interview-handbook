---
id: cu-sensitive-action-confirm
section: computer-use
order: 6
level: S
title: Computer-use Agent 对敏感动作如何做确认与防误触？
quick: "按 UI 语义识别删除、支付、发送、改权限这类动作，由 harness 弹系统确认框，展示解析后的收款人、金额、路径等关键参数，用户点了才放行。默认 deny，超时取消，全程写审计，模型不能既提议又批准。"
tags:
  - Safety
  - Computer Use
  - Confirmation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Developing a computer use model (Anthropic)
    url: https://www.anthropic.com/news/developing-computer-use
    type: primary
---

敏感动作要按 UI 语义识别，由系统侧弹确认，默认 deny，超时取消，写审计，模型不能既提议又批准。常见的错法是让模型在网页里自己点「确认」按钮，或者只按 tool 名（`click` / `type`）分类。

computer-use 的敏感动作藏在 UI 语义里，看起来是普通点击，实际是转账、删库、改权限或外发。比如同一个 `click`，点「保存草稿」和点「确认转账」风险完全不同；只拦 tool 名的话，这两下在分类器眼里一模一样。所以整套做法分三块：敏感动作的分类规则、和被控页面隔离的确认 UI、专门测能不能绕过确认的红队。光检查模型有没有发出提醒是不够的。这和 `cu-security-evaluation` 的 deny-state 一致，和 `agent-approval-boundaries` 的人审分层是同一个控制面。

## 按 UI 语义分类

敏感集合至少覆盖资金移动、不可逆删除、权限 / ACL 变更、对外发送、安装 / 提权、导出含秘密的文件。分类器检查的是解析后的目标：按钮名、对话框文案、收款人、金额、收件人域、路径，`click(x,y)` 本身看不出什么。白名单只放用户显式授权过的收款人、域名、目录，设金额 / 次数上限，过期收回。白名单还要能撤销，一次「记住这个收款人」不能变成永久自动转账。

风险分可以写成 $r(a) = s(a)\cdot u(a)$，$s$ 是动作类别的严重度，$u$ 是参数的不确定性。只有 $r(a)\lt\tau_{\mathrm{auto}}$ 才免确认，其余默认 deny。阈值 $\tau$ 按产品损失来标定，别按模型自报的置信度。

## 确认放在系统侧

确认 UI 由 harness 弹出，展示解析后的关键参数，比如收款人全名、金额、附件 hash、将要删除的路径，用户点系统按钮才放行。确认不许画进被控浏览器，也不许模型生成一个假对话框再自己点。超时 $T$ 内没响应就当取消，动作 deny 并记审计。连续的同类请求要聚合，避免审批疲劳；疲劳之后「全点允许」要当安全事故处理，别当成效率优化。

日志字段包括动作类、解析参数、是否确认、确认耗时、是否超时、是否命中白名单。没有这些字段，出了事只能说「当时点了」。生产上我会把确认策略和工具权限写在同一张表里，别等事后补一条输入提示（prompt）。Anthropic 一类 computer-use 安全说明的核心也是这个：模型操作计算机时，破坏性动作光靠模型自检是不够的。

红队至少测这几种：诱导连续点击、在截图上伪造系统确认框、隐藏真实收款人只显示昵称、把高风险按钮做得像「下一步」。评测报三个数：敏感动作未确认就执行的比例、确认绕过成功率、正常低风险任务被过度拦截的比例。「模型说了请确认」不算过关，环境里副作用已经发生就是失败。会让评测结果虚高的做法有：用 tool 名黑名单代替语义分类、确认框画在网页里、超时当允许、不测伪造确认 UI。

## 追问

**为什么不能让模型自己点网页里的确认？**
被控页面是不可信环境。攻击者伪造一个确认框或者改掉收款人，模型点的就是攻击者的按钮。

**只拦 `send_email` 够吗？**
不够。普通 `click` 也能提交支付表单，必须解析 UI 语义和参数。

**超时为什么默认取消？**
默认允许，等于把没响应当成授权。资金和删除类动作必须 fail-closed。

**和 `cu-security-evaluation`、`agent-approval-boundaries` 怎么分？**
`cu-security-evaluation` 定义攻击成功和 deny-state，这题是生产闸门，讲敏感动作怎么强制人审。`agent-approval-boundaries` 讲通用的人审分层和防疲劳，这题落到 computer-use 的系统确认控件和伪造 UI 红队。
