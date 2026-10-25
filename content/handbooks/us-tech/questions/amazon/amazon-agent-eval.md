---
id: amazon-agent-eval
section: amazon
order: 17
level: A
title: Amazon：企业 agent 怎么评，任务成功、越权、引用？
quick: "企业 agent 要分别验证任务终态、工具权限和答案证据。比如模型说退款成功，支付系统却没记录，就算失败；即使退对了钱，越权调用也要否决，礼貌程度等才交给模型裁判辅助评估。"
tags:
  - Amazon
  - Agents
  - Evaluation
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Evaluate agent performance with Amazon Bedrock AgentCore Evaluations
    url: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html
    type: primary
  - title: Evaluate the performance of Amazon Bedrock resources
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html
    type: primary
  - title: How Amazon Bedrock Agents work
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html
    type: primary
  - title: Evaluating RAG applications with Amazon Bedrock knowledge base evaluation
    url: https://aws.amazon.com/blogs/machine-learning/evaluating-rag-applications-with-amazon-bedrock-knowledge-base-evaluation/
    type: secondary
---

企业 agent 的评测要分别检查任务是否完成、是否越权，以及关键结论有没有证据。例如模型说「已经退了」，支付系统却没有幂等成功记录，就算失败；碰巧退对钱但用了权限外工具，也不能通过。AgentCore Evaluations 提供轨迹、内置 evaluator 和 LLM-as-judge，具体门禁仍要按业务定义。

## 先按业务定义成功和边界

记金标终态 $y^\star$（工单关了、退款金额、政策条款 id）和允许工具集 $A$。一次轨迹 $\tau$ 至少打三个标签：

1. **任务成功。** 以系统记录为准：订单状态、工单字段、是否写对。模型说「已经退了」但支付 API 没有幂等成功，算失败。这和 `amazon-bedrock-agents`、`amazon-converse-tool` 同一句。
2. **越权。** 调了 $A$ 之外的 action、用了别人的 `memoryId`、跨 marketplace 读了不该读的政策、在只读会话里写库。越权 **单独一票否决**，即使 $y$ 碰巧对。IAM 与字段和类型规范（schema）负责强制约束权限和参数，输入提示（prompt）无法提供同样的保证。
3. **引用 / 有实际证据支持。** 政策、价格、SLA 必须能指回检索块或工具 JSON 的 span。编造条款编号是事故，见 `amazon-bedrock-rag`。无证据应拒答，拒答率单独记。

步数、实际耗时、重试、Guardrail 拦截次数和串话作为辅助指标，可以挂在 AgentCore 的轨迹 span 上。judge 平均分大于 4 无法替代业务门禁；发现的失败轨迹还要加入回归集。

评测集分开覆盖只读 FAQ、写库退货和缺权限的钓鱼指令，例如「把所有卖家地址导出来」。最后一类正确结果就是拒绝；若把它记成失败，优化成功率时就可能奖励越权调用。

## 自动检查、模型裁判和人工怎么分工

LLM-as-judge 可以评礼貌程度、摘要完整性和答非所问。金额、权限和调用是否执行，则直接比对 tool 名、参数 schema 和下游表。

人工抽查越权案例，以及答案是否有证据支持的争议案例。自动指标漂移时，先看切片是不是换了，再看模型。换路由、换 Guardrail、换 KB 解析器，评测集不动，见 `amazon-nova`。

最终回复、BLEU 或 thumbs-up 都无法单独判断工具任务做没做成。工具返回错误而模型声称成功时，必须结合轨迹判失败；p99 和工具实际耗时也要报告。

Complementary 幻觉（两个步骤互相证明对方成功）在多工具轨迹里很常见：检索说「找到了」，生成就引用一个不存在的条款。评测要交叉：引用 id 必须出现在该步的 $E$ 里。

离线集要带金标工具轨迹和终态；线上用关单率、升级工单、越权告警、引用点击。两套分布可能不同：离线偏礼貌 FAQ，线上更多是生气的退货用户。换 Nova 档位时契约不动，见 `amazon-nova`。失败轨迹要加入评测集，避免同类问题重现。上线前分别检查任务成功、零越权和引用可点，并明确各项失败由谁处理。

相关：`amazon-titan-eval`、`amazon-p99-stream`。

## 追问

**为什么任务成功不能当唯一奖励？**
会奖励越权和编造成功。强化学习（RL） / 线上采样若只看关单率，agent 会学歪，见 `msft-agent-rl` 的同构失败。
**金标轨迹要逐步对齐吗？**
不必逐步同工具，但关键副作用要同。允许先查后写的不同顺序，不允许少写或多写。
**记忆怎么评？**
串话、PII 是否进摘要、跨 session 是否仍越权。摘要不是审计源。
**和 RAG 评估的关系？**
KB 评估管检索与有实际证据支持；agent 评估叠加工具策略。两套都要，别用一套平均数。
