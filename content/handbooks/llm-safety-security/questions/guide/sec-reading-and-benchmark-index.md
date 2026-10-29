---
id: sec-reading-and-benchmark-index
section: guide
order: 1
level: S
title: "Reference Book：重点 papers、benchmarks 与 2026 更新索引"
quick: "我会先读 AgentDojo 来理解交互式 injection evaluation，再读 CaMeL 与 design patterns 理解执行结构能提供什么保护。接着看 Skill-Inject、AgentDyn、AgentLAB、OSGuard，把攻击面和任务复杂度扩展出去。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
  - "2026 Research"
realInterview: false
status: published
format: markdown
collapseAnswer: false
updatedAt: '2026-10-28'
sources:
  - title: "PIArena: A Platform for Prompt Injection Evaluation"
    url: "https://aclanthology.org/2026.acl-long.1533/"
    type: primary
  - title: "AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks"
    url: "https://arxiv.org/abs/2602.16901"
    type: primary
  - title: "Prompt Injection as Role Confusion"
    url: "https://arxiv.org/abs/2603.12277"
    type: primary
  - title: "Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks"
    url: "https://arxiv.org/abs/2601.04603"
    type: primary
  - title: "StegoMemory: Agentic Memory Acts as Covert Steganographic Channel"
    url: "https://arxiv.org/abs/2610.04589"
    type: primary
  - title: "Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents"
    url: "https://arxiv.org/abs/2610.23254"
    type: primary
  - title: "PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action"
    url: "https://arxiv.org/abs/2409.00138"
    type: primary
  - title: "Is Vibe Coding Safe? Benchmarking Vulnerability of Agent-Generated Code in Real-World Tasks"
    url: "https://arxiv.org/abs/2512.03262"
    type: primary
---

## 题目描述

已有许多相关论文，但你需要知道先读哪几篇、分别支持什么问题，以及哪些是近期尚待复现的结果。

需要讨论：用阅读顺序与 benchmark comparison 建立参考索引，并把文献结论与手册方案区分。

## 回答思路

> **Situation：** 已有许多相关论文，但你需要知道先读哪几篇、分别支持什么问题，以及哪些是近期尚待复现的结果。  
> **Task：** 用阅读顺序与 benchmark comparison 建立参考索引，并把文献结论与手册方案区分。  
> **Approach / Why：** 基础 benchmark → architectural defenses → dynamic/persistent threats → evaluation validity → 自拟实验。  
> **Result / Check：** 每条参考能对应至少一个具体 card，说明年份、来源类型和最重要的限制。

## 可以这样回答

我会先读 AgentDojo 来理解交互式 injection evaluation，再读 CaMeL 与 design patterns 理解执行结构能提供什么保护。接着看 Skill-Inject、AgentDyn、AgentLAB、OSGuard，把攻击面和任务复杂度扩展出去。

最后读 outcome audits 与 adaptive-attacker 方法：它们帮助判断论文的安全结论有没有被能力不足、弱攻击或 scorer 误差夸大。Memory 与 CoT monitoring 则作为深入方向。

这份索引只采用论文原文、作者官方材料和协议文档。每个自拟实验都写成“会怎样做”，不会把自己的设想写成论文已验证的结论。

## 新增：官方报告实际采用的 Benchmarks

[[report-benchmarks-map]] 整理本轮优先阅读顺序；[[report-benchmarks-evidence]] 提供 31 个条目的报告、章节、版本与公开程度。下方保留首批研究 references，与新章相互补充。

## Benchmark comparison：别把不同分数直接平均

