# Jiabao Ji × AFM — 个人 Reference 来源审计

核对日期：2026-10-27。入口为用户提供的主页，跟随公开论文和CV；补充benchmark仅使用原论文、官方代码库及Apple公开研究页。核对范围为资料阅读，未运行这些benchmark或复现论文。

## 事实边界

- 公开作者身份说明参与研究，无法证明具体模块、实验或团队决策由本人主导。正文只写coauthor/参与，职责留待本人确认。
- CV列Apple AKI实习主题为Ambiguity-aware Knowledge QA Data Synthesis；不把AKI写成AFM团队，也不推测内部系统与用户数据。
- 主页与CV有发表状态、标题及年份差异（如DeepAmbigQA、scene text editing）；reference避免据此判定最终venue，内容引用固定论文版本。
- 论文历史模型与成绩不是当前榜单；优先保留setting与方法，不堆旧排名。没有把不同基准的子集、版本或语言合并。
- 主文中的建议设置、oracle替换、数据干预和后续训练均为面试讨论方案，不是新增实验结果。英文为参考表达，个人职责仍需确认。
- 提供公开内容的研究总结，不复制大段原文；未读取或推断非公开实习细节。

## 重点核对位置

| 研究 | 阅读位置 | 核对内容 |
| --- | --- | --- |
| DeepAmbigQA | 方法§3、数据§4、实验§5 | QA生成、答案完整性、自然性与正确性检查 |
| HarnessLLM | §3–4 | harness反馈、SFT/RLVR、测试质量和跨代码生成器评价 |
| HARDTESTGEN | ICLR proceedings §5 | 固定训练问题换verifier；LiveCodeBench-105语言/版本边界 |
| Skill Usage | §3.3、§4 | 递进检索设定、query-specific refinement、Terminal-Bench 2.0 |
| Joint Agent–Speculator RL | §3、§4.1及表2 | 自身rollout、双模式、训练/评测数据和Hit@1边界 |
| VisualSkill | §2、§3.1、附录F | 图文配对、探索补丁、两种verifier和OSWorld补充 |
| ULD | §3.2 | TOFU forget/retain和效用 |

## 原始链接

- [Jiabao Ji — personal homepage](https://question406.github.io/)
- [Jiabao Ji — public CV](https://question406.github.io/assets/cv/cv.pdf)
- [DeepAmbigQA — public paper v1](https://arxiv.org/html/2511.01323v1)
- [HarnessLLM — public paper v1](https://arxiv.org/html/2511.01104v1)
- [HARDTESTGEN — ICLR 2026 proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf)
- [How Well Do Agentic Skills Work in the Wild — v1](https://arxiv.org/html/2604.04323v1)
- [Speculate While You Reason — v1](https://arxiv.org/html/2607.25816v1)
- [VisualSkill — v1](https://arxiv.org/html/2606.18448v1)
- [Reversing the Forget-Retain Objectives — v1](https://arxiv.org/html/2406.08607v1)
- [AmbigQA — EMNLP 2020](https://aclanthology.org/2020.emnlp-main.466/)
- [ASQA: Factoid Questions Meet Long-Form Answers](https://arxiv.org/abs/2204.06092)
- [MuSiQue: Multihop Questions via Single-hop Question Composition](https://arxiv.org/abs/2108.00573)
- [EvalPlus: rigorous evaluation of generated code](https://arxiv.org/abs/2305.01210)
- [LiveCodeBench — original benchmark paper](https://arxiv.org/abs/2403.07974)
- [SkillsBench — official repository](https://github.com/benchflow-ai/skillsbench)
- [tau-bench — original benchmark](https://arxiv.org/abs/2406.12045)
- [tau2-bench — dual-control environment](https://arxiv.org/abs/2506.07982)
- [OSWorld — original benchmark paper](https://arxiv.org/abs/2404.07972)
- [TOFU: A Task of Fictitious Unlearning for LLMs](https://arxiv.org/abs/2401.06121)
- [Apple Foundation Models Tech Report 2025](https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025)
