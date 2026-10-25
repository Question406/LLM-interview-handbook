# Machine Learning 101 · 基础面试题

这本题册有 142 道中文面试练习，分成 12 章。每题提供能独立口述的短答、完整解释、具体例子和追问。题目按公开面试准备资料中的常见主题整理，答案重新编写，并用官方文档、教材作者资料、课程讲义或原论文核对。其中 130 题为通用备考练习（`realInterview: false`）；新增 12 题有 Google 候选人原帖披露的选题依据（`realInterview: true`），题内区分已披露内容与手册补充的解释、接口和边界条件。该标记表示存在面经报告，不表示公司官方确认。

初学时可以先读「学习与泛化」「数据与验证」「评价与决策」，再进入各类模型。概率、统计、线代章节可以按需回查；准备手推公式时，重点看变量定义、成立条件和数值例子。

| 章节 | 题数 |
| --- | ---: |
| 01 · 概率与统计 | 16 |
| 02 · 线性代数与数值基础 | 8 |
| 03 · 学习与泛化 | 11 |
| 04 · 数据与验证 | 17 |
| 05 · 评价与决策 | 12 |
| 06 · 线性与概率模型 | 11 |
| 07 · 树与集成 | 12 |
| 08 · 经典分类与近邻 | 11 |
| 09 · 优化与预处理 | 9 |
| 10 · 聚类与降维 | 12 |
| 11 · 神经网络基础 | 12 |
| 12 · 实践与排查 | 11 |

## 选题来源与答案依据

选题覆盖参考了 [DataCamp 的机器学习面试题单](https://www.datacamp.com/blog/top-machine-learning-interview-questions)、[Interview Query 的机器学习面试题单](https://www.interviewquery.com/p/machine-learning-interview-questions)，以及 [Interview Kickstart 课程页上的公开样题](https://interviewkickstart.com/courses/machine-learning-interview-masterclass)。没有复制这些网站的答案，也没有沿用未经核实的公司归属或题目频率；部分数学前置题是为补齐学习顺序而扩充的。

每题 front matter 的 `sources` 是核对答案的技术依据，主要包括 scikit-learn、NumPy、SciPy、PyTorch 官方文档，Stanford、MIT、Berkeley 等课程讲义，D2L 作者教材、Google ML Crash Course，以及相关算法原论文。具体条件以题内来源和解释为准。

Exponent 的目录只读到外层，Educative 页面无法读取，部分 Interview Kickstart 题单返回限流；这些页面没有被当作已核实的逐题来源。

## 一亩三分地面经练习

2026-10-22 通过已登录的 Chrome 核对了涉及 7 家公司的 12 篇原帖，整理出 [30 个基础练习点与来源对应](../../sources/1point3acres-ml101-2026-10-22/README.md)。索引链接到本题册现有答案，并标出部署、延迟排查、冷启动和现场 EDA 等缺口。该索引的 30 个练习点不等于新增 30 张题卡；后续正式新增 12 题见 Google 专项清单。原帖只披露主题的地方有明确标记。

Google 专项可读 [Google 基础题与原帖证据](../../sources/1point3acres-ml101-2026-10-22/google.md)，包含 L1 稀疏性几何解释、前反向传播，以及推荐和 LLM／RE 方向的补充路线。

## 维护方式

正式源文件位于 `questions/<section>/<id>.md`。新增或修改后运行 `npm run content:check`，接入前端时运行 `npm run content:build`。生成索引和页面内容由构建器维护。

最初 120 题均经过独立全文审阅；审阅中修正了概率校准示例、预测时点泄漏、log-odds 用词、去重门槛方向和最小二乘损失缩放条件等问题。

有候选人面经依据的题卡共 12 道，清单见 Google 专项。编程练习还包括下方新增的通用实现题。安装 NumPy 后，运行 `python3 scripts/check-ml101-practice.py` 可直接提取题卡代码验证；39 项测试覆盖边界、概率、优化目标和逐参数／输入的有限差分梯度检查。

## 2026-10-23 通用基础扩充

新增 10 题均为通用教学练习，`realInterview: false`，不附 Google 公司标签。它们补充已有概念题的推导和动手实现；采用的接口、边界与示例在各题中说明。

| 练习 | 内容 |
| --- | --- |
| [Softmax backward](questions/neural-networks/ml101-softmax-backward.md) | Jacobian、任意上游梯度、稳定前向。 |
| [BatchNorm forward／backward](questions/neural-networks/ml101-batchnorm-backward.md) | batch 依赖、gamma／beta、累计统计量与推理。 |
| [二维卷积 forward／backward](questions/neural-networks/ml101-conv-backward.md) | 多通道、stride、padding、共享与重叠梯度。 |
| [SGD／Momentum／Adam](questions/optimization/ml101-optimizer-implementation.md) | 跨步状态、偏差校正与非原地更新。 |
| [决策树单层分裂](questions/ensemble/ml101-decision-stump-implementation.md) | Gini／熵、加权增益、平票、叶子限制。 |
| [PCA 实现](questions/unsupervised/ml101-pca-implementation.md) | 训练均值、SVD、投影、重构与误差。 |
| [样本方差的 n−1](questions/probability/ml101-unbiased-variance.md) | 无偏推导、已知均值、MLE 与相关样本。 |
| [频率学派与贝叶斯](questions/probability/ml101-bayesian-frequentist.md) | 参数、不确定性、置信区间与可信区间。 |
| [缺失机制](questions/data/ml101-missing-mechanisms.md) | MCAR／MAR／MNAR、可识别性与敏感性。 |
| [下采样后的概率修正](questions/metrics/ml101-downsampling-probability.md) | odds 修正、采样条件、逆概率加权与校准。 |
