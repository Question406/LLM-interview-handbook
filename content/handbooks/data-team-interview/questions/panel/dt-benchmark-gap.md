---
id: dt-benchmark-gap
section: panel
order: 4
level: S
title: Panel：benchmark 上有能力缺口，怎么诊断，数据干预怎么选？
quick: "先查评测是否污染、自动指标与人评是否一致，再按任务、难度、语言和工具步骤定位失败。根据证据选择补覆盖、改标注、换评测或换奖励检查。不要看到一个低分就直接加 SFT 数据。"
companies:
  - apple
tags:
  - Apple
  - Evaluation
  - Debugging
  - Data Intervention
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "LiveCodeBench: Holistic and Contamination Free Evaluation"
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
---

GSM8K 低分不一定说明数学数据不足。先排除评测污染和指标口径问题，再按失败类型定位原因，最后决定数据措施。覆盖不足可以补可验证合成，标签不一致要改协议，泄漏要换评测，奖励 hack 则需要独立 oracle。

不这么选的理由：guideline 写的是 benchmark-driven debugging。给你一个 capability gap，先做诊断。直接提出 GRPO 或「再 SFT 10 万条」，还没有说明这些措施针对什么原因。

## 诊断顺序

假设门禁上「工具任务成功 41%，人评说指令跟随还行」。我不会先谈 GRPO。

1. 这是不是真缺口。评测是否泄漏、是否翻译腔、是否和产品任务同分布。AFM 多语不用翻译题，要母语者写 输入提示（prompt）。LiveCodeBench 一类「按时间切新题」就是为了防背题。先报污染率和新旧题差，再谈能力。
2. 口径。自动指标和人评是否在说同一件事。IFEval 过、人评不过，多半是格式合法但没帮上忙。数学 exact match 不过、过程对，是解析器问题。
3. 切片。按任务、难度、locale、是否要工具、是否要看图切开。总榜 41% 可能是「第二跳参数幻觉 70% 失败」，第一跳其实 90%。
4. 对照。同一 checkpoint 在邻近任务上如何。图表读数轴行、算差值不行，是推理覆盖，视觉编码器没坏。
5. 病因对上干预。只在这一步碰训练数据。

| 病因 | 怎么证实 | 数据干预 |
| --- | --- | --- |
| 评测泄漏 | 训练侧 n-gram / 题面嵌入重叠高；新题掉、旧题高 | 换门禁，旧题降级为开发集 |
| 覆盖空洞 | 训练 mix 中该类 token 或轨迹接近 0；邻近类正常 | 验证合成或人写种子，进对的阶段 |
| 格式 / schema | 参数不合法、语言不匹配，任务逻辑对 | 小量 监督微调（SFT） 或 constrained decoding 数据 |
| 标签噪声 | 人标不一致，AFM 报过偏好 20-30% 分歧 | 改协议、丢掉低 cohesion 题，见 `dt-reward-pref` |
| 过程假、答案对 | 抽查推理链（CoT），发现引用了不存在的量 | 过程门或只监督最终答 |
| 奖励 hack | proxy 涨、gold / 人评平 | 换 oracle，冻结旧 奖励模型（RM） |
| 解码预算 | 加长上下文或给工具就过 | 不是数据量问题；改评测或产品预算 |
| 污染评测自身 | 合成题当门禁 | 门禁用真源 |

AFM 自己的例子：continued PT 把多语权重从 8% 提到 30%，并验证合成。那是「覆盖 + 配比」诊断之后的干预。看见 MMMLU 低就加参数，对不上这条。

## 一次只动一维

数据干预必须能回放：`dataset_version`、过滤阈值、教师 id。同时改 mix、奖励和解码，分不清是谁在涨。小模型或小步数 sweep 出 $\Delta$，再放到目标模型。DataComp-LM / FineWeb 的公开方法就是：固定模型，只动数据，看哪些过滤赢。

证伪也要事先写。补了 5 万道验证数学，冻结 MATH 切片不动、合成 holdout 暴涨，就是在背自己的生成器。飞轮怎么避免自我表扬见 `dt-data-flywheel`。

现场我会这么收：「MGSM 掉在非英语。先看这些题是不是翻译的：翻译题不自然，AFM 也弃了。再看该语言在 mix 里的实际 token 份额，以及过滤器通过率。若英语质量门误杀了该语言，先按语言校准阈值（`dt-quality-filter-code`）。若份额就是低，走 continued PT 的课程：先抬该语言配额，合成题要过标准答案。门禁仍用母语者题，不用我们合成的平行题。」

## 追问

- **自动指标和人评打架听谁的？** 产品门禁听人评和 locale；自动指标当回归，用来定位切片。AFM 公开主叙事也是人评加 adapter 分层。
- **缺口在端侧 3B，server 没有，怎么办？** 先确认是容量还是数据。容量不够就别往 3B 灌竞赛很长的推理过程，改路由或 adapter；数据不够则两端用同一套验证合成，3B 用短轨迹。
- **能不能用 LLM-as-judge 当诊断？** 可以当开发信号，和人评对齐过才能当门。Judge 和生成器同族时，会一起幻觉。
