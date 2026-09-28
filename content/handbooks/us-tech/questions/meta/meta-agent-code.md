---
id: meta-agent-code
section: meta
order: 30
level: A
title: Meta：代码 agent——仓库索引、补丁评测，和 AI coding 面试差在哪
quick: >-
  面试轮 `meta-ai-coding` 考你怎么指挥现成助手把测试跑绿。本题考系统设计：索引要权限和新鲜，agent
  循环是读 / 搜 / 补丁 / 沙箱测试，评测用 fail-to-pass 而不是 HumanEval。公开锚点是 Code Llama 和
  SWE-bench，不要编内部代码助手架构。
tags:
  - Meta
  - Code agent
  - SWE-bench
  - System design
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Code Llama — Open Foundation Models for Code
    url: https://arxiv.org/abs/2308.12950
    type: primary
  - title: SWE-bench — Can Language Models Resolve Real-World GitHub Issues
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: secondary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: secondary
---

和 `meta-ai-coding` 差在评什么人。那一轮是 **60 分钟、多文件仓库、编辑器里带 LLM**：考拆任务、读 diff、跑测试。本题是 **GenAI 系统设计**：你要建的是那个助手后面的系统。白板骨架和 `design-code-assistant` 同源，但 Meta 岗会把模型换成 Llama / Code Llama，评测口径钉在补丁和 CI，而不是补全接受率。不是某次现场逐字题。

## 索引：符号比 embedding 先干活

仓库不是一篇文档。分层：路径 + 树解析符号（函数 / 类）+ 文本块 + 可选 embedding。标识符拼写 BM25 很强；dense 补自然语言 issue。增量按 commit：改了的路径重切，删了的文件立刻从索引消失，否则 agent 会引用幽灵 API。

权限键是 `repo_id + acl + commit`。用户只能检索他能 clone 的路径。跨私有仓的「语义相似」是泄漏。无权限时不要用「检索为空 vs 有结果但拒绝」区分仓库在不在。私有代码默认不进权重；评测集别从客户仓抽。密钥扫描在进上下文前做：`.env`、私钥、高熵串直接丢，不要靠模型「注意别泄漏」。

整仓塞进 $128\mathrm{k}$ 不是答案：权限、新鲜、p95、中间丢失。索引 + 定点 `read_file` 更像工程师。Embedding 升级要双写，新旧向量不能混排。

检索查询要先按 ACL 过滤再 ANN，不要先召回再丢弃：向量碰撞不能把邻仓文件打进上下文。存在性泄漏：无权限时检索为空和「有结果但拒绝」不要可区分。索引滞后单独报 SLA：文件删除后多少秒从补全和 agent 检索里消失。

## Agent 循环和沙箱

产品不是行内补全。补全 SLO 是几十到一百多毫秒，见 `design-code-assistant`；仓库 agent 的 SLO 是任务完成和误改，墙钟可以秒到分钟。工具要少而硬：读文件、搜（grep / 符号）、打补丁、跑测试。循环写在宿主，模型只出结构化调用，见 `design-tool-prod`、`design-agent-harness`。

沙箱：无网或白名单、只读镜像加可写工作树、CPU / 内存配额、短 TTL。写操作先出 diff 再应用。失败模式：改测试来「通过」、删断言、把 flake 标 skip。隐藏测试和只读测试树防这个。超时要能杀进程，不要让 decode 槽位空等。

Code Llama 公开故事是专用代码基座（填充 infilling、长窗、Python 特化），Herd 把代码当 mix 的一档并报 HumanEval / MBPP。Agent 题不要停在 HumanEval：那是函数补全，不是修 issue。工具调用的自监督前史见 `meta-toolformer`；生产 schema 仍要宿主校验。

## 评测：fail-to-pass，不要口头 resolved

SWE-bench：给定 issue 文本和仓库快照，系统交补丁，跑作者测试。**fail-to-pass 必须过，pass-to-pass 不能回归。** 报 resolved 率要写：子集（Full / Lite / Verified）、是否泄漏 gold 补丁、是否看见测试文件、步数和工具集。Verified 是人滤过的题面，不能和 Full 混报。污染：公开 PR 和解法博客会进预训练，见 `meta-llama-eval`。

内部产品集应是「内部 issue → 补丁 → CI」，口径仍要 fail-to-pass。人评看 diff 是否最小、是否改测试作弊。指标再加：步数、误改文件数、沙箱逃逸（零容忍）、索引滞后 SLA（删除后多少秒从检索消失）。

和 AI coding 面试对照表：面试给你失败测试和现成 runner，考的是人；agent 系统要自己建 runner、镜像、超时和权限。面试里模型是可选助手；这里模型是循环里的策略网络，宿主必须不信任它。IDE 补全和仓库 agent 不要共用一个 70B 池：补全要前缀缓存和低延迟；agent 要工具循环和沙箱，见 `design-code-assistant`。

## 追问

- **为什么不把 monorepo 塞长上下文？** 权限和新鲜做不到，p95 也做不到。索引 + 定点读是默认。
- **HumanEval 高就能发代码助手？** 不能。那是单函数合成；产品失败在多文件、环境、权限。
- **和 AI-enabled coding 轮重复吗？** 不。那轮评候选人怎么用助手；本题评你怎么设计助手。
- **测试可见怎么办？** 产品上可以跑测；评测要声明是否可见。隐藏测试防改测试作弊。
- **Code Llama 还是 Llama 3？** 专用代码基座对 infilling 和仓库续写仍有用；通用 70B/405B 更强的是指令和工具。Agent 里两者可以分工，不要说成一个 checkpoint 包打天下。
