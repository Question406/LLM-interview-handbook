---
id: dt-labs-map
section: labs
order: 1
level: S
title: 各家 data 岗公开在问什么？
quick: "各家公开题型大多考同一组数据方法：网页抽取与去重、配比、代码执行合成、工具与 GUI 轨迹、偏好标注、诚实评测，以及数据泄漏和合成数据坍缩。答法是先给选择，再讲方法为什么有效、哪里要调整，最后说明数据从哪来、由谁验证。涉及用户日志的题，先确认这类来源能不能用。"
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
updatedAt: 2026-10-12
sources:
  - title: Novel Data Mining from Large Unlabeled Datasets (AceOffer / OpenAI reports)
    url: https://aceoffer.app/interviews/oai_novel_data_mining_from_large_unlabeled_datasets_system_desig
    type: secondary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: "DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining"
    url: https://arxiv.org/abs/2305.10429
    type: primary
  - title: Constitutional AI
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: Tesla AI
    url: https://www.tesla.com/AI
    type: primary
  - title: "Tulu 3: Pushing Frontiers in Open Language Model Post-Training"
    url: https://arxiv.org/abs/2411.15124
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: "Let's Verify Step by Step"
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: Berkeley Function Calling Leaderboard
    url: https://gorilla.cs.berkeley.edu/leaderboard
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: "RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement Learning"
    url: https://arxiv.org/abs/2410.02089
    type: primary
  - title: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
    url: https://arxiv.org/abs/2406.12045
    type: primary
  - title: Deliberative Alignment
    url: https://arxiv.org/abs/2412.16339
    type: primary
  - title: "s1: Simple test-time scaling"
    url: https://arxiv.org/abs/2501.19393
    type: primary
  - title: Classifier Training and Analysis (AceOffer, OpenAI reports)
    url: https://aceoffer.app/interviews/oai_classifier_training_and_analysis
    type: secondary
  - title: Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)
    url: https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: "Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training"
    url: https://arxiv.org/abs/2401.05566
    type: primary
  - title: "The Curse of Recursion: Training on Generated Data Makes Models Forget"
    url: https://arxiv.org/abs/2305.17493
    type: primary
  - title: Textbooks Are All You Need
    url: https://arxiv.org/abs/2306.11644
    type: primary
  - title: LiveBench
    url: https://arxiv.org/abs/2406.19314
    type: primary
---

Panel 和 Director 常借别家的公开题型，追问你是否真正理解数据方法。下面两张表按题型列出公开来源和答题要点，具体数字和论文解释放在各题里。

每道题的答法是：先说你会作什么选择，再解释方法为什么有效、在什么情况下要调整。预训练题重点检查输入来源和过滤；后训练题还要检查轨迹从哪里来，以及由谁验证奖励。涉及用户日志的设计题，先确认这类来源能不能用，见 `dt-privacy-feedback`。`realInterview` 只标在能核对到来源的那几张卡上，其余来自论文和公开设计题。

