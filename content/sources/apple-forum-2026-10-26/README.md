# Apple 一亩三分地原帖核对

采集日期：2026-10-26。应用户要求，由主 agent 与 sub-agent 在 Chrome 的独立标签中查看候选人原帖与相关作者回复，已完成三轮检索／补查。没有登录、购买、发帖或绕过访问限制；部分积分段在当前会话中已显示可浏览。页面时间未标明时区，不推断为 Pacific Time。

候选人报告不等于 Apple 官方出题规则。这里只记录实际可见的题型、问题或主题，不从若干帖子推算频率；完整接口、场景和答案为手册补充。未披露的业务、规模、团队身份保持未知。

| 原帖 | 页面日期 | 团队与可核对内容 | 本次处理 |
| --- | --- | --- | --- |
| [Foundation Model 电面](https://www.1point3acres.com/bbs/thread-1145559-1-1.html) | 2025-09-13 | 作者明确 Foundation Model team；RAG 项目、减少幻觉、evaluation；类似 LC732 的小数时间题 | 新增 2 题；data 子团队未披露 |
| [Apple MLE Onsite](https://www.1point3acres.com/bbs/thread-1170085-1-1.html) | 2026-03-24 | 作者回复确认 Siri response generation；一次编辑布尔判定、向量化 k-means、SFT／DPO、回复事实性与口播长度 | 新增一次编辑；其余已有相关覆盖 |
| [Apple Sr MLE onsite](https://www.1point3acres.com/bbs/thread-1170122-1-1.html) | 2026-03-25 | 作者回复确认 IS&T；TTL 语义与删除时机，以及其他 ML／项目主题 | 新增 TTL 练习；不当作 AFM 题 |
| [Apple AIML MLE 面经](https://www.1point3acres.com/bbs/thread-1141557-1-1.html) | 2025-08-14 | 中国 AIML MLE；数据配比、替代方案、模型比较、项目动机与注意力 | 新增有来源的配比项目深挖 |
| [AIML 纯研究团队 onsite](https://www.1point3acres.com/bbs/thread-1145563-1-1.html) | 2025-09-13 | reasoning 研究进展与必要性，beam search、attention、推理加速主题 | 新增研究陈述题；已有代码主题不重复 |
| [Apple MLE 虚拟 onsite](https://www.1point3acres.com/bbs/thread-789348-1-1.html) | 2021-08-17 | 作者回复确认 Siri；搜索系统、简单分类器系统、Simplicity／Build Trust 主题 | 新增 2 道设计来源题、1 道文化主题扩展 |
| [Apple MLE 技术电面](https://www.1point3acres.com/bbs/thread-1165265-1-1.html) | 2026-02-15 | 作者回复确认 Siri；场景、数据挑战、预处理、模型与训练，手写 k-means | 补充分类器系统题依据；不重复 k-means |
| [Vision MLE 电面](https://www.1point3acres.com/bbs/thread-1180339-1-1.html) | 2026-06-15 | 手写 MHA | 已有 `apple-mha-code`，不新增 |

首轮共 9 张题卡：8 张有候选人可见问题依据，`realInterview: true`；1 张只依据文化主题扩展，`realInterview: false`。`true` 指问题或题型的面经依据，不表示手册补充的详细题面是逐字原题。

## 第二轮继续检索

新核对 10 个原帖，从其中 6 个新增 10 张卡（8 张编程、2 张讨论）；其中 9 张 `realInterview: true`，论文层的具体公式未披露，因此该形式扩展卡为 `false`。两轮累计 19 张来源题／主题扩展：17 张为 `true`，2 张为 `false`。

| 原帖 | Chrome 显示的发帖日期 | 可核对主题与处理 |
| --- | --- | --- |
| [Apple MLE 新鲜面经](https://www.1point3acres.com/bbs/thread-1084615-1-1.html) | 2024-09-05 14:00:32 | 数据集现场建模、训练、指标、降维与可视化；新增完整 pipeline。搜索结果可能显示次日，采用 Chrome 页面值，不推断时区 |
| [果子电面＋昂赛](https://www.1point3acres.com/bbs/thread-1158691-1-1.html) | 2025-12-19 13:58:52 | DS／分析岗位，手写 K-fold 与 k-means；新增 K-fold，k-means 去重 |
| [苹果 ML Engineer VO](https://www.1point3acres.com/bbs/thread-1041756-1-1.html) | 2024-01-29 16:07:11 | 作者回复确认 AIML 视频组；新增 BatchNorm 状态，KL 与旋转等不重复扩充 |
| [水果 CVML 全套](https://www.1point3acres.com/bbs/thread-1129820-1-1.html) | 2025-05-21 10:23:20 | 经历字段标 2024 Q4；新增 kNN、circular padding、生成图像评价；作者对 DS／gen-AI evaluation 身份不确定，不升级为 AFM 证据 |
| [AIML Infra 全套](https://www.1point3acres.com/bbs/thread-1149108-1-1.html) | 2025-10-07 14:14:15 | 新增 JSON、DAG、Flask；原始修 bug 程序未披露，不伪造四个 bug |
| [Apple CV/ML 面经](https://www.1point3acres.com/bbs/thread-950206-1-1.html) | 2022-12-02 14:37:36 | 明确论文 layer 实现、导数／GD、code review；只新增形式扩展，门控公式为手册自拟 |
| [分享一个苹果家 MLE 挂经](https://www.1point3acres.com/bbs/thread-1120533-1-1.html) | 2025-03-27 12:14:59 | Jupyter、NN／LLM、AB 测试与设计轮只有主题，保留记录，不补原题 |
| [Foundation Model HR 讨论](https://www.1point3acres.com/bbs/thread-1150910-1-1.html) | 2025-10-20 17:35:44 | 两页均检查，主要在询问面试内容，无足够具体新题，排除 |
| [Apple 店面](https://www.1point3acres.com/bbs/thread-1177713-1-1.html) | 2026-05-22 15:25:14 | vision encoder 与 LLM 性能主题已有覆盖，无新增细节，不重复建卡 |
| [Apple Video MLE](https://www.1point3acres.com/bbs/thread-1176800-1-1.html) | 2026-05-14 17:11:00 | 视频压缩与 diffusion 只披露主题；不推导成具体技术题或 AFM 的 coding 豁免规则 |

新增题目 ID 见 [继续检索清单](continued-search-manifest.json)。原始核对范围分别见：

- [第二轮数据／CVML](forum-data-round2-20261026-source-audit.json)
- [第二轮编程](forum-coding-round2-20261026-source-evidence.json)
- [第二轮基础设施与排除项](forum-panel-round2-20261026-source-audit.json)
- [论文实现面试形式](forum-root-round2-20261026-source-audit.json)

## 第三轮补查

重新检查已收录的 [1084615 原帖](https://www.1point3acres.com/bbs/thread-1084615-1-1.html)，确认还有两道此前未整理的明确设计问题：相册照片排序、大型视频摘要系统。各新增一张卡，均 `realInterview: true`；详细需求和参考方案仍为手册扩展，团队未确认 AFM。不将它们计为新帖子。

本轮另核对一亩三分地 [1159873](https://www.1point3acres.com/bbs/thread-1159873-1-1.html)，内容是 LLM evaluation 职业讨论，无实际面试题；Aced 的 Apple Senior AI PM 经历在 Chrome 只显示概述，详细内容受限。两者均未生成题卡，也没有用搜索摘要补写不可见内容。

来源题／主题扩展累计 21 张：19 张有候选人问题依据，2 张为主题扩展。核对范围见 [补充设计题记录](forum-root-round3-20261026-source-audit.json) 与 [本轮排除项](forum-data-round3-20261026-source-audit.json)。

详细记录分别保存为：

- [AFM／数据与研究方向](forum-data-20261026-source-audit.json)
- [编程方向](forum-coding-20261026-source-evidence.json)
- [系统设计与文化方向](forum-panel-20261026-source-audit.json)

记录保留采集方式、可见范围、团队限定、原帖主题与未披露内容，不批量复制帖子正文。[进入题目目录](../../handbooks/data-team-interview/README.md)。
