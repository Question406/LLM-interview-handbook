---
id: msft-copilot-ground
section: microsoft
order: 2
level: S
title: Microsoft：Copilot grounding（代码/文档检索），引用和权限
quick: "Copilot 的答案要能定位到检索证据，检索证据又必须限制在当前用户权限内。先带身份查代码或 Graph 对象，再用短块生成并绑定 URI 与跨度；证据缺失或矛盾时降级。分别评召回、引用可定位与越权率，避免让引用分掩盖泄漏。"
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

Copilot grounding 要同时满足证据支持和访问权限：每个关键论断能指回检索跨度，证据只能来自当前用户可见内容。比如同一句问题，两个同事得到不同检索结果，可能恰好说明 ACL 正常生效。

Microsoft 365 Copilot 的公开路径是 Graph 加语义索引，GitHub Copilot Chat 则检索仓库代码。这是公开系统设计讨论，未声明逐字面经。同类证据契约见 `apple-siri-grounded`、`amazon-bedrock-rag`，企业环境还要保持租户隔离和 Graph ACL 一致。

## 让身份沿检索链路传下去

先以 Entra / GitHub 身份取得证据 $E$，每次检索继续带身份。索引可全量建 embedding，但查询要先裁权限；全量检索后过滤既可能留下越权日志，也会在误传给模型时泄漏。

M365 的证据是会议、邮件、SharePoint 页等 Graph 对象，排序可利用最近打开、共同编辑、频道成员和协作信号，权限仍由对象 ACL 决定。代码证据则是文件、符号、diff 块，权限跟 repo / branch / PR，索引应按函数、类、滑动窗口和符号图组织，按 512 token 生切可能截断 API 签名。

关键词、向量和 repo、path、site、时间等元数据结合检索。代码优先符号与调用图，文档优先标题和 ACL。只把 top-k 短块交给生成，每个断言绑定 `uri`、行号或段落 id，并可点击到当前身份下的原文、突出显示跨度。

Embedding 可以缓存，用户 A 的检索结果不能直接给 B。频道移除、链接失效或 sensitivity label 变更要及时作用到检索，Purview 文件还需核对使用权限。GitHub 公开代码匹配的 code referencing 是另一条通道，不能与私有 repo 回答的权限混为一谈。

## 分开处理引用错误与越权

句子在 $E$ 中找不到支持，或绑定无关文件，是幻觉引用；句子正确但当前用户无法打开源文件，是越权引用。两者根因和修复不同，服务账号扫全库、索引未带 ACL 都可能造成后者。

带引用问答不应使用预训练记忆补出「常见写法」，即使 IDE 补全允许生成这种建议。检索为空、$E$ 冲突或跨度对不上时，删句、说「没找到 / 不确定」，或者询问缺哪份文件。评测加入仓库不存在的 API 和不可见设计文档，检查是否拒答。

离线给定 $(q, E_{\mathrm{gold}})$，测 recall@k、引用可定位率和越权率（要求 $0$）；线上看引用点击和安全泄漏工单。无关但可见的 wiki 会影响相关性，不可见文档则违反安全约束，不能平均成一个质量分。只列文件名也不能证明可核验，要有实际跨度。

IDE 补全可按几十毫秒检索加短生成设计，仓库问答可接受 1-2 秒，两段分别打点。检索 40 个文件后全放 prompt 会增加 TPM 和 lost-in-the-middle，见 `msft-azure-tpm`、`msft-long-context`，不能只看表面引用数。

## 追问

**为什么不能生成后再查 ACL？**
模型已看到越权 token，日志或思维链也可能暴露，应在证据进入前过滤。

**文件正确但行号漂移呢？**
索引按 commit SHA 存块，工作区脏了按 buffer 重检索，或说明基于旧 commit。核验以跨度文本为准。

**用户要求忽略权限怎么办？**
产品层拒绝，可以说明无权访问，不能换管理员索引。

**与普通网页 RAG 差在哪？**
网页证据通常可公开引用，Copilot 的 $E$ 随用户权限变化。

**旧文档怎么更新？**
按 item id 删除旧块再写新块，回答带时间戳。过期由元数据处理，向量不会自行过期。