| 别处怎么问 | 公开来源 | 答题要点 | 卡 |
| --- | --- | --- | --- |
| 海量无标数据里挖新的、高质量的 | OpenAI phone screen，AceOffer 记过多次 | 种子来自评测失败和许可集；分类器打分，迭代筛 | `dt-novel-bootstrap` |
| 设计用户对话 → SFT 管线 | OpenAI DE 公开练习题 | 先查训练许可；没有许可就换研究集 / 合成复现 | `dt-userlog-contrast` |
| 全局 MinHash 是不是更好 | FineWeb 消融 | 跨快照去重会误杀反复出现的好页 | `dt-global-dedup` |
| mix 能不能自动学 | DoReMi（Google） | 小代理给初值，下游切片上再定 | `dt-doremi-mix` |
| 预训练末段抬代码 / 数学 | Llama 3 annealing | 末段上采样代码 / 数学；评测训练集不进 | `dt-llama-anneal` |
| 质量分类器用合成标签 | Llama 3 / Phi / FineWeb-Edu | 按语言校准，代码桶不用网页分类器 | `dt-quality-clf-synth` |
| 开源合成集自称 GSM8K +15% | Anthropic 风格陷阱题 | 先对门禁做 n-gram / 嵌入，再谈质量 | `dt-synth-bench-trap` |
| RLAIF / 宪法反馈自循环 | Constitutional AI | judge 和生成器分家，人评门禁 | `dt-rlaif-loop` |
| RLHF 奖励不诚实 / 谄媚 | Anthropic RE 面经 | 数据里造「短而直」对，见长度卡 | `dt-sycophancy-data` |
| 车队 trigger / 影子模式 | Tesla / AV 设计题 | LLM 版用评测失败和低置信触发收集 | `dt-trigger-ood` |
| HTML 抽取、行级去重 | Llama 3 §3.1 | 行级去重会误杀好句，按内容类型检查 | `dt-llama-extract` |
| 按权重的 DataBatcher | Anthropic CoderPad（AceOffer） | token 配额 + offset checkpoint，对上温度 mix | `dt-weighted-batcher` |
| 从 X 时间线灌 Grok | xAI 公开设计题 | 按时间分区的流式管线；先过许可 | `dt-x-feed` |
| 开源网页集从 WET 起步 | DataComp-LM | 先问 WARC 还是 WET，再谈分类器 | `dt-dclm-wet` |
| 安全门禁被训练看见了 | Anthropic 风格治理题 | 先停发布，换时间切 / 私有题 | `dt-contam-hold` |
| 离线 DPO 对过期 | Tulu 3 on-policy 偏好 | 当前策略重采；可验证走规则奖励 | `dt-onpolicy-pref` |
| edited > chosen > rejected，丢掉差不多的对 | Llama 3 §4 | cohesion / 弱档不进 DPO | `dt-llama-edit-pref` |
| 过程监督标签怎么采 | Let's Verify；R1 不用神经 PRM | 可执行用规则；过程假不进 CE | `dt-prm-steps` |
| RLVR / GRPO 的数据是什么 | DeepSeek-R1、Tulu 3 | 数据是 prompt + grader，没有偏好对 | `dt-rlvr-data` |
| 微调后 value drift 怎么量 | Anthropic RE CodeSignal | KL + 行为套件 + 安全税 + 人评分维 | `dt-value-drift` |
| 工具对话按段还是按跳标 | Llama 3 工具节 | message 级；工具返回不能改 | `dt-tool-turn-pref` |
| 代码合成改自己的单测 | Llama 3 §4.3 | 先冻测试；改测试的轨迹隔离 | `dt-code-exec-synth` |
| 开源合成自称 HumanEval +9% | 代码评测泄漏论文、LiveCodeBench | 时间切新题；SWE 再去 issue / 测试文件 | `dt-code-bench-bleed` |
| SWE 过测轨迹整段进 SFT | SWE-Prime、SWE-Hero | 成功仍可能脏；改测试文件就扔 | `dt-swe-success-noise` |
| 目录里没有能用的工具还是调了 | BFCL irrelevance | 造「不该调」和「先查再调」 | `dt-tool-irrelevance` |
| 换工具名就不会了 | PIPE / 轨迹 SFT | 别名评测；示范长得像产品 schema | `dt-tool-alias` |
| 终局状态对、中间少一次只读 | BFCL V3 | must_call + 参数血缘 | `dt-agent-state-path` |
| 公开测当对话、私有测当奖 | RLEF | 两套测分哈希；stderr 不进 CE | `dt-rlef-split` |
| 工具返回里写「忽略指令」 | OpenAI instruction hierarchy | observation 按低权限内容处理 | `dt-tool-inject` |
| 屏幕点击轨迹整段进 SFT | OSWorld / AndroidWorld | 对得上当时的树；过期帧扔掉 | `dt-gui-traj` |
| 没有引用怎么标事实 | WebGPT | 浏览轨迹和带出处答案分开 | `dt-webgpt-cite` |
| 后训练再灌新百科 | Llama 3 factuality probe | 对齐「会不会」，知识仍在预训练 | `dt-knows-what` |
| 有搜索就搜 | Llama 3 工具节 | 必须搜 / 禁止搜 / 可搜可答三桶 | `dt-when-to-search` |
| 客服过一次库状态 | τ-bench $\mathrm{pass}^{k}$ | 跨次稳定才进 SFT；政策单独 grader | `dt-tau-passk` |
| 网上长思考当蒸馏集 | R1 800k | 只留对的；混语言丢掉；小模型只 SFT | `dt-r1-distill` |
| 推理时贴整份安全政策 | deliberative alignment | SFT 撕掉 spec，逼模型回忆条款 | `dt-deliberate-spec` |
| 网页点击序列对齐人 | WebArena | 看功能断言，失败回放不当正例 | `dt-webarena-traj` |
| IFEval 541 条写进 SFT | Google / Tulu RLVR-IFeval | 评测留下；同族约束叠到自己的混 | `dt-ifeval-overlay` |
| 推理 SFT 越大越好 | s1K | 难度 / 多样 / 质量三道门；1k 对已对齐学生 | `dt-s1k` |

