---
id: pdd-window-not-always-better
section: systems
order: 162
level: A
title: 拼多多：上下文窗口越大越好吗？对显存、延迟、成本和效果有何影响？
quick: "窗口更大只表示能放进更多内容，实际填入更长输入会增加 prefill 计算、KV 显存、延迟和费用，也可能因无关信息和中间遗忘降低效果。比如三个工具的 JSON 远比用户问题长时，应先精简结果、检索和摘要，再给必要证据留窗口。"
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

上下文窗口更大，能容纳更多内容，但效果要看模型能否用对这些内容，以及任务是否值得付出相应成本。实际输入变长，会增加 prefill 计算和 KV 显存；无关日志还可能稀释 attention，中间证据更容易漏掉，训练长度之外的位置外推也可能掉点。

比如把整店目录和全部工具 trace 都塞进去，模型可能既慢又选错 SKU。我会先检索缩短输入，用摘要保留会话状态，再留近轮原文和必要证据。窗口、便宜地处理长文本和溢出策略需要一起设计。

## 显存、延迟、成本

KV 约随 $\mathrm{layers}\times \mathrm{kv\_heads}\times \mathrm{dim}\times \mathrm{seq}\times \mathrm{batch}\times \mathrm{bytes}$ 线性涨。GQA 降的是 kv_heads，量化降 bytes，长度 $N$ 仍线性。Decode 每步扫更长 cache，带宽随 $N$ 涨；prefill attention 近二次方（即使用 FA 也随 $N$ 变贵）。连续 batching 下，超长请求会占住 KV 页，挤掉短请求，p99 变差，这是公平性，见 `sys-kv-fair-allocation`。成本：按 token 计费时，填入不必要的上下文会增加费用；自建集群则是 GPU 时和 HBM。评估是否省了多轮调用时，也要比较一次长 prefill 与两轮检索的实际成本。

Agent 还有隐藏长度：工具返回、检索文档、系统 字段和类型规范（schema）。三个工具的 JSON 可能比用户问题长一个数量级。减 schema、只留命中文档，比把 `max_model_len` 从 32k 调到 128k 更有效。

## 效果：更长不等于更准

长窗能装下合同，但中间位置的条款召回更差；噪声上下文（过期会话、无关 SKU）会抢 attention。位置外推（线性插值、NTK）在训练 out-of-distribution 会掉点。评测要用真实长工单，而不是只报窗口数字。业务评测要检查模型是否正确使用了证据。短名单 + 强制引用 id，比 100 页原文更可控。

溢出策略：滑动窗口丢最旧轮（会话记忆另存）、摘要压缩、检索替换全文。静默截断头部或尾部都可能砍掉价格/除外条款。超预算应降级或让用户缩小范围。



给真正需要的证据留空间：近轮对话、命中的 $k$ 条商品字段、当前工具结果。系统提示固定并 prefix cache。任务预算写进产品：客服 8k、比货 16k、禁止整店。和 `pdd-long-context-cheap` 衔接：先缩短，再对必须进模型的部分用 GQA/量化/分块。

## 追问

**KV 怎么涨？**
近似线性于 $\mathrm{seq}\times\mathrm{kv\_heads}\times\mathrm{layers}\times\mathrm{bytes}$。GQA 和量化只改系数。逐 token 生成（decode） 每步扫全 cache，所以延迟也随 $N$ 涨；prefill attention 即使走 FA 仍随 $N$ 变贵。
**为什么效果可能变差？**
Lost in the Middle：中间位置的条款更难被用上。噪声工具日志稀释 attention。训练 out-of-distribution 的位置外推掉点。看见了不等于用对了。短名单 + 强制引用 id 往往更准。
**工具日志要不要全放？**
不要。只留本轮结果和必要状态。全量 trace 是最贵的噪声，也是 Agent 窗口被撑爆的主因。减 schema、只暴露候选工具，比把窗口调到 128K 更有效。
**128K 能不能当默认？**
当上限。默认填入仍应是检索/摘要后的短上下文，否则成本和中间遗忘先爆。支持 128K 不是已经优化过延迟。
**和公平调度的关系？**
超长请求占满 KV 页会使短请求长时间等待，p99 变差。要按 token 预算做 admission，见 `sys-kv-fair-allocation`。只调大窗口不管调度，短问句先受伤。
