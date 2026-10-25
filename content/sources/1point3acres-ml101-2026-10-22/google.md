# Google ML 基础面试补充

2026-10-22 继续通过用户已登录的 Chrome 阅读 Google 原帖。首次专项核对 9 篇，第二次再核对 6 篇，第三次核对 5 篇 Google 与 1 篇 X 项目报告；第四次查阅 10 篇，其中 8 篇 Google、1 篇 X、1 篇公司归属有冲突。另引用最初综合采集时已读的 3 篇。以下是备考优先级，不是题目频率统计，也不意味着每个岗位使用同一题库。原帖日期是发帖日期，轮次与岗位来自候选人自述。

## 已补为正式题卡

ML 101 当前共 142 题。面经采集后分两批新增的 12 题如下，均附可独立口述的短答、完整解释、例子和追问；代码题有完整实现。`realInterview: true` 表示有候选人报告支持该选题，不表示代码接口、例子与全部追问都是公司原题。

| 题卡 | 面经依据 | 补充范围 |
| --- | --- | --- |
| [KDE](../../handbooks/ml-101/questions/classical-models/ml101-kde.md) | 1116207 | 密度、带宽、先验与分类的教学解释。 |
| [最近邻与类别均值](../../handbooks/ml-101/questions/classical-models/ml101-neighbor-centroid.md) | 1116207 | 自定数值例子、模型假设及复杂度比较。 |
| [KNN 实现](../../handbooks/ml-101/questions/classical-models/ml101-knn-implementation.md) | 1116207 | 手册约定接口、平票、异常规则；标准库参考实现。 |
| [Bigram 预测](../../handbooks/ml-101/questions/probability/ml101-bigram-prediction.md) | 1116207 | 手册约定句界、词序平票、未知上下文；标准库参考实现。 |
| [无现成标签的查询分类](../../handbooks/ml-101/questions/data/ml101-no-label-classifier.md) | 836854 | 标注、弱监督、独立评估的重构方案。 |
| [半监督 GMM](../../handbooks/ml-101/questions/unsupervised/ml101-semisupervised-gmm.md) | 786697 | 固定表示、每类一个高斯的重构推导，非原帖确认的唯一解。 |
| [K-means 实现](../../handbooks/ml-101/questions/unsupervised/ml101-kmeans-implementation.md) | 824942 | NumPy 完整实现，初始化、空簇、停止、目标与复杂度；边界为手册约定。 |
| [N-gram 训练与生成](../../handbooks/ml-101/questions/probability/ml101-ngram-generation.md) | 1094501 | 句界、采样、上下文回退的重构实现，不冒称原帖规定了这些规则。 |
| [WordPiece 编码](../../handbooks/ml-101/questions/data/ml101-wordpiece-implementation.md) | 894226 | 固定词表的最长匹配与失败语义；原帖只确认 WordPiece 实现主题。 |
| [EM 一轮手算与实现](../../handbooks/ml-101/questions/unsupervised/ml101-em-worked-step.md) | 894226 | 一维 GMM 责任度、M 步、稳定性与似然；题目数据与代码为教学补充。 |
| [约 2000 类文本标注](../../handbooks/ml-101/questions/data/ml101-many-class-labeling.md) | 894226 | 明确单标签与拒识的重构场景，评价候选覆盖、分类与人工成本。 |
| [手写两层网络 backprop](../../handbooks/ml-101/questions/neural-networks/ml101-mlp-backprop-implementation.md) | 1166705 | 原帖确认白板前反向、loss、更新；ReLU 网络、NumPy 接口及梯度检查为重构练习。 |

运行 `python3 scripts/check-ml101-practice.py` 会直接提取题卡里的 Python 代码执行，需要 NumPy。39 项测试覆盖平票、异常、句界、采样分布、EM 似然、K-means 目标，以及两层网络所有参数与输入坐标的有限差分梯度检查。原先 120 道通用题的 `realInterview` 和公司标签保持不变。本文件同时保留已覆盖题目与尚待扩充的来源线索。

## 先练通用基础：能解释，也能写出来

