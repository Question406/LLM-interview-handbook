---
id: msft-copilot-agent
section: microsoft
order: 18
level: A
title: Microsoft：Copilot agent 模式，仓库权限和循环预算？
quick: "Agent 会自己选文件、改代码、跑命令。权限必须是当前用户 ACL，不能先搜全仓库再过滤。循环要限制轮数、token 用量和总耗时和写操作确认。Ask / Edit / Agent 不是同一个风险面。"
tags:
  - Microsoft
  - Copilot
  - Agent
  - Permissions
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Chat with GitHub Copilot in your IDE
    url: https://docs.github.com/en/copilot/how-tos/chat-with-copilot/chat-in-ide
    type: primary
  - title: Copilot coding agent access management
    url: https://docs.github.com/en/copilot/concepts/agents/coding-agent/access-management
    type: primary
  - title: VS Code Copilot agents overview
    url: https://code.visualstudio.com/docs/copilot/agents/overview
    type: primary
  - title: Data, Privacy, and Security for Microsoft 365 Copilot
    url: https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy
    type: secondary
---

GitHub / VS Code / M365 岗把 Copilot 从「补全」问到「自己改仓库」。公开文档：IDE agent 模式会选文件、出 diff、建议终端命令，直到任务完成或你停；云端 coding agent 在沙箱里开分支、提 PR。企业默认常关，要管理员打开。有实际证据支持和 ACL 仍是 `msft-copilot-ground` 那条：检索集合不能大于当前用户可见集。不是逐字真题。

## 权限先于聪明

我会把身份画在工具前面：

1. **读。** 代码检索、打开文件、搜符号，必须带用户 / PAT / GitHub App 的仓库权限。私有依赖、另一个 org 的 secret、`.env` 不在授权里就不能进上下文。先全库 embedding 再事后过滤，是泄漏窗口。
2. **写。** 改文件、`git push`、删分支、发评论。IDE 里用权限档位（默认确认 / 跳过确认 / Autopilot）。云端 agent 通常只写它创建的分支，而不是默认分支。
3. **终端 / 网络。** 跑测试可以；`curl | sh`、读云元数据、出网打生产，默认否。沙箱不是「模型保证安全」。

工具边界和 `msft-semantic-kernel` 同一句：原生函数有副作用，确认在运行时，不在 system 输入提示（prompt）。多 agent 编排见 `msft-autogen`，不要把 GroupChat 直接接仓库写 API。

## 循环预算是宿主代码

Agent 失败典型是停不下来：修测试 → 再修 → 再修，TPM 和实际耗时炸，见 `msft-azure-tpm`。预算：

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

再加：单轮最大改文件数、禁止的路径、测试失败重复次数。上下文不要每轮粘全仓库，$T$ 线性涨会 lost-in-the-middle，见 `msft-long-context`。Ledger / working set 只留当前任务文件。

评测：任务是否真的绿（CI，不是模型说绿）、越权读、重复 push、预算终止率、幻觉 API。不要报「diff 看起来像人写的」。云端 agent 还要看 PR 描述是否引用了真实文件。

常见误区是：Autopilot 当默认给企业；用应用身份扫租户代码；把 Ask 模式的引用契约丢了：agent 更会编「我已经改了」。状态以 git 和 CI 为准。

## 追问

- **Ask / Edit / Agent 怎么选？** 问答用 Ask；指定文件内改用 Edit；跨文件任务才 Agent。能力越大，确认越硬。
- **为什么企业默认关 coding agent？** 写仓库是副作用。管理员按仓库 opt-in，不是模型自己判断「这是开源所以可以」。
- **和 Semantic Kernel 插件？** SK 管企业工具中间件；Copilot agent 管代码工作区。权限模型都是身份向下传。
- **循环里工具失败？** 结构化错误回模型，计失败次数，超限交还人。不要把超时总结成「测试已经过了」。
