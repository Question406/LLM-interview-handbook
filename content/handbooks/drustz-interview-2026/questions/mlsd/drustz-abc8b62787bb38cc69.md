---
id: drustz-abc8b62787bb38cc69
section: mlsd
order: 210
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 13. 论文与代码清单（按阅读价值排序）
quick: 作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 13. 论文与代码清单（按阅读价值排序）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md
    type: primary
---
## 13. 论文与代码清单（按阅读价值排序）

| 工作 | 一句话 | 链接 |
|---|---|---|
| **SWE-bench** | 定义了 F2P/P2P 三步验证。**先读这个** | [swebench.com](https://www.swebench.com/original.html) · [harness 文档](https://www.swebench.com/SWE-bench/reference/harness/) |
| **SWE-smith** | 环境优先 + 四种造 bug 策略。128 仓库 5 万实例，&#36;1,360 | [arXiv 2504.21798](https://arxiv.org/abs/2504.21798) · [swesmith.com](https://swesmith.com) |
| **SWE-rebench V2** | 语言无关的自动化漏斗，20 语言 3.2 万任务。**工程细节最全** | [arXiv 2602.23866](https://arxiv.org/abs/2602.23866) · [HF: nebius/SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) |
| **SWE-Gym** | 第一个训练用环境，2,438 实例 + rejection sampling + verifier | [arXiv 2412.21139](https://arxiv.org/abs/2412.21139) · [GitHub](https://github.com/SWE-Gym/SWE-Gym) |
| **R2E-Gym / SWE-GEN** | 从 commit 回译，**不依赖 PR 和人写的测试** | [GitHub](https://github.com/R2E-Gym/R2E-Gym) |
| **SWE-RL** | 1,100 万 PR，**不搭环境**，用 patch 相似度当 reward | [arXiv 2502.18449](https://arxiv.org/abs/2502.18449) |
| **DeepSWE** | 全开源 RL 训练配方 | [together.ai/blog/deepswe](https://www.together.ai/blog/deepswe) |
| SWE-bench Verified | OpenAI 人工核验的 500 题子集 + **标注 rubric** | — |
| SWE-Factory / SWE-Bench++ / DockSmith | 自动化环境构建的不同流派 | — |

**读的顺序建议**：SWE-bench（定义）→ SWE-smith（规模怎么来的）→
SWE-rebench V2（工程细节）→ SWE-RL（另一条路的取舍）。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