[Google 26ng SWE PhD AI/ML 过经 + TL](https://www.1point3acres.com/interview/thread/1166705)（2026-02-27）明确列出以下方向。候选人提到边讲边写公式、画图，并具体披露 L1 稀疏性与反向传播的追问。

| 原帖证实的问题／主题 | 对应题卡 | 本手册建议的练法（不是额外真题证据） |
| --- | --- | --- |
| Bias–Variance Tradeoff | [偏差与方差](../../handbooks/ml-101/questions/generalization/ml101-bias-variance.md) | 解释训练误差与验证误差的不同表现，再给一个模型容量的例子。 |
| Logistic Regression | [逻辑回归](../../handbooks/ml-101/questions/linear-models/ml101-logistic-regression.md) | 写出概率模型、损失和梯度，解释系数与决策边界。 |
| Gradient Descent | [梯度下降](../../handbooks/ml-101/questions/optimization/ml101-gradient-descent.md)、[mini-batch](../../handbooks/ml-101/questions/optimization/ml101-sgd-minibatch.md) | 写一次更新；比较全量与小批量计算。原帖未指定优化器变体。 |
| Cross-Entropy | [交叉熵](../../handbooks/ml-101/questions/linear-models/ml101-cross-entropy.md) | 从似然解释损失，再练 sigmoid／softmax 与交叉熵的梯度。原帖只确认交叉熵主题，未披露这份具体推导题干。 |
| L1 与 L2 的区别 | [L1／L2](../../handbooks/ml-101/questions/generalization/ml101-l1-l2.md) | 同时解释目标函数与约束形式。 |
| 为什么 L1 产生稀疏性？画约束形状，从几何角度解释零系数 | 同上 | 画二维菱形、圆和损失等高线；避免说成 L1 保证所有问题都得到零系数。这个几何追问是原帖明确披露的。 |
| Forward／Backward Propagation，loss、链式法则与参数更新 | [反向传播](../../handbooks/ml-101/questions/neural-networks/ml101-backprop.md) | 用一个小网络写清前向值、loss、局部梯度、参数梯度及更新，检查维度。原帖明确要求说明完整计算流程。 |

这是一篇细节较充分的直接报告，不能据单帖把所有主题标成 Google 高频。现有 ML 101 已覆盖这些主要教学答案，因此以补充 Google 面经证据与练习路线为主，避免重复建卡。

## 推荐／搜广推方向

[狗 mle recsys l4 全套过经](https://www.1point3acres.com/interview/thread/1170627)（2026-03-28）明确披露 cold start、如何使用各种 feature 的问答。它没有列出完整算法清单，不把作者回答里举的 content-based embedding、TIGER 自动变成面试官指定题。

建议额外练三组问题：

1. 新用户和新物品分别缺什么信息？有哪些可用的内容、上下文和热门兜底信号？这一细分是手册练法，原帖只确认 cold start。
2. 一个特征怎样从可获取、预测时点、泄漏风险、线上延迟和增量收益判断是否适用？对照 [数据泄漏](../../handbooks/ml-101/questions/data/ml101-data-leakage.md)、[特征选择](../../handbooks/ml-101/questions/data/ml101-feature-selection.md)、[训练服务偏差](../../handbooks/ml-101/questions/diagnosis/ml101-train-serve-skew.md)。这些检查维度是备考扩展。
3. 如何设计商品或视频推荐？[Google MLE虚拟表演](https://www.1point3acres.com/interview/thread/1177712)（2026-05-22）明确披露推荐系统设计，但没有具体子问题。可以据此练 retrieval、ranking、标签、评价与部署，不能声称这些子题都在原帖出现。

上一轮的 [Google L4 AI/ML 面经](https://www.1point3acres.com/interview/thread/1175462)（2026-05-03）还明确提到拍照识别叶子类别的 retrieval + ranking；它是应用设计题，不等同于分类算法定义题。

## LLM／概率模型／RE 方向

[Google RE 面经](https://www.1point3acres.com/interview/thread/1187652)（2026-08-27）明确披露下列问题，并强调解释定义、在 LLM 中的用途及原因。发帖者称岗位偏 RE、LLM，不能推广到所有 MLE。

| 原帖披露内容 | 现有基础覆盖／缺口 |
| --- | --- |
| KL divergence 是什么，如何及为何使用？ | [熵与 KL](../../handbooks/ml-101/questions/probability/ml101-entropy-kl.md)覆盖基础；LLM 使用场景需专题练习。 |
| Perplexity 是什么，如何及为何使用？ | [交叉熵](../../handbooks/ml-101/questions/linear-models/ml101-cross-entropy.md)提供前置；值得补独立题，尤其说明 tokenizer 和评测数据对比较的影响。 |
| Importance sampling 是什么，如何及为何使用？ | 当前 ML 101 缺独立题；值得补权重、支持集与方差的基础练习。 |
| VAE、ELBO；为什么加入 KL？ | 当前 ML 101 缺完整生成模型题。 |
| Reparameterization trick，为什么这样做？ | 当前 ML 101 缺独立推导。 |
| GRPO、pipeline parallelism | 只披露主题，属于后训练／系统专题。 |
| 后训练方法分别针对什么问题、什么阶段？ | 后训练专题，不能只背名称。 |
| Reward hacking 有哪些表现，如何防止？ | 需能给具体失效例子并解释检测与改进。 |

另一篇 [L4 过经](https://www.1point3acres.com/interview/thread/1181435)（2026-06-26）也披露 post-training、fine-tuning、prompt engineering、基础 Transformer，只有主题，没有具体子问。上一轮已核实的 [Google NG R1](https://www.1point3acres.com/interview/thread/1162811)（2026-01-27）明确问微调方式及优缺点、AE／VAE／VQ-VAE；[Google L5 NLP](https://www.1point3acres.com/interview/thread/1164473)（2026-02-08）明确问 tokenization 方法比较和 LLM 推荐的 mini-case。这些报告支持按所选方向准备，不能给出可靠的出现频率。

[Google MLE虚拟表演](https://www.1point3acres.com/interview/thread/1177712)另外披露 Transformer + SwiGLU 实现，包括 MHA 与 gate；偏 ML coding，不能用口述八股练习替代。

## 项目同样需要准备

[Google L4 AI/ML R1+时间线](https://www.1point3acres.com/interview/thread/1177561)（2026-05-21）明确说没有问 ML breadth，问题全部围绕简历；最后问研究项目能否用于 Google 产品、怎么用。[Google L4 SWE AI/ML全套过经](https://www.1point3acres.com/interview/thread/1175184)（2026-04-30）选择 Deep Learning／CNN，但实际更接近项目讨论与 ML 设计，没有披露具体 CNN 八股。

因此建议用真实项目练：为什么选择这个模型、为什么没选替代方案、指标与数据怎么确定、最差的样本或切片是什么、如何应用到一个产品。这是从报告归纳的备考提纲，不是五道逐字还原的 Google 原题。

## 本轮读取但未扩写成题目的报告

- [PhD SWE AI/ML 26 Start onsite面经](https://www.1point3acres.com/interview/thread/1188057)（2026-08-31）：只确认 ML 问题与面试官背景有关，没有具体 ML 题干。
- [狗家面筋](https://www.1point3acres.com/interview/thread/1189302)（2026-09-12）：只确认 AI/ML 基础与简历、推荐系统设计，不足以支持新增具体八股。

这两篇与上述 7 篇新读原帖合计为本轮 9 篇。上一轮的 3 篇引用不重复计入。所有技术扩展都作为练习建议，未批量修改现有题卡的公司标签或 `realInterview`。

## 第二次补充：传统分类与实际决策

同日另查 6 篇原帖。下面增加的是具体练习点；同一次面试的连贯追问分行列出，不能把行数当成独立面试题数或出现频率。

| 编号 | 原帖与发帖日期 | 已确认范围 |
| --- | --- | --- |
| G1 | [Google L5 MLE VO面经](https://www.1point3acres.com/interview/thread/1116207)，2025-03-06 | 一维分类，nearest neighbor、mean-based clustering、高斯核密度方法比较，KNN 实现；另有 bigram 词预测。 |
| G2 | [骨骼电面](https://www.1point3acres.com/interview/thread/1161213)，2026-01-13 | 欺诈检测系统设计，cold start 和类别不平衡；未披露具体处理方法。 |
| G3 | [Google MLE面试凉经](https://www.1point3acres.com/interview/thread/1157141)，2025-12-07 | 实时推荐，冷启动、监控与迭代，以及明确的 latency／accuracy 权衡。作者反思中提到 cache／近线 serving，不能将其当成面试官指定答案。 |
| G4 | [狗家MLE挂经](https://www.1point3acres.com/interview/thread/1159435)，2025-12-28 | 大规模短视频模糊去重：规模、高并发、误判申诉后的人工校准、embedding 维度与延迟量化。另有短期 A/B 收益与长期体验冲突的行为场景。 |
| G5 | [Google ML Design](https://www.1point3acres.com/interview/thread/1150617)，2025-10-18 | 违规内容检测并采取行动，面试官关心 LLM 成本与便宜模型的权衡。 |
| G6 | [Google MLE L4 面经](https://www.1point3acres.com/interview/thread/1095441)，2024-11-02 | ML 轮只披露简历项目讨论，未提供新 ML 题干；不据此扩写八股。 |

### 新增复习提示

| # | 已披露题意／主题 | 来源 | 对应基础与练法 |
| ---: | --- | --- | --- |
| 1 | 给两组一维样本 A、B，怎样判断新值 X 属于哪一类？ | G1 | [模型选择](../../handbooks/ml-101/questions/diagnosis/ml101-model-choice.md)。先澄清目标和样本代表性；不要仅凭给定少量样本认定分布。 |
| 2 | 最近邻与按均值分类，各有什么优缺点？ | G1 | [KNN](../../handbooks/ml-101/questions/classical-models/ml101-knn.md)、[LDA／QDA](../../handbooks/ml-101/questions/classical-models/ml101-lda-qda.md)部分相关。均值方法不能自动等同 LDA，原帖未给协方差假设。 |
| 3 | 用 Gaussian kernel density 方法是否更合适？ | G1 | 已补 [KDE](../../handbooks/ml-101/questions/classical-models/ml101-kde.md)。带宽、密度估计到分类、类先验是教学扩展，原帖没有逐项披露这些追问。 |
| 4 | 实现 KNN。 | G1 | 已补 [KNN 实现](../../handbooks/ml-101/questions/classical-models/ml101-knn-implementation.md)；原帖未规定距离、k、平票或空输入规则，题卡明确约定这些细节。 |
| 5 | 用训练文本的 bigram frequency，提供输入词到最可能下一个词的 API。 | G1 | 已补 [Bigram 预测](../../handbooks/ml-101/questions/probability/ml101-bigram-prediction.md)。分词、未见词、平票规则是手册练习约定。 |
| 6 | 欺诈检测中怎样处理类别不平衡？ | G2 | [不平衡数据](../../handbooks/ml-101/questions/metrics/ml101-imbalance.md)。练习时比较重采样、加权、阈值与评价目标；这些方法不是原帖逐项披露的追问。 |
| 7 | 推荐系统中 latency 与 accuracy 怎么取舍？ | G3 | 缺完整性能权衡场景。建议测量不同方案的端到端延迟与质量，再说明业务约束；具体测量方案为手册练法。 |
| 8 | embedding 维度与系统 latency 的权衡，怎样建模并量化分析？ | G4 | [近似近邻](../../handbooks/ml-101/questions/classical-models/ml101-approx-neighbors.md)部分覆盖；可练质量、内存、检索吞吐与延迟的实测曲线。 |
| 9 | 去重误判后，博主申诉，如何设计 human-in-the-loop 校准？ | G4 | [错误分析](../../handbooks/ml-101/questions/diagnosis/ml101-error-analysis.md)部分覆盖；需补人工复核、反馈标签与评测样本选择的场景题。 |
| 10 | 产品规模很大且高并发时，怎样快速筛选相似视频？ | G4 | 原帖候选人回答特征压缩、quantization、LSH；这些不是已验证的标准答案。对照 [近似近邻](../../handbooks/ml-101/questions/classical-models/ml101-approx-neighbors.md)，练解释选择依据与漏检代价。 |
| 11 | A/B test 很好，但 manager 认为损害长期体验，怎么办？ | G4 | [A/B testing](../../handbooks/ml-101/questions/probability/ml101-ab-testing.md)、[业务指标](../../handbooks/ml-101/questions/metrics/ml101-business-metrics.md)。原帖属于行为轮；可用来练长期指标、护栏与沟通，不应改标成纯统计推导题。 |
| 12 | 违规内容检测中，LLM 与便宜模型的成本怎么权衡？ | G5 | [业务指标](../../handbooks/ml-101/questions/metrics/ml101-business-metrics.md)部分覆盖；可练级联与升级处理方案，但原帖并未披露“必须使用级联”的要求。 |

上述 KDE、KNN 实现、bigram 条件概率预测、最近邻与均值分类对比，现已补为正式题卡。其余线索适合继续补充模型评价和实践场景；具体题意以原帖披露范围为准。

## 第三次补充：少标签、分布假设与数据准备

| 原帖与发帖日期 | 已核实的新内容 | 处理方式 |
| --- | --- | --- |
| [狗家vo挂经](https://www.1point3acres.com/interview/thread/836854)，2022-01-07 | 判断搜索 query 是否电影相关；没有现成 truth data；特征、模型、优化，特征重要性和 Adam。作者 2022-01-17 回复说明树模型 feature importance 与 Adam 的追问背景。 | 电影查询分类补为正式题；重要性对照 [已有题](../../handbooks/ml-101/questions/diagnosis/ml101-feature-importance.md)，Adam 已覆盖。旧帖，不推断当前题库。 |
| [狗家VO面经](https://www.1point3acres.com/interview/thread/786697)，2021-08-09 | 少见未标注符号；复用已有识别网络；embedding 的各类高斯分布、对角协方差；如何把标签一起用上。 | 补半监督 GMM 推导。原帖作者对部分题意有不确定，候选人猜测不是官方答案；固定 embedding 的方案为手册重构。 |
| [Google SWE AI/ML PhD Early Career](https://www.1point3acres.com/interview/thread/1135566)，2025-07-03 | Harmful content detection/classification，从 data preparation 开始细讲，规模讨论较少。 | 收录数据准备与分类设计主题，未披露标签、loss 或指标的具体追问，不补造成原题。 |
| [google Ai tech screen面经](https://www.1point3acres.com/interview/thread/1172803)，2026-04-13 | LLM 的 data、pretraining、post-training、Transformer 架构及变体权衡。 | 收录专题主题；没有具体数学题干，无法作为新增传统 ML 题。 |
| [狗 mle vo](https://www.1point3acres.com/interview/thread/1113179)，2025-02-18 | 自然语言查询检索对应 dashboard 和 components 的 NLP／GenAI 设计。 | 收录检索应用题方向，接口与完整检索算法未披露。 |
| [射月工厂 心得](https://www.1point3acres.com/interview/thread/987213)，2023-04-11 | X 的 Mineral／Chorus 项目，包含 convolution／augmentation 操作，算子反向传播、loss、数值稳定性，以及无标签／弱标签图像推荐。 | 站内归在 google 标签，但正文是 X 项目，单独标注，不归为 Google 常规 MLE 题库。Mineral 部分回忆的是 2019 面试，报告整体较旧。 |

本轮检索 `google svm` 没有结果，没有据此声称核实了 Google SVM 专题原题；通用 SVM 教学卡仍是原来的备考题。新来源里最贴近基础题册的两道场景已经补卡，其余有已有覆盖或只有主题，保留为复习线索。

## 第四次补充：K-means 编程、N-gram 与 NLP

第四次检索通过同一个 Chrome 登录会话查阅 10 篇未收录的报告。8 篇 Google 报告中，7 篇披露了至少一个 ML 题目／主题，1 篇只讨论招聘进度。以下区分完整问法、主题和候选人自己的解法；随后补入正式题卡的结果见本文件开头清单。

| 编号 | 原帖与发帖日期 | 已核实内容与边界 |
| --- | --- | --- |
| H1 | [MLE 昂赛](https://www.1point3acres.com/interview/thread/824942)，2021-11-29 | ML 轮要求实现 K-means，追问怎样用于 plagiarism detection，以及整句抄袭的情况。原帖提及 N-gram，但没有给向量表示、阈值或具体抄袭判定规则。旧帖。 |
| H2 | [Google 10月初vo fail](https://www.1point3acres.com/interview/thread/1094501)，2024-10-28 | 防抄袭系统设计；另有编程轮写 N-gram，包含训练和生成两个函数，并问优化。作者提及“递归从 bigram 开始”，具体优化规则未披露，不扩写为已确认的 backoff 接口。 |
| H3 | [Google MLE L5 面经](https://www.1point3acres.com/interview/thread/894226)，2022-05-10 | 明确问 EM、WordPiece 如何实现、文本分类；另一轮是约 2000 类 text labeling 的 assignment 优化，有每类 keyword-based 的已标注日志。扩展关键词增加 recall、分类过滤提高 precision 是候选人提出的方案，未获官方确认。旧帖。 |
| H4 | [Google VO coding interview（LLM相关）](https://www.1point3acres.com/interview/thread/1048352)，2024-02-27 | 明确要求对 corpus 做 tokenization 并有 follow-up，但没有说明采用 BPE、WordPiece 或其他算法，也未给出追问内容。只作为 tokenization coding 主题。 |
| H5 | [狗MLE现场表演](https://www.1point3acres.com/interview/thread/893989)，2022-05-10 | L6：手机 activity tracker app 的端到端系统与 ML 设计；Google 搜索问答功能，讨论数据、模型、测试、上线。未披露传感器、特征与模型架构，不将这些补造成原题条件。旧帖。 |
| H6 | [MLE 过经](https://www.1point3acres.com/interview/thread/1125321)，2025-04-21 | 两轮设计分别是 product recommendation 与 music recommendation；没有具体基础追问。商品推荐属于已有主题，音乐推荐是新的应用变体。 |
| H7 | [狗家phd ng mle 昂赛面经](https://www.1point3acres.com/interview/thread/1038945)，2024-01-16 | ML 设计为重复图片检测。与此前短视频模糊去重相关，计为新的独立报告，不计为全新基础概念。 |
| H8 | [狗家面试求分析](https://www.1point3acres.com/interview/thread/1187375)，2026-08-25 | 只有面试反馈和 HC／team match 讨论，没有具体 ML 题干，不计新增题。 |
| H9 | [谷歌 X 实习 面经](https://www.1point3acres.com/interview/thread/698533)，2020-12-20 | 正文明确为 Google X，问 overfit、skew dataset 与处理，未披露更具体问法；保留 X 归属，不当作 Google 常规 MLE 的额外高频证据。旧帖。 |
| H10 | [再贡献一个Quant的电面挂经](https://www.1point3acres.com/interview/thread/1116768)，2025-03-09 | 站内岗位／公司标签写 google，但标题明确为 Quant，正文没有确认 Google；内容有 UNet、矩阵乘法与骰子期望。归属冲突，排除在已核实 Google 题单之外。 |

### 可以接着练的具体问题

- **实现 K-means，并说明空簇、初始化和停止条件。** H1 只确认实现要求；这些边界是手册建议澄清的条件。已有 [K-means 原理题](../../handbooks/ml-101/questions/unsupervised/ml101-kmeans.md)与 [完整编程练习](../../handbooks/ml-101/questions/unsupervised/ml101-kmeans-implementation.md)。
- **怎样用聚类帮助查找抄袭，整句复用又怎么处理？** H1 确认这条应用追问。可以练文本表示、候选查找与精确核验的分工，但不能认为“同簇就判抄袭”是已确认答案。
- **实现 N-gram 训练和文本生成。** H2 的要求比当前 [Bigram 预测](../../handbooks/ml-101/questions/probability/ml101-bigram-prediction.md)更宽，后者只取最可能的下一个词。随机采样、结束标记、上下文长度和未见上下文规则都需要另行约定。
- **EM 的 E 步与 M 步分别在做什么？** H3 只披露 EM 主题，具体推导可练 [GMM／EM](../../handbooks/ml-101/questions/unsupervised/ml101-gmm-em.md)；不声称原帖指定了某个分布的推导。
- **WordPiece 怎样实现？** H3 明确披露该问法。词表学习和编码过程应分开准备；原帖没有给某个库或特殊 token 规则。
- **约 2000 个文本类别，有历史关键词标注日志，怎样优化标注分配？** H3 确认该场景。先澄清“分配”指候选类别还是人工标注任务安排，原帖没有完整接口，不能擅自变成单一标准算法题。
- **设计手机活动识别、搜索问答或音乐推荐。** H5／H6 确认这些应用题目，适合复用数据、标签、模型、评估、部署的分析过程；具体细节是练习时补充的假设。

新增内容仍以 ML 面试为范围，没有把同帖里的 BFS、投票、最短路径等普通算法题混入基础 ML 题册。

## 手写 backprop 的证据与练习顺序

2026-10-22 再次用 Chrome 核对了两篇已收录原帖，未重复计为新来源：

- [Google NG 1166705](https://www.1point3acres.com/interview/thread/1166705)：明确要求白板写公式，讲清 forward／backward、loss、链式法则和参数更新。没有披露必须用 NumPy 写某个两层网络的接口。
- [X Chorus 987213](https://www.1point3acres.com/interview/thread/987213)：明确提到 ML coding 推导 backprop、实现部分算子的反向步骤及 loss，测试并讨论 numerical stability。正文是 X 项目，不当成 Google 常规 MLE coding 的同等证据。

可按这个顺序练：先手算标量链式法则，再解释矩阵乘法与偏置广播的反向求和，最后完成 [两层网络的手写前反向与更新](../../handbooks/ml-101/questions/neural-networks/ml101-mlp-backprop-implementation.md)。这张新卡用 ReLU、稳定 softmax 交叉熵和显式 NumPy 梯度，并用中心差分验证所有参数和输入梯度。已有 [反向传播原理](../../handbooks/ml-101/questions/neural-networks/ml101-backprop.md)与 [梯度检查](../../handbooks/ml-101/questions/optimization/ml101-gradient-check.md)提供前置。
