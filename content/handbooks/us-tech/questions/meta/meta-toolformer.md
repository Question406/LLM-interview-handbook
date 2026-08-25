---
id: meta-toolformer
section: meta
order: 28
level: A
title: Meta：Toolformer 式自监督工具调用
quick: >-
  不是 SFT 出来的 function calling。用少量示范让 LM 在语料上采样 API 调用，执行后只留下「能降低后续 token
  NLL」的调用，再拿这些文本微调。学的是何时调用、填什么参数、怎么把返回值接回生成。和 Llama 3 指令工具、生产
  schema 不是同一层，见 `openai-function-calling`。
tags:
  - Meta
  - Toolformer
  - Tools
  - Self-supervised
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Toolformer — Language Models Can Teach Themselves to Use Tools
    url: https://arxiv.org/abs/2302.04761
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: secondary
  - title: Function calling — OpenAI
    url: https://platform.openai.com/docs/guides/function-calling
    type: secondary
---

FAIR 2023 的 Toolformer（Schick et al.）是工具题的「自监督」标准答法。基座是 GPT-J $6.7\mathrm{B}$，不是 Llama 3。Llama 岗问它，是看你能不能把它和 **Herd 里的指令工具 / JSON 调用** 拆开。生产执行、超时、幂等见 `design-tool-prod`；代码 agent 的工具环见 `meta-agent-code`。

## 流水线：采样 → 执行 → 用损失过滤 → 微调

工具是文本 API：计算器、问答（论文用 Atlas）、维基检索、翻译、日历。每种只给 **极少人工示范**。然后：

1. 在普通 LM 语料上，用 in-context 示范让模型插入调用，形如 `QA("...")` 或计算器表达式，位置自己选。
2. 真的执行，把结果写成 `调用 → 返回值`。
3. **过滤：** 只留对预测 **后面的词** 有帮助的调用。
4. 用过滤后的文本做普通因果微调。推理时生成到调用边界就停、执行、把结果当前缀继续写。

过滤是这篇文章的核心，不是「会输出 JSON」。对位置 $i$ 的候选调用 $c_i$、返回 $r_i$，看后续 token 的加权 NLL：

$$
L_i^{+}=L_i\big(e(c_i,r_i)\big),\quad L_i^{-}=\min\big(L_i(\varepsilon),\,L_i(e(c_i,\varepsilon))\big)
$$

$e(\cdot)$ 是把调用（和可选结果）放到前缀里；$L_i(\varepsilon)$ 是完全不调用。留下当且仅当 $L_i^{-}-L_i^{+}\ge\tau_f$。直觉：光写调用语法、执行失败、或返回值和下文无关，都不如不调。论文把 $e(c,r)$ 放在 **前缀** 而不是插进句子中间，因为过滤阶段模型还没见过这种格式，插中间会无故抬 perplexity。

```python
def keep_call(L_none, L_call_empty, L_call_result, tau):
    L_minus = min(L_none, L_call_empty)
    return (L_minus - L_call_result) >= tau
```

例子：「Pittsburgh is known as the Steel City。」若 QA 返回 Steel City，后续那几个词的 NLL 会掉一大截，调用留下；若问了无关问题，NLL 几乎不降，丢掉。计算器同理：只有后文真是那个数字才留。

## 它学到的和学不到的

学到的：何时调、调哪个、参数怎么填、结果怎么抄回。论文报在若干零样本下游上，小模型加工具能接近更大的纯 LM，同时语言模型能力不明显塌——因为微调数据仍是原来的语料分布，只是多了有用的调用。

学不到的：多步规划、用户级权限、失败重试、并行工具。过滤目标是 **语料 next-token**，不是「用户想完成任务」。语料里很少出现「先搜再算再写邮件」，模型就不会规划。有害调用只要能帮它猜下一个词，过滤器也会放行——所以这不是安全层。

和 Llama 3 工具的差别：Herd / 3.1 把工具当 **指令跟随**：schema、SFT、偏好对齐、评测用 Nexus / BFCL 一类，见 `meta-llama-eval`。那是「用户 / 系统要求你调」。Toolformer 是「为了写对这句话自己决定调」。现场把两套损失画开，比背 API 名字有用。

错法：说 Toolformer 就是 ReAct。ReAct 是推理轨迹 + 标注或提示；Toolformer 是自监督过滤。错法二：过滤用执行成功率或人工赞。论文用的是 NLL 差。错法三：生产上让模型直接 `eval` 参数字符串。过滤可以在离线语料上跑；在线必须宿主校验，见 `openai-function-calling`。

## 追问

- **$\tau_f$ 太大怎么办？** 几乎调不成，退回纯 LM。太小则插入对 perplexity 无用的调用，浪费上下文、也教坏格式。要在验证 NLL 和下游之间扫。
- **工具会不会泄漏训练答案？** 会。QA / 检索若索引了评测集，数字是检索不是能力。过滤集和评测要隔离。
- **能不能代替 SFT 工具？** 不能当产品唯一来源。它适合给小模型补计算器 / 检索。对话助手、写库、要确认的副作用，仍要 schema + 宿主状态机。
- **调用格式为什么用方括号文本？** 2023 年的可解析约定，不是 JSON Schema。今天会改成结构化解码，过滤准则仍可复用。
- **和检索增强呢？** 维基工具是按需检索，调用与否由损失决定。和「每条请求都 embedding 检索」不同。始终检索更稳、更贵；Toolformer 更省、更易漏。
---
