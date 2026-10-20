---
id: design-code-assistant
section: design
order: 16
level: S
title: 设计：代码助手（仓库索引、权限、补全延迟、SWE-bench 口径）
quick: >-
  补全和 agent 改仓库是两条 SLO。索引要权限和新鲜；补全要几十毫秒级前缀缓存；评测用 SWE-bench 要钉 harness、
  仓库快照、测试命令，不要口头「resolved 高了」。私有代码不能进训练或跨租户检索。
tags:
  - Microsoft
  - GitHub
  - Meta
  - SWE-bench
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: SWE-bench — Can Language Models Resolve Real-World GitHub Issues?
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: primary
  - title: GitHub Copilot documentation
    url: https://docs.github.com/en/copilot
    type: secondary
---

Microsoft Copilot、Meta 内部代码助手、OpenAI 评测岗会问代码产品。SWE-bench 给的是「issue + 仓库快照 + 补丁 + 测试」口径；Verified 说明原集有题面噪声。白板要索引、权限、延迟、评测。不是某次现场逐字题。有实际证据支持见 `msft-copilot-ground`；检索骨架见 `design-prod-rag`；对话服务见 `design-chat-serving`。不要把推荐广告架构套过来。

## 索引和权限

仓库不是一篇文档。索引要分层：文件路径 + 符号（树解析）+ 文本块（函数/类）+ 可选 embedding。BM25 对标识符很强；dense 补自然语言 issue。构建增量：按 commit 更路径，删文件立刻从索引消失，否则助手会引用幽灵 API。

权限：用户只能检索他能 clone 的路径。跨私有仓库的「语义相似」是泄漏。索引键含 `repo_id + acl + commit`。多租户 SaaS 尤其不能把 A 公司的代码块打进 B 的上下文。存在性泄漏：无权限时不要用「检索为空 vs 有结果但拒绝」区分仓库在不在。

训练：默认私有代码不进权重。IDE 遥测要同意和脱敏。评测集别从客户仓库抽。补全若用仓库内邻接文件，仍是检索 ACL，不是「模型已经看过」。

## 补全延迟 vs agent

两条产品：

- 行内补全。 预算极紧：键入到建议出现。小模型或 speculative、FIM、只读当前文件 + 近邻窗口。前缀缓存打文件头和 import，见 `sys-prefix-cache`。p95 是几十到一百多毫秒量级的交互，不是对话那套首 token。错建议的代价是打断，宁可不弹。
- 仓库 agent。 读 issue、改多文件、跑测。SLO 是任务完成和误改，实际耗时可以秒到分钟。工具：读文件、搜、补丁、测试沙箱。沙箱无网、只读镜像、CPU 配额，见 `design-agent-harness`、`design-tool-prod`。写操作要 diff 确认。

不要用同一 70B 模型、同一批处理池伺候两种 SLO。补全走专用低延迟池；agent 走工具循环池。索引构建本身也是产品：增量按 commit、删文件立刻下线、标识符拼写上符号表和 BM25 往往比 embedding 更要紧。embedding 升级要双写，新旧向量不能混排，见 `design-prod-rag`。

失败：索引滞后导致建议已删 API；权限穿透；补全把密钥从邻接文件补出来；agent 改测试来「通过」而不是改产品代码。密钥扫描要在进上下文前做：`.env`、私钥、高熵串直接丢弃，不要靠模型「注意别泄漏」。

## SWE-bench 口径

SWE-bench：给定 issue 文本和代码库快照，系统交补丁，跑作者测试：fail-to-pass 必须过，pass-to-pass 不能回归。报 resolved 率要写：子集（Full / Lite / Verified）、是否 gold 补丁泄漏、是否用测试名提示、agent 步数和工具集、是否允许看测试文件。Verified 是人滤过的题面，数字不能和 Full 混报。

污染：公开 PR 和解法博客会进预训练，见 `align-eval-contam`。内部代码助手不要只刷 SWE-bench 当发版。私有「内部 issue → 补丁 → CI」才是产品集，口径仍要 fail-to-pass 定义清楚。

评测平台：冻结仓库镜像、测试命令、超时、随机性。和 `design-offline-eval` 同一套版本管理。人评看 diff 是否最小、是否改测试作弊。

指标：补全接受率要小心虚荣（乱接受）；加上回退率、编译失败、CI 红。Agent：resolved、步数、误改文件数、沙箱逃逸零容忍。内部评测用真实 PR 抽样，口径仍写 fail-to-pass，不要只报「程序员觉得有用」。

## 追问

- **为什么不把整个 monorepo 塞长上下文？** 权限、新鲜、p95、中间丢失，见 `design-long-doc`。索引 + 定点读文件更像工程师。
- **SWE-bench 高就能发 Copilot？** 不能。口径是公开 GitHub issue，不是你的 IDE 分布和延迟。
- **补全能用对话模型吗？** 能，但要用 FIM 训练和低延迟池。对话模板的套话在补全里是事故。
- **测试泄漏怎么办？** 产品上可以跑测；评测要声明是否可见。隐藏测试防改测试作弊。
- **多租户索引怎么隔离？** 键带 `repo_id` 和 ACL，查询先过滤再 ANN。向量碰撞也不能跨仓返回。
- **补全接受率当北极星？** 不行。加上回退、编译失败、事后删除。虚荣接受会鼓励啰嗦补全。

发布闸门：补全 p95、越权检索零、沙箱逃逸零、SWE-bench Verified 只作参考、内部 PR fail-to-pass。缺权限项不能发。索引滞后 SLA 单独报：文件删除后多少秒从补全消失。

IDE 插件和对话 agent 分版本号。补全模型升了、agent 提示没钉，会把对话套话打进行内建议。见 `design-prompt-mgmt`。
