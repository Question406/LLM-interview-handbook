---
id: msft-copilot-agent
section: microsoft
order: 18
level: A
title: Microsoft：Copilot agent 模式，仓库权限和循环预算？
quick: >-
  Agent 模式会跨文件修改并运行命令，读写都要继承当前用户权限，再由宿主限制终端、网络和副作用。循环设置轮数、token、总耗时与重复失败上限，以 git
  和 CI 核实完成。Ask、Edit、Agent 按任务范围选择，并分别管理风险。
tags:
  - Microsoft
  - Copilot
  - Agent
  - Permissions
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Chat with GitHub Copilot in your IDE
    url: 'https://docs.github.com/en/copilot/how-tos/chat-with-copilot/chat-in-ide'
    type: primary
  - title: Copilot coding agent access management
    url: >-
      https://docs.github.com/en/copilot/concepts/agents/coding-agent/access-management
    type: primary
  - title: VS Code Copilot agents overview
    url: 'https://code.visualstudio.com/docs/copilot/agents/overview'
    type: primary
  - title: 'Data, Privacy, and Security for Microsoft 365 Copilot'
    url: >-
      https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy
    type: secondary
---

Copilot agent 要先有工具权限和循环预算，再让模型规划跨文件任务。比如模型说「测试已通过」，真正的完成依据仍应是 CI 或命令结果；如果它反复改同一个失败测试，宿主也应到预算就停。

公开文档中，IDE agent 会选择文件、生成 diff、建议命令，直到完成或被停止；云端 coding agent 在沙箱中建分支、提 PR，企业常由管理员显式开启。本卡讨论公开能力。证据与 ACL 延续 `msft-copilot-ground`：检索范围限定在当前身份可见集合。

## 读、写和执行分别授权

读代码、文件与符号时传用户 / PAT / GitHub App 权限，未授权的私有依赖、其他 org 的 secret 和 `.env` 不进入上下文。全仓库 embedding 可以有自己的索引策略，但检索必须先按身份裁剪，不能等生成后过滤。

改文件、`git push`、删分支和发评论需要单独控制。IDE 使用默认确认、跳过确认、Autopilot 等权限档位；云端 agent 通常只写它创建的分支。终端和网络也有限制：测试可以在授权环境运行，`curl | sh`、云元数据和生产网络默认不开放。

确认发生在工具运行时，native function 的 side-effect constraints 见 `msft-semantic-kernel`。多 agent 协作仍遵守同一规则，不能直接将 GroupChat 接到仓库写 API，见 `msft-autogen`。

## 到预算停下，并核实最终结果

反复修测试会同时消耗 TPM 与实际时间，见 `msft-azure-tpm`。宿主限制轮数、token 和耗时：

```python
def run_copilot_agent(step, *, max_rounds=12, max_tokens=80000, max_wall_s=600):
    used, t0 = 0, time.time()
    for r in range(max_rounds):
        if used >= max_tokens or time.time() - t0 > max_wall_s:
            return {"status": "budget", "round": r}
        out = step(r)
        used += out["tokens"]
        if out["done"] or out.get("needs_human"):
            return out
    return {"status": "max_round"}
```

还可加单轮最多改文件数、禁止路径和重复测试失败次数。Ledger / working set 保留当前任务文件，避免每轮复制全仓库，让 $T$ 增长并触发 lost-in-the-middle，见 `msft-long-context`。

评测分别看真实任务通过（CI）、越权读、重复 push、预算终止和 hallucination API。云端 PR 描述也要引用真实文件。Autopilot 权限应由企业设定，应用身份扫全租户代码或把模型自述当完成都会扩大风险；状态以 git 和 CI 为准。

## 追问

**Ask / Edit / Agent 怎么选？**
问答用 Ask，指定文件内修改用 Edit，跨文件任务再用 Agent，并按副作用范围配置确认。

**为什么企业要显式开启 coding agent？**
写仓库会产生副作用，管理员需要按仓库 opt-in，公开代码也不等于模型自动获得写权限。

**与 Semantic Kernel 有何关系？**
SK 管企业工具中间件，Copilot agent 管代码工作区，两者都要求身份向下传递。

**工具超时怎么处理？**
返回结构化错误并累计失败，超限交还人处理。不能把超时总结成测试通过。
