# AFM 三条数据 Pipeline — 来源与设计边界

核对日期：2026-10-27。公开资料只支持所述方法主题；任务、schema、质量门、训练manifest、实验与英文表达均为面试设计扩展，未运行benchmark或采集真实训练数据。

- Skill Usage：用来区分检索、选择、适配；不把runtime refinement误称权重更新。
- HarnessLLM / HARDTESTGEN / EvalPlus：用来讨论代码测试反馈，本文树任务为教学具体化；不把某个子集结果冒充完整benchmark。
- AgentTrek：新补多模态轨迹合成公开案例，含教程筛选、结构化任务、实际回放与VLM评价。VLM评价不能保证状态正确，独立文件/状态checker是本文设计扩展。
- VisualSkill / OSWorld：用于图文技能、真实软件工具与状态评价背景；票据转表格不是声称这些论文已提供的标准任务。
- JSONL均为示意记录，不存在真实图像/程序hash或实测成功率；用途字段是有条件候选，正式训练前须完整采集与审计。

## 原始链接

- [Skill Usage in Realistic Settings](https://arxiv.org/html/2604.04323v1)
- [VisualSkill](https://arxiv.org/html/2606.18448v1)
- [HarnessLLM](https://arxiv.org/html/2511.01104v1)
- [HARDTESTGEN — ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf)
- [EvalPlus](https://arxiv.org/abs/2305.01210)
- [AgentTrek — paper](https://arxiv.org/abs/2412.09605)
- [AgentTrek — official project](https://agenttrek.github.io/)
- [OSWorld](https://arxiv.org/abs/2404.07972)
