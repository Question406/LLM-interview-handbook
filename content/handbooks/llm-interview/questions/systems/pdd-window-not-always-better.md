---
id: pdd-window-not-always-better
section: systems
order: 162
level: A
title: 拼多多：上下文窗口越大越好吗？对显存、延迟、成本和效果有何影响？
quick: >-
  更大窗口提高 prefill 计算与 KV 显存，延迟和费用近似随长度涨，但「中间遗忘」和噪声上下文可能让效果变差。先检索 / 摘要，窗口只给真正需要的证据。
tags:
  - PDD
  - Long Context
  - KV Cache
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多 AI Agent 岗两轮技术面经
    url: https://www.nowcoder.com/discuss/918542384726540288
    type: candidate-first-hand
  - title: Lost in the Middle
    url: https://arxiv.org/abs/2307.03172
    type: primary
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：AI Agent
- 届别 / 流程：二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“上下文窗口越大越好吗？它对显存、延迟、成本和模型效果有什么影响？”**

错法：答成「窗口越大效果越好」。更大窗口提高 prefill 计算与 KV 显存，延迟和费用近似随长度涨，但无关工具日志会稀释注意力，中间证据更容易丢（Lost in the Middle）。训练若从未见过这么长，外推还会掉点。窗口是上限不是目标。和「能看长但不贵」、溢出策略组成一套：检索缩短 → 摘要保状态 → 窗口只留近轮原文。拼多多 Agent 把整店目录或全量工具 trace 塞满窗口，往往既贵又错。

## 显存、延迟、成本

KV 约随 $\mathrm{layers}\times \mathrm{kv\_heads}\times \mathrm{dim}\times \mathrm{seq}\times \mathrm{batch}\times \mathrm{bytes}$ 线性涨。GQA 降的是 kv_heads，量化降 bytes，长度 $N$ 仍线性。Decode 每步扫更长 cache，带宽随 $N$ 涨；prefill 注意力近二次方（即使用 FA 也随 $N$ 变贵）。连续 batching 下，超长请求会占住 KV 页，挤掉短请求，p99 变差，这是公平性，见 `sys-kv-fair-allocation`。成本：按 token 计费时塞满窗口就是烧钱；自建集群则是 GPU 时和 HBM。不要用「一次塞进去省多轮」掩盖单次 prefill 已经贵过两轮检索。

Agent 还有隐藏长度：工具返回、检索文档、系统 schema。三个工具的 JSON 可能比用户问题长一个数量级。减 schema、只留命中文档，比把 `max_model_len` 从 32k 调到 128k 更有效。

## 效果：更长不等于更准

长窗能装下合同，但中间位置的条款召回更差；噪声上下文（过期会话、无关 SKU）会抢注意力。位置外推（线性插值、NTK）在训练分布外会掉点。评测要用真实长工单，而不是只报窗口数字。业务上「看全」常常是错觉：模型看见了不等于用对了。短名单 + 强制引用 id，比 100 页原文更可控。

溢出策略：滑动窗口丢最旧轮（会话记忆另存）、摘要压缩、检索替换全文。静默截断头部或尾部都可能砍掉价格/除外条款。超预算应降级或让用户缩小范围。

## 怎么选窗口

给真正需要的证据留空间：近轮对话、命中的 $k$ 条商品字段、当前工具结果。系统提示固定并 prefix cache。任务预算写进产品：客服 8k、比货 16k、禁止整店。和 `pdd-long-context-cheap` 衔接：先缩短，再对必须进模型的部分用 GQA/量化/分块。

## 追问

- **KV 怎么涨？** 近似线性于 $\mathrm{seq}\times\mathrm{kv\_heads}\times\mathrm{layers}\times\mathrm{bytes}$。GQA 和量化只改系数。decode 每步扫全 cache，所以延迟也随 $N$ 涨；prefill 注意力即使走 FA 仍随 $N$ 变贵。
- **为什么效果可能变差？** Lost in the Middle：中间位置的条款更难被用上。噪声工具日志稀释注意力。训练分布外的位置外推掉点。看见了不等于用对了。短名单 + 强制引用 id 往往更准。
- **工具日志要不要全放？** 不要。只留本轮结果和必要状态。全量 trace 是最贵的噪声，也是 Agent 窗口被撑爆的主因。减 schema、只暴露候选工具，比把窗口调到 128K 更有效。
- **128K 能不能当默认？** 当上限。默认填入仍应是检索/摘要后的短上下文，否则成本和中间遗忘先爆。支持 128K 不是已经优化过延迟。
- **和公平调度的关系？** 超长请求占满 KV 页会饿死短请求，p99 变差。要按 token 预算做 admission，见 `sys-kv-fair-allocation`。只调大窗口不管调度，短问句先受伤。
