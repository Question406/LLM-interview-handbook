---
id: design-agent-budget
section: design
order: 22
level: A
title: 设计：Agent 的步数与美元预算，以及降级到无工具
quick: "预算由宿主循环执行，分别记录步数、工具次数、token、实际耗时和美元，任何一项耗尽就停止继续调用。调用前先估成本，耗尽后摘要已有结果、降级无工具或请求追加预算。验收同时看成功率、单位任务成本和降级后的幻觉率。"
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

## 题目描述

本题是手册归纳的系统设计练习，不是某家公司现场题面的逐字记录。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

设计 agent 的预算管理与降级机制。一个任务可能多次调用模型和外部工具，各操作消耗步数、调用次数、token、时间和费用。

### 需要满足的功能

- 为每个任务接受上限配置，并能报告已用和剩余预算。
- 在任务继续推进、并行调用、失败重试和用户取消时更新账目。
- 无法继续完成时，给出可解释的停止、降级或申请额外预算结果。

### 约束与交付物

限额具有实际执行效力，不能只作为模型提示。需要定义预计与实际费用、并行预留、部分失败和迟到计费的语义，且不能为节省预算跳过业务上必要的确认。

请给出需求边界、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

任务还剩 0.01 美元，而一次搜索的最低预计费用为 0.02 美元时，该搜索不能无提示地继续执行；最终应返回当前已完成内容和停止原因或可选替代路径。

## 解题思路与参考答案

Agent 的预算要放在宿主循环里硬性执行，每次调用前先判断剩余额度够不够。比如搜索已经超出剩余美元，应该直接进入降级路径；只在 prompt 里说“节省一点”，挡不住继续调用。这是 Microsoft Copilot、Anthropic 长工具循环和 OpenAI agent 产品的工程设计题型，公开博客强调预算放在循环外，不是某次现场逐字题。沙箱与确认见 `design-agent-harness`，成本门禁见 `design-eval-agent`。

## 在每步执行前后记账

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

## 预算耗尽后怎样结束任务

预算耗尽后的行为要事先写进产品契约：

1. 停 + 摘要。 已执行步骤、已引用证据、还缺什么，交给用户。禁止静默重试。
2. 无工具生成。 只用当前上下文和参数记忆，并口头标明「我没查实时数据」。有实际证据支持产品里这往往要拒答而不是猜，见 `apple-siri-grounded`。
3. 更便宜的只读路径。 缓存检索、小模型、缩短思考预算。不允许换成更贵的模型「再试一次」。思考预算泄漏见 `align-cot-leak`。
4. 请用户授权加预算。 确认框展示将增加的步数 / 美元，而不是藏在条款里。

降级策略要写进产品契约，并进评测：故意把预算打到极小，看是否还敢调支付。无工具成功率、超预算率、降级后的幻觉率是一等指标。平均步数往上走、任务成功不动，就是在烧美元刷 trace，和 `align-tool-rl` 的过程奖刷分同类。

每步剩余预算都要进入 trace，复盘时才能区分重复无效操作和上限设置不合理。前端流式告诉用户「还在检索，预算还剩几次」，可取消。取消要能杀掉进行中的只读调用。

还要覆盖预算失效的情况：超 token 后截断工具结果，可能导致模型凭空生成；超美元后换未审计工具，会绕开控制。多 agent 各自领取预算会把总开销放大，见 `align-agent-rl`；浏览器 agent 也不能在步数耗尽后继续盲点，见 `design-browser-agent`。

发版表加一列：P50/P95 USD 每任务、P95 步数、降级占比、降级后事故率。质量涨、成本涨一个数量级时，闸门应拦住。

## 追问

**为什么不让模型自己看余额？**
可以当提示，不能当执法。执法在 `charge` 抛错。
**无工具会不会幻觉？**
会。契约是声明不确定或拒答，不是用预训练补实时事实。
**预算按用户还是按会话？**
都要。会话防单次失控；用户日限额防刷。工具 ACL 另算。
**和确认框谁先？**
预算不够根本不要弹出不可逆确认。确认是权限，预算是资源。
