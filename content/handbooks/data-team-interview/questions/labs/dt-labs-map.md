---
id: dt-labs-map
section: labs
order: 1
level: S
title: 各家 data 岗公开在问什么？
quick: >-
  这张卡按题型列出各家 data 岗公开在问什么，大多是同一组数据方法：网页抽取与 deduplication、data mix、代码执行合成、工具与 GUI
  trajectories、偏好标注、诚实评测，以及 data leakage 和 synthetic data
  坍缩。每题都先给选择，再讲方法为什么有效、哪里要调，最后说数据从哪来、谁来验证；涉及用户日志的题，先确认这类来源能不能用。
companies:
  - apple
tags:
  - Apple
  - OpenAI
  - Meta
  - Anthropic
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      Novel Data Mining from Large Unlabeled Datasets (AceOffer / OpenAI
      reports)
    url: >-
      https://aceoffer.app/interviews/oai_novel_data_mining_from_large_unlabeled_datasets_system_desig
    type: secondary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: 'DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining'
    url: 'https://arxiv.org/abs/2305.10429'
    type: primary
  - title: Constitutional AI
    url: 'https://arxiv.org/abs/2212.08073'
    type: primary
  - title: DataComp-LM
    url: 'https://arxiv.org/abs/2406.11794'
    type: primary
  - title: Tesla AI
    url: 'https://www.tesla.com/AI'
    type: primary
  - title: 'Tulu 3: Pushing Frontiers in Open Language Model Post-Training'
    url: 'https://arxiv.org/abs/2411.15124'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Let's Verify Step by Step
    url: 'https://arxiv.org/abs/2305.20050'
    type: primary
  - title: Berkeley Function Calling Leaderboard
    url: 'https://gorilla.cs.berkeley.edu/leaderboard'
    type: primary
  - title: LiveCodeBench
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: >-
      RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement
      Learning
    url: 'https://arxiv.org/abs/2410.02089'
    type: primary
  - title: 'τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains'
    url: 'https://arxiv.org/abs/2406.12045'
    type: primary
  - title: Deliberative Alignment
    url: 'https://arxiv.org/abs/2412.16339'
    type: primary
  - title: 's1: Simple test-time scaling'
    url: 'https://arxiv.org/abs/2501.19393'
    type: primary
  - title: 'Classifier Training and Analysis (AceOffer, OpenAI reports)'
    url: 'https://aceoffer.app/interviews/oai_classifier_training_and_analysis'
    type: secondary
  - title: 'Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)'
    url: >-
      https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: >-
      Sleeper Agents: Training Deceptive LLMs that Persist Through Safety
      Training
    url: 'https://arxiv.org/abs/2401.05566'
    type: primary
  - title: 'The Curse of Recursion: Training on Generated Data Makes Models Forget'
    url: 'https://arxiv.org/abs/2305.17493'
    type: primary
  - title: Textbooks Are All You Need
    url: 'https://arxiv.org/abs/2306.11644'
    type: primary
  - title: LiveBench
    url: 'https://arxiv.org/abs/2406.19314'
    type: primary
---

这张卡当索引用：按「别处怎么问」找到题型，看一眼答题要点，再点进右边的卡看具体数字和论文。Panel 和 Director 常借别家的公开题型，追问你是不是懂数据方法本身。

每道题的答法都差不多：先说你会怎么选，再讲方法为什么有效、什么情况下要调整。pre-training 题重点讲输入来源和过滤；post-training 题还要讲 trajectories 从哪来、奖励由谁验证。涉及用户日志的设计题，先确认这类来源能不能用，见 `dt-privacy-feedback`。`realInterview` 只标在能核对到来源的那几张卡上，其余来自论文和公开设计题。

