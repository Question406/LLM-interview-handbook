---
id: dt-benchmark-gap
section: panel
order: 4
level: S
title: Panel：benchmark 上有能力缺口，怎么诊断，数据干预怎么选？
quick: "先诊断再干预。查评测有没有污染、自动指标和人评是不是在说同一件事，再按任务、难度、语言和工具步骤切片定位失败；病因对上了才选数据措施，覆盖不足补可验证合成，标签不一致改协议，泄漏换评测，奖励 hack 换独立 oracle。看到低分就直接加 SFT 数据，往往补错了地方。"
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

先诊断再干预。我会先排除评测污染和指标口径的问题，再切片定位是哪类失败，病因对上了才动数据：覆盖不足补可验证合成，标签不一致改协议，泄漏换评测，奖励 hack 换独立 oracle。

比如门禁上「工具任务成功 41%，人评说指令跟随还行」。一上来就说上 GRPO 或者「再 SFT 10 万条」，还没讲清这些措施针对的是什么原因。低分背后可能是题泄漏、解析器误判、某一跳的参数幻觉，每种原因要的干预完全不同。同理，GSM8K 低分也不一定说明数学数据不够。guideline 里写的 benchmark-driven debugging，给你一个 capability gap，考的就是这个诊断。

我会先确认是不是真缺口：评测有没有泄漏、有没有翻译腔、和目标任务是不是同分布。AFM 的多语评测用母语者写的输入提示（prompt），不用翻译题；LiveCodeBench 一类做法按时间切出新题，就是为了防背题。先报污染率和新旧题的差，再谈能力。

然后看口径，自动指标和人评是不是在说同一件事。IFEval 过了、人评没过，多半是格式合法但没帮上忙；数学 exact match 没过、过程却是对的，那是解析器的问题。

口径没问题再切片，按任务、难度、locale、要不要工具、要不要看图切开。总榜 41% 拆开可能是第一跳 90%，第二跳参数幻觉、70% 失败。切完找对照，看同一个 checkpoint 在邻近任务上的表现：图表题里读坐标轴没问题、算差值不行，说明缺的是推理覆盖，视觉编码器没坏。到这一步才去动训练数据。

## 病因和干预对照

| 病因 | 怎么证实 | 数据干预 |
| --- | --- | --- |
| 评测泄漏 | 训练侧 n-gram / 题面嵌入重叠高；新题掉、旧题高 | 换门禁，旧题降级为开发集 |
| 覆盖空洞 | 训练 mix 中该类 token 或轨迹接近 0；邻近类正常 | 验证合成或人写种子，进对的阶段 |
| 格式 / schema | 参数不合法、语言不匹配，任务逻辑对 | 小量监督微调（SFT）或 constrained decoding 数据 |
| 标签噪声 | 人标不一致，AFM 报过偏好 20-30% 分歧 | 改协议、丢掉低 cohesion 题，见 `dt-reward-pref` |
| 过程假、答案对 | 抽查推理链（CoT），发现引用了不存在的量 | 过程门或只监督最终答 |
| 奖励 hack | proxy 涨、gold / 人评平 | 换 oracle，冻结旧奖励模型（RM） |
| 解码预算 | 加长上下文或给工具就过 | 与数据量无关；改评测或推理预算 |
| 污染评测自身 | 合成题当门禁 | 门禁用真源 |

动数据的时候一次只动一维，而且要能回放：记下 `dataset_version`、过滤阈值、教师 id。同时改 mix、奖励和解码，就分不清是谁让分数涨的。我会先用小模型或小步数 sweep 出 $\Delta$，再放到目标模型上。

怎样算干预失败也提前写下来。比如补了 5 万道验证过的数学题，冻结的 MATH 切片纹丝不动，合成 holdout 却暴涨，那就是在背自己的生成器。飞轮怎么避免这种自我表扬，见 `dt-data-flywheel`。

## 追问

**MGSM 掉在非英语，你会怎么查？**
先看这些题是不是翻译的，翻译题不自然，本身就该换掉。再看这门语言在 mix 里的实际 token 份额和过滤器的通过率。如果是英语质量门误杀了这门语言，先按语言校准阈值（`dt-quality-filter-code`）；如果份额本来就低，就走 continued PT 的课程，先抬高该语言的配额，合成题要过标准答案。门禁仍用母语者写的题，自己合成的平行题只进训练。

**先固定模型、只动数据，有公开的先例吗？**
有。DataComp-LM 和 FineWeb 的公开方法都是固定模型、只动数据，看哪种过滤赢。AFM 的 continued PT 把多语权重从 8% 提到 30%，合成数据也要经过验证，同样是先诊断出覆盖和配比不足，再做干预。

**自动指标和人评打架时听谁的？**
门禁听人评和 locale。自动指标当回归测试，用来定位切片。

**缺口只在小模型上出现，大模型没有，怎么办？**
先确认是容量问题还是数据问题。容量不够，就别往小模型灌竞赛级的长推理过程，改走路由；数据不够，就两边用同一套验证合成，小模型用短轨迹。

**能不能用 LLM-as-judge 做诊断？**
可以当开发信号，和人评对齐过才能当门禁。Judge 和生成器同族时，会一起幻觉。
