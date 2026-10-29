---
id: meta-toolformer
section: meta
order: 28
level: A
title: Meta：Toolformer 式自监督工具调用
quick: >-
  Toolformer 用少量工具示范让 LM 在语料中提出调用，实际执行后，只保留能降低后续 token NLL
  的结果，再做因果微调。它由损失变化学习何时调用和怎样填参；权限、重试与多步任务规划仍要另外设计。
tags:
  - Meta
  - Toolformer
  - Tools
  - Self-supervised
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Toolformer — Language Models Can Teach Themselves to Use Tools
    url: 'https://arxiv.org/abs/2302.04761'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: secondary
  - title: Function calling — OpenAI
    url: 'https://platform.openai.com/docs/guides/function-calling'
    type: secondary
---

## 可以这样回答

Toolformer 用后续文本的预测损失来筛选工具调用，再把有帮助的调用写进微调数据。比如一句话要补出 Pittsburgh 的别名，QA 工具返回 Steel City，若让后面几个词更容易预测，这条调用就留下。FAIR 2023 的 Schick et al. 工作使用 GPT-J $6.7\mathrm{B}$，与 Llama 3 Herd 的指令工具训练不同。

$e(\cdot)$ 是把调用（和可选结果）放到前缀里；$L_i(\varepsilon)$ 是完全不调用。留下当且仅当 $L_i^{-}-L_i^{+}\ge\tau_f$。直觉：光写调用语法、执行失败、或返回值和下文无关，都不如不调。论文把 $e(c,r)$ 放在 **前缀** 而不是插进句子中间，因为过滤阶段模型还没见过这种格式，插中间会无故抬 perplexity。

## 技术备查

Toolformer 用后续文本的预测损失来筛选工具调用，再把有帮助的调用写进微调数据。比如一句话要补出 Pittsburgh 的别名，QA 工具返回 Steel City，若让后面几个词更容易预测，这条调用就留下。FAIR 2023 的 Schick et al. 工作使用 GPT-J $6.7\mathrm{B}$，与 Llama 3 Herd 的指令工具训练不同。

## 为什么用后续 NLL 筛调用

工具是文本 API：计算器、问答（论文用 Atlas）、维基检索、翻译、日历。每种只给 **极少人工示范**。然后：

1. 在普通 LM 语料上，用 in-context 示范让模型插入调用，形如 `QA("...")` 或计算器表达式，位置自己选。
2. 真的执行，把结果写成 `调用 → 返回值`。
3. **过滤：** 只留对预测 **后面的词** 有帮助的调用。
4. 用过滤后的文本做普通因果微调。推理时生成到 call interface 就停、执行、把结果当前缀继续写。

筛选依据是调用对后续预测有没有帮助。对位置 $i$ 的候选调用 $c_i$、返回 $r_i$，看后续 token 的加权 NLL：

$$
L_i^{+}=L_i\big(e(c_i,r_i)\big),\quad L_i^{-}=\min\big(L_i(\varepsilon),\,L_i(e(c_i,\varepsilon))\big)
$$

$e(\cdot)$ 是把调用（和可选结果）放到前缀里；$L_i(\varepsilon)$ 是完全不调用。留下当且仅当 $L_i^{-}-L_i^{+}\ge\tau_f$。直觉：光写调用语法、执行失败、或返回值和下文无关，都不如不调。论文把 $e(c,r)$ 放在 **前缀** 而不是插进句子中间，因为过滤阶段模型还没见过这种格式，插中间会无故抬 perplexity。

```python
def keep_call(L_none, L_call_empty, L_call_result, tau):
    L_minus = min(L_none, L_call_empty)
    return (L_minus - L_call_result) >= tau
```

回到「Pittsburgh is known as the Steel City。」这个例子，无关 QA 不会明显降低后续 NLL，就会被丢掉。计算器同理，只有返回数字确实帮助预测后文时才留。

## 这种训练能支持到什么范围

模型由此学习何时调用、选哪个工具、怎么填参数和引用返回值。论文报在若干零样本下游上，小模型加工具能接近更大的纯 LM，同时语言模型能力没有明显下降，因为微调数据仍是原来的语料分布，只是多了有用的调用。

这项过滤没有直接监督多步规划、用户级权限、失败重试和并行工具。过滤目标是 **语料 next-token**，不是「用户想完成任务」。语料里很少出现「先搜再算再写邮件」，模型就不会规划。有害调用只要能帮它猜下一个词，过滤器也会放行，所以这不是安全层。

和 Llama 3 工具的差别：Herd / 3.1 把工具当 **指令跟随**：字段和类型规范（schema）、SFT、偏好对齐、评测用 Nexus / BFCL 一类，见 `meta-llama-eval`。那是「用户 / 系统要求你调」。Toolformer 是「为了写对这句话自己决定调」。所以要分别说明指令跟随的损失与语料预测的损失。

它与 ReAct 的训练来源也不同：ReAct 依靠推理轨迹及标注或提示，Toolformer 用自监督 NLL 差过滤，执行成功率和人工点赞都不是这里的筛选目标。离线过滤完成后，上线仍须宿主校验，不能直接 `eval` 模型给的参数字符串，见 `openai-function-calling`。

相关：`design-tool-prod`、`meta-agent-code`。

## 追问

**$\tau_f$ 太大怎么办？**
几乎调不成，退回纯 LM。太小则插入对 perplexity 无用的调用，浪费上下文、也教坏格式。要对比不同阈值下的验证 NLL 与下游任务表现。
**工具会不会泄漏训练答案？**
会。QA / 检索若索引了评测集，数字是检索不是能力。过滤集和评测要隔离。
**能不能代替 SFT 工具？**
不能当产品唯一来源。它适合给小模型补计算器 / 检索。对话助手、写库、要确认的副作用，仍要 schema + 宿主状态机。
**调用格式为什么用方括号文本？**
2023 年的可解析约定，不是 JSON Schema。今天会改成结构化 decoding，过滤准则仍可复用。
**和检索增强呢？**
维基工具是按需检索，调用与否由损失决定。和「每条请求都 embedding 检索」不同。始终检索更稳、更贵；Toolformer 更省、更易漏。