| 别处怎么问 | 公开来源 | 答题要点 | 卡 |
| --- | --- | --- | --- |
| 海量无标数据里挖新的、高质量的 | OpenAI phone screen，AceOffer 记过多次 | seed 来自评测失败和许可集；分类器打分，迭代筛 | `dt-novel-bootstrap` |
| 设计用户对话 → SFT pipeline | OpenAI DE 公开练习题 | 先查训练许可；没有许可就换研究集 / 合成复现 | `dt-userlog-contrast` |
| 全局 MinHash 是不是更好 | FineWeb ablation study | 跨快照 deduplication 会 false rejection 反复出现的好页 | `dt-global-dedup` |
| mix 能不能自动学 | DoReMi（Google） | 小代理给初值，下游 evaluation slices 上再定 | `dt-doremi-mix` |
| pre-training 末段抬代码 / 数学 | Llama 3 annealing | 末段上 sampling 代码 / 数学；评测 training set 不进 | `dt-llama-anneal` |
| 质量分类器用合成标签 | Llama 3 / Phi / FineWeb-Edu | 按语言做 calibration，代码桶不用网页分类器 | `dt-quality-clf-synth` |
| 开源合成集自称 GSM8K +15% | Anthropic 风格陷阱题 | 先对 evaluation gate 做 n-gram / embedding，再谈质量 | `dt-synth-bench-trap` |
| RLAIF / 宪法反馈自循环 | Constitutional AI | judge 和生成器分家，human evaluation evaluation gate | `dt-rlaif-loop` |
| RLHF 奖励不诚实 / sycophancy | Anthropic RE 面经 | 数据里造「短而直」对，见长度卡 | `dt-sycophancy-data` |
| 车队 trigger / 影子模式 | Tesla / AV 设计题 | LLM 版用评测失败和低置信触发收集 | `dt-trigger-ood` |
| HTML 抽取、行级 deduplication | Llama 3 §3.1 | 行级 deduplication 会 false rejection 好句，按内容类型检查 | `dt-llama-extract` |
| 按权重的 DataBatcher | Anthropic CoderPad（AceOffer） | token 配额 + offset checkpoint，对上温度 mix | `dt-weighted-batcher` |
| 从 X 时间线灌 Grok | xAI 公开设计题 | 按时间分区的流式 pipeline；先过许可 | `dt-x-feed` |
| 开源网页集从 WET 起步 | DataComp-LM | 先问 WARC 还是 WET，再谈分类器 | `dt-dclm-wet` |
| safety evaluation gate 被训练看见了 | Anthropic 风格治理题 | 先停发布，换时间切 / 私有题 | `dt-contam-hold` |
| 离线 DPO 对过期 | Tulu 3 on-policy 偏好 | current policy 重采；可验证走 rule-based reward | `dt-onpolicy-pref` |
| edited > chosen > rejected，丢掉差不多的对 | Llama 3 §4 | cohesion / 弱档不进 DPO | `dt-llama-edit-pref` |
| 过程监督标签怎么采 | Let's Verify；R1 不用神经 PRM | 可执行用规则；过程假不进 CE | `dt-prm-steps` |
| RLVR / GRPO 的数据是什么 | DeepSeek-R1、Tulu 3 | 数据是 prompt + grader，没有 preference pairs | `dt-rlvr-data` |
| fine-tuning 后 value drift 怎么量 | Anthropic RE CodeSignal | KL + 行为套件 + 安全税 + human evaluation 分维 | `dt-value-drift` |
| 工具对话按段还是按跳标 | Llama 3 工具节 | message 级；工具返回不能改 | `dt-tool-turn-pref` |
| 代码合成改自己的单测 | Llama 3 §4.3 | 先冻测试；改测试的 trajectories 隔离 | `dt-code-exec-synth` |
| 开源合成自称 HumanEval +9% | 代码 evaluation leakage 论文、LiveCodeBench | 时间切新题；SWE 再去 issue / 测试文件 | `dt-code-bench-bleed` |
| SWE 过测 trajectories 整段进 SFT | SWE-Prime、SWE-Hero | 成功仍可能脏；改测试文件就扔 | `dt-swe-success-noise` |
| 目录里没有能用的工具还是调了 | BFCL irrelevance | 造「不该调」和「先查再调」 | `dt-tool-irrelevance` |
| 换工具名就不会了 | PIPE / trajectories SFT | 别名评测；示范长得像产品 schema | `dt-tool-alias` |
| 终局状态对、中间少一次只读 | BFCL V3 | must_call + 参数血缘 | `dt-agent-state-path` |
| 公开测当对话、私有测当奖 | RLEF | 两套测分哈希；stderr 不进 CE | `dt-rlef-split` |
| 工具返回里写「忽略指令」 | OpenAI instruction hierarchy | observation 按低权限内容处理 | `dt-tool-inject` |
| 屏幕点击 trajectories 整段进 SFT | OSWorld / AndroidWorld | 对得上当时的树；过期帧扔掉 | `dt-gui-traj` |
| 没有引用怎么标事实 | WebGPT | 浏览 trajectories 和带出处答案分开 | `dt-webgpt-cite` |
| post-training 再灌新百科 | Llama 3 factuality probe | 对齐「会不会」，知识仍在 pre-training | `dt-knows-what` |
| 有搜索就搜 | Llama 3 工具节 | 必须搜 / 禁止搜 / 可搜可答三桶 | `dt-when-to-search` |
| 客服过一次库状态 | τ-bench $\mathrm{pass}^{k}$ | 跨次稳定才进 SFT；政策单独 grader | `dt-tau-passk` |
| 网上长思考当 distillation 集 | R1 800k | 只留对的；混语言丢掉；small model 只 SFT | `dt-r1-distill` |
| inference 时贴整份安全政策 | deliberative alignment | SFT 撕掉 spec，逼模型回忆条款 | `dt-deliberate-spec` |
| 网页点击序列对齐人 | WebArena | 看功能 assertion，失败 replay 不当正例 | `dt-webarena-traj` |
| IFEval 541 条写进 SFT | Google / Tulu RLVR-IFeval | 评测留下；同族约束叠到自己的混 | `dt-ifeval-overlay` |
| 推理 SFT 越大越好 | s1K | difficulty / diversity / quality criteria；1k 对已对齐 student | `dt-s1k` |

