---
id: tencent-moe-vs-dense
section: arch
order: 202
level: A
title: 腾讯混元一面：MoE 相对 Dense 赚在哪、亏在哪？
quick: >-
  赚的是同等激活参数下容量更大；亏的是路由不均、专家通信和训练/推理两套并行。我会画
  top-$k$ 路由，并说出何时 Dense 更稳：数据少、延迟硬约束、或还不会做负载均衡。
tags:
  - Tencent
  - Hunyuan
  - MoE
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯 · 混元
- 岗位：大模型日常实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“MoE 和 Dense 比，优势和代价是什么？”**

这块容易只复读「稀疏省算力」。MoE 总参数往往更大，省的是每 token 激活的 FFN；代价是路由、通信、训推两套并行。和同面「Qwen vs DeepSeek」连问时，落到共享专家与 MLA，见 `tencent-qwen-vs-deepseek`、`arch-moe`。参数怎么拆见 `minimax-param-breakdown`。

## 赚：容量与激活解耦

Dense 每层 FFN 全量激活；MoE 把 FFN 换成 $E$ 个专家，token 经 router 选 top-$k$（可加共享专家）：

$$
y=\sum_{i\in\mathrm{Top}k} g_i(x)\,E_i(x).
$$

总参数可到百 B / 万亿，单 token 只跑 $k$ 个专家，激活 FLOPs 接近「小 Dense」。同等激活下容量更大，长尾知识、多领域更好装。Router 本身是 $d\times E$，相对专家矩阵可忽略。我会画：token → 门控 logits → softmax/sigmoid → 取 top-$k$ → 分发到专家 → 加权合回。

何时 Dense 更稳：数据少（专家学不热、路由塌缩）、延迟硬约束（小 batch 时 all-to-all 吃掉稀疏红利）、团队还不会做负载均衡。不要在 7B 数据、单机推理场景硬上 MoE。

## 亏：不均、通信、训推两套世界

- **负载不均**：少数专家吃掉流量，其余坏死；aux loss / sequence-level balance / capacity factor 防塌缩，见 `arch-moe-balance`、`ant-moe-aux-load-balance`、`code-moe-router-aux-loss`。capacity 太紧则 drop token，见 `sys-moe-capacity-token-drop`。
- **通信**：expert parallel 要把 token 按专家 all-to-all；EP size 绑通信体积。小 batch、decode 单 token 时 MoE 并不更快。
- **训推不一致**：训练 drop / 不同 capacity，serving 另一套 top-$k$ 或 EP，路由统计对不齐，见 `sys-moe-train-infer-routing-mismatch`。RL 还会让路由跟着政策漂，见 `stepfun-rl-moe-gspo`。

评测时必须关掉训练专用的随机 drop，用与线上一致的路由。混元若追「和 Dense 训练稳定性」，承认 MoE 超参面更大：lr、aux 系数、$k$、capacity 要一起拧。

## 追问

- **稀疏一定省钱吗？** 训练算力按激活，存盘和通信按总参数与 EP。小 batch 推理常更慢。报激活 FLOPs，不要报总参数当算力。
- **$k=1$ 和 $k=2$？** $k=1$ 更省、更脆；$k=2$ 是常见折中。共享专家等于再加固定激活，见 DeepSeek 细粒度 MoE。
- **aux loss 挂了还塌缩？** 系数过小、数据偏科、或 RL 后分布变了。看专家利用率直方图，不要只看平均 loss。
- **为何数据少时 Dense 更好？** 专家需要被足够 token 训热；样本不够则大量专家欠拟合，还不如一份 Dense FFN。
- **和 GQA/MLA 是一回事吗？** 不是。GQA/MLA 压 KV cache；MoE 压的是 FFN 激活。同面连问时分开讲，见 `arch-mla`。
