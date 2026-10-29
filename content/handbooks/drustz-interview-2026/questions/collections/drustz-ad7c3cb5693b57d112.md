---
id: drustz-ad7c3cb5693b57d112
section: collections
order: 40
level: A
title: OpenAI 题库（爬取全量） · ML Coding 题
quick: 作者文档章节 · OpenAI 题库（爬取全量） · ML Coding 题
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/openai.md
    type: primary
---
## ML Coding 题

### MLE 面试（2026-06 通过）：transformer 抓虫 + cell simulation + post-training 细节追问
*medium · 频率: single report; transformer debugging 本身 very high · 2026-06*

thread-1179644（2026-06-09 前后，MLE 全职 onsite，已通过）：'面试主要是 transformer 抓虫（debugging），coding 是 cell simulation，另外考了 post-training 的细节。我主要面试的材料是 Andrej Karpathy 的 youtube'。确认 2026 年 Research/Applied ML 轮 = transformer debugging + 模拟类 coding + post-training（SFT/RLHF/数据）知识性追问三件套。对候选人（Meta post-training 背景）来说 post-training 细节追问是主场。

**解法**: transformer debug 常见 bug 点：causal mask 方向/位置（pre-softmax）、softmax 维度、√ $d_k$  缩放缺失、位置编码未加、训练/eval 模式、loss 的 target 未 shift。post-training 追问按自身项目准备：RLHF/DPO 对比、reward hacking 处理、SFT 数据配比、eval 设计。Karpathy 的 'Let's build GPT' 和 'Deep Dive into LLMs' 是面经作者点名的备考材料。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1179644-1-1.html&gt;)

### PracHub 2026-04-03 MLE tech screen：Debug MiniGPT + 手推 matmul 反向 + KV cache 实现
*medium · 频率: transformer debugging 家族 very high；此具体版本 single report · 2026-04*

两 part，共约 1 小时（MLE technical screen，上报 2026-04-03）。Part A：decoder-only transformer 代码语法正确但autoregressivedecoding输出错误文本，要求 debug 并加 KV cache。考点：各阶段 tensor shape、causal mask 机制、attention 计算、位置编码、loss 对齐（next-token shift）、train/eval 模式、greedy/sampling。期望交付：找出并修复 bug（mask 错误/softmax 轴/√ $d_h$  缩放/位置编码/target shift/模式类 bug）、prefill 与 decode 干净分离、O(T) decode vs O( $T^{2}$ ) 重算、内存讨论（MQA/GQA/量化）。Part B：自定义 C=A@B 的 forward+backward：从  $C_{ij}$ = $Σ_r$   $A_{ir}$   $B_{rj}$  逐 index 推导 dA=dC@Bᵀ、dB=Aᵀ@dC，支持 batch/broadcast，用 torch.autograd.Function + save_for_backward，gradcheck 验证。追加 follow-up：Hillis-Steele prefix scan 的 O(n log n) work / O(log n) depth，及 scan vs reduction 何时划算；Blelloch scan 对比。

**解法**: 来源已给完整解法框架（见 detail）。补充：dA/dB 的 broadcast 情形要对被广播的轴求和还原形状；KV cache 只改 attention 的 K/V 拼接与 mask 的增量部分，Q 只算新 token。

来源: &lt;[来源链接](https://prachub.com/interview-questions/debug-minigpt-and-backpropagate-matmul&gt;)

### MLE 电面（2026-06）：resumable iterator 存状态——recruiter 提前给 topic 且很准
*medium · 频率: high (staple; 1 new report Jun 2026) · 2026-06*

thread-1180787（2026-06-20，MLE 电面详细面经）：LinkedIn recruiter reach out，给了大概的面试 topic，'实际上还是挺准的'。题目：'设计一个 resumable iterator，能够存状态并且[恢复]...'（预览截断）。与已知高频 resumable iterator 一致：getState()/setState()，list→多文件 JSON→async 递进。Hello Interview 社区版本（OpenAI，2024-12 senior/2025-10 mid 两次上报）要求 async 版：AsyncCompositeIterator 跨多文件，state 可序列化（JSON dict），多 iterator 并发互不干扰；常见坑：直接存不可序列化的 iterator 对象、把 byte offset 当逻辑位置、漏 await。另注意 thread-1181120（2026-06-24 MLE）专门讨论'recruiter 给的 onsite problem prompt 有多准'——社区共识是大体准但建议全面准备。

**解法**: 分层实现：ResumableListIterator(index state) → MultiFileIterator(state=(file_idx, inner_state))，处理空文件（advance 逻辑放 helper，setState 后也要 skip empty）→ async 版把 next() 变 coroutine。必须写单测覆盖 get/set state 各时刻和 StopIteration。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1180787-1-1.html&gt;)

