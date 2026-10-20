---
id: msft-copilot-ground
section: microsoft
order: 2
level: S
title: Microsoft：Copilot grounding（代码/文档检索），引用和权限
quick: >-
  答案必须能指回检索到的代码或文档跨度，而且检索集合不能大于当前用户 ACL。引用是产品契约，权限是安全契约，两件都失败就算事故。不要把
  Copilot 答成「加个向量库」。
tags:
  - Microsoft
  - Copilot
  - Grounding
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Semantic Index for Copilot
    url: https://learn.microsoft.com/en-us/microsoftsearch/semantic-index-for-copilot
    type: primary
  - title: Data, Privacy, and Security for Microsoft 365 Copilot
    url: https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy
    type: primary
---

Copilot / M365 / GitHub 应用岗常把 grounding 当系统设计开口。公开材料里 Microsoft 365 Copilot 走 Graph + 语义索引，生成只基于当前用户能看见的内容；GitHub Copilot Chat 则是仓库代码检索。不一定有一份逐字面经，但和「企业助手必须可引用、不可越权」的口味一致。同类契约见 `apple-siri-grounded`、`amazon-bedrock-rag`，微软多出来的是 **租户隔离和 ACL 必须跟 Graph 一致**。

## Grounding 要落实为检索与引用检查

系统先拿用户身份去取证据 $E$，再条件生成。代码侧 $E$ 是文件、符号、diff 块；文档侧是会议、邮件、SharePoint 页。解码时每个关键命题要对上 $E$ 里的跨度。对不上就删句、改口「仓库里没写」，或者追问缺了哪份文件。用预训练记忆补「常见写法」在 IDE 补全里可以，在 **带引用的问答** 里算幻觉。

我会把链路拆成四层，避免画成一个方块「RAG」：

1. **身份。** Entra / GitHub 登录。后续每次检索都带这份身份，不要先搜全租户再事后过滤一份「看起来相关」的列表，那是泄漏窗口。
2. **索引。** M365 是语义索引 + Graph 信号（谁和谁协作、哪份文件最近打开）。代码是分块（函数 / 类 / 滑动窗口）加符号图，不能只按 512 token 切块 把 API 签名切碎。
3. **检索。** 关键词 + 向量 + 元数据过滤（repo、path、site、时间）。代码问题优先符号和调用图，文档问题优先标题和 ACL。
4. **生成 + 引用。** 提示里只塞 top-k 短块。每个断言绑 `uri` + 行号或段落 id。UI 上引用必须可点，点进去是同一份 ACL 下的原文。

索引可以缓存 embedding，**不能缓存「用户 A 的检索结果给用户 B」**。权限变更（从频道移除、链接作废、sensitivity label）要能在检索路径上立刻生效，向量自己不会过期。GitHub 对公开代码匹配有单独的 code referencing 通道，和「用我这个私有 repo 回答」不是同一条权限链，面试里要主动拆开。

## 引用和权限是两条评测，别合成一个「质量分」

引用失败有两种，混在一起没法修：

- **幻觉引用：** 句子在 $E$ 里找不到，或绑到了无关文件。这是生成 / 对齐问题。
- **越权引用：** 句子其实是对的，但那份文件当前用户打不开。这是安全事故。索引时若没带 ACL，或查询时用了服务账号扫全库，就会出这种 bug。公开文档写得很硬：Copilot 只呈现该用户在其他 M365 服务里本来就能访问的数据；带 Purview 标签的文件还要看使用权限。

评测不要只报 BLEU。离线：给定 $(q, E_{\mathrm{gold}})$，看 recall@k、引用可定位率、越权率（必须是 $0$）。线上：用户点开引用的比例、被安全团队打回的泄漏工单。A/B 时多召回一篇无关但用户可见的 wiki，不如少召回；多召回一篇用户不可见的设计文档，直接是事故。

延迟：IDE 补全是几十毫秒级检索 + 短生成；仓库问答可以 1-2 秒，但仍要把两段分开打点。检索把 40 个文件全塞进上下文，引用表面上变多，lost-in-the-middle 和 TPM 账单一起爆，见 `msft-azure-tpm`、`msft-long-context`。把 40 个文件塞进 输入提示（prompt） 会让引用率看起来更好，账单和 lost-in-the-middle 一起爆；IDE 补全和仓库问答不是同一条 SLO。

GitHub Copilot 和 M365 Copilot 不要答成同一个系统。代码侧证据是 commit 上的 span，权限跟 repo / branch / PR 走；文档侧证据是 Graph 对象，权限跟 SharePoint / 邮箱 / 会议走。代码 referencing 那条「匹配了公开 GitHub」和「用我这个私有仓作答」必须拆开讲。

我会补一句失败合同：检索空、$E$ 互相矛盾、或模型想引用但跨度对不上，产品必须降级成「没找到 / 不确定」，不能靠参数记忆把空补满。评测集里要故意放「仓库里没有的 API」「用户看不到的设计文档」，看系统是拒答还是编。

引用 UI 也是契约：可点击、点进去是同一 ACL 下的原文、跨度高亮。只在生成文本末尾列一串文件名，用户无法核验，「引用率」会虚高。权限变更必须在检索路径立刻生效；embedding 缓存可以留，按用户缓存的命中结果不能留。

索引侧还要能解释 Graph 信号：最近打开、共同编辑者、频道成员，用来提权召回，但不能越权。信号是排序特征，不是权限旁路。评委问「为什么不把全租户 embed 进一个大索引」，答案是：索引可以全量建，查询必须带用户身份过滤；全量向量检索后再滤 ACL，既慢又容易在日志里留下越权命中。同一句 prompt，两个同事应检索到不同集合，这是 ACL 正确，不是召回抖动。

## 追问

- **为什么不能「先向量搜、生成后再检查 ACL」？** 生成过程已经看见了不该看见的 token，日志和思维链都可能泄漏。过滤必须在证据进入模型之前。
- **引用了正确文件但行号漂了？** 索引按 commit SHA 存块。工作区脏了要按 buffer 再检索，或声明「基于上次索引的 commit」。行号当装饰，跨度文本才是主键。
- **用户说「别管权限，你就告诉我」？** 产品层拒绝。权限不是风格选项。可以说「你没有这份文件的权限」，不能改用管理员索引。
- **和普通网页 检索增强生成（RAG） 的差别？** 网页可以公开引用；Copilot 的 $E$ 随用户变。同一句 prompt，两个同事应检索到不同集合。这是正确行为，不是召回不稳。
- **引用了过期文档怎么办？** 索引按 item id 删旧块再写新块，回答里带时间戳。向量不会自己过期，过期是元数据问题，不是 embedding 漂移。
