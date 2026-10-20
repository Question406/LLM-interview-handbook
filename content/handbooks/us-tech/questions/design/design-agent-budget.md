---
id: design-agent-budget
section: design
order: 22
level: A
title: 设计：Agent 的步数与美元预算，以及降级到无工具
quick: "硬顶比「请你节省」有用：步数、工具次数、token 数、实际耗时、美元分别记账，任一见底就停。超预算不是偷偷换更贵的模型续跑， 而是降级成无工具回答、摘要已做步骤、或请用户加预算。成功率和单位任务成本一起报。"
tags:
  - Agent
  - Anthropic
  - Microsoft
  - Cost
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
  - title: System Design in a Hurry
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

Microsoft Copilot、Anthropic 的长工具环、OpenAI 的 agent 产品都会问「谁来停」。公开工程博客强调循环在宿主、预算在循环外。不是某次现场逐字题。沙箱和确认框见 `design-agent-harness`；本题把记账、降级、发版指标写全。评测要把成本列进门禁，见 `design-eval-agent`。

## 五本账，一本见底就停

我会先问：每任务的美元上限、是否允许用户加购、只读与写入是否分开、超时谁背锅。然后在宿主里记账，不把「省着点」写进 system 输入提示（prompt） 当唯一控制。

```python
class AgentBudget:
    def __init__(self, max_steps, max_calls, max_tokens, max_ms, max_usd):
        self.left = dict(steps=max_steps, calls=max_calls,
                         tokens=max_tokens, ms=max_ms, usd=max_usd)

    def charge(self, **kw):
        for k, v in kw.items():
            self.left[k] -= v
            if not (self.left[k] >= 0):
                raise BudgetGone(k)
```

`usd` 按内部计价：输入/输出 token、工具目录价、浏览器分钟。面试说 USD 和单价表版本，不在题面里写货币符号。调用前能估的先估：要跑昂贵搜索而剩余美元不够，直接走降级，不要先打再超。写入工具还要预留确认失败的补偿成本。

步数和调用次数防死循环；token 防把整页 HTML 读进上下文；实际耗时防用户挂着；美元防「成功了但公司亏」。重复同一工具同一参数要单独熔断，不算「探索」。

免费档 / 付费档是不同预算档案，不是不同模型口号。难查询可以提高上限，但要用户可见。不要在面试里承诺某一个美元数字。

## 降级路径：无工具是合法出口

见底之后的合法动作：

1. 停 + 摘要。 已执行步骤、已引用证据、还缺什么，交给用户。禁止静默重试。
2. 无工具生成。 只用当前上下文和参数记忆，并口头标明「我没查实时数据」。有实际证据支持产品里这往往要拒答而不是猜，见 `apple-siri-grounded`。
3. 更便宜的只读路径。 缓存检索、小模型、缩短思考预算。不允许换成更贵的模型「再试一次」。思考预算泄漏见 `align-cot-leak`。
4. 请用户授权加预算。 确认框展示将增加的步数 / 美元，而不是藏在条款里。

降级策略要写进产品契约，并进评测：故意把预算打到极小，看是否还敢调支付。无工具成功率、超预算率、降级后的幻觉率是一等指标。平均步数往上走、任务成功不动，就是在烧美元刷 trace，和 `align-tool-rl` 的过程奖刷分同类。

追踪：每步剩余预算进 trace，事故才能复盘是重复无效操作还是上限设置不合理。前端流式告诉用户「还在检索，预算还剩几次」，可取消。取消要能杀掉进行中的只读调用。

失败模式：超 token 后截断工具结果导致模型凭空生成；超美元后改走未审计的开源工具；多 agent 每人一份预算等于乘起来，见 `align-agent-rl`；浏览器 agent 用步数耗尽当「我尽力了」然后乱点，见 `design-browser-agent`。

发版表加一列：P50/P95 USD 每任务、P95 步数、降级占比、降级后事故率。质量涨、成本涨一个数量级时，闸门应拦住。

## 追问

- **为什么不让模型自己看余额？** 可以当提示，不能当执法。执法在 `charge` 抛错。
- **无工具会不会幻觉？** 会。契约是声明不确定或拒答，不是用预训练补实时事实。
- **预算按用户还是按会话？** 都要。会话防单次失控；用户日限额防刷。工具 ACL 另算。
- **和确认框谁先？** 预算不够根本不要弹出不可逆确认。确认是权限，预算是资源。
