---
id: drustz-cef1ade98228d40578
section: collections
order: 22
level: A
title: Google DeepMind 题库（爬取全量） · ML 理论
quick: 作者文档章节 · Google DeepMind 题库（爬取全量） · ML 理论
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md
    type: primary
---
## ML 理论

### Glassdoor RE math/ML quiz questions: convex functions, gradient descent, Newton's method, second-order methods, Bayes' formula
*medium · 频率: very high (recurring across Glassdoor, Blind, Reddit, IGotAnOffer) · 2024*

Reported verbatim on the Glassdoor DeepMind Research Engineer interview page: 'Why do we want convex functions?', 'What is gradient descent?', 'Describe Newton's method', 'What are second-order optimisation algorithms?', 'How can the 2nd derivative be used in an optimisation algorithm?', 'What is Bayes' Formula?'. These come from the ML/math fundamentals interview (the 'quiz'). Recruiters usually tell candidates in advance that maths and stats will be covered. Page stats: RE interview difficulty 3.3/5, 61% positive experience, avg 46 days to hire, ~18 RE interview reports. Direct page is bot-blocked (403) — content recovered via search snippets.

**解法**: Convexity: any local min is global; gradient descent has convergence guarantees (O(1/k) for convex, linear rate for strongly convex). Newton's method: x ← x −  $H^{-1}$ ∇f, second-order Taylor approximation, quadratic local convergence but O( $d^{3}$ ) Hessian inversion — motivates quasi-Newton (L-BFGS) and diagonal approximations (Adam as preconditioned SGD). Bayes: P(A|B)=P(B|A)P(A)/P(B); be ready for ball/urn-style application problems. (standard textbook answers)

来源: &lt;[来源链接](https://www.glassdoor.com/Interview/Google-DeepMind-Research-Engineer-Interview-Questions-EI_IE1596815.0,15_KO16,33.htm&gt;)

### GDM 经典第二轮 Quiz：2 小时 Hangouts 四连考——数学/CS/统计/ML 各 30 分钟
*medium · 频率: very high（同格式 5+ 帖：540650/813950/942891/918169/825115） · 2019-03*

《DeepMind Research Engineer 面试经验分享》（2019，thread 540650）。流程：第一轮 casual conversation（非标准 BQ），聊研究兴趣、为什么来 DeepMind；第二轮为 quiz，通过 Google Hangouts 进行，覆盖四大块：Mathematics、Computer Science、Statistics、Machine Learning，总时长两小时，每块约 30 分钟。该 quiz 形式是 GDM 区别于 Google 普通 SWE 面试的标志性环节，在 813950（intern 版 1 小时精简 quiz：linear algebra + probability 为主的 statistics + ML 概念 + 代码阅读）、942891（数学题+code comprehension+基础 ML）、825115（Math&Statistics 1h + ML 1h）等帖中反复出现。

**解法**: 我的推断+多帖佐证的高频考点：线代（特征值/SVD/正定性/矩阵求导）、概率（贝叶斯、期望方差、常见分布、大数定律）、统计（假设检验、MLE/MAP、bias-variance）、CS（复杂度、数据结构、递归）、ML（overfitting与regularization、SVM/logistic/树模型原理、backprop、CNN/RNN 基础）。口头快答形式，重反应速度和第一性原理推导，不重写码。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/interview/deepmind-machine-learning-540650.html&gt;)

### Quiz 考点全景：线代/概率/统计/CS 四领域（Glassdoor 多条报告）
*hard · 频率: very high（quiz 是 GDM 区别于 Google 的标志性环节，报告极多） · 2019-2024 各年报告*

QTN_2480984（RE）：“Linear algebra, probability theory, statistics and cs fundamental questions”。QTN_2186118：“四个领域的 quizzes，之后是一场 software engineering 面试和与 research engineering lead 的对话”。其他 Glassdoor 摘要补充的具体考点：Bayes rule、可逆矩阵（invertible matrices）、凸函数、梯度下降、gradient computation、KL divergence 的性质、sampling算法、收敛性证明、数据结构、Python 与 C++ 对比。历史格式为 2 小时笔试式 quiz（CS/Math/ML/Stats 各一部分），后演变为 2 场 back-to-back 口头快问快答，2025 起部分岗位取消（见另条）。

