---
id: baichuan-ragas-eval
section: fundamentals
order: 120
level: A
title: 百川智能：RAGAS 评估指标、流程和数据如何获取？
quick: >-
  RAGAS 从忠实度、答案相关性、上下文精确率和召回率几维拆开评 RAG，适合做检索到生成这条管线的回归；judge 会漂，要拿小批人工金标
  calibration，业务任务是否完成也要单独测。数据优先用带证据文档 ID
  的问答和线上会话抽样，尤其是用户纠正过的负例；流程是冻结索引和模型、跑检索和生成、存下 query / contexts /
  answer、分维分切片算分，再用人审样本 calibration。
tags:
  - Baichuan
  - RAGAS
  - RAG Evaluation
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: 'https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530'
    type: candidate-first-hand
  - title: RAGAS — Automated Evaluation of Retrieval Augmented Generation
    url: 'https://arxiv.org/abs/2309.15217'
    type: primary
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“ragas 评估指标 评估流程 数据如何获取”**

RAGAS 是把一次 RAG 调用拆成几维来评：答案对上下文是否忠实、答案和问题是否相关、检索到的上下文精确率和召回率。它适合当检索到生成这条管线的回归仪表，但它用的是 LLM-as-judge 和启发式，judge 自己会漂，所以要用小规模人工金标去 calibration（`fund-judge`），业务任务有没有完成也要单独测。RAGAS 分数不等于业务成功。

几维为什么要分开看？举两个情况：上下文召回高、忠实度低，说明检索对了、生成在胡编；忠实度高、相关性低，说明模型只敢复述无关段落。合成一个「RAGAS 总分」当唯一看板，就把这些都盖住了，所以至少四维分列，再按语言、表结构、是否多跳、是否长文档切片。比如表格问答要把单元格坐标当证据，拿整页 HTML 当证据就没法判忠实。同类的拆分思路见 `ali-rag-eval`、`jd-rag-accuracy-eval`，检索怎么组合见 `fund-rag`。

流程是这样：冻结索引和模型版本，对评测集跑检索和生成，存下 query / contexts / answer，算各维分数，按切片看，再把和人工不一致的 case 抽出来看。每次回归要留下索引哈希、embedding / 检索器版本、生成模型和 decoding 参数、$k$、chunk 策略、评测集版本，缺一项，下周分数动了就不知道是谁的功劳。改 prompt 时评测集冻结；改索引时生成配置冻结，交叉对照。人工 calibration 每周或者每两次大改抽一小批，算和 judge 的一致率，低于阈值就冻结自动分数、只看人审。calibration 集要和开发 prompt 隔离，免得「改完 prompt 再在 calibration 集上看起来更一致」。

数据从哪来？优先用已有的带引用文档问答、表格问答和线上会话抽样。线上日志里最值钱的是「用户改写了问题」或「点开的引用不对」这类负例，比让 GPT 再造一百条同质问答有用。没有金标时，可以让强模型生成、再人工改。每条至少要有 query、检索到的 contexts、生成的 answer 和可定位的证据文档 ID，最好还有任务成功标签；没有引用字段的会话，先补上证据文档 ID 再进评测，否则忠实度没有参照。最小的增量做法是从线上抽一周会话，补证据 ID 和「是否解决」标签，先别急着造一千条合成问答，合成题容易和教师同分布，judge 分数会虚高。表格、多跳、低资源语言必须单独成层，否则平均忠实度看着健康，真实用户全卡在表上。线上抽样还要注意 exposure bias，搜索点击不能直接当「上下文充分」，position bias 会让热门但无关的段落显得相关（`baichuan-search-vs-rec`）。

最后和业务成功一起报：工单有没有解决、引用有没有被点开、用户有没有再追问。RAGAS 涨了、工单没降，说明在优化 judge，产品没变好。常见的失败有三种：把会漂的 judge 当唯一 KPI；评测集和训练集文档重叠；只报平均 faithful，安全和多跳切片崩了看不见。

## 追问

**没有参考答案能评吗？**
忠实度可以相对 contexts 评；相关性最好还是有人标，或者用业务标签来 calibration。

**RAGAS 能替代人审吗？**
不能。它是回归仪表，定义由人审定义，judge 漂了，分数照样会很好看。

**上下文召回高、忠实度低，先改哪里？**
检索可能是对的，生成在编。先加引用约束或拒答，别急着换检索器。

**评测集能和训练文档重叠吗？**
不能按文档泄漏，重叠会让召回虚高，见 `data-contamination`。