第二张表覆盖分类器、事实评测和数据治理。准备这些题时，同样要说明质量检查怎么做、数据从哪来。

| 别处怎么问 | 公开来源 | 答题要点 | 卡 |
| --- | --- | --- | --- |
| 现场训分类器、摸数据集 | OpenAI 高频 ML coding，AceOffer 19 次 | 先切集再拟合；正例来自评测失败和许可集 | `dt-oai-classifier` |
| 聊天日志里挖新概念的代表图 | OpenAI 系统设计 | 种子用新出现的实体和评测失败；质量门先于新颖度 | `dt-chatlog-concept` |
| 用户上传工具照片，怎么改进识别训练 | OpenAI ML 轮，AceOffer 6 次 | 许可目录图、受控拍摄 + 验证合成 | `dt-tool-photo` |
| 模型是诚实还是仅仅流畅 | Anthropic RE 电面 | 造「流畅但错 / 短而对」；忠实维单报 | `dt-honest-fluent` |
| 读过 Sleeper Agents 吗，后门怎么清 | Anthropic 论文；面经默认你读过 | 当数据事故拦植入；安全训清不掉 | `dt-sleeper-data` |
| 用 token logprob 做二分类 | Anthropic MLE | Yes/No 一个 token；阈值按切片校准 | `dt-llm-clf-logprob` |
| 评测台当成生产系统来设计 | DeepMind / Gemini 评测岗 | 五元组哈希；2 点涨在误差内 | `dt-eval-harness` |
| 泄漏和记忆怎么分开 | ConTAM；Gemini 预训练评测 JD | 命中不等于涨分；金丝雀 + 扰动题 | `dt-canary-leak` |
| 合成一直回流会不会塌 | DeepSeek data chemistry；Shumailov | 每代留许可源；只留过 oracle 的 | `dt-synth-collapse` |
| Phi 教科书数据好在哪 | Phi-1 / Phi-4 | 质量是轴，规模不取消；教师泄漏单独查 | `dt-phi-textbook` |
| 偏好数据一致率低怎么修 | Cohere / xAI；InstructGPT | 先改协议；可验证走规则奖励 | `dt-pref-collect` |
| 没有金标、专家很贵，评测怎么造 | Cohere / Harvey | 自动题先上；人只标校准和不知道的轴 | `dt-eval-no-gold` |
| 榜涨了用户说更差 | Cognition 等 agent 岗；OpenAI 停报 Verified | 先查脏、偏、错题、偏分布 | `dt-bench-vs-user` |
| Prompt、RAG 还是微调 | OpenAI / Cohere / Mistral | 私有知识走 RAG；行为走后训练 | `dt-prompt-rag-ft` |
| 微调后旧能力掉了 | Mistral forgetting | mix 留锚点回放；KL 代替不了数据 | `dt-forget-sft` |
| 线上评测记什么、怎么 A/B | Perplexity / Cohere | 线上用来发现失败；补数据用许可复现 | `dt-online-eval` |
| 样本轴 double descent 作业 | Anthropic take-home | 加样本不单调；对照仍是只换数据 | `dt-sample-descent` |

## 追问

- **先刷哪组？** 预训练先闭卷讲 OpenAI bootstrap 和 FineWeb 全局去重。后训练先按 Panel 的偏好轮刷完，再补代码和 agent：执行合成会不会改测试、RLEF 公私测、SWE 成功轨迹、BFCL 不该调、工具别名、中间少调只读、工具注入、该不该搜。第二张表先刷分类器笔试、诚实 vs 流畅、评测台、Prompt vs RAG vs 微调，这几张跨公司重复最多。
- **网页 / GUI 轨迹和推理蒸馏怎么配着练？** 轨迹质量和 `dt-traj-quality` 对照着刷；R1 蒸馏和 s1K 和 `dt-synth-reasoning` 对照着刷。
- **别家题答完，要不要评价他们该不该用用户日志？** 不用。说清各自的数据使用条件即可，重点放在方法本身。
