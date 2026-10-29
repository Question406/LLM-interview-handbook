---
id: drustz-88dc6bc9f25068c7b4
section: collections
order: 46
level: A
title: 通用 ML 理论 + ML System Design 资源库 · 流程与情报
quick: 作者文档章节 · 通用 ML 理论 + ML System Design 资源库 · 流程与情报
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md
    type: primary
---
## 流程与情报

### 2026 年 AI labs/高薪公司面试大盘（ExperiencedDevs 讨论）：店面要求 100% 全对、多段实践题取代单题 leetcode、Python 速度成硬约束
*unknown · 频率: high-engagement discussion (corroborates 10+ threads) · 2026-06*

r/ExperiencedDevs 2026-06 高质量讨论帖（7YoE 双 FAANG，刚挂 Anthropic/Databricks）：(1) >&#36;400-500K 岗位现在要求店面每部分（含'optional'）全对，'差一个 edge case 就挂'，代码必须可运行且输出正确、零容错——归因于裁员潮候选人过剩+AI 作弊泛滥；(2) 趋势：从单题 leetcode 转向 5 段渐进 practical 多部分题（各大 lab 一致），必须秒出解+零 debug 才能写完；(3) 用 Java 做多段 OA 是自杀（类型样板太多），Python 是速度刚需；(4) referral 只保面试不保 offer；networking/跟人跳槽才是 senior+ 的真实通道。与 Anthropic/OpenAI 各 thread 的观察完全一致。

