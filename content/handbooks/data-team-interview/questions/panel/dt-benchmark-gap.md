---
id: dt-benchmark-gap
section: panel
order: 4
level: S
title: Panel：benchmark 上有能力缺口，怎么诊断，数据干预怎么选？
quick: >-
  先诊断再干预。查评测有没有 contamination、自动指标和 human evaluation 是不是在说同一件事，再按任务、难度、语言和工具步骤
  evaluation slices 定位失败；病因对上了才选数据措施，覆盖不足补可验证合成，标签不一致改协议，leakage 换评测，奖励 hack 换独立
  oracle。看到低分就直接加 SFT 数据，往往补错了地方。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: 'LiveCodeBench: Holistic and Contamination Free Evaluation'
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: FineWeb-Edu
    url: 'https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu'
    type: primary
---

先诊断再干预。我会先排除 evaluation contamination 和指标定义的问题，再 evaluation slices 定位是哪类失败，病因对上了才动数据：覆盖不足补可验证合成，标签不一致改协议，leakage 换评测，奖励 hack 换独立 oracle。

比如 evaluation gate 上「工具任务成功 41%，human evaluation 说 instruction following 还行」。一上来就说上 GRPO 或者「再 SFT 10 万条」，还没讲清这些措施针对的是什么原因。低分背后可能是题 leakage、解析器误判、某一跳的参数 hallucination，每种原因要的干预完全不同。同理，GSM8K 低分也不一定说明数学数据不够。guideline 里写的 benchmark-driven debugging，给你一个 capability gap，考的就是这个诊断。

我会先确认是不是真缺口：评测有没有 leakage、有没有翻译腔、和目标任务是不是同分布。AFM 的 multilingual 评测用母语者写的 prompt，不用翻译题；LiveCodeBench 一类做法按时间切出新题，就是为了防背题。先报 contamination rate 和新旧题的差，再谈能力。

然后看定义，自动指标和 human evaluation 是不是在说同一件事。IFEval 过了、human evaluation 没过，多半是格式合法但没帮上忙；数学 exact match 没过、过程却是对的，那是解析器的问题。

定义没问题再 evaluation slices，按任务、难度、locale、要不要工具、要不要看图切开。总榜 41% 拆开可能是第一跳 90%，第二跳参数 hallucination、70% 失败。切完找对照，看同一个 checkpoint 在邻近任务上的表现：图表题里读坐标轴没问题、算差值不行，说明缺的是推理覆盖，视觉编码器没坏。到这一步才去动训练数据。

## 病因和干预对照

| 病因 | 怎么证实 | 数据干预 |
| --- | --- | --- |
| evaluation leakage | 训练侧 n-gram / 题面 embedding 重叠高；新题掉、旧题高 | 换 evaluation gate，旧题降级为 development set |
| 覆盖空洞 | 训练 mix 中该类 token 或 trajectories 接近 0；邻近类正常 | 验证合成或人写 seed，进对的阶段 |
| 格式 / schema | 参数不合法、语言不匹配，任务逻辑对 | 小量 SFT 或 constrained decoding 数据 |
| label noise | 人标不一致，AFM 报过偏好 20-30% 分歧 | 改协议、丢掉低 cohesion 题，见 `dt-reward-pref` |
| 过程假、答案对 | 抽查 chain-of-thought (CoT)，发现引用了不存在的量 | reasoning verification 或只监督最终答 |
| 奖励 hack | proxy 涨、gold / human evaluation 平 | 换 oracle，冻结旧 reward model（RM） |
| decoding 预算 | 加 long context 或给工具就过 | 与数据量无关；改评测或 inference budget |
| contamination 评测自身 | 合成题当 evaluation gate | evaluation gate 用真源 |

动数据的时候一次只动一维，而且要能 replay：记下 `dataset_version`、过滤阈值、teacher id。同时改 mix、奖励和 decoding，就分不清是谁让分数涨的。我会先用 small model 或小步数 sweep 出 $\Delta$，再放到目标模型上。

怎样算干预失败也提前写下来。比如补了 5 万道验证过的数学题，冻结的 MATH evaluation slices 纹丝不动，合成 holdout 却暴涨，那就是在背自己的生成器。飞轮怎么避免这种自我表扬，见 `dt-data-flywheel`。

## 追问

**MGSM 掉在非英语，你会怎么查？**
先看这些题是不是翻译的，翻译题不自然，本身就该换掉。再看这门语言在 mix 里的实际 token 份额和过滤器的通过率。如果是英语 data quality checks false rejection 了这门语言，先按语言对 threshold 做 calibration（`dt-quality-filter-code`）；如果份额本来就低，就走 continued PT 的课程，先抬高该语言的配额，合成题要过标准答案。evaluation gate 仍用母语者写的题，自己合成的平行题只进训练。

**先固定模型、只动数据，有公开的先例吗？**
有。DataComp-LM 和 FineWeb 的公开方法都是固定模型、只动数据，看哪种过滤赢。AFM 的 continued PT 把 multilingual 权重从 8% 提到 30%，synthetic data 也要经过验证，同样是先诊断出覆盖和 data mix 不足，再做干预。

**自动指标和 human evaluation 打架时听谁的？**
evaluation gate 听 human evaluation 和 locale。自动指标当 regression tests，用来定位 evaluation slices。

**缺口只在 small model 上出现，large model 没有，怎么办？**
先确认是容量问题还是数据问题。容量不够，就别往 small model 灌竞赛级的长推理过程，改走路由；数据不够，就两边用同一套验证合成，small model 用短 trajectories。

**能不能用 LLM-as-judge 做诊断？**
可以当开发信号，和 human evaluation 对齐过才能当 evaluation gate。Judge 和生成器同族时，会一起 hallucination。