第二张表是分类器、事实评测和数据治理这几类。这些题同样要讲清质量怎么查、数据从哪来。

| 别处怎么问 | 公开来源 | 答题要点 | 卡 |
| --- | --- | --- | --- |
| 现场训分类器、摸数据集 | OpenAI 高频 ML coding，AceOffer 19 次 | 先切集再拟合；正例来自评测失败和许可集 | `dt-oai-classifier` |
| 聊天日志里挖新概念的代表图 | OpenAI 系统设计 | seed 用新出现的实体和评测失败；data quality checks 先于新颖度 | `dt-chatlog-concept` |
| 用户上传工具照片，怎么改进识别训练 | OpenAI ML 轮，AceOffer 6 次 | 许可目录图、受控拍摄 + 验证合成 | `dt-tool-photo` |
| 模型是诚实还是仅仅流畅 | Anthropic RE 电面 | 造「流畅但错 / 短而对」；忠实维单报 | `dt-honest-fluent` |
| 读过 Sleeper Agents 吗，后门怎么清 | Anthropic 论文；面经默认你读过 | 当数据事故拦植入；安全训清不掉 | `dt-sleeper-data` |
| 用 token logprob 做二分类 | Anthropic MLE | Yes/No 一个 token；阈值按 evaluation slices calibration | `dt-llm-clf-logprob` |
| 评测台当成生产系统来设计 | DeepMind / Gemini 评测岗 | 五元组哈希；2 点涨在误差内 | `dt-eval-harness` |
| leakage 和记忆怎么分开 | ConTAM；Gemini pre-training 评测 JD | 命中不等于涨分；金丝雀 + 扰动题 | `dt-canary-leak` |
| 反复用 synthetic data 训练会不会塌 | DeepSeek data chemistry；Shumailov | 每代留许可源；只留过 oracle 的 | `dt-synth-collapse` |
| Phi 教科书数据好在哪 | Phi-1 / Phi-4 | 质量是轴，规模不取消；teacher leakage 单独查 | `dt-phi-textbook` |
| preference data 一致率低怎么修 | Cohere / xAI；InstructGPT | 先改协议；可验证走 rule-based reward | `dt-pref-collect` |
| 没有 gold labels、专家很贵，评测怎么造 | Cohere / Harvey | 自动题先上；人只标 calibration 和不知道的轴 | `dt-eval-no-gold` |
| 榜涨了用户说更差 | Cognition 等 agent 岗；OpenAI 停报 Verified | 先查脏、偏、错题、偏分布 | `dt-bench-vs-user` |
| Prompt、RAG 还是 fine-tuning | OpenAI / Cohere / Mistral | 私有知识走 RAG；行为走 post-training | `dt-prompt-rag-ft` |
| fine-tuning 后旧能力掉了 | Mistral forgetting | mix 留 regression data replay；KL 代替不了数据 | `dt-forget-sft` |
| 线上评测记什么、怎么 A/B | Perplexity / Cohere | 线上用来发现失败；补数据用许可复现 | `dt-online-eval` |
| 样本轴 double descent 作业 | Anthropic take-home | 加样本不单调；对照仍是只换数据 | `dt-sample-descent` |

## 追问

**pre-training 这组先刷哪几张？**
先闭卷讲 OpenAI bootstrap 和 FineWeb global deduplication。

**post-training 这组怎么排？**
先按 Panel 的偏好轮刷完，再补代码和 agent：执行合成会不会改测试、RLEF 公私测、SWE 成功 trajectories、BFCL 不该调、工具别名、中间少调只读、工具注入、该不该搜。

**第二张表先刷哪几张？**
分类器笔试、诚实 vs 流畅、评测台、Prompt vs RAG vs fine-tuning，这几张跨公司重复最多。

**网页 / GUI trajectories 和推理 distillation 怎么配着练？**
trajectories 质量和 `dt-traj-quality` 对照着刷；R1 distillation 和 s1K 和 `dt-synth-reasoning` 对照着刷。

**别家题答完，要不要评价他们该不该用用户日志？**
不用。说清各自的数据使用条件就行，重点放在方法本身。
