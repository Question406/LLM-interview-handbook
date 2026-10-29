---
id: drustz-8ede3196cafd9484d6
section: mlsd
order: 141
level: A
title: 17 · Case：设计合成数据生成系统 · 15. 常见追问 + 应答要点
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 15. 常见追问 + 应答要点
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 15. 常见追问 + 应答要点

1. **「怎么证明合成数据真的有用？」**
   固定架构/tokenizer/优化器/总 token/eval 版本/多个随机种子，只变"是否加这批数据"，在**纯真实** held-out 上比较，并报confidence interval。加做 scaling 检查：在两个模型规模上都有增益才有外推价值——小模型喜欢的数据不一定让大模型受益（[07 §13.4](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)）。不显著就写不显著。

2. **「用 GPT/Claude 生成数据训自己的模型，合规吗？」**
   先看服务条款，很多商业 API 明确禁止用输出训竞品模型。合规路径是用宽松许可的开源权重模型——Nemotron-4 340B 就是明确为这个用途发布的。这是法务约束，我会拉法务确认而不是自己判断。

3. **「多样性和质量怎么权衡？给个具体做法。」**
   不用一个标量去 trade off。做法是：质量设**硬门**（闸门必须过），多样性设**下限约束**（taxonomy 网格覆盖率 ≥ A%、每格 ≥ N 条），然后在满足两者的前提下最大化产量。温度不是这个旋钮——它把成本从生成端推到筛选端而已。

4. **「judge 和 generator 用同一个模型可以吗？」**
   能用但要知道代价：自我偏好会让通过率虚高。缓解——judge 用不同家族的模型；拆成客观二元判定降低主观空间；用人工锚点集测 judge 与人的一致率。**如果只能用同一个模型，就必须把人工抽检比例提上去。**

5. **「怎么知道模型坍塌开始了？」**
   不要看整体指标，看**尾部**：罕见 token 频率、embedding 聚类熵、低频类别的召回、用**冻结**reference model算的 perplexity 分布的方差。这些会先动，整体指标可能还在涨。

6. **「加多少比例的合成数据合适？」**
   没有通用答案，必须 ablation 扫（5/10/20/40%）。可以引用两侧的文献张力：accumulate 策略下误差有与代数无关的上界；但也有工作指出即便很小比例的合成数据也可能造成可测量的退化。**所以我给的是方法不是数字。**

7. **「合成数据能不能用来做 eval？」**
   一般不行。合成 eval 系统性偏向和 generator 同族的模型，且极易被训练污染。唯一例外是**诊断性 challenge set**——故意构造已知缺陷的样本来测特定失败模式（我在 Anthropic take-home 里做的 137 对扰动测试套件就是这类）。但这类集合是用来**定位问题**的，不能当主指标。

8. **「verifier 本身错了怎么办？」**
   verifier 要有自己的测试集和单元测试。监控它的通过率突变。对被 verifier 判错的样本做分层人工抽检。另外要防"verifier 可被 hack"——比如答案匹配用了过松的正则，模型学会输出一堆数字碰运气命中（对应 [03](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) 的 reward hacking）。

9. **「怎么防止合成数据污染 benchmark？」**
   exact string match 远远不够——generator 可能"重新发明"benchmark 题目。要做 n-gram 重叠 + embedding 近重复检测，且对所有 eval 集都做。并且**不承诺"零污染"**，而是报告检测方法和检出率（[07 §8.3](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)）。

10. **「人工抽检抽多少、怎么抽？」**
    量级上几百到几千条即可（目的是估计准确率，不是过滤）。**关键是分层**：按 judge 判定（通过/拒绝/边界）、按 taxonomy 类别、按 generator 版本分层，这样才能同时估 precision 和 recall，并定位系统性盲区。只抽通过的样本永远发现不了误杀率。

11. **「多语言/低资源语言的合成数据？」**
    最大的问题是 generator 在低资源语言上本身就弱——生成出来的东西可能语法都不对，而你的 judge 也是同一个弱模型，测不出来。做法：以翻译 / 跨语言反推为主（事实来自高资源语言的真实语料），并且**低资源语言的人工抽检比例要显著高于高资源语言**。评估必须用母语者，不能只看翻译过来的 benchmark。

12. **「如果这套系统交给别人接手，最容易出问题的是什么？」**
    provenance 和 judge 版本管理。生成一批数据很容易，难的是半年后有人问"这批数据是哪个模型、哪个 prompt、哪个闸门版本产出的，为什么当时通过率是 32%"。所以每条样本必须带 generator / checkpoint / prompt 版本 / seed 来源 / 闸门通过记录，judge 必须有版本号和固定的回归锚点集。**这条如果做不到，整套系统是不可维护的。**

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