**解法**: 复习清单：MML book（线代/概率/优化）、Bayes/共轭先验、MLE vs MAP、CLT、假设检验、KL/cross entropy性质、SGD 收敛条件、排序/查找/图算法复杂度。

来源: &lt;[来源链接](https://www.glassdoor.com/Interview/Linear-algebra-probability-theory-statistics-and-cs-fundamental-questions-QTN_2480984.htm&gt;)

### ML fundamentals signature question: mathematical intuition for L1 vs L2 regularization sparsity
*medium · 频率: high (multiple sources) · 2023*

Reported on Blind and highlighted by IGotAnOffer as emblematic of DeepMind's ML fundamentals bar: it is NOT enough to say L1 produces sparse features — you must 'explain the intuition, in terms of how the gradients affect the weights in L1 to cause that sparsity.' Also seen as 'What is the difference between L1 and L2 regularization? When would you use each?'. DeepMind ML rounds systematically ask WHY, not just WHAT; every claim gets a first-principles follow-up.

**解法**: L1 gradient is constant magnitude λ·sign(w) regardless of |w|, so it keeps pushing small weights all the way to exactly 0 (and subgradient at 0 lets them stay there); L2 gradient 2λw shrinks proportionally, so updates vanish as w→0 and weights never reach exactly zero. Geometric view: L1 ball has corners on axes where the loss contour typically touches. Bayesian view: Laplace vs Gaussian prior.

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-research-engineer-interview-process-wp1gjgyb&gt;)

### Glassdoor RS loop: math + ML + coding/CS technical rounds; AI fundamentals, transformers, finetuning, Gemini/DeepSeek training approaches
*hard · 频率: high (13+ Glassdoor RS reviews) · 2025*

From Glassdoor DeepMind Research Scientist page (27 questions, 13 reviews; difficulty 3.2/5, avg 49 days): typical loop = HR chat → hiring manager chat → 3 technical interviews: math, ML, and coding/CS → interviews with several research scientists → program manager behavioral. Rounds with 1-3 scientists included 'leetcode style questions, AI fundamentals, Transformers, Finetuning, Training approach of large models like Gemini, Deepseek etc.' Other reports: basic maths, stats, ML, CS concepts; programming language basics and style; implement an algorithm in a language of your choice; linear algebra, calculus, algorithms, big-O, statistics + a coding challenge. One 2025 Cambridge RS report: explain your research projects in detail with follow-up questions, then technical questions about transformers, reinforcement learning, and LLM reasoning. ML fundamentals interviews covered optimization, regularization, loss functions, transformers, plus practical training and inference questions. ML system design for research roles described as 'more ML focused than system focused.'

**解法**: For 2025-26 loops expect LLM-era content: transformer architecture details, SFT/RLHF/DPO finetuning tradeoffs, MoE (DeepSeek/Gemini), RL for reasoning (GRPO/PPO), scaling laws, inference-time compute. Candidate's Meta post-training background maps directly. (my inference)

