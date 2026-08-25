---
id: amazon-titan-eval
section: amazon
order: 9
level: A
title: Amazon：Bedrock/Titan 类应用怎么评，不能只报 BLEU？
quick: >-
  BLEU 只看 n-gram 重叠，改写对了、事实错了它仍高。应用要拆检索、接地、任务成功、安全和延迟。离线用标注加 LLM-as-judge，线上用客户行为和事故率。Titan
  还是 Claude，评的是应用契约，不是模型排行榜。
tags:
  - Amazon
  - Titan
  - Bedrock
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Evaluating RAG applications with Amazon Bedrock knowledge base evaluation
    url: https://aws.amazon.com/blogs/machine-learning/evaluating-rag-applications-with-amazon-bedrock-knowledge-base-evaluation/
    type: primary
  - title: New RAG evaluation and LLM-as-a-judge capabilities in Amazon Bedrock
    url: https://aws.amazon.com/blogs/aws/new-rag-evaluation-and-llm-as-a-judge-capabilities-in-amazon-bedrock/
    type: primary
  - title: Evaluate RAG responses with Amazon Bedrock, LlamaIndex and RAGAS
    url: https://aws.amazon.com/blogs/machine-learning/evaluate-rag-responses-with-amazon-bedrock-llamaindex-and-ragas/
    type: primary
---

Bedrock 应用、Nova / Titan 和内部助手岗都会问评测。AWS 自己的 Knowledge Base evaluation 写明：ROUGE / F1 会被字面相似骗过，意思可以完全不对。BLEU 同源，是机器翻译的 n-gram 精度，不是客服政策问答的指标。公开材料不是某次逐字真题。按 Amazon 口味：先契约，再数字；数字要能拦上线，见 `amazon-lp-ml`。

## BLEU 在这里测不到什么

BLEU / ROUGE 要一份参考译文。生成式应用常常没有唯一金句：同一条款可以有三种合法说法。模型换词复述，BLEU 低但客户满意；复制检索块再加一句幻觉，BLEU 可能还不低。开放问答经常没有参考答案，指标直接未定义。

所以面试先钉任务：

- **RAG / 政策助手。** 拆检索和生成。检索：Recall@$k$、命中金标条款、引用覆盖 / 引用精度（Bedrock 现成指标）。生成：忠实度（是否只能从源里来）、相关性、完整性、拒答是否该拒。源没有就该说没有，这和 `apple-siri-grounded`、`amazon-bedrock-rag` 同一契约。
- **工具 / Agent。** 参数是否合法、是否调对工具、任务成功（工单是否解了），不是句子漂亮。
- **分类 / 抽取（Titan 也常干这个）。** Precision / Recall / 校准，别用 BLEU。
- **安全。** 漏拦、误拦、PII 残留，和 `amazon-guardrails` 同一套 case，不要揉进「质量 0.82」。

Bedrock 的 LLM-as-a-judge 把正确性、有帮助、有害、拒答等打到 $0$–$1$ 并给理由。它快，但会偏：评委模型和被评模型同族会互相抬。人评仍要抽查，尤其是高风险域。RAGAS 一类 faithfulness / answer relevancy 可以当离线扫描，不能当唯一门禁。

## 一套能上线的报表

我会报四层，缺一层就说门禁不完整：

1. **检索层。** 标识符 query 和语义 query 切开，见 `amazon-kendra-hybrid`。标识符失败不是生成模型的锅。
2. **接地层。** 句子级能否对齐到块 id；对不上就删句。幻觉率按「错误且无引用」计，不要和文风分混在一起。Automated Reasoning 适合硬规则（退货窗口、限额），不适合开放闲聊。
3. **任务层。** Seller Support：一次解决、升级工单、错误引用过期条款。搜索式生成：是否帮用户落到可购买 ASIN。没有任务层，评测在自嗨。
4. **系统层。** TTFT / E2E 的 p99、限流、成本，见 `amazon-p99-stream`。质量涨 1 个点、p99 翻倍，Insist on the Highest Standards 不会放行。

线上：客服改写率、用户重问、点赞点踩、Guardrail 干预率、事故工单。A/B 预注册。不要上线后才决定「我们看 BLEU」。离线集要含失败回溯：上次幻觉、上次 PII、上次冷启动零结果，见 `amazon-cold-start`。Learn and Be Curious 是把生产失败写回 eval，不是换一个更大的 Titan。

Titan 和 Claude 换底座时，应用评测集不动。底座排行榜（MMLU、内部对话竞技场）只能解释「为什么换」，不能替代应用门禁。蒸馏双塔那类论文用相关性加线上 A/B，也不是 BLEU，见 `amazon-two-tower`。

人评协议写清楚：独立于生成模型的标注员、金标条款 id、允许的改写范围。两个评委 disagreement 高，先修指南再刷模型。LLM judge 的 prompt 和温度要版本化，否则这周分数和上周不可比。

一个具体形状：100 条政策问答，金标是条款 id 不是金句。检索报 Recall@5；生成报忠实度（人 + judge）和「错误引用过期条款」计数；安全报 PII 漏拦；系统报 TTFT p99。BLEU 可以当附录，不能当门禁。

离线和线上打架时，先信线上任务指标，再回头查离线集是不是过时、位置偏差或 judge 漂移。不要为了把 BLEU 刷高去改提示。

## 追问

- **完全没有金标怎么办？** 先做检索命中（有没有回到已知源）和忠实度（是否超出源）；任务层用线上代理指标。人评一小份校准 LLM judge，再放大。不要用 BLEU 假装有金标。
- **faithfulness 高就能量产？** 不够。可以忠实但拒答过度，或忠实但检索就错了——忠实于错误条款更危险。检索切片和任务成功必须同时过。
- **评测模型用不用 Titan？** 可以，但交叉用另一个厂的模型当 judge，抽人审。自家模型评自家输出，偏差要写进局限，不能藏。
- **和 Guardrails 评测怎么分工？** Guardrails 报漏拦 / 误拦；应用评测报接地和任务成功。两套 case 不要合成一个「安全分」，见 `amazon-guardrails`。