来源: &lt;[来源链接](https://www.reddit.com/r/ExperiencedDevs/comments/1uky9ws/2026_interview_experience/&gt;)

### deep-ml.com 站点结构、题库分类与难度体系（爬取总览）
*unknown · 频率: 平台题库结构（1127 题，抓取日期 2026-07） · 2026-07*

deep-ml.com 是一个专注 ML 的开源刷题平台（类比 LeetCode 但全是 ML 题），题目在浏览器内用 Pyodide 跑 Python 评测。抓取自 sitemap.xml：站点共有约 1127 道 problems（/problems/{id}，id 连续到 1132）、34 个 labs（/labs/{id}，真实数据集项目）、articles、collections、learn（学习路径）、contests、leaderboard、jobs、premium、interview-prep。每题有难度标签，取值为 easy / medium / hard（页面 meta 描述里明确写 'a easy/medium/hard &lt;Category&gt; coding challenge'）。按类别统计（对全部 1127 题的 SSR meta 解析）：Deep Learning 278、Machine Learning 255、Reinforcement Learning 192、NLP 71、Linear Algebra 50、Computer Vision 32、pytorch 30、tinygrad 30、sql 26、Probability 17、Statistics 14、Optimization 14、MLOps 14、Inference 12、Data Structures 12、Algorithms 11、triton 10、LLM 9、Calculus 9，另有少量 Information Theory / Game Theory / Financial ML 等。官方对外宣传的主类别是 Linear Algebra、Machine Learning、Deep Learning、NLP、Computer Vision（见 llms.txt）。约 164 题在开源仓库 github.com/Open-Deep-ML/DML-OpenProblem 有完整题干+solution.py+learn.md+tests，其余高编号新题目前只有站点上题干。每题 URL 形如 [来源链接](https://www.deep-ml.com/problems/107) 。

**解法**: 抓取旁路：站点是 Next.js 客户端渲染，题库列表走受保护的 Firestore，但每个 /problems/{id} 页面的 &lt;meta name=description&gt; 做了 SSR，含 '标题 + 难度 + 类别'，可批量 curl 全部 id 解析。robots.txt 显式欢迎 GPTBot/ClaudeBot 并提供 [来源链接](https://www.deep-ml.com/llms.txt) 与 llms-full.txt。sitemap: [来源链接](https://www.deep-ml.com/sitemap.xml)

来源: &lt;[来源链接](https://www.deep-ml.com/problems&gt;)

### Interview Prep 页面（/interview-prep）内容与运作方式
*unknown · 频率: 官方功能页（lastmod 2026-06-21） · 2026-06*

页面标题 'Interview Prep: Company-Specific ML Interview Preparation'。定位：'Pick a company, choose a role, and train for it.' 每个公司 track 提供：(1) 该公司面试流程与轮次说明；(2) 该公司筛选简历时看重的 resume projects（对应站点 Labs/Projects）；(3) 限时 mock interview（timed mock interviews）；(4) 按 readiness 追踪的分阶段学习计划（paced study plan，从 2 周到 3 个月）。页面从 Firestore 'companies' 集合动态加载公司卡片（含 company_name、logo、role_count / roles），并把用户进度存到 'user_interview_prep' 集合。公司 track 页面 URL 形如 /interview-prep/{slug}（如 /interview-prep/openai、/interview-prep/anthropic、/interview-prep/google-deepmind、/interview-prep/google、/interview-prep/meta 均返回 200）。注意：具体公司列表、轮次文案、mock 题目均由登录+受保护的 Firestore 驱动，未登录时抓不到明细（见 source_summary）。

**解法**: 公司 track 具体题单/轮次需登录；但站点用公开的 Collections 承载各公司 interview-prep 题单（见下条），可作为等价替代来源。

来源: &lt;[来源链接](https://www.deep-ml.com/interview-prep&gt;)

### 公司专属 Interview Prep 合集（Collections）——含 OpenAI / Anthropic / DeepMind
*mixed · 频率: 3 家目标公司均有专属合集 · 2026-07*

deep-ml 的 /collections 里有专门的公司面试合集（每个合集是一组精选题目+徽章）。与候选人目标直接相关的有：
- OpenAI Research Scientist Interview Prep → [来源链接](https://www.deep-ml.com/collections/OpenAI%20Research%20Scientist%20Interview%20Prep)
- Anthropic Interview Prep → [来源链接](https://www.deep-ml.com/collections/Anthropic%20Interview%20Prep)
- DeepMind Interview Prep → [来源链接](https://www.deep-ml.com/collections/DeepMind%20Interview%20Prep)
- MLE Interview Prep → [来源链接](https://www.deep-ml.com/collections/MLE%20Interview%20Prep)
- Data Science I Interview Prep → [来源链接](https://www.deep-ml.com/collections/Data%20Science%20I%20Interview%20Prep)
每个合集页 SSR meta 为 'Complete the "X" collection on Deep-ML. Practice curated machine learning problems and earn your badge.' 合集内的具体题目清单由受保护的 Firestore 'collections' 集合加载（未登录 403），无法从 HTML 直接抓到成员题 id。合集完整列表见 sitemap.xml。

**解法**: 合集成员题 id 抓不到（Firestore 权限拒绝）。但根据合集主题，OpenAI/Anthropic/DeepMind 合集几乎必然由下面列出的 attention/transformer、optimizer、loss、sampling、RLHF/GRPO/DPO、KV-cache 类题目构成——可按下列 topic 题单自行覆盖。

来源: &lt;[来源链接](https://www.deep-ml.com/collections&gt;)

### 与 LLM/post-training 相关的主题学习路径（Collections / learn）
*mixed · 频率: 官方主题合集 · 2026-07*

从 sitemap 抓到的、与 LLM post-training / agentic / 深度学习强相关的主题合集（学习路径），可作为分主题刷题的 curriculum：
- Attention Is All You Need；Attention in Transformers: From Queries to Multi-Head；Inside a Transformer: Embeddings, Attention, and Softmax；How LLMs Work: From Next-Token Prediction to Transformers
- Build GPT from Scratch: Karpathy Walkthrough；GPT-2 to gpt-oss；Karpathy makemore 系列（Bigram / MLP Part 2 / Activations,Gradients&BatchNorm / WaveNet Part5 / Backprop Ninja）；Micrograd Builder；Karpathy's Micrograd
- Deconstructing GRPO: From RAFT to Reinforce-Rej；Fine-Tuning LMs from Human Preferences；Reinforcement Learning: An Introduction（Sutton&Barto 对应题）
- DeepSeek R1；DeepSeek's Multi-Head Latent Attention Explained；DeepSeek-V4；Llama 3；SPARSELY GATED MoE
- optimizers；Muon Optimizer: From Motivation to NumPy Implementation
- Inference Engineering；VLLM；Quantization Basics: Why, When, and How；LLM Evaluation Methods
- PyTorch Basics；Tinygrad Essentials；Triton Essentials
合集 URL 形如 [来源链接](https://www.deep-ml.com/collections/optimizers) （名称含空格需 URL 编码）。学习路径入口 [来源链接](https://www.deep-ml.com/learn) 。

**解法**: 这些合集是把下方 topic 题单按论文/课程重新编排；候选人 post-training 背景优先做：Deconstructing GRPO、Fine-Tuning LMs from Human Preferences、Inference Engineering、Muon Optimizer、Attention 系列。

来源: &lt;[来源链接](https://www.deep-ml.com/collections&gt;)

### Hack2Hire 题库结构与旁路抓取说明（供后续复用）
*unknown · 频率: n/a · 2026-07*

站点结构：公司页路径 /question-bank/companies/{company}/{coding-questions|system-design|ml-system-design|sql-questions|object-oriented-design|interview-resources}。有效 company slug 含 openai、anthropic、google（DeepMind 无独立数据，deepmind/google-deepmind 页面为空壳，实际归 google）。题目详情正文对未登录用户 isLocked=true 只给预览，但每题的 AI insights（quickSummary、whatThisTests、commonPatterns、hints、likelyInterviewFollowUps）、难度、stages(OA/SCREENING/ONSITE)、各公司频率(1-10)、首发/最近报告日期均在 Next.js SSR flight 数据中公开可取。System Design/ML-SD 正文与代码模板需登录，仅标题/元数据可得。后端 API：[来源链接](https://api.hack2hire.com/algro/v1（如) GET /company-directory 列全部公司；GET /post/filter?companyTags={ENUM}&page=1&perPage=999 列某公司全部题，companyTags 用大写枚举如 OPENAI/ANTHROPIC/GOOGLE）。/coding/{id} 详情需 SSR key（401），故详情走 practice 页 SSR。

**解法**: 抓取法：curl practice 页 → 提取 self.__next_f.push 里的 flight 字符串 → unicode_escape decoding → 取 codingQuestionSsrResponse 平衡括号 JSON（含 description 预览 + insights）。Blog 正文在 flight 的 'NN:T{hexlen},' 文本块里。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank&gt;)

### Mimansa Jaiswal《LLM (ML) Job Interviews - Resources》：面试资源与流程索引页
*unknown · 频率: unknown · 2025*

研究者整理的 LLM/ML 求职资源索引（题库、公司流程、准备清单的元列表），可作为继续深挖 OpenAI/Anthropic/GDM 各家 RS/RE 流程信息的入口。本次任务主要用其定位题库来源；页面本身无具体题目。

来源: &lt;[来源链接](https://mimansajaiswal.github.io/posts/llm-ml-job-interviews-resources/&gt;)

### Yuan Meng 'MLE Interview 2.0': frontier-lab round taxonomy (LLM coding, ML infra design, research talk)
*unknown · 频率: first-person + aggregated · 2026-01*

First-person 2025-2026 loop taxonomy: frontier labs (OpenAI, Anthropic, DeepMind, xAI) add non-standard rounds — multi-level OOP (Time-Based KV Store, In-Memory Database, Circuit Breaker w/ rate limiting, LRU/LFU cache, Thread Pool/Task Scheduler; signal = thread safety + production thinking); LLM coding (implement Transformer encoder/decoder, LoRA, KV cache, beam search, autograd internals — 'even daily PyTorch users rarely know how computation graphs are built'); ML infra design (feature stores, distributed training, checkpointing, continuous retraining, serving: feature fetching, latency reduction, caching, logging); research presentation (job-talk style, ~10 slides defending technical work); project deep dives. ML model design framework: problem framing → high-level online/offline paths → retrieval → L1/L2 ranking → deep dives (scaling, cold start, positional bias, diversity). Company notes: OpenAI/Roblox/Databricks/Notion demand OOP excellence; Google random-hard LC; Meta AI-assisted coding round. Prep advice: only start after screens confirm the loop; NeetCode 250, UDL book ch.1-9+11-12, PyTorch-in-one-hour, Deep-ML.com.

来源: &lt;[来源链接](https://www.yuan-meng.com/posts/mle_interviews_2.0/&gt;)

### Curated resource maps for frontier-lab MLE/RS prep (Mimansa Jaiswal; Evidently AI case-study DB)
*unknown · 频率: n/a (meta-resources) · 2025*

Mimansa Jaiswal's post-interview resource list (built while interviewing for LLM/ML roles): MLSD via Educative Grokking-ML free section; LLM internals via Transformer Family v2 (Lilian Weng), Transformer Math 101 (EleutherAI), JAX scaling book (jax-ml.github.io/scaling-book — TPU/GPU parallelism for training/inference); RLHF via Chip Huyen RLHF post + HF 'N implementation details of RLHF with PPO' + '37 PPO implementation details' + GRPO guide (yugeten); inference/decoding via Chip Huyen sampling post; retrieval via yuan-meng EBR/LTR/negative-sampling posts + Weaviate RAG eval; ML coding via alirezadir notebooks, Hands-On-LLMs, deep-ml.com — noting interviews asked FNN/LSTM/RNN from scratch and cached/grouped/multi-head attention implementations; her design-round opener pattern: offer discriminative vs generative paths and let interviewer choose. Evidently AI database: 800 real ML/LLM system design case studies from 150+ companies, filterable by industry/use-case (https://www.evidentlyai.com/ml-system-design) — best source of real-world grounding examples to cite in SD answers.

来源: &lt;[来源链接](https://mimansajaiswal.github.io/posts/llm-ml-job-interviews-resources/&gt;)

### Sundeep Teki《AI Research Engineer Interview Guide: OpenAI, Anthropic, DeepMind (2026)》要点
*hard · 频率: 聚合指南 · 2026*

三家对比：OpenAI——4-6 小时 onsite（1-2 天），端到端 6-8 周，流程去中心化可同时考虑多岗位，“明显更偏 coding 而非 research”，含 coding/system design/ML debugging/research discussion/behavioral；Anthropic——平均 ~20 天，90 分钟 CodeSignal 需 100% 正确才能进入下一轮，面试周期内做严格 reference check，重 FAANG 式 system design + AI 研究答辩 + 伦理口试；GDM——录取率 <1%，含 rapid-fire quiz 考本科级基础，“像 PhD 答辩混合严格工程考试”，资深工程师也常挂 quiz。通用题型：Transformer 是“AI 面试的 Hello World”——手写 Multi-Head Attention、完整 Transformer layer、NN+训练循环 from scratch、不用 sklearn 写 K-means、纯 Python 算 AUC；ML Debugging 轮格式：“给一个能跑但不学习的 notebook”，典型 bug：broadcast 错误、softmax 维度错、CrossEntropyLoss 前重复 softmax、忘 zero_grad、dataloader shuffle 问题；ML system design 标准题：“How would you train a 100B+ parameter model?”（必须讲 data/pipeline/tensor 三种并行及硬件约束下的选择）；推理优化：KV caching、INT8/FP8 量化 trade-off、speculative decoding（2-3x 加速）；RAG 全架构；research discussion：提前 2-3 天给论文，讨论贡献/方法/结果/局限/扩展。行为面红旗：lone wolf、傲慢、只想发财。

来源: &lt;[来源链接](https://www.sundeepteki.org/advice/the-ultimate-ai-research-engineer-interview-guide-cracking-openai-anthropic-google-deepmind-top-ai-labs&gt;)

### letsdatascience 三大 lab 招聘流程与进入策略（含 GDM 7-9 轮结构）
*unknown · 频率: 聚合指南 · 2025~2026*

GDM：7-9 轮、4-6 周——recruiter screen → 1-3 轮 LC 式 coding → ML theory（Transformers、finetuning 方法、大模型训练、Gemini/DeepSeek 等新架构）→ research discussion（详细走查自己的技术工作）→ team fit。RS 必须 PhD+顶会发表；RE 无发表硬性要求（Gordic 案例）。OpenAI：6 阶段（简历→recruiter 30min→coding 60min→project review 60min→system design 60min→onsite 4-6h），4-6 周；system design 重实际 ML infra：real-time feature stores、red-teaming pipelines、大规模部署；40 万+年申请量；Residency 项目面向数学/物理/神经科学转行者。Anthropic：6 阶段（recruiter→90min CodeSignal→HM deep dive→onsite 4h 4-6 轮：coding/system design/ML theory/AI safety reasoning→team matching 2-4 周→reference+offer），3-8 周；~50% technical staff 无 PhD；safety 认同必须真实。跨 lab：内推者拿 offer 概率 ~7x（Pinpoint 450 万申请数据）；给出 6-12 个月建立 visible work→社区参与→内推的路线图。

来源: &lt;[来源链接](https://letsdatascience.com/blog/how-to-land-a-job-at-openai-anthropic-or-google-deepmind&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/theory-and-mlsd.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md)。作者整理资料；许可和第三方来源范围见阅读指南。
