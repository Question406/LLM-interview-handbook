---
id: tencent-grpo-data-requirements
section: data
order: 103
level: S
title: 腾讯 TEG：使用 GRPO 时，构造数据要符合什么要求？
quick: "同一个 prompt 采出的多个回答要能比较、能验证、得分有差异：难度落在当前 policy 的可探索带，太易全对、太难全错都没有学习信号；验证器要稳定，认得等价解，防得住格式和长度投机；题目分布对准真实目标并做去污。先看有效 group 比例，再加样本量。"
tags:
  - Tencent
  - TEG
  - GRPO
  - RL Data
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯Teg大模型暑期算法面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/cce12c13c4af401788cfe08bd76b94b9?urlSource=sitemap
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：TEG；大模型暑期算法
- 届别 / 流程：暑期实习；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-05-18
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“使用 GRPO 时，构造数据要符合什么要求”**

GRPO 的数据要满足一个核心条件：同一个 prompt 采出来的 $G$ 条回答，能比较、能验证，而且得分有差异。GRPO 的信号来自同一输入提示下 $G$ 条采样轨迹（rollout）的相对优势，组内几乎全对或全错时，group-normalized advantage 接近零，加再多条也是空转。所以我会先报有效 group 比例，再报样本量。把它讲成「再多采一些 SFT 题」就答偏了。

公式上看得更清楚，advantage 是组内相对量：$\hat A_i=(r_i-\bar r)/\sigma_r$。构造数据就是在设计 $r$ 的可分性。比如一道数学题，当前模型采几次有对有错，这组就有信号；模型已经稳定做对的题，组内方差为零，只会白占 rollout。全同组零优势见 `byte-grpo-all-same-zero-adv`、`ali-grpo-advantage`。

第一个要求是难度。题目要落在当前 policy 的可探索区间，太易全对，太难全错，只堆 benchmark 最难的题也不行。选题和过滤同 `data-rlvr-select`，用 pass@$k$ 和 pass@$1$ 的差衡量还有没有探索空间。构造阶段就拒绝两类题：看起来很难、当前政策却零通过的，留给 SFT 或者更强的教师模型（teacher）去示范；已经 95% 通过的，它们只会制造空组。训练中也要动态过滤：pass 率已经饱和的题降权或移出，全错的题先回到 SFT 或降难度，免得空转浪费 rollout。方差 $\approx 0$ 的退化 group 要动态过滤或重采样，别静默地当成零梯度样本。必要时做 curriculum，先中等难度再放长尾；curriculum 的意思是始终维持一个探索带，让一部分题的 pass@$1$ 一直在中间，从易到难一条路走完并不对。

第二个要求是 reward 稳定。可执行的验证器（verifier）优先于 LLM judge，数学和代码优先跑测试或符号等价；开放任务才上 judge 或奖励模型（RM），而且要抽样人审、看校准和对抗套话（`data-verifier`）。同一个输入提示的 $G$ 条里，要允许格式对答案错、答案对但过程长、以及等价解。verifier 只认唯一字符串时，等价的正确答案会被打成负例，政策就学会套模板。格式和长度投机要有防护（`data-length-hacking`），等价解、格式变体、部分正确都要在 reward 设计里显式处理，否则组方差是假的，全是格式分在抖。组内熵塌缩时，先查数据是不是全变成了模板，别先去加大学习率（`data-entropy-collapse`）。

第三个要求是分布和去污。训练和 eval 要去重，检查领域和长度分布、重复题模板，改几个数字的同一道题要去掉；控制长度分布，免得长题占满上下文、短题学不到。奖励直方图应该能看到中间质量，只有两极说明有问题。prompt 分布要对着产品 query，只对着公开榜单的话，holdout 涨了，产品 query 不动。

这题和「什么时候 GRPO 不好用」是同一面的前后问（`tencent-teg-grpo-when-bad`）：奖励不可靠、组内没方差、格式都还没学会时，先别上 GRPO，数据要求就是把这三类情况挡在进池之前。有效 group 比例要写进 dashboard，低于阈值就停下来查 verifier 和配比，别把学习率加大。常见的失败有：监督微调（SFT）已经会的题继续 GRPO，结果全是空 group；verifier 不认等价答案，惩罚了正确的推理；评测题泄漏，造成假涨。SFT 示范正确轨迹，强化学习（RL）要可打分的难例，两者别混成同一份 jsonl。

## 追问

**有效 group 怎么定义？**
组内 reward 的标准差明显大于噪声，并且至少有一条可学的相对排序。全 $0$ 或全 $1$ 都无效。

**没有程序 verifier 能做吗？**
能用 RM 或 judge，但要把它当成需要校准的对象，hack 风险就回到了基于人类反馈的强化学习（RLHF）那一套。能用规则、单测和 schema 校验的，优先用。

**和 PPO 的数据有什么区别？**
都要 on-policy、可打分。GRPO 更依赖组内方差，因为没有价值评估模型（critic）来平滑，对「全对 / 全错」更敏感。

**$G$ 越大越好吗？**
$G$ 增大能让组内估计更准，但 rollout 成本线性上涨。先保证难度带，再加 $G$。

**泄漏怎么防？**
做题面指纹和评测 n-gram 重叠表。泄漏会让有效 group 看起来很健康，holdout 却是假的。