来源: &lt;[来源链接](https://www.glassdoor.com/Interview/Google-DeepMind-Research-Scientist-Interview-Questions-EI_IE1596815.0,15_KO16,34.htm&gt;)

### r/leetcode 2026-05: RE ML fundamentals round — toy ML problem + binary classification loss + deep transformers/NLP + evaluation
*hard · 频率: single detailed report; topic mix corroborated by Glassdoor RS reports · 2026-05*

Same candidate's ML round (1 hour): asked to solve a toy ML problem and go very deep on fundamentals. Details: initially couldn't think of a solution and forgot which loss to use for binary classification (noted softmax over 2 classes ≈ sigmoid/BCE); eventually produced an unusual working solution ('first time I hear a solution like this' per interviewer). Then went 'very deep on NLP and transformers' (candidate reports no linear algebra beyond QKV in transformers, only basic DL, 'lots of transformers though'), finishing with a discussion of evaluation. Takeaway per candidate: 'it's a lot about the fundamentals and not so much about memorizing specific techniques and models.' Passed despite a disastrous first 30 minutes — recovery and reasoning mattered.

**解法**: Binary classification: sigmoid output + binary cross-entropy (equivalent to 2-class softmax + CE). Expect derivations: attention QKV mechanics, why scaling by sqrt( $d_k$ ), positional encodings, tokenization, decoding strategies, and eval methodology (held-out metrics, human eval, contamination). (my inference on likely probe areas)

来源: &lt;[来源链接](https://old.reddit.com/r/leetcode/comments/1tfu311/how_i_passed_deepmind_technical_rounds_with_3/&gt;)

### r/MachineLearning 2026-01: topic list from a past GDM candidate — derive SGD/Newton-Raphson, Taylor expansion, covariance, floating point, information theory, ELBO
*medium · 频率: single thread, multiple corroborating commenters incl. GDM staff · 2026-01*

A commenter who previously interviewed at DeepMind lists what to review for the quantitative/ML rounds: 'a lot of linear algebra, basic optimisation (derive SGD or Newton-Raphson, Taylor expansion), basic probability, understanding of covariance, dot product and intuitive understanding of similarity metrics, precision, how numbers are stored, I would guess information theory (CE, KL, entropy etc)'. ML depth questions are tailored to your claimed expertise — for them it was deep learning (thorough understanding of training CNNs/transformers); they skipped RL entirely since it wasn't their area. Also: 'can you easily derive the ELBO' for graphical-model people. Same thread has current GDM staff confirming: publication bar 'it depends'; RE→RS transition is fluid internally once hired; recruiter relationships are the main interview channel. Also a Prepfully coach: technical rounds cover 'gradient descent variants, attention mechanisms, optimization theory — not just implementation but the math behind it', and behavioral genuinely matters (research collaboration, handling ambiguity).

**解法**: Drill: SGD derivation from empirical risk minimization; Newton-Raphson from 2nd-order Taylor; KL(p||q)=Σp log(p/q), CE = H(p)+KL; ELBO: log p(x) =  $E_q$ [log p(x,z)/q(z)] + KL(q||p(z|x)) ≥ ELBO; float32/bf16/fp16 layouts (sign/exponent/mantissa) and why bf16 preserves dynamic range for training.

来源: &lt;[来源链接](https://old.reddit.com/r/MachineLearning/comments/1q2wiub/d_google_deepmind_research_engineerscientist/&gt;)

### Sundeep Teki 2026 cross-lab guide: DeepMind's rapid-fire fundamentals quiz fails industry veterans; core content areas
*hard · 频率: prep-site synthesis · 2026*

Guide covering OpenAI/Anthropic/DeepMind notes DeepMind uniquely 'consistently tests undergraduate-level fundamentals via a rapid-fire quiz round' and that 'candidates who have been in industry for years often fail the quiz round because they've forgotten formal definitions of linear algebra concepts they use implicitly every day. Reviewing textbooks is mandatory.' Content areas: (1) math/linear algebra — eigenvalues/eigenvectors, rank, singularity, SVD, PCA; (2) ML coding — implement Transformer / multi-head attention blocks, neural nets from scratch; (3) ML debugging — identify bugs in models that don't learn; (4) system design — distributed training (data/pipeline/tensor parallelism); (5) research discussion — paper analysis and extensions; (6) safety & ethics — alignment, responsible scaling. Overall vibe: 'PhD defense mixed with a rigorous engineering exam'; values 'research taste'. Sells a paid DeepMind-specific guide (JAX-native implementations, TPU-optimized training, 5-8 rounds, hiring committee decides, RS median TC &#36;336-406K).

**解法**: Refresh formal definitions: eigendecomposition conditions, rank-nullity, positive definiteness, SVD vs eigendecomposition, PCA as variance-maximizing projection / low-rank approximation (Eckart-Young). Practice writing multi-head attention + AdamW + training loop from scratch in numpy/PyTorch/JAX within 30 min.

来源: &lt;[来源链接](https://www.sundeepteki.org/advice/the-ultimate-ai-research-engineer-interview-guide-cracking-openai-anthropic-google-deepmind-top-ai-labs&gt;)

### Dataford RS guide question bank (ML fundamentals + research design)
*medium · 频率: prep-site question bank (partially candidate-sourced, unverified) · 2025*

Google DeepMind Research Scientist guide (dataford.io): process = HR screening → technical rounds (quiz-style + practical coding) → research discussions with senior staff/team leads, 3-5 weeks. Sample questions: derive backpropagation for a multi-layer perceptron; manage bias-variance tradeoff in deep networks; mathematical properties of a metric space; compare loss functions for classification vs regression; explain Bayes' theorem to non-technical stakeholders; CNN vs Transformer architectural differences; data-structure tradeoffs under memory constraints; concurrency in HPC; systematically debug an underperforming model; design real-time data ingestion for large-scale models; describe influential recent papers; scope a research experiment. Most-frequent tagged questions: 'Explain Transformer Architecture and Attention Mechanisms' (Hard), 'Supervised vs Unsupervised Learning' (Easy). Requirements listed: advanced Python, JAX/PyTorch/TF, strong math; nice-to-have: large-scale distributed training, C++, publications. STAR for research discussions.

来源: &lt;[来源链接](https://dataford.io/interview-guides/google-deepmind/research-scientist&gt;)

### Educative 'Top 20 GDM questions' (editorial list — breadth checklist)
*easy · 频率: editorial/synthesized — treat as checklist, not reports · 2025*

Editorially compiled question list (NOT verified candidate reports, useful as breadth checklist). Coding/algorithms: explain time/space complexity of favorite sorting algorithm; implement a hash table from scratch; detect cycle in linked list; find duplicates in large dataset efficiently. AI/ML: supervised vs unsupervised; CNN advantages for images; how RL works + real-world example; GD vs SGD. System design: recommendation system for music streaming; scalable AI for autonomous vehicles (perception/prediction/planning); NoSQL vs SQL tradeoffs in AI systems; fault-tolerant AI application requirements. Research/theory: importance of MDPs in RL; overfitting and mitigation (L1/L2, dropout, cross-validation); how to evaluate model success (metrics + interpretability + efficiency); ethical considerations in AI research. Behavioral: collaborative problem-solving experience; handling team disagreements; a failed AI project and response; task prioritization across projects. Educative also describes phases: online assessments → technical interviews → research interviews (past projects, recent papers) → behavioral (teamwork, ethics, mission alignment).

来源: &lt;[来源链接](https://www.educative.io/blog/google-deepmind-interview-questions&gt;)

### 4dayweek.io DeepMind data science interview: 5-stage process + 15 sample ML questions
*medium · 频率: prep-site synthesis · 2025*

Data-science-flavored but DeepMind-branded guide: process = recruiter screen (30-60 min, ~1 wk after application) → 2+ technical coding interviews (45-90 min each) → 2+ technical ML interviews (45-90 min) → hiring manager (60-90 min) → cultural fit (60-90 min); 4-6 weeks total; difficulty 3.2/5, 62% positive. Sample questions (likely editorial): feature selection methods; hyperparameter tuning process and significance; build a recommendation system with collaborative filtering; model performance assessment and key metrics; L1 vs L2 regularization in linear/logistic regression; gradient descent and its variants; handling imbalanced datasets; time series analysis steps; missing data imputation techniques; CNN working principles and CV applications; bias-variance tradeoff; feature selection/engineering in high-dimensional data; plus behaviorals (data-driven decision story; multidisciplinary team role). Notes interviewers are 'generally kind and supportive, though occasionally lacking deep subject expertise'; little post-interview feedback.

来源: &lt;[来源链接](https://4dayweek.io/interview-process/deepmind-interviews&gt;)

### Informal LLM post-training probe from GDM-adjacent commenter: GRPO rollout assumptions
*hard · 频率: single informal exchange · 2026-01*

In the 2026-01 r/MachineLearning DeepMind thread, a commenter stress-tested an aspiring candidate with a post-training depth question of exactly the style GDM ML rounds favor (why-not-what): 'What is the assumption on the rollouts while doing GRPO?' — expected answer: GRPO replaces the critic with empirical statistics (mean/std) of rollout rewards per prompt, which requires rollouts to be IID samples from the behavior/old policy and enough of them for the advantage estimate to be reliable. Follow-up: 'How would you modify the optimization objective for independent but non-identical rollouts (e.g., rollouts from different models/prompts)?' — expected: adjust the importance-sampling denominator so each rollout's policy ratio uses the actual policy it was sampled from (pi_theta_old_i per source model), and rethink the group-normalized advantage across heterogeneous sources. Not a confirmed GDM interview question, but a realistic sample of the depth expected from a post-training candidate.

**解法**: Included above; also be ready to derive GRPO objective from PPO by substituting group-relative advantage Â_i=( $r_i$ −mean(r))/std(r), and discuss bias introduced by std normalization and non-IID sampling.

来源: &lt;[来源链接](https://old.reddit.com/r/MachineLearning/comments/1q2wiub/d_google_deepmind_research_engineerscientist/&gt;)

### GDM RE 第二轮 ML 面（背靠背 2 小时）：实际工业信号数据的 ML 应用题 + 基础概念深挖（含完整评论区，Wayback 全文）
*medium · 频率: single report（细节最全的 RE ML 轮实录） · 2021-11*

《DeepMind research engineer 第二轮ML过经》2021-11-30，物理 PhD 转 MLE 两年半，LinkedIn 被 GDM tech recruiter 主动联系，先 1 小时友好交流，11/11 第一轮 coding，第二轮 ML 背靠背两小时（题目正文积分墙，但评论区楼主透露关键内容）：题目围绕机器运转遥测信息——"就是一些机器运转信息，比如温度啦，机器型号啦，读写load啦之类的信号"，让你设计 ML 方案，不需要 NLP 知识；另一位面试者补充自己的 loop 是 1-hour Math&Statistics + 1-hour ML。楼主经验总结："math的部分没有很难或者很深，但我也按照地里之前发的准备了一些probability和linear algebra的题"；"面试官并不在意你的背景，更在意你在你了解的领域是不是真的知识点扎实……比如你提到了SVM，你就应该知道SVM是什么，切忌不懂装懂"。结果 timeline：第二轮次日 HR 电话通过；终轮 manager 面"有大概一半甚至以上的时间是问简历上的经历里的某个具体model，以及BQ"；面完一周内出结果，intern final round 面完次日 HR 说 working out offer。备考材料：楼主推荐 medium 上的 ML 面试题清单（link.medium.com/b1SNS3VxMlb）及地里 deepmind 相关 cheat sheet，花一两天速览。

**解法**: 针对遥测信号题（我的推断）：按 ML design 框架答——明确预测目标（故障预测/异常检测）、特征工程（温度/负载时序聚合、机型类别 embedding）、标签稀疏与类别不平衡处理、时序 train/test split 防泄漏、指标选 PR-AUC、冷启动与部署监控。面试官要的是基础扎实+变通，不是堆 SOTA。

来源: &lt;[来源链接](http://web.archive.org/web/20220813055622/https://www.1point3acres.com/bbs/thread-825115-1-1.html&gt;)

### GDM research tech 电面（统计 PhD）：HR 发官方备考 PDF；实考 functional analysis + RL + deep learning（超纲）
*hard · 频率: single report · 2020-11*

《deepmind research，tech店面》2020-11-20。原文："hr给的pdf介绍的很全了，补充几个：楼主被问到了functional analysis, reinforcement learning, deep learning。functional anlysis似乎不在pdf的推荐阅读里。可能统计phd[会被问]……"。两个关键信息：(1) GDM 会给候选人官方 prep PDF（含推荐阅读清单，覆盖 quiz 四大块）；(2) 实际提问会根据候选人背景超出 PDF 范围（统计 PhD 被问泛函分析），印证 825115 楼主观察：面试官按你自称懂的领域往深挖。

**解法**: 注：此条目原帖为 thread-689380（tag 页恢复），正确直链应为 [来源链接](https://www.1point3acres.com/bbs/thread-689380-1-1.html。我的推断：拿到) recruiter PDF 后逐条过推荐阅读，同时把自己 PhD 领域的研究生级核心课内容复习到能口头推导。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/interview/google-machine-learning-628812.html&gt;)

### （补充来源，知乎转载性质）GDM 面试实录：BQ+简历项目+RNN/GRU/LSTM 对比+链表基础，面试官控制提问节奏
*easy · 频率: single report · 2024-10*

知乎专栏《谷歌DeepMind面试惊险通过！面试官不让多问！》(p/983167020，约 2024-10)。zhihu 正文被反爬，搜索快照可见内容：一位博士生的 GDM 面试（疑似 student researcher/intern 轨第一轮），面试官温柔，先 BQ 和简历项目深挖，技术部分考：RNN vs GRU vs LSTM 的优劣对比（序列建模场景选型）、链表等数据结构概念；标题含义为面试官限制候选人反问时间。通过。非 1p3a 来源，作为 2024 年 GDM 中文面经补充。

**解法**: RNN/GRU/LSTM 标准答案（我的补充）：RNN 梯度消失难捕长依赖；LSTM 三门+cell state 解决长依赖但参数多；GRU 两门更省参数、小数据上常更好；实践中长序列/大数据选 LSTM 或直接 Transformer，资源受限选 GRU。

来源: &lt;[来源链接](https://zhuanlan.zhihu.com/p/983167020&gt;)

### ML fundamentals（quiz）真题集（IGotAnOffer 六题 verbatim）
*hard · 频率: 聚合（多条 Glassdoor/Blind 报告） · 2026-06（指南更新时间）*

RE ML fundamentals 轮（候选人俗称 the quiz，现为对话式）真题：1) Explain the difference between gradients and weights；2) What are convex functions, and what's special about them?；3) 袋中有不同颜色的球，给定若干观察，求下一个抽到某颜色的概率（贝叶斯/后验预测）；4) Why would you prefer L1 over L2 regularization? 必须讲清梯度如何作用于权重导致稀疏的数学直觉；5) Walk me through how regression, SVMs, kernel SVMs, and Bayesian networks work, and when you'd use each；6) Derive the ELBO for a graphical model。评分核心是数学直觉：不能只背结论，要能推导并联系模型实际行为。

**解法**: L1：次梯度幅度恒为 λ·sign(w)，与 w 大小无关，可把小权重直接推到 0；L2 梯度 2λw 按比例收缩、不为零。ELBO：log p(x)= $E_q$ [log p(x,z)/q(z)]+KL(q||p(z|x))≥ $E_q$ [log p(x,z)]- $E_q$ [log q(z)]，用 Jensen 或 KL 非负两种推法都要会。

来源: &lt;[来源链接](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q2&gt;)

### RS/RE ML 深度题：解释 transformer 训练全流程（SFT+RL）与 attention O( $n^{2}$ ) 内存及替代方案
*hard · 频率: multiple reports · 2025*

Glassdoor RS 报告：被要求“在 LLM 语境下解释 transformers、解释训练 transformers 的过程、其中的 supervised finetuning 和 RL”。letsdatascience 汇总：GDM ML theory 轮要求解释“为什么 attention 在内存上是 O( $n^{2}$ )”并讨论替代方案；强调架构内部机理而非 API 使用。

**解法**: O( $n^{2}$ ) 来自  $QK^T$  attention矩阵的显式物化；替代：FlashAttention（tiling+重计算，内存 O(n)）、滑窗/稀疏attention、linear attention（kernel 化）、MQA/GQA 减 KV heads、PagedAttention 推理侧。SFT→RL：预训练 next-token → SFT 指令数据 → RM/偏好建模 → PPO/GRPO/DPO，讲清每步目标函数与 KL 正则。

来源: &lt;[来源链接](https://letsdatascience.com/blog/how-to-land-a-job-at-openai-anthropic-or-google-deepmind&gt;)

### Dataford：GDM Research Scientist 题库样题 15 条（442 题库）
*hard · 频率: 题库聚合（标注 Very common/Common） · 2025~2026*

流程：HR screening → technical rounds（quiz 式+实操 coding）→ research discussions，3-5 周。ML/研究基础：Explain the derivation of the backpropagation algorithm for a MLP；How do you manage the bias-variance trade-off in deep neural networks?；Describe the mathematical properties of a metric space；Compare loss functions for classification vs regression；How would you explain Bayes' theorem to a non-technical stakeholder? Coding/CS：实现特定数据变换/文本解析函数；内存受限场景数据结构 trade-off；高性能计算中的并发/线程；给定算法优化时空复杂度；CNN vs Transformer 架构差异。研究设计：走查研究项目方法论与技术难点；设计大规模模型的实时数据摄取系统；模型表现不佳时的系统化 debug 流程；讲一篇影响你方法论的近期论文；如何确定研究实验的合理 scope。

来源: &lt;[来源链接](https://dataford.io/interview-guides/google-deepmind/research-scientist&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/gdm.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md)。作者整理资料；许可和第三方来源范围见阅读指南。