| Setting | 参考资料 | 主要保护目标 / attack surface | 要另外补测什么 |
| --- | --- | --- | --- |
| Indirect injection | AgentDojo | 交互式 tools 与任务中的第三方内容 | Clean capability、adversarial utility、版本与权限 |
| Tool-integrated IPI | InjecAgent | Tool-returned data 对 agent 行为的影响 | 固定 context 与完整 trajectory 的差别 |
| Broad agent attacks | ASB | 多场景、多阶段 agent attack/defense | 各 attack category 的独立定义与 scorers |
| Malicious user requests | AgentHarm | Tool-assisted harmful task completion | Benign twins、refusal 与实际完成程度 |
| Web misuse | SafeArena | Web agents 的 deliberate misuse | 正常 web task 能力与环境隔离 |
| Web injection | WASP | Web observations 中的 hijacking | 视觉 / DOM、开始执行与最终成功 |
| MCP metadata | MCPTox | Tool descriptions / metadata poisoning | Discovery exposure、跨 tools 影响 |
| Skills | Skill-Inject | Third-party skill instructions | Legitimate compliance、代码与文字两种影响 |
| Dynamic tasks | AgentDyn | Helpful instructions 与 dynamic planning | Over-defense、开放流程中的安全路径 |
| Long-horizon attacks | AgentLAB | 多步 adaptive interaction | Horizon、retry budget、持久状态 |
| Computer-use risks | OS-BLIND / OSGuard | 正常目标下的 context/state-dependent harms | Action judgement 与 end-to-end 的差距 |
| Sabotage / control | SHADE-Arena | Hidden side goal 与 monitoring | Attacker knowledge、monitor access、审计预算 |
| Privacy behavior | PrivacyLens | Contextual privacy norms in actions | Recipient/purpose、必要信息保留 |
| Monitoring | MonitorBench | CoT 提供的可监控信息 | Task dependence、stress tests、其他 observations |
| Generated code | SusVibes | Functional correctness 与 software security | Secure + functional joint pass、测试完整性 |
| Cyber capability | CyberGym | Vulnerability reproduction capability | Agent authorization / containment 另测 |

## 8 篇起步阅读