### Transformer Bug Hunt（变形金刚抓虫）——MLE/RS/RE tech screen 60min，4 处 bug
*medium · 频率: high（12 帖） · 2025-11 ~ 2026-06-09*

官方题库：transformer-bug-hunt，coding，high，12 帖，60min，roles MLE/RS/RE，tech screen+onsite coding，tags: ml-knowledge/transformer/debugging，首报 2025-11-01，last_asked 2026-06-09。断档期细节：thread-1171609（2026-04-05, MLE 店面《变形金刚抓虫细节问题》）镜像摘要：讨论 transformer 实现中 4 个主要 bug，明确提到 MLP dimensions（FFN 维度错）和 positional encoding initialization（位置编码初始化错）两处；thread-1179644（2026-06-09 MLE onsite）三件套：transformer debugging + cell simulation coding + post-training 细节 deep dive（对口 post-training 背景候选人）。thread-1178049 回复区称其'捉虫'。

**解法**: （我的推断+社区常见 bug 清单）逐模块跑 shape/数值检查：常见 4 类=①attention scale 忘除 sqrt( $d_k$ ) 或 mask 加错；②FFN/MLP 隐层维度写反（ $d_{model}$ ↔4· $d_{model}$ ）；③positional encoding 初始化/相加位置错（如 embed 后忘加或训练中被覆盖）；④residual/LayerNorm 顺序或 softmax 维度错。现场先写 sanity test（小 batch overfitting、输出分布对称性）再定位。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1171609-1-1.html&gt;)

### Classifier with Noisy Annotators / Human-Data 分类器——MLE/RS/RE tech screen 60min
*medium · 频率: high（9 帖） · 2026-01 ~ 2026-05-26*

官方题库：classifier-noisy-annotators，coding，high，9 帖，60min tech screen，roles MLE/RS/RE，tags: ml-knowledge/data-cleaning，last_asked 2026-05-26。断档期细节：thread-1178049（2026-05-26 MLE 视频面过经）两轮 screening 共 4 题，其一为 'human data 分类器'（回复区问是否用 pandas——楼主答有 utility）；thread-1176684（2026-05-14《OAI research technical 整套面经》）镜像摘要含 'noisy data handling'。OJ 镜像：'Find the Incorrect Data Labeler'、'Human Labeling and Training a Classifier (ML Coding)'。与候选人 post-training 数据管线背景高度对口。

**解法**: （我的推断）给多标注员对同一样本的标签：先算 inter-annotator agreement / 每标注员与多数票的一致率找出坏标注员；清洗后训练简单分类器（logistic regression / 小 NN）；进阶讨论 Dawid-Skene 式标注员置信度加权、类别不平衡与confidence interval。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1178049-1-1.html&gt;)

### NumPy 1-NN → 改写成 Wx+b 神经网络 + entropy 计算——MLE/RE 60min
*medium · 频率: high（8 帖） · 2026-01 ~ 2026-05-20*

官方题库：numpy-1nn-wx-b，coding，high，8 帖，60min tech screen+onsite，roles MLE/RE，tags: ml-knowledge/numpy/linear-algebra，last_asked 2026-05-20。断档期细节：thread-1177444（2026-05-20《OpenAI ML Coding》onsite）镜像摘要：'entropy calculation and 1-NN implementations with vectorization and neural networks'——即同场先手写 entropy、再向量化 1-NN、再把 1-NN 改写为神经网络前向（权重构造）。OJ 镜像：'Implement 1-Nearest Neighbor (1NN) Classifier with NumPy; Rewrite as Neural Network Weights'、'Vectorized 1-NN and Neural Network Forward Pass'。

