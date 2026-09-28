---
id: amazon-agent-eval
section: amazon
order: 17
level: A
title: Amazon：企业 agent 怎么评，任务成功、越权、引用？
quick: >-
  不要报 BLEU 和「看起来会办事」。门禁三件：任务是否在系统里完成、有没有调权限外的工具、关键命题能否指回证据。轨迹成功但越权是事故；引用漂亮但没写库也是失败。LLM-as-judge
  只能当辅指标。
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

Seller Support、内部运维助手、Bedrock Agents 岗会把评测问成所有权：谁证明它办成了，谁证明它没越权。公开层有模型 / RAG 评估，以及 AgentCore Evaluations（轨迹、内置 evaluator、LLM-as-judge）。底座仍是 `amazon-titan-eval` 的「别只报 BLEU」；本题把对象换成带工具的 agent。

## 三件事分开计，不要合成一个「智能分」

记金标终态 $y^\star$（工单关了、退款金额、政策条款 id）和允许工具集 $A$。一次轨迹 $\tau$ 至少打三个标签：

1. **任务成功。** 以系统记录为准：订单状态、工单字段、是否写对。模型说「已经退了」但支付 API 没有幂等成功，算失败。这和 `amazon-bedrock-agents`、`amazon-converse-tool` 同一句。
2. **越权。** 调了 $A$ 之外的 action、用了别人的 `memoryId`、跨 marketplace 读了不该读的政策、在只读会话里写库。越权 **单独一票否决**，即使 $y$ 碰巧对。IAM 和 schema 是硬边界，prompt 不是。
3. **引用 / 接地。** 政策、价格、SLA 必须能指回检索块或工具 JSON 的 span。编造条款编号是事故，见 `amazon-bedrock-rag`。无证据应拒答，拒答率单独记。

辅指标：步数、墙钟、重试、Guardrail 拦次数、串话。AgentCore 可以把这些挂到轨迹 span 上，但上线门禁不要改成「judge 平均分大于 4」。Learn and Be Curious 是把失败轨迹写回集，不是换更大 Nova。

切片：只读 FAQ、要写库的退货、缺权限的钓鱼指令（「把所有卖家地址导出来」）。第三类金标是 **拒绝**。把拒当成任务失败，模型会学会乱调工具刷成功率。

## Judge 和人评放哪

LLM-as-judge 适合：口头是否礼貌、摘要是否完整、是否答非所问。不适合：金额、权限、是否真的调用。这些用确定性检查：比对 tool 名、参数 schema、下游表。

人评抽越权和接地争议。自动指标漂移时，先看切片是不是换了，再看模型。换路由、换 Guardrail、换 KB 解析器，评测集不动，见 `amazon-nova`。

错法：用对话 BLEU；只评最终回复不看轨迹；把「工具返回错误但模型圆过去」标成成功；线上只盯 thumbs-up。p99 和工具墙钟仍要报，见 `amazon-p99-stream`。

Complementary 幻觉（两个步骤互相证明对方成功）在多工具轨迹里很常见：检索说「找到了」，生成就引用一个不存在的条款。评测要交叉：引用 id 必须出现在该步的 $E$ 里。

离线集要带金标工具轨迹和终态；线上用关单率、升级工单、越权告警、引用点击。两套分布会漂：线下全是礼貌 FAQ，线上全是生气的退货。换 Nova 档位时契约不动，见 `amazon-nova`。把失败轨迹写回评测，比换更大模型更像 Ownership。门禁三票分开过：任务成功、零越权、引用可点。合成一个「智能分」发版，Bar Raiser 会追问事故归属。

## 追问

- **为什么任务成功不能当唯一奖励？** 会奖励越权和编造成功。RL / 线上采样若只看关单率，agent 会学歪，见 `msft-agent-rl` 的同构失败。
- **金标轨迹要逐步对齐吗？** 不必逐步同工具，但关键副作用要同。允许先查后写的不同顺序，不允许少写或多写。
- **记忆怎么评？** 串话、PII 是否进摘要、跨 session 是否仍越权。摘要不是审计源。
- **和 RAG 评估的关系？** KB 评估管检索与接地；agent 评估叠加工具策略。两套都要，别用一套平均数。