| 顺序 | Reference | 读完要能说清楚 |
| --- | --- | --- |
| 1 | [AgentDojo](https://arxiv.org/abs/2406.13352) | 一个 attack-task episode 如何执行与评分 |
| 2 | [CaMeL](https://arxiv.org/abs/2503.18813) | Guarantee 依赖什么，哪些情况不覆盖 |
| 3 | [Design Patterns](https://arxiv.org/abs/2506.08837) | 哪些架构限制适合哪些产品任务 |
| 4 | [Skill-Inject](https://arxiv.org/abs/2602.20156) | Skill 带来哪些新的 instructions / execution surfaces |
| 5 | [AgentDyn](https://arxiv.org/abs/2602.03117) | Helpful instructions 为什么影响 utility-security evaluation |
| 6 | [AgentLAB](https://arxiv.org/abs/2602.16901) | 多步、adaptive 的 attacker 比单次 payload 多什么能力 |
| 7 | [OSGuard](https://arxiv.org/abs/2606.15034) | 如何保留正常目标并增加 state-based safety constraints |
| 8 | [The Attacker Moves Second](https://arxiv.org/abs/2510.09023) | Defense-aware attack 怎样影响结果可信度 |

之后按方向读 memory、privacy、preference training 或 AI control。研究年份以首次公开为主；conference、revision 与首次公开年份可能不同。未写会议的条目不暗示已经 peer reviewed。

## 首批 51 个 primary references 与对应题目

下面的“用途与限制”是阅读提示；reference 的 method 与结果以原文版本为准。论文、官方报告、协议文档分别列出，协议规范不作为实验结果使用。

| Reference | 年份 / 类型 | 用途与限制 | 对应 cards |
| --- | --- | --- | --- |
| [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) | 2024 · NeurIPS 2024 | Tool-output injection 的交互环境；结论依赖 tasks、tools 与 attacker permissions。 | [[sec-safety-security-threat-model]]、[[sec-indirect-injection-causal-chain]]、[[sec-benchmark-selection-matrix]] |
| [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://arxiv.org/abs/2403.02691) | 2024 · Findings of ACL 2024 | Tool-integrated indirect injection；需要区分固定上下文测试与完整执行。 | [[sec-indirect-injection-causal-chain]]、[[sec-exfiltration-vs-answer-corruption]]、[[sec-benchmark-selection-matrix]] |
| [Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents](https://arxiv.org/abs/2410.02644) | 2024 · ICLR 2025 | 多类 agent attacks / defenses；不同版本的 tasks、metrics 和实现需要固定。 | [[sec-attacker-control-budget]]、[[sec-benchmark-selection-matrix]] |
| [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://arxiv.org/abs/2410.09024) | 2024 · research paper | 主要研究 malicious user requests 与 tool-assisted harmful completion。 | [[sec-safety-security-threat-model]]、[[sec-benchmark-selection-matrix]] |
| [SafeArena: Evaluating the Safety of Autonomous Web Agents](https://arxiv.org/abs/2503.04957) | 2025 · research paper | Web-agent misuse；与 benign-user indirect injection 的 attacker model 不同。 | [[sec-benchmark-selection-matrix]] |
| [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) | 2025 · research paper | Control/data flow 分离与 capabilities；保证依赖 policy、interpreter、tools 和建模假设，论文讨论 side channels。 | [[sec-memory-lineage-write-controls]]、[[sec-camel-security-guarantees]]、[[sec-privileged-quarantined-models]] |
| [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) | 2025 · research paper | 架构 design patterns 与案例分析；不提供任意通用 agent 的无条件安全保证。 | [[sec-tool-schema-semantic-authorization]]、[[sec-dom-screenshot-provenance]]、[[sec-privileged-quarantined-models]] |
| [The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/abs/2404.13208) | 2024 · research paper | 训练模型区分 instruction priority；learned behavior 与外部 authorization 分别验证。 | [[sec-authorization-vs-refusal]]、[[sec-model-defenses-struq-secalign]] |
| [Improving instruction hierarchy in frontier LLMs](https://openai.com/index/instruction-hierarchy-challenge/) | 2026 · official research report | IH-Challenge 与 instruction hierarchy training；报告中的测量设置不能直接外推到所有 harness。 | [[sec-proposal-security-preference-data]] |
| [StruQ: Defending Against Prompt Injection with Structured Queries](https://arxiv.org/abs/2402.06363) | 2024 · research paper | Special format 与专门训练共同作用；仅添加 delimiters 不等于复现 StruQ。 | [[sec-model-defenses-struq-secalign]] |
| [SecAlign: Defending Against Prompt Injection with Preference Optimization](https://arxiv.org/abs/2410.05451) | 2024 · research paper | 针对 injected inputs 的 preference optimization；需评估 unseen attacks 与 task utility。 | [[sec-model-defenses-struq-secalign]]、[[sec-privacy-preserving-feedback-pipeline]]、[[sec-proposal-security-preference-data]] |
| [Meta SecAlign: A Secure Foundation LLM Against Prompt Injection Attacks](https://arxiv.org/abs/2507.02735) | 2025 · research paper | 公开模型和训练方案；论文中的 robustness 是指定 evaluation 下的经验结果。 | [[sec-model-defenses-struq-secalign]] |
| [IPIGuard: A Novel Tool Dependency Graph-Based Defense Against Indirect Prompt Injection in LLM Agents](https://arxiv.org/abs/2508.15310) | 2025 · EMNLP 2025 | Planned Tool Dependency Graph 约束执行；dynamic replanning 与 tool arguments 仍需单独分析。 | [[sec-ipiguard-dynamic-planning]] |
| [MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers](https://arxiv.org/abs/2508.14925) | 2025 · research paper | Tool metadata poisoning；不需要先执行该 malicious tool 才能影响 agent。 | [[sec-mcp-tool-metadata-poisoning]] |
| [MCP Security Best Practices · 2025-11-25 documentation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) | 2025 · official protocol documentation | Confused deputy、token passthrough、session security 等工程依据；属于协议文档，区别于实验论文。 | [[sec-tool-schema-semantic-authorization]]、[[sec-mcp-confused-deputy]]、[[sec-tool-update-toctou]] |
| [Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks](https://arxiv.org/abs/2602.20156) | 2026 · preprint | Skill-file injection-task pairs；比较 harmful instruction avoidance 与 legitimate compliance。 | [[sec-skill-inject-supply-chain]]、[[sec-tool-update-toctou]]、[[sec-leakage-contamination-splits]] |
| [SkillGuard: A Permission-Centric Framework for Agent Skill Security](https://arxiv.org/abs/2606.03024) | 2026 · preprint | Skill-level context influence 与 action side effects；permission framework 的假设和表达能力需要检查。 | [[sec-skill-permission-principals]]、[[sec-proposal-skill-permission-generalization]] |
| [AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases](https://arxiv.org/abs/2407.12784) | 2024 · research paper | Poisoned long-term memory / knowledge base 的 trigger-based agent attacks。 | [[sec-memory-attacker-models]] |
| [A Practical Memory Injection Attack against LLM Agents (MINJA)](https://arxiv.org/abs/2503.03704) | 2025 · research paper | 通过 queries 与 output observations 向 memory 注入 records；不等于任意直接写数据库。 | [[sec-memory-attacker-models]]、[[sec-memory-persistence-recovery]] |
| [MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval](https://arxiv.org/abs/2512.16962) | 2025 · preprint | Poisoned successful experiences 影响未来任务；特定 agent 的结果需要跨实现复验。 | [[sec-memorygraft-procedural-learning]]、[[sec-proposal-secure-self-improvement]] |
| [Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents](https://arxiv.org/abs/2604.02623) | 2026 · preprint | eTAMP 研究由 environment observation 引入的跨 session / site memory poisoning。 | [[sec-memory-attacker-models]]、[[sec-memory-lineage-write-controls]]、[[sec-memory-persistence-recovery]] |
| [StegoMemory: Agentic Memory Acts as Covert Steganographic Channel](https://arxiv.org/abs/2610.04589) | 2026 · preprint · 2026-10 | Synthetic payload 的跨 session covert transmission；需要独立复现，不能把摘要结果当现实发生率。 | [[sec-stegomemory-covert-channels]] |
| [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models](https://arxiv.org/abs/2402.07867) | 2024 · research paper | Knowledge corruption 与 attacker-chosen answers；不与授权违规完全等同。 | [[sec-exfiltration-vs-answer-corruption]] |
| [WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks](https://arxiv.org/abs/2504.18575) | 2025 · research paper | 隔离 web 环境中的 agent hijacking；不同 observation modes 与 attacker control 分别报告。 | [[sec-attack-transfer-and-budget]]、[[sec-multimodal-ocr-vs-adversarial-image]]、[[sec-dom-screenshot-provenance]] |
| [Image Hijacks: Adversarial Images can Control Generative Models at Runtime](https://arxiv.org/abs/2309.00236) | 2023 · research paper | 特定 VLM 上的 adversarial image 机制；与人可读 OCR text injection 需分开。 | [[sec-multimodal-ocr-vs-adversarial-image]] |
| [Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents Exponentially Fast](https://arxiv.org/abs/2402.08567) | 2024 · research paper | 随机 pairwise chat 的大规模模拟 proof of concept；不直接证明现实组织中的传播速度。 | [[sec-multiagent-infection-delegation]]、[[sec-multiagent-monitor-collusion]] |
| [The Blind Spot of Agent Safety: How Benign User Instructions Expose Critical Vulnerabilities in Computer-Use Agents](https://arxiv.org/abs/2604.10577) | 2026 · preprint | OS-BLIND：benign instructions 下的 contextual threats 与 agent-initiated harms。 | [[sec-computer-use-benign-context-risk]]、[[sec-multiagent-infection-delegation]] |
| [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) | 2026 · preprint · revision 2026-10 | Action-level judgement 与 state-based end-to-end safety；单步 accuracy 不代替完整 trajectory。 | [[sec-safe-completion-objective]]、[[sec-computer-use-benign-context-risk]]、[[sec-judge-robustness-state-oracles]] |
| [AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks](https://arxiv.org/abs/2602.16901) | 2026 · ICML 2026 | Long-horizon、adaptive interaction threats；不从固定 step ASR 推断整段任务风险。 | [[sec-long-context-multiturn-risk]]、[[sec-adaptive-tool-chain-attacks]]、[[sec-2026-dynamic-long-horizon-evals]] |
| [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) | 2026 · preprint | Dynamic planning 与 helpful third-party instructions；security 与 over-defense 同时测量。 | [[sec-safe-completion-objective]]、[[sec-helpful-third-party-instructions]]、[[sec-ipiguard-dynamic-planning]] |
| [PIArena: A Platform for Prompt Injection Evaluation](https://aclanthology.org/2026.acl-long.1533/) | 2026 · ACL 2026 | 统一 evaluation 平台；adapter、scorer 与 threat model 仍需固定。 | [[sec-2026-dynamic-long-horizon-evals]]、[[sec-judge-robustness-state-oracles]]、[[sec-proposal-safety-data-pipeline]] |
| [Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents](https://arxiv.org/abs/2610.23254) | 2026 · preprint · 2026-10 | 小型 tool-using agents 的 failure-outcome audit；不能泛化为所有模型的全局规律。 | [[sec-ignored-not-refused-outcomes]]、[[sec-proposal-research-pitch]] |
| [Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks](https://arxiv.org/abs/2607.28685) | 2026 · preprint | 区分 benchmarks 的 target constructs、scorers 与 model-panel effects。 | [[sec-ignored-not-refused-outcomes]]、[[sec-asr-denominators-statistics]] |
| [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023) | 2025 · research paper | Defense-aware adaptive evaluation；具体突破取决于 attacker access 与计算预算。 | [[sec-attacker-control-budget]]、[[sec-jailbreak-generalization]]、[[sec-attack-transfer-and-budget]] |
| [Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?](https://arxiv.org/abs/2510.05244) | 2025 · research paper | Tool-input/output firewalls 与 benchmark limitations；“perfect”只针对指定实验。 | [[sec-firewall-saturation-replication]] |
| [Prompt Injection as Role Confusion](https://arxiv.org/abs/2603.12277) | 2026 · ICML 2026 | Role probes 与 style-induced role confusion；预测信号不自动构成因果或安全证明。 | [[sec-role-confusion-probes]] |
| [Constitutional Classifiers: Defending against Universal Jailbreaks across Thousands of Hours of Red Teaming](https://arxiv.org/abs/2501.18837) | 2025 · research paper | 基于 synthetic data 的 classifiers；universal jailbreak 的成功定义与单次违规不同。 | [[sec-classifier-cascades-calibration]] |
| [Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks](https://arxiv.org/abs/2601.04603) | 2026 · preprint | Exchange classifiers、cascade 与 probes；性能依赖 traffic distribution 和 threshold。 | [[sec-classifier-cascades-calibration]] |
| [HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal](https://arxiv.org/abs/2402.04249) | 2024 · research paper | 主要测 harmful content 与 red teaming；完整 agent authorization 另需环境状态。 | [[sec-jailbreak-generalization]]、[[sec-leakage-contamination-splits]] |
| [XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models](https://arxiv.org/abs/2308.01263) | 2023 · research paper | Benign prompts 与 unsafe contrasts 的 over-refusal；可迁移其设计思路，不把它称作 agent benchmark。 | [[sec-jailbreak-generalization]]、[[sec-proposal-security-preference-data]] |
| [Many-shot jailbreaking](https://www.anthropic.com/research/many-shot-jailbreaking) | 2024 · official research report | 长 context 下的 demonstrations 影响安全行为；与累积单步风险分别分析。 | [[sec-long-context-multiturn-risk]] |
| [SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents](https://www.anthropic.com/research/shade-arena-sabotage-monitoring) | 2025 · official research report | 模拟 benign tasks + hidden malicious side goals 与 monitoring，区别于外部 injection。 | [[sec-sabotage-vs-external-attacker]] |
| [Evaluating Control Protocols for Untrusted AI Agents](https://arxiv.org/abs/2511.02997) | 2025 · research paper | SHADE-Arena 中的 control protocols 和 adaptive attackers；monitor access 是重要实验条件。 | [[sec-reference-monitor-sandbox]]、[[sec-control-protocols-critical-actions]]、[[sec-monitor-optimization-reward-hacking]] |
| [Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety](https://arxiv.org/abs/2507.11473) | 2025 · research paper | CoT monitoring 的潜力与局限；monitorability 不等于所有 reasoning 都 faithful。 | [[sec-cot-monitorability-faithfulness]] |
| [MonitorBench: A Comprehensive Benchmark for Chain-of-Thought Monitorability in Large Language Models](https://arxiv.org/abs/2603.28590) | 2026 · COLM 2026 | Monitorability evaluation；需要检查 evaluation tasks 与适用的 reasoning formats。 | [[sec-cot-monitorability-faithfulness]] |
| [Agentic Misalignment in Summer 2026](https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/) | 2026 · official research case studies | 受控 simulations 中的四个 case studies；来源明确区别于真实部署事件。 | [[sec-safety-security-threat-model]]、[[sec-sabotage-vs-external-attacker]]、[[sec-monitor-optimization-reward-hacking]] |
| [Alignment faking in large language models](https://arxiv.org/abs/2412.14093) | 2024 · research paper | 特定 training-awareness setups 的 demonstration；不推断所有模型普遍拥有相同意图。 | [[sec-alignment-faking-backdoors]] |
| [Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training](https://arxiv.org/abs/2401.05566) | 2024 · research paper | 人为训练的 deceptive/backdoor proof of concept；与自然产生的 deception 分开。 | [[sec-alignment-faking-backdoors]] |
| [PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action](https://arxiv.org/abs/2409.00138) | 2024 · research paper | Contextual privacy norms 与 agent actions；“知道规则”与“执行守规”分别测量。 | [[sec-authorization-vs-refusal]]、[[sec-contextual-integrity-privacy]]、[[sec-egress-indirect-leakage]] |
| [Is Vibe Coding Safe? Benchmarking Vulnerability of Agent-Generated Code in Real-World Tasks](https://arxiv.org/abs/2512.03262) | 2025 · ICML 2026 · revision 2026-09 | Repository-scale functional correctness 与 software security 分开；任务数量随版本变化。 | [[sec-proposal-coding-security-vs-cyber-capability]] |
| [CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale](https://arxiv.org/abs/2506.02548) | 2025 · research paper · revision 2026-03 | 主要评估 vulnerability reproduction capability；不等于 agent 自身抵抗 injection 的能力。 | [[sec-proposal-coding-security-vs-cyber-capability]] |


## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 按下方表格选 8 篇主线资料，每篇填写相同的 threat-model 与 evaluation notes。
- **Baselines / Ablations：** 同主题找一种 model-level 与一种 runtime-level 方法，使用一致维度做对照。
- **Metrics 与判读：** 最终准备三份讨论：一个 benchmark critique、一个机制解释和一个两周能启动的 project proposal。

## 追问与容易误判的地方

原文 abstract 与完整 artifact 的证据深度不同。准备复现实验时还需读具体 scorer、config 与代码，不能只靠本书摘要。

## 论文依据与适用范围

- [PIArena: A Platform for Prompt Injection Evaluation](https://aclanthology.org/2026.acl-long.1533/) · 2026 · ACL 2026。
- [AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks](https://arxiv.org/abs/2602.16901) · 2026 · ICML 2026。
- [Prompt Injection as Role Confusion](https://arxiv.org/abs/2603.12277) · 2026 · ICML 2026。
- [Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks](https://arxiv.org/abs/2601.04603) · 2026 · preprint。
- [StegoMemory: Agentic Memory Acts as Covert Steganographic Channel](https://arxiv.org/abs/2610.04589) · 2026 · preprint · 2026-10。
- [Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents](https://arxiv.org/abs/2610.23254) · 2026 · preprint · 2026-10。
- [PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action](https://arxiv.org/abs/2409.00138) · 2024 · research paper。
- [Is Vibe Coding Safe? Benchmarking Vulnerability of Agent-Generated Code in Real-World Tasks](https://arxiv.org/abs/2512.03262) · 2025 · ICML 2026 · revision 2026-09。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
