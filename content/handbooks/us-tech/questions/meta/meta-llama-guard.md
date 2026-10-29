---
id: meta-llama-guard
section: meta
order: 17
level: A
title: Meta：Llama Guard 当独立安全分类器，和基座对齐怎么分工
quick: >-
  Llama Guard 是独立训练的因果 LM 安全分类器，输入风险策略和对话，输出 safe / unsafe 与风险类别，用首 token
  概率设阈值。基座对齐负责改变生成行为，Guard 提供可独立更新的输入输出检查，两者互补，同时要量延迟、FPR 与 over-refusal。
tags:
  - Meta
  - Llama
  - Safety
  - Llama Guard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Llama Guard — LLM-based Input-Output Safeguard for Human-AI Conversations
    url: 'https://arxiv.org/abs/2312.06674'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: PurpleLlama Llama Guard
    url: 'https://github.com/meta-llama/PurpleLlama'
    type: primary
  - title: Llama Guard 3 8B model card
    url: 'https://huggingface.co/meta-llama/Llama-Guard-3-8B'
    type: primary
---

Llama Guard 与基座对齐分开，是为了让安全分类按独立的策略、损失和发布节奏更新。基座学习怎样有用地回答与拒绝，Guard 则读输入或输出，给出可调阈值的风险判定，同一 Guard 也能服务多个基座。

原始 Guard（2023）基于 Llama 2-7B 指令微调，Guard 3 用 Llama 3.1-8B，Herd 建议与 3.1 一起部署。它仍是因果 LM，输入含明文风险 taxonomy、要判 user prompt 还是 assistant response、完整对话，输出首 token `safe` 或 `unsafe`，unsafe 时下一行列类别。分数从首个生成 token 读取，不是另接 $[D, 2]$ 线性头。

例如同一句“怎么做炸弹”，用户侧是在提出请求，回答侧则要分清是教了还是拒绝，两种指令的标签可能不同。训练时丢类别、打乱编号等增强，使策略可以作为文本替换，支持 zero-shot / few-shot 适配；实际改 taxonomy 仍要在自己的政策集画 PR，不能保证无损。与 OpenAI Moderation、ToxicChat 的公开对比也因 taxonomy 不同，只能谨慎比较量级。

## 部署时怎样分工

预训练、SFT、DPO 的安全改变基座生成分布，政策变更可能要重训，也可能影响能力，合成 SFT 还会改变拒答风格，见 `meta-synth-sft`。Guard 作为独立 7B/8B 检查器可单独改 prompt 或微调权重，无需每次改政策重训 405B；系统仍需正则、工具白名单与检索过滤等其他 safeguards。

主模型生成外再跑 Guard，相当于额外 $8\mathrm{B}$ prefill，也可只对高风险流量用，不能当零成本。短输入通常较容易接受，长上下文要考虑量化、分类窗口截断或触发词后的满窗检查，同时验证覆盖。分类不能只看最后一句，RAG 检索片段与代码工具结果也需进入 response 判定，避免遗漏有害引用。

模板必须与训练一致，多一个 `begin_of_text` 或角色头，都可能使首 token 分布漂移。用首 token $\log p(\texttt{unsafe})$ 设阈值，别把 Guard 的文本当聊天回答，也别把 chat 回复“我不能帮你”当稳定风险分。只拦输出会让越狱先进入主模型上下文，输入检查也有意义。

按类别可用 1-vs-all，每次 prompt 只放一个类别读 unsafe 概率，但成本乘类别数，生产常先二分类、再对 unsafe 解多标签。Guard 3 对齐 MLCommons 危害并加 Code Interpreter Abuse，覆盖多语言工具调用；Herd 也提示系统安全提高时良性请求误拒可能增加，要同时报 FPR 与拒答率。

测试集需与 taxonomy 对齐，并留政策外 holdout，避免公开 jailbreak 既进 SFT 又被拿来报告安全。能力套餐见 `meta-llama-eval`，MMLU 无法证明安全。基座可一周升级一次，政策变化只换 Guard prompt 或微调 8B，体现独立维护的价值。

## 追问

**能给基座加分类头吗？**
能，但策略文本替换与 zero-shot taxonomy 适配方式会变，独立模型也更便于跨基座复用。

**与 RLHF 拒答重复吗？**
互补，RLHF 改生成行为，Guard 做事前事后检查与阈值决策。

**误拒怎么降？**
调阈值、few-shot 加硬负例，或按产品政策微调，同时量 PR、FPR 和任务效果。

**Prompt Guard、Code Shield 是同一模型吗？**
不是。前者拦注入，后者拦不安全代码，Llama Guard 做对话危害分类，不能绑成一个 checkpoint。