**解法**: （我的推断）1-NN 向量化： $dist^{2}$ =||x||²+||c||²-2xCᵀ 一行广播实现；改写为 NN：W=2C, b=-||c||²，argmax(Wx+b) 等价于最近邻（负平方距离线性化），可讲成'1-NN 是特定权重的线性层'；entropy 部分注意 0·log0=0 与数值稳定。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1177444-1-1.html&gt;)

### Streaming Entropy（流式熵，online + block-wise 更新）——RS/RE tech screen 60min
*medium · 频率: medium（4 帖） · 2026-04-01 ~ 2026-06-22*

官方题库：streaming-entropy，coding，medium，4 帖，60min tech screen，roles RS/RE，tags: numerical-stability/streaming，reported_from 2026-04-01（4 月上新），last_asked 2026-06-22。OJ 镜像标题：'Streaming Entropy with Online and Block-wise Updates'。与 thread-1173645（RS 四轮）中 'entropy calculation task' 呼应——熵计算是 research 轨 AI-coding 题池成员。

**解法**: （我的推断）维护词频 dict + 两个累积量 N 与 S=Σc·log c，则 H=log N − S/N；单元素更新 c→c+1 时 S += (c+1)log(c+1)−c·log c，O(1)；block-wise 合并两个直方图同理可加；讨论 log-sum 数值稳定与大流量下的近似（count-min sketch）。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/company/openai&gt;)

### Autograd / 矩阵乘 forward+backward / Hillis-Steele scan——RS/RE 75min ML coding
*medium-hard · 频率: medium（6 帖） · 2026-02 ~ 2026-05-31*

官方题库：autograd-hillis-steele-scan，coding，medium，6 帖，75min，roles RS/RE，tech screen+onsite，tags: ml-knowledge/autograd/pytorch/parallel-algorithm，last_asked 2026-05-31。佐证：thread-1171922（2026-04-07《OpenAI onsite coding 新题 + 求 75min ML coding》）楼主明言 75min ML coding 与 'linear algebra or autograd' 相关；thread-1173645 回复区问 'AI coding I (autograd) 是 60min 还是 75min'——autograd 是 research 轨 AI coding 题池固定成员。OJ 镜像：'Implement Matrix Multiplication Forward and Backward (Autograd-Style) in PyTorch'。

**解法**: （我的推断）实现 Tensor 类 + 计算图：matmul forward 存 (A,B)，backward dA=dC·Bᵀ, dB=Aᵀ·dC；拓扑序backpropagation；Hillis-Steele 部分=O(log n) 步并行前缀和（每步 stride 翻倍），考并行思维与 work-efficiency 对比 Blelloch scan；用 numpy/pytorch 张量原语表达'并行'。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1171922-1-1.html&gt;)

### OpenAI Research Engineer 全套面经（2026-03）：5 技术轮 + 1 BQ + 1 deep dive，含 transformer debugging
*hard · 频率: single report · 2026-03*

thread-1168926 'OAI Research Engineer 全套面经'（约 2026 年 3 月）：完整 loop = 5 个技术轮 + 1 个 behavioral + 1 个 deep dive，技术轮含 transformer debugging 成分。正文在登录墙后未能获取完整题目清单。（候选人若已有 4 月前整理可能已覆盖此帖；列出备查。）

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1168926-1-1.html&gt;)

### PracHub 2026-04-24 MLE onsite：数值稳定的流式 entropy（logits 分块）+ 向量化 1-NN 及其神经网络等价形式
*medium · 频率: 2 reports (Apr & May 2026) · 2026-04*

