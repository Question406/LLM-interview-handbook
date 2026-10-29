---
id: amazon-titan-eval
section: amazon
order: 9
level: A
title: Amazon：Bedrock/Titan 类应用怎么评，不能只报 BLEU？
quick: >-
  Bedrock / Titan 应用要分别评检索、证据支持、任务成功、安全和延迟。BLEU 只看 n-gram
  重叠，既会低估正确改写，也可能漏掉事实错误。先用标注和 LLM judge 建 offline evaluation
  criteria，再用线上客户行为与事故验证，换模型时保持应用评测集不变。
tags:
  - Amazon
  - Titan
  - Bedrock
  - Evaluation
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Evaluating RAG applications with Amazon Bedrock knowledge base evaluation
    url: >-
      https://aws.amazon.com/blogs/machine-learning/evaluating-rag-applications-with-amazon-bedrock-knowledge-base-evaluation/
    type: primary
  - title: New RAG evaluation and LLM-as-a-judge capabilities in Amazon Bedrock
    url: >-
      https://aws.amazon.com/blogs/aws/new-rag-evaluation-and-llm-as-a-judge-capabilities-in-amazon-bedrock/
    type: primary
  - title: 'Evaluate RAG responses with Amazon Bedrock, LlamaIndex and RAGAS'
    url: >-
      https://aws.amazon.com/blogs/machine-learning/evaluate-rag-responses-with-amazon-bedrock-llamaindex-and-ragas/
    type: primary
---

## 可以这样回答

我会围绕任务是否正确完成来评测，把检索、证据支持、安全和延迟分别报告。BLEU 可以补充观察措辞相似度，但不能决定客服政策助手是否上线。比如复制大段正确条款再加一句 hallucination，n-gram 重叠仍可能很高；换一种合法说法，分数又可能很低。

BLEU 是机器翻译中的 n-gram 精度指标，BLEU / ROUGE 依赖参考文本，开放问答可能没有唯一参考。AWS 的 Knowledge Base evaluation 也提醒 ROUGE / F1 会被字面相似误导。先明确应用验收要求，再定指标和 acceptance checks，见 `amazon-lp-ml`。

## 技术备查

我会围绕任务是否正确完成来评测，把检索、证据支持、安全和延迟分别报告。BLEU 可以补充观察措辞相似度，但不能决定客服政策助手是否上线。比如复制大段正确条款再加一句 hallucination，n-gram 重叠仍可能很高；换一种合法说法，分数又可能很低。

BLEU 是机器翻译中的 n-gram 精度指标，BLEU / ROUGE 依赖参考文本，开放问答可能没有唯一参考。AWS 的 Knowledge Base evaluation 也提醒 ROUGE / F1 会被字面相似误导。先明确应用验收要求，再定指标和 acceptance checks，见 `amazon-lp-ml`。

## 指标跟着任务走

RAG / 政策助手先拆检索与生成。检索看 Recall@$k$、金标条款命中、引用覆盖和精度，Bedrock 提供相应指标；生成看忠实度、相关性、完整性和拒答是否合理。源里没有的信息应明确说明，相关契约见 `apple-siri-grounded`、`amazon-bedrock-rag`。

工具 / Agent 看参数合法、工具选择和工单是否解决。分类与抽取看 Precision / Recall / calibration。安全单列漏拦、误拦和 PII 残留，与 `amazon-guardrails` 共用 case，避免混成一个「质量 0.82」。

Bedrock 的 LLM-as-a-judge 可以对正确性、有帮助、有害和拒答给 $0$ 到 $1$ 分及理由，适合扩大离线检查规模。评委与被评模型同族可能互相抬分，高风险领域仍需人抽查。RAGAS 的 faithfulness / answer relevancy 可作扫描，也需要其他 acceptance checks 配合。

## 从检索一路检查到生产结果

先按标识符和语义 query 分组看召回，见 `amazon-kendra-hybrid`。再检查生成句子能否对齐块 id，对不上的删去。这里将 hallucination 按「错误且无引用」计数，并与文风分分开。Automated Reasoning 适合退货窗口、限额等硬规则，开放闲聊则不适用。

任务层看 Seller Support 的一次解决、升级工单和错误引用过期条款；搜索式生成看是否帮助用户找到可购买 ASIN。系统层报告 TTFT / E2E p99、限流和成本，见 `amazon-p99-stream`。质量涨 1 个点但 p99 翻倍，也可能不满足 Highest Standards。

一个报表示例是 100 条政策问答，金标保存条款 id，允许多种措辞。检索报 Recall@5，生成用人和 judge 评忠实度并数过期条款错误，安全报 PII 漏拦，系统报 TTFT p99。BLEU 可放附录。

上线 A/B 前预注册指标，再看客服改写率、重问、点赞点踩、Guardrail 干预和事故工单。上次 hallucination、PII 和冷启动零结果写回离线集，见 `amazon-cold-start`。这是 Learn and Be Curious 的具体做法。

Titan 换 Claude 时保留同一应用集。MMLU 或内部对话竞技场可以说明更换底座的理由，应用仍需单独验收。`amazon-two-tower` 的 distillation 检索也用相关性和线上 A/B，BLEU 无法替代它们。

人评协议要写清金标条款 id、允许改写范围，并由独立于生成模型的标注员评分。两个评委分歧大，先修指南；LLM judge 的 prompt 和温度也要版本化。离线与线上冲突时，优先检查线上任务结果，再查离线集过时、position bias 和 judge 漂移。

## 追问

**没有金标怎么开始？**
先查已知源的检索命中和忠实度，任务层用线上代理指标。做一小份人评 calibration judge，再扩大规模。

**faithfulness 高就能上线吗？**
还要看检索和任务成功。忠实复述错误条款、或 over-refusal，都可能伤害用户。

**能用 Titan 当 judge 吗？**
可以，但要用另一厂模型交叉验证并抽人审，把同族偏差写进局限。

**Guardrails 和应用评测怎么分？**
Guardrails 报漏拦与误拦，应用报证据支持和任务成功。两套 case 分别保留，见 `amazon-guardrails`。
