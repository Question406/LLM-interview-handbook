# 一亩三分地 ML 基础面试题：原帖核对与复习索引

2026-10-22 通过用户已登录的 Chrome 阅读。下列 12 篇原帖涉及 7 家公司；其中整理出 30 个基础练习点，并附上专题方向。它们不是 30 道新增正式题卡，也不是完整原题还原。最初采集时仅建立索引；后续已补为 142 张正式题卡，新增清单见 [Google 专项](google.md)。

题目用自己的话归纳，只以候选人正文为面试证据。站内 `problems/company/…` 汇总页用于找原帖，不把其 AI Insights、参考答案或自行扩写的追问计为实际考题。公司、轮次和时间均为发帖者自述，未获公司确认；不据此推断题目频率。日期列是发帖日期，可能晚于面试日期。没有回帖解锁或复制受限帖子全文。

## 原帖来源

| 编号 | 公司／帖子 | 发帖日期 | 核实到的内容与范围 |
| --- | --- | --- | --- |
| S1 | [Capital One MLE VO过经](https://www.1point3acres.com/interview/thread/1155534) | 2025-11-21 | Set A 基础概念、项目；Set B 部署、监控、50ms 延迟要求。正文可读。 |
| S2 | [Linkedin DS Intern面经](https://www.1point3acres.com/interview/thread/1171137) | 2026-04-01 | LR 梯度、反向传播、mini-batch 伪代码、Adam。标题为 DS Intern，岗位标签为机器学习；保留这一差异。 |
| S3 | [买它超级智能挂经](https://www.1point3acres.com/interview/thread/1181687) | 2026-06-30 | 优化器、scaling law、K-means、GMM；只披露主题，没有具体子问题。另有 attention coding。 |
| S4 | [宏迪昂赛](https://www.1point3acres.com/interview/thread/1164026) | 2026-02-04 | 给 x、y 建模，看包含两个分布的图，最后问 cold start；原图与具体追问未披露。 |
| S5 | [红笛老年MLE店面](https://www.1point3acres.com/interview/thread/1173459) | 2026-04-17 | Notebook 现场 EDA、CTR 建模；提及 LR、SVM、RF、Boosting 比较，实际做到 LR 和 XGBoost。 |
| S6 | [买他 RDS](https://www.1point3acres.com/interview/thread/854261) | 2022-02-20 | 信用卡欺诈分类，LR 与线性回归、系数含义、检验、分类与评价。公司来自标题俗称，正文未给正式公司名；这是旧帖。 |
| S7 | [Voleon Data Scientist tech Interview](https://www.1point3acres.com/interview/thread/945716) | 2022-11-14 | Pandas、回归系数分析、显示为 0 的 p 值、bootstrap 与总体期望。原文只写 LR，不能确定是线性还是逻辑回归；这是旧帖。 |
| S8 | [门冲 MLE 全套](https://www.1point3acres.com/interview/thread/1169615) | 2026-03-21 | 饭店推荐，同时提高 CVR、降低配送时间；长短期特征处理。候选人的双 head 想法不是已确认正确答案。 |
| S9 | [DD ML秒跪经](https://www.1point3acres.com/interview/thread/1155359) | 2025-11-20 | Knowledge 轮问了很多 A/B testing，只确认主题，未披露具体题干。 |
| S10 | [Google 26NG SDE AI/ML R1面经](https://www.1point3acres.com/interview/thread/1162811) | 2026-01-27 | LLM 微调方式及优缺点、AE/VAE/VQ-VAE；属于生成模型专题。 |
| S11 | [Google MLE L5 挂经](https://www.1point3acres.com/interview/thread/1164473) | 2026-02-08 | NLP track 的 tokenization 比较、用 LLM 做推荐的 mini-case。 |
| S12 | [Google L4 AI/ML四轮全套面经，罕见coding题](https://www.1point3acres.com/interview/thread/1175462) | 2026-05-03 | Agent 表现不佳的分析、拍叶子识别类别的 retrieval + ranking 设计。 |

## 30 个基础练习点

下表把已披露问题改写为复习提示。标作“主题”的条目只确认考过该方向；具体练法由本手册补充。题卡链接指向现有答案，标作“部分覆盖”的地方仍需补题，不能把相关卡当成已经回答了完整场景。

| # | 练习提示 | 原帖 | 现有答案／缺口 |
| ---: | --- | --- | --- |
| 1 | 解释 bias–variance tradeoff。 | S1 | [偏差与方差](../../handbooks/ml-101/questions/generalization/ml101-bias-variance.md) |
| 2 | parameter 与 hyperparameter 有何区别？ | S1 | [超参数搜索](../../handbooks/ml-101/questions/diagnosis/ml101-hyperparameter-search.md)部分覆盖；值得补独立短答。 |
| 3 | batch inference 与 real-time inference 有什么区别？ | S1 | 缺独立题；勿与 batch gradient descent 混淆。 |
| 4 | 训练数据量太大，怎么处理？ | S1 | 缺完整场景题；应先区分内存、吞吐、存储和计算瓶颈。 |
| 5 | 什么是特征工程，为什么重要？ | S1 | [特征交互](../../handbooks/ml-101/questions/data/ml101-feature-interactions.md)、[类别编码](../../handbooks/ml-101/questions/data/ml101-categorical-encoding.md)部分覆盖。 |
| 6 | 从头到尾讲一次 ML lifecycle。 | S1 | 缺独立端到端流程题。 |
| 7 | 用自己做过的项目串起端到端过程。 | S1 | 缺项目口述练习模板；须使用自己的经历。 |
| 8 | 你怎么部署一个 ML 模型？ | S1 | [训练与服务偏差](../../handbooks/ml-101/questions/diagnosis/ml101-train-serve-skew.md)部分覆盖。 |
| 9 | 上线以后，怎么监控模型？ | S1 | [数据集漂移](../../handbooks/ml-101/questions/diagnosis/ml101-dataset-shift.md)、[延迟标签](../../handbooks/ml-101/questions/diagnosis/ml101-delayed-labels.md)部分覆盖。 |
| 10 | 欺诈模型经 API 提供服务，达不到小于 50ms 的要求，怎么办？ | S1 | 缺延迟排查场景题。原帖未规定 p50/p95/p99，练习时应先澄清。 |
| 11 | 解释逻辑回归及其 gradient descent。 | S2 | [逻辑回归](../../handbooks/ml-101/questions/linear-models/ml101-logistic-regression.md)、[梯度下降](../../handbooks/ml-101/questions/optimization/ml101-gradient-descent.md)；应补现场推导与实现练习。 |
| 12 | 用数学公式写出神经网络反向传播。 | S2 | [反向传播](../../handbooks/ml-101/questions/neural-networks/ml101-backprop.md) |
| 13 | 写 mini-batch gradient descent 伪代码。 | S2 | [SGD 与 mini-batch](../../handbooks/ml-101/questions/optimization/ml101-sgd-minibatch.md)；应补动手写循环的练习。 |
| 14 | Adam 由哪些部分构成？ | S2、S3（优化器主题） | [Momentum 与 Adam](../../handbooks/ml-101/questions/optimization/ml101-momentum-adam.md) |
| 15 | Adam 为什么利用平方梯度调整更新尺度？ | S2 | 同上。原帖措辞不严谨：Adam 分母是校正后二阶矩的平方根加 epsilon，不是直接除以梯度平方；不沿用原帖误述。 |
| 16 | 解释 scaling law。（主题） | S3 | 超出当前基础题册；待补模型／数据／计算量的权衡练习。 |
| 17 | 解释 K-means。（主题） | S3 | [K-means](../../handbooks/ml-101/questions/unsupervised/ml101-kmeans.md) |
| 18 | 解释 GMM。（主题） | S3 | [GMM 与 EM](../../handbooks/ml-101/questions/unsupervised/ml101-gmm-em.md) |
| 19 | 给一个 x 和一个 y，你怎么建模？ | S4 | [分类与回归](../../handbooks/ml-101/questions/generalization/ml101-classification-regression.md)、[模型选择](../../handbooks/ml-101/questions/diagnosis/ml101-model-choice.md) |
| 20 | 面对两种分布的图，怎么解释并用于建模？ | S4 | 缺看图口试。原图未披露，不能声称原帖明确问过 Bayes error、分布重叠或某个阈值公式。 |
| 21 | 怎样处理 cold start？（主题） | S4 | 缺新用户／新物品冷启动基础题。 |
| 22 | 对帖子数据做 EDA、训练 CTR 模型，并比较 LR／SVM／RF／Boosting。 | S5 | [模型选择](../../handbooks/ml-101/questions/diagnosis/ml101-model-choice.md)、[SVM 与 LR](../../handbooks/ml-101/questions/classical-models/ml101-svm-logistic.md)、[随机森林](../../handbooks/ml-101/questions/ensemble/ml101-random-forest.md)、[XGBoost](../../handbooks/ml-101/questions/ensemble/ml101-xgboost.md)；缺完整 notebook 练习。 |
| 23 | 逻辑回归与线性回归有什么区别？ | S6 | [逻辑回归](../../handbooks/ml-101/questions/linear-models/ml101-logistic-regression.md)、[线性回归](../../handbooks/ml-101/questions/linear-models/ml101-linear-regression.md) |
| 24 | 逻辑回归中系数等于 0.1，是什么意思？ | S6 | [逻辑回归](../../handbooks/ml-101/questions/linear-models/ml101-logistic-regression.md)；要解释 log-odds，不能说概率固定增加 0.1。 |
| 25 | 给出一个假设检验的统计量，能得出什么结论？ | S6 | [假设检验](../../handbooks/ml-101/questions/probability/ml101-hypothesis-test.md)；原帖未给自由度、假设或具体值。 |
| 26 | 拿到逻辑回归输出后，怎么分配类别？ | S6 | [阈值选择](../../handbooks/ml-101/questions/metrics/ml101-threshold.md) |
| 27 | 信用卡欺诈检测应该选什么评价指标？ | S6 | [类别不平衡](../../handbooks/ml-101/questions/metrics/ml101-imbalance.md)、[业务指标](../../handbooks/ml-101/questions/metrics/ml101-business-metrics.md)；不要把 F1 或 recall 当成所有业务下的唯一答案。 |
| 28 | 统计软件显示 p-value 为 0，合理吗，怎么处理？ | S7 | [假设检验](../../handbooks/ml-101/questions/probability/ml101-hypothesis-test.md)部分覆盖；值得补数值精度／显示截断的解释。 |
| 29 | bootstrap 与总体期望是什么关系？（主题） | S7 | [Bootstrap](../../handbooks/ml-101/questions/probability/ml101-bootstrap.md)；原帖未给完整 expectation 题，不能还原具体计算。 |
| 30 | 饭店排序希望提高 CVR，又降低配送时间，怎么设目标？ | S8 | [业务指标](../../handbooks/ml-101/questions/metrics/ml101-business-metrics.md)部分覆盖；缺多目标建模场景题。 |

## 额外方向与证据边界

- **A/B testing**：S9 确认知识轮考这个方向，但没有披露显著性、样本量等子问题。先复习现有 [A/B testing](../../handbooks/ml-101/questions/probability/ml101-ab-testing.md)，不把其全部追问标成 DoorDash 真题。
- **特征服务**：S8 明确问长短期特征的不同处理及工具／数据库选择。可在生命周期题后练；这部分偏 ML engineering。
- **生成模型**：S10 明确提到微调方法及优缺点、AE／VAE／VQ-VAE；属于 ML 基础向生成模型的延伸，当前题册仍没有完整覆盖。
- **NLP 与应用设计**：S11 的 tokenization 比较和 LLM 推荐，S12 的 agent 排查、叶子识别 retrieval + ranking，适合按目标岗位补充；不宜都算成通用 ML 101。
- **原帖与站内汇总的差别**：S4 只说“两个分布”，站内题解进一步讨论重叠、Bayes error、成本阈值等。这些可以另写为手册重构练习，但本次不把它们列成原帖证实的具体追问。

## 建议的练法

Google 专项补充见 [Google ML 基础面试路线与原帖证据](google.md)：另列四次补充检索的来源、正式新增题卡和复习路线，不重复计入上面的 12 篇。

先练 1、11–15、17–18、23–27：定义说清楚后，能写公式、解释变量，再做一个小数值例子。然后用 19–22、30 练从数据和业务目标做选择。最后串起 3–10，练部署、监控、延迟和自己的项目。

优先补题的缺口是：参数与超参数、批量与实时推断、大数据训练、ML 生命周期与项目口述、API 延迟排查、冷启动、EDA 到 CTR 建模、多目标排序。现有题卡的 `realInterview: false` 没有批量修改；此文件提供来源对应关系，不把整篇教学答案及其全部追问自动升级为公司真题。
