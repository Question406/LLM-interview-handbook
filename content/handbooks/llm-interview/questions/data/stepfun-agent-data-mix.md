---
id: stepfun-agent-data-mix
section: data
order: 163
level: S
title: 阶跃：RL 训 Agent 调工具时，数据怎么优化、配比如何定？
quick: >-
  配比为奖励和探索服务：保留难例、失败恢复和长尾工具，给「一搜就中」的简单成功轨迹设上限，按工具和失败桶的 holdout 成功率与有效 group
  比例来调，条数 1:1 说明不了什么。过期环境的轨迹要丢掉或在新环境重放标注，一次只改一维比例，并记下环境 hash。
tags:
  - StepFun
  - Agent RL
  - Data Mixture
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰agent算法面经分享
    url: 'https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee'
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：Agent 算法
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-30
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“怎么优化 RL 训练 agent 调用工具的数据，数据配比策略是怎样的”**

我的思路是，RL 的数据配比为奖励和探索服务：简单成功轨迹设上限，难例、失败恢复和长尾工具要保住，比例按各桶的 holdout 成功率和有效 group 比例来调。「成功 : 失败 = $1:1$」或者「每种工具条数一样」都说明不了什么，条数相等还会掩盖「一条热轨迹被复制了一万次」。评委想听的是 sampling 怎么服务奖励和探索，把 jsonl 凑齐没有用。

原因在 group 里。比如池子被「搜一下就能答」的题占满，同一个 prompt 采出来的几条轨迹几乎全对，advantage 塌成零，策略学不到澄清、换工具和失败恢复。sampling 温度再高，池子里没有难例也探索不出来。这和 GRPO 全同组的问题是同一件事，配比决定你能不能采到 $G$ 条可比较的轨迹。同一面的奖励设计见 `stepfun-agent-tool-training`，配比是奖励的 sampling 侧，两边要讲成一个故事。

先分清 SFT 和 RL 的数据。SFT 冷启动要覆盖合法的字段和类型规范（schema）、典型的失败恢复和拒绝越权，这是合法格式的基础训练，当不了 RL 的主信号。Agent 后训练的阶段划分见 `byte-agent-posttrain-data-stage`：SFT 示范正确轨迹，RL 要可打分的难例，两套数据别混成同一份。

RL 池按工具、步数、失败类型、环境版本分组统计。低成功的桶提高 sampling，热轨迹设上限，防止一条「总能搜到」的路径刷奖励。选例逻辑和 `data-rlvr-select`、`meituan-easy-hard-sft-balance` 同类，难度要落在当前 policy 能探索的区间。我会把每个 prompt 看成「在当前政策下的难度标签」，它会随政策变化，和静态的题型分类不一样。每周用当前 actor 在 holdout 上估 pass@$1$ 和 pass@$k$：两者的差接近零，说明这个桶该降权或者移出 RL，改回 SFT 示范；差很大、pass@$1$ 又低，说明值得加 sampling。工具维度再切一刀：主路径工具（搜索、读文件）设上限，免得占满 batch；长尾工具（冷门 API、少见错误码）设下限，但每条都必须能回放。失败恢复轨迹单独记账，「第一次 call 错、第二次改参成功」比「一次成功」更值钱，因为 credit 落在过程上。

数据本身也要洗。用验证器（verifier）丢掉不可回放、schema 非法或者环境版本对不上的轨迹（`data-verifier`）；成功但步数虚高的轨迹降权，避免长度投机（`data-length-hacking`）。过期 API 或沙箱的旧轨迹必须丢掉或重放标注，否则奖励是在教过时的行为；和环境版本绑定的轨迹，一旦 schema 改了字段，整桶作废，别靠在 prompt 里写「忽略旧字段」混过去。线上的工具超时、空结果、权限拒绝要进失败桶，不能丢，否则政策从没见过真实噪声，也学不会在噪声里换工具，只会走演示路径。

配比数字我会给一个能复述的起点，例如主成功不超过 $30\%$，失败恢复 $25\%$，长尾工具 $20\%$，需澄清 / 拒答 $15\%$，其余是 general-capability regression data。这些只是实验起点。调的时候一次只改一类（比如长尾工具或「需澄清」桶），并写清环境 hash，同时看这一类的 holdout 有没有升、regression tasks 有没有掉、平均步数和工具错误率怎么变。来源级配额比按原始 volume 直接拼接更稳，思路同 `kuaishou-sft-source-mix`。监控上看有效 group 率、平均工具步数、非法 call 率和各桶的奖励方差；方差掉下去，先查配比是不是被简单成功淹没，再查奖励是不是被长度或格式投机主导。配比账本要进实验记录，和 `dataset_version`、环境 hash、奖励分数（reward）版本绑在一起，否则下周说不清「这一版成功率为什么掉」。

几种典型的失败：只堆成功演示，探索就没了；不过滤过期环境，离线表现涨、线上却掉；调整 data mix 时不检查 regression performance，长尾工具学会了，主路径却回归了。

## 追问

**条数 1:1 为什么不够？**
简单成功轨迹容易拿到正奖励、条数又多，会淹没难例。要按错误类型分别统计成功率和有效 group 率来调 sampling。

**过期环境的轨迹怎么处理？**
丢掉，或者在新环境里重放标注，不能靠 importance weight 硬修不可回放的轨迹。环境 hash 写进样本元数据，对不上就拒收。

**和奖励设计怎么分工？**
奖励定义「什么算对」，配比决定「哪些对和错被看到」。先冻结 reward 再扫 mixture，否则分不清是奖励漂了还是 sampling 漂了。

**失败恢复要不要算成功？**
最终成功可以给正奖励，但步数虚高要降权；过程中的非法 call 仍然要罚，免得学会「先乱调再碰对」。

**SFT 和 RL 能共用一份配比吗？**
不能。SFT 要覆盖合法格式和 refusal criteria，RL 要难度带和方差。混用会把简单示范重复送进 group，有效 group 率会掉。