Part 1：给 logits z，p=softmax(z)，计算 H(p)=−Σ  $p_{i}$  log  $p_{i}$ ；要求 (a) log-sum-exp 防溢出；(b) 流式：logits 分块到达、全量放不进内存，单 pass、O(1) 状态。关键恒等式：H = log Z −  $E_p$ [z]，Z 为配分函数；流式维护 running max M 和两个累加器  $Σe^{z_{i}−M}$ 、 $Σz_{i}$  $e^{z_{i}−M}$ ，M 更新时 rescale（online softmax 同款技巧）。Part 2： $X_{train}$ (n,d),  $y_{train}$ ,  $X_{query}$ (m,d)：(a) 全向量化 L2 1-NN（禁 Python 循环）：‖q− $x_{i}$ ‖²=‖q‖²+‖ $x_{i}$ ‖²−2q· $x_{i}$ ，一次 matmul + broadcast，argmax 时 ‖q‖² 项可丢；(b) 把 L2 1-NN 表示成 linear layer + softmax（W=2X_train, b=−‖ $x_{i}$ ‖²，argmax 恢复最近邻）；(c) L1 变体为什么仿射层不够——需要 ReLU 网络（分段线性）。Follow-ups：为何 argmax 下 softmax 单调性重要、O(1) 状态维护 logits 的 running variance、L1 网络隐层数随 n,d 如何扩展、训练集固定时的预计算。另一独立上报：'Implement 1NN with NumPy'（2026-05-19，MLE screen）。这与 2025 面经中的 KL divergence/cross-entropy 数学题一脉相承，确认 2026 年 ML 轮仍考数值稳定+向量化基本功。

**解法**: 来源含完整解法（见 detail）。

