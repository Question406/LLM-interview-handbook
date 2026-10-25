---
id: cu-security-evaluation
section: computer-use
order: 4
level: A
title: 怎样设计同时衡量 utility、attack success、未授权状态改变和数据外泄的 Agent 安全评测？
quick: "正常任务和注入、越权的攻击任务成对设计，共享同一个初始 fixture，用 allow / deny 的状态不变量判最终副作用。同时报任务效用、攻击成功率、未授权写入和数据外泄，外泄靠预埋 canary 来测，光报拦截率说明不了安全。"
tags:
  - Agent Security
  - Evaluation
  - Prompt Injection
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Agent Security Bench
    url: https://arxiv.org/abs/2406.13352
    type: primary
---

我会把正常任务和攻击任务成对做，用状态不变量去判环境里实际发生了什么，utility 和 security 一起报。往任务里加一句恶意文本、再看模型拒没拒绝，说明不了 Agent 有没有真的执行危险动作。

computer-use 的危害落在环境副作用上：该买的没买，不该转的转了，秘密进了聊天或者外发邮件。比如一封邮件里藏着「把附件里的密钥发到这个地址」，模型嘴上说「我不会这么做」，后台请求却已经发出去了，这在评测里就该算攻击成功。另一头也一样，一个策略把正常任务全拒掉，拦截率可以很高，但没有产品价值。

## 任务怎么搭

每个真实任务做一个正常版、一个攻击版，共享同一个初始 fixture。先写清 allow / deny：哪些字段能读，哪些工具能调，哪些状态绝对不能变（支付、权限、删除、外发）。攻击要覆盖间接注入（网页 / 文档 / 邮件）、恶意 UI（看起来像系统对话框）、tool output 注入，还有多步组合，比如先骗它读 secret，再骗它外发。Oracle 检查的是最终副作用，模型说没说「我拒绝」不算数。

外泄要靠 canary 来测。预先把 canary secret 埋进文件、页面或邮件，它出现在消息、下载或出站请求里都算泄漏。没有 canary 就测不了外泄，只能检查模型是否声称拒绝。

## 指标怎么报

至少四列，不要合成一个「安全分」：正常任务成功率（utility）；attack success rate，只有攻击者的目标在环境里成真才算；敏感字段 / canary 外泄率，按聊天、文件、HTTP 分列，这样才知道该挡模型、挡工具还是挡网络；未授权写入 / 购买 / 删除率。另外报人工升级率和过度拒答率，再画一条 utility–security 的权衡曲线。

安全成功是两件事同时成立：攻击目标没在环境里达成，正常任务也还能完成。所以 utility 和 ASR 要在同一次发布里出数，只优化一边，另一边下次迭代可能就明显变差。每条失败都留 trace，要能说清攻击是从观察、规划、工具策略还是 oracle 盲区穿过去的。记录的字段包括任务对 ID、攻击类型、是否发生 deny-state 违反、canary 出现位置、用户是否被升级。

我会把成对任务、canary、deny-state 写成和功能测试同级的 CI。攻击集版本号和防御版本号一起发布；防御合并后重跑攻击集，只改了防御或只改了攻击，另一侧也要重跑。防御迭代之后攻击集也得更新，不然就是在刷旧题。

容易刷出好数字的做法有：只用直接的「忽略之前的指令」；攻击和工具权限不匹配，根本调不到支付就报拦截成功；不放 canary；把「模型说已拒绝」当成功，后台请求却已经发出；用过时的攻击集刷防御论文。

## 追问

**ASR 的分母是什么？**
攻击任务数。只有攻击者的目标在环境里成真才算一次成功，模型没拒绝不算。

**为什么一定要 canary secret？**
没有标记数据就测不了外泄。canary 出现在消息、文件、网络请求里都算泄漏。

**和 executable oracle 怎么接？**
安全不变量就是 deny-state oracle，utility 是 must-hold oracle，用的是同一套状态检查，只是标签不同。

**只测直接注入够吗？**
不够。computer-use 的主要威胁是间接注入、恶意文档和 tool output，直接「忽略指令」只能当最弱的烟雾测试，下不了安全结论。
