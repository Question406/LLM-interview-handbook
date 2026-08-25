---
id: anthropic-agent-eval
section: anthropic
order: 29
level: S
title: Anthropic：OSWorld / WebArena 类公开基准怎么讲？污染和成功定义卡在哪？
quick: >-
  先报功能正确性，不要报动作序列匹配。WebArena 查终态，OSWorld 有的题是 [0, 1] 完成度不能先二值化。公开题面、评测脚本、黄金轨迹都可能进预训练。讲分数先讲污染、步数预算和「不可完成」题怎么计。
tags:
  - Anthropic
  - Agents
  - Evaluation
  - Computer use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments"
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: Developing a computer use model (Anthropic)
    url: https://www.anthropic.com/research/developing-computer-use
    type: primary
---

Agent / 评测岗会把「Claude 电脑用得怎么样」问成公开基准。我会主动把 WebArena、OSWorld 从排行榜数字拆成三件事：成功怎么定义、分数怎么加总、训练数据是不是已经见过题。这不是某一场隐藏面经，是你能不能避免用错指标给 computer use 表功。

## 成功是终态，不是点击序列

WebArena（Zhou 等，约 812 题）在可自托管的站点上做电商、论坛、开发协作、CMS。评测写的是 **functional correctness**：用脚本查数据库、页面内容、最终 URL，不是拿智能体轨迹去对一条人类演示。同一题可以有很多条合法路径。原论文最好的 GPT-4 配置端到端大约 14%，人类大约 78%。那条鸿沟才是故事：不是差一个选择器，是长程规划和恢复。

OSWorld（Xie 等，约 369 题）把环境换成真桌面（论文主评 Ubuntu，也谈 Windows / macOS）：文件、办公套件、浏览器、跨应用。评测查文件系统、应用输出、有时查网络副作用。官方说明：**不是每题都是 0/1**。有的完成度在 $[0,1]$。排行榜是把原始分求和再除以题数，再四舍五入，不先二值化。早期智能体大约一成二，人类大约七成二；人类中位耗时也比 WebArena 长一截。面试若把 OSWorld 说成「对了或错了再平均」，分数会对不上。

和 `anthropic-computer-use` 对齐：这些基准测的是「任务做完了没有」，不测「支付前有没有弹确认」。安全失败要另开一列：越权点击、执行了注入指令。把安全违规折进成功率里，模型会为了分去点同意条款。

## 污染：公开基准默认会漏

污染不只是「题面出现在 Common Crawl」。Agent 基准更肥：

| 漏什么 | 为什么涨分 | 怎么查 |
| --- | --- | --- |
| GitHub 上的任务 JSON / README | 模型背指令和站点结构 | 训练切分、检索重叠 |
| 评测脚本 | 直接优化检查器而不是任务 | 换等价检查器看分是否崩 |
| 人类示范视频和轨迹 | 变成逐步克隆 | 打乱 UI 主题 / 分辨率 |
| 排行榜本身 | 在测试集上调 prompt | 留私有持出、定期换题 |

WebArena 的站点是公开镜像，OSWorld 的配置和检查器也在仓库里。预训练若扫过 GitHub，等于题和答案形状都见过。UI 还版本敏感：Ubuntu 22 的「Save」到 24 换了位置，背轨迹的模型会静默掉点。正确叙事：公开分是能力下界加污染上界；对内发版用冻结私有集、任务轮换、必要时直播站。不要拿「我们 OSWorld 又高了三个点」当唯一上船证据。

`anthropic-eval-honesty` 那套「针不在文档里还自信」这里变成「检查器要的文件已经在磁盘上，智能体却去点了一圈无关菜单仍拿分」——所以必须看轨迹抽样，不能只看均值。

## 怎么报，才不像在刷榜

我会固定这些再报一个数字：

1. **检查器版本和是否允许不可完成题。** WebArena 有一类不可完成意图；乱试和正确认输要分开统计。
2. **步数 / 时间预算。** 预算加倍成功率涨，不声明预算的对比无效。
3. **输入模态。** 纯 DOM / 无障碍树 vs 只截图 vs 两者。Claude computer use 是截图加动作，和 WebArena 早期文本智能体不是同一个 ACI。
4. **加总协议。** OSWorld 用原始 $[0,1]$；不要偷偷对 0.5 取阈再报「准确率」。
5. **失败类型。** 接地（点错像素）、知识（不知道菜单在哪）、注入（执行了页面上的指令）、超时。Anthropic 研究文把早期失败主要归到 grounding 和操作知识。

错法：用 LLM 看截图当裁判还把分数当功能正确；在测试集上穷举 system prompt；把确认框关掉以提高 OSWorld；只报总分、不报办公 / 浏览器分域。

和训练的接口见 `anthropic-computer-rl`：公开检查器当轨迹奖励，等于直接 RL 测试集。奖励必须来自私有任务或训练分裂。

## 追问

- **动作匹配当指标行不行？** 不行。合法绕路会被判零，过拟合演示会被判满分。动作匹配只适合测接地单元测试。
- **LLM 裁判呢？** 可做分析和失败聚类，不当主指标。它会被「看起来忙」的长轨迹骗，也有长度偏差。
- **和针测、Arena 怎么分工？** `anthropic-needle` 测窗口检索；公开对话 Arena 测观感。Agent 基准测副作用是否发生。三套分数不能互相替代。
- **内部该补什么？** 带注入的截图、分辨率扰动、确认框是否在敏感动作前拦住。这些公开集几乎不测。