来源: &lt;[来源链接](https://prachub.com/interview-questions/compute-entropy-and-implement-1-nn&gt;)

### Research Engineer 高难轮（Exponent 详细复盘）：分布式 all_gather + 噪声信道误差界推导；transformer 四区域找 bug + KV cache
*hard · 频率: single detailed report; 各子题均另有多个独立报告 · 2025-06*

Exponent 上的 RE 面经（约 2025 年中，7 周流程，技术轮后被拒）：(1) 最难轮（ML statistics/information theory）：实现多节点 all_gather → 信道有噪声时推导达到目标误差所需轮数的 worst-case 公式 → naive bound 太慢如何改进 → 利用'传的是 float 而非任意实数'设计更优算法（利用浮点表示的有限性）。研究生级信息论，面试官几乎不给提示。(2) ML debugging 轮：transformer 实现有四个标注区域各藏一个 bug，逐一找出；然后实现 KV caching 并讨论需要改哪些部分和进一步优化。(3) 算法轮：'给一个 Python package，找支持它的最新 Python 版本'——分层二分查找（对应已知 version dependency 题）。(4) 手速轮：乐器 beat string → 乐谱记法转换，扩展多乐器、建模休止符（对应 interviewdb 'Beat Notations'）。(5) 系统轮：KV store serializer/deserializer + 关机后持久化恢复 + 关机状态下的查询处理。总体评价：比 FAANG 少提示、不可套路（'less gameable'）。

**解法**: all_gather 噪声题思路：重复传输+多数表决使错误概率指数衰减（Chernoff bound 给轮数 O(log(1/ε))），float 优化利用有限位宽做逐位纠错/校验和而非整值重传（我的推断）。version 题：外层对版本序列分段（major 变更点），内层二分。

来源: &lt;[来源链接](https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2&gt;)

### 新题（2026）：Debug a Concurrent Job Scheduler（MLE 向并发 debug 题）
*medium · 频率: single report each (2026) · 2026-06*

PracHub（MLE，medium）：给一个有 bug 的 Python 并发 job scheduler——多个独立 job 并发执行，每个 job 有 ID、callable、依赖等，要求找出并修复并发 bug。与 coditioning 记录的'race condition 识别与修复'方向一致（read-modify-write 原子性、锁/原子操作修复）。DS 轨还有 'Debug and fix a PyTorch Transformer training loop'（hard：极小 causal decoder LM 的训练循环 debug+优化）。

**解法**: 常见植入 bug：共享 dict/counter 无锁、future 结果未 join、依赖图有环时死锁、异常吞掉导致 job 静默失败；用 threading.Lock/queue.Queue/concurrent.futures 规范化并补上失败重试与超时（我的推断）。

来源: &lt;[来源链接](https://prachub.com/interview-questions/debug-a-concurrent-job-scheduler&gt;)

### MLE/RE 轨 recruiter prompt 原文合集（4-5 月）：ML coding 轮考纲
*medium-hard · 频率: 4 帖互证 · 2026-04-14 ~ 2026-05-07*

三份断档期 prompt/考纲：(1) thread-1174800（2026-04-28, RE 岗）prompt 原文：'60 minute ML coding interview - We'll cover math and coding and have an open-ended discussion/brainstorm about research ideas. A basic understanding of NumPy is [expected]… evaluated on your problem solving ability and ability to write clean, well-designed code.'（数学+编码+研究想法头脑风暴三合一）。(2) thread-1175470（2026-05-03《MLE prompt分享》）镜像摘要考纲：ML coding、debugging、mathematical coding、dataset analysis，核心概念=modern ML architectures 与 PyTorch autograd。(3) thread-1172952（2026-04-14, MLE onsite prompt 求助）镜像摘要：四轮 coding，聚焦 backpropagation、PyTorch、simulation design。另 thread-1175861（2026-05-07）讨论 MLE vs SWE track 怎么选（MLE 轨换掉部分算法轮为 ML coding）。

**解法**: 考纲映射（我的推断）：math+coding=streaming entropy/stopping time；debugging=transformer bug hunt；dataset analysis=noisy annotators；autograd=matmul forward/backward。research ideas 讨论环节提前备 2-3 个 post-training/agentic 方向的开放式想法。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1174800-1-1.html&gt;)

### [RS 挂经] 2026-05-31 全新 RS onsite 题面：推断时间概率、矩阵乘、负载均衡、softmax 实现
*hard · 频率: 3 帖（RS 轨 5 月密集sampling） · 2026-05-14 ~ 2026-05-31*

thread-1178705（2026-05-31《[爱开放]挂经 RS - 新鲜》，MLE 标签/Onsite）镜像 AI 摘要：'detailed probability and coding challenges including inference time, matrix multiplication, load balancing, and softmax implementations'——即四类题：①推断时间（inference time）概率/期望计算（math reasoning 变体）；②矩阵乘实现（autograd 族）；③负载均衡（load balancing，算法/系统混合）；④softmax 数值稳定实现。与 thread-1173645 的 RS 四轮结构（2 AI coding+1 general coding+1 math reasoning）完全吻合，是 5 月底 RS 题池的最新sampling。另 thread-1177093（2026-05-17 Research 岗电面）：coding+ML debugging+SD 三轮，反馈强调 communication；thread-1176684（2026-05-14 research technical 整套）：infectious disease modeling + noisy data handling + matrix operations，附改进建议。

**解法**: （我的推断）softmax：max-shift 数值稳定+log-sum-exp；inference time：排队论/期望递推（如 batch 推理延迟分布）；load balancing：一致性哈希或 power-of-two-choices 并分析尾延迟；矩阵乘：分块+backward 推导。RS 轨四题全部可提前 overfit——原帖作者原话『如果你不能 overfit，这个题目还是很有难度』。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1178705-1-1.html&gt;)

### OpenAI Research Engineer / Applied ML 轨流程变化（2025-12）：新增 general coding + ML coding 双轨编码面
*unknown · 频率: 2 threads (same OP) + 1 corroboration · 2025-12*

csMajors/leetcode 双发帖（2025-12）：'Recently they changed process to include both general coding and ml coding'——RE 轨现在同时考通用编码和 ML 编码。发帖人询问 general coding 是否与 SWE 相同（评论区确认走同一题库方向）。结合其他情报：ML coding 部分为实现训练/推理组件（社区通识：如 attention/sampler/数据管线），60min DSA 店面（intern/NG RE 轨'no ML knowledge'）。AI research intern 轨（2026-05 帖）：'不考 leetcode，考 conceptual ML + 讲解简历上的项目'。注意区分轨道。

**解法**: 我的推断：ML coding 按业界惯例练——numpy/torch 手写 multi-head attention、KV cache sampling循环、BPE tokenizer、简单训练 loop debug；这与 GDM/Meta 的 ML coding 轮同构。

来源: &lt;[来源链接](https://www.reddit.com/r/csMajors/comments/1ps0cd2/openai_interview_for_research_engineer_roles/&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
