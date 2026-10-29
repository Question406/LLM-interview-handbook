---
id: meta-agent-code
section: meta
order: 30
level: A
title: Meta：代码 agent——仓库索引、补丁评测，和 AI coding 面试差在哪
quick: "代码 agent 系统要把权限与 commit 一起纳入仓库索引，再由宿主控制读文件、搜索、打补丁和沙箱测试的循环。验收用 issue 补丁的 fail-to-pass 与 pass-to-pass，加上误改、权限和索引新鲜度；AI coding 面试则是在评候选人如何使用现成助手。"
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

代码 agent 的核心是按权限找到当前版本的代码，提出补丁，再在可控环境中验证。它与 `meta-ai-coding` 的区别在于：那一轮 60 分钟、多文件仓库、编辑器带 LLM，考人怎样拆任务、审 diff、跑测试；这里要设计助手背后的索引、工具与执行系统。这道系统题来自公开材料，整体架构见 `design-code-assistant`。

仓库索引可以按路径、语法树符号、文本块和可选 embedding 分层。标识符精确拼写适合 BM25，自然语言 issue 用 dense 补充。每个 commit 增量更新改动路径，删除文件立即退索引，避免引用不存在的 API；embedding 升级双写，新旧向量不能混排。整仓塞进 $128\mathrm{k}$ 仍有权限、新鲜度、p95 和中间信息丢失问题，默认采用检索加定点 `read_file`。

权限键为 `repo_id + acl + commit`，先 ACL 过滤再 ANN，只搜用户能 clone 的路径。无权限时不要通过“检索为空”与“有结果但拒绝”的差别泄露仓库存在性。进上下文前扫描 `.env`、私钥和高熵串，私有代码默认不进权重，客户仓也不直接抽成评测题。索引滞后单独报 SLA，包括删除后多少秒退出补全和 agent 检索。

## 工具循环与补丁验证

宿主控制读文件、grep / 符号搜索、打补丁、跑测试的循环，模型只提交结构化调用，调用 schema 仍由宿主检查，见 `design-tool-prod`、`design-agent-harness`。补全需要几十到一百多毫秒延迟，仓库 agent 则以任务完成和误改为重点，可花秒到分钟，不能让两者随意共用一个 70B 服务池。补全更需要前缀缓存，agent 更需要工具与沙箱。

沙箱关闭网络或使用白名单，以只读镜像配可写工作树，限制 CPU、内存和短 TTL。写操作先给 diff，再应用；隐藏测试和只读测试树防止改测试、删断言、把 flaky 测试标 skip。超时必须清理进程，避免让 decode 槽位一直等工具。

Code Llama 是 infilling、长窗、Python 特化的专用代码基座；Llama 3 Herd 在训练 mix 中包含代码并报 HumanEval / MBPP。但函数补全分数不能证明能修多文件 issue，工具调用的早期自监督背景见 `meta-toolformer`。

SWE-bench 给 issue 与仓库快照，提交补丁后用作者测试判定：fail-to-pass 必须通过，pass-to-pass 不能回归。Resolved 率要同时注明 Full / Lite / Verified 子集、是否看过测试、gold 补丁是否泄露、步数和工具集。Verified 是人工筛选题，不能与 Full 混报；公开 PR、解法博客进入预训练的风险见 `meta-llama-eval`。

内部产品同样按“issue → 补丁 → CI”验收，再看 diff 是否最小、是否改测试作弊、步数、误改文件数、沙箱逃逸（零容忍）和索引删除 SLA。HumanEval 高分仍可能在环境、权限、多文件修改中失败。

## 追问

**为什么不用长上下文装整个 monorepo？**
默认很难同时满足权限、新鲜度与 p95，检索后定点读取更可控。

**测试可见怎么办？**
产品可正常跑测试，评测必须声明可见性，并用隐藏测试防止作弊。

**Code Llama 和 Llama 3 怎么选？**
专用基座可负责 infilling、仓库续写，通用 70B/405B 可负责指令和工具，按任务分工验证，不假定一个检查点包办全部。

**与 AI-enabled coding 轮重复吗？**
不重复。那轮评人怎样使用现成 runner，这里要自己设计 runner、镜像、权限和超时，并校验模型动作。
