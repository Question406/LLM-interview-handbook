# 旧题卡细查与修复记录（2026-10-18）

本轮范围是「美国 Tech / Frontier Lab 真题」手册中不以 `p3a-` 开头的 **420 张旧卡**，不是整个六本手册，也不是重新遍历网站所有面经。

## 覆盖与结果

| 项目 | 数量 | 检查深度 |
|---|---:|---|
| 全部旧卡 | 420 | 结构、题型、代码块与题间引用盘点 |
| 完整编程/实验练习 | 70 | 题面、接口、示例、实现、测试、复杂度逐项核对 |
| 本轮补全的旧卡 | 50 | 44 张白板题，加 6 张公司题卡，原 ID 不变 |
| 上轮已补全 | 20 | 复查展示代码并重新执行题内测试 |
| 技术知识/系统设计讲解 | 328 | 保留讲解用途；未把它们冒称为 coding 原题 |
| 流程/备考/导航 | 22 | 保留原用途 |

70 张旧卡合计 61 份不同的展示程序。共享实现不等于新增独立题目。完整目录及逐卡分类见 `inventory.csv` / `inventory.json`，本轮修改文件见 `manifest.json`。

## 主要问题与修正

| 问题 | 修正与验证 |
|---|---|
| 故意错误示例与参考代码混杂 | 正确实现移至卡片最前；9 张教学 debug 卡保留独立标记的错误起始片段，验证器只执行正确实现与测试 |
| 大量白板题只有函数片段 | 44 张均补齐独立接口、约束、示例、完整实现、可执行测试和复杂度；旧片段合并到参考实现，避免两套答案冲突 |
| Gumbel-max 温度位置错误 | 硬类别采样使用 `argmax(z/tau+g)`，标准松弛使用 `softmax((z+g)/tau)`；固定种子与分布频率测试 |
| 全局减常数被错说成改变 softmax 语义 | 区分精确平移不变与浮点下溢风险；验证逐行平移不变性 |
| log_softmax 在大 logits 上发生抵消误差 | 保持在减过行最大值的坐标中计算，与框架结果对照 |
| CE 全忽略返回 NaN，正 ignore_index 先 gather 越界 | 先筛有效行；空目标返回连接计算图的零；检查零梯度 |
| MQA 投影矩阵标成 `[D,D]` 却 reshape 到单 KV head | 明确 Wk/Wv 为 `[D,D/H]`；与 scaled_dot_product_attention 对照 |
| 全 mask 采样偷偷返回 token 0 | 明确抛错；补极小温度与合法 token mask 测试 |
| Gumbel 随机数端点保护在 float32 下失效 | 使用 dtype 对应的可表示端点，验证噪声有限 |
| ALiBi 非 2 幂 heads 套用了简化公式 | 按原作者参考实现生成斜率，并验证 H=3 与 prefill/decode 对照 |
| fused CE 把分块前向内存误说成训练峰值保证 | 明确普通 autograd 可能累计保留各块；补前向、梯度、全忽略测试 |
| RoPE cache 负下标默默索引末尾 | 增加位置范围检查与负下标测试 |
| BPE 合并修改传入 merge 表 | 返回新表；覆盖重叠 pair、tie-break、无 pair 与不修改输入 |
| Paged KV 在批次中途 OOM 后留下半更新状态 | 先规划整批页需求再写入；失败后检查页表、长度、空闲页均未改变 |
| 空 batch 的 packing 调用 torch.cat([]) | 定义空 packed 与 cu=[0] |
| RMSNorm 参数使半精度输出意外升 dtype | 在权重相乘后转回输入 dtype |
| beam 只有扩展一步的片段 | 补完整循环、EOS 停止、确定性排序与最终长度惩罚重排 |
| noisy all-gather 混用了不同信道假设 | 明确 BSC、值域、误差和失败概率，给 ring 模拟及多数重复码 union bound；不声称原帖唯一答案 |
| JAX 只有未定义的 block 伪代码 | 补真正可运行的 scan/remat Transformer，并对照 Python 层循环、jit、梯度和因果性 |
| VLIW take-home 只有官方仓库介绍 | 补独立的简化 SSA 指令调度与 SIMD 执行练习；验证同周期读旧状态、槽上限、环检测。明确不是官方完整作业提交答案 |

Gumbel 松弛语义核对：[PyTorch 官方文档](https://docs.pytorch.org/docs/main/generated/torch.nn.functional.gumbel_softmax.html)。ALiBi 斜率核对：[原作者代码](https://github.com/ofirpress/attention_with_linear_biases/blob/master/fairseq/models/transformer.py)。JAX 语义核对：[scan](https://docs.jax.dev/en/latest/_autosummary/jax.lax.scan.html)、[checkpoint](https://docs.jax.dev/en/latest/_autosummary/jax.checkpoint.html)。VLIW 背景：[Anthropic 公开仓库](https://github.com/anthropics/original_performance_takehome)。

## 验证与复现

- `python3 scripts/check-legacy-audit.py`：检查覆盖、完整题面、代码语法、展示源码与执行源码哈希。
- `python3 scripts/check-rendered-legacy-code.py`：确认全部 70 张卡的 HTML 展示代码与当前 Markdown 逐字一致，9 张故意错误示例也已保留并标记。
- `python3 scripts/check-legacy-coding.py`：执行上轮 20 张旧卡的 14 份不同实现。
- 安装本目录 `requirements.txt` 后，`python scripts/check-legacy-audit.py --execute` 可重新执行全部 61 份不同展示程序。
- 本次分别执行了本轮实现及上轮实现；使用 CPU 验证数值、梯度与状态语义，未宣称验证 GPU 吞吐、多卡通信或官方隐藏测试。
- 原有题号与链接保留；未增加新的“真实面经”标记。练习缺失条件明确为手册约定。

## 检查边界与剩余项

本轮针对的是旧 coding 卡的完整性与可执行性。其余 350 张知识/设计/流程卡完成结构和题型盘点，**没有逐条重新核实所有公司动态、产品名称、岗位流程、论文之外的外部事实**。不应把本报告理解为“420 张卡所有事实均已审定”。正式性能 take-home 的完整机器优化、GPU fused kernel、TPU sharding 等仍需各自真实运行环境；本轮添加的是明确约定的可运行练习。

## 本轮修复清单


### anthropic

- [Anthropic：开源的性能 take-home，是一台 VLIW SIMD 机器](../../../content/handbooks/us-tech/questions/anthropic/anthropic-perf-takehome.md) (`anthropic-perf-takehome`)

### apple

- [Apple 电面：温度、top-k、nucleus 顺序，端侧为什么常 top-k？](../../../content/handbooks/us-tech/questions/apple/apple-topk-sample.md) (`apple-topk-sample`)

### coding

- [白板：数值稳定 softmax，为什么减 max，轴怎么选](../../../content/handbooks/us-tech/questions/coding/coding-softmax-stable.md) (`coding-softmax-stable`)
- [白板：log-sum-exp trick，和 cross entropy 的关系](../../../content/handbooks/us-tech/questions/coding/coding-logsumexp.md) (`coding-logsumexp`)
- [白板：从 logits 写 cross entropy，不要先 softmax 再 log](../../../content/handbooks/us-tech/questions/coding/coding-cross-entropy.md) (`coding-cross-entropy`)
- [白板：MQA 单 KV head，怎么对 query heads broadcast](../../../content/handbooks/us-tech/questions/coding/coding-mq-attn.md) (`coding-mq-attn`)
- [白板：Gumbel-max 采样，和 softmax 温度的关系](../../../content/handbooks/us-tech/questions/coding/coding-gumbel-max.md) (`coding-gumbel-max`)
- [白板：AdamW 一步更新，m/v、bias correction、decoupled decay](../../../content/handbooks/us-tech/questions/coding/coding-adamw.md) (`coding-adamw`)
- [白板：SiLU / Swish 手写，数值上哪里会炸](../../../content/handbooks/us-tech/questions/coding/coding-silu.md) (`coding-silu`)
- [白板：SwiGLU / Llama MLP，门控和中间维为什么是 8/3](../../../content/handbooks/us-tech/questions/coding/coding-swiglu.md) (`coding-swiglu`)
- [白板：LayerNorm vs 在 feature 维上的标准化，eps 和仿射](../../../content/handbooks/us-tech/questions/coding/coding-layernorm.md) (`coding-layernorm`)
- [白板：RMSNorm 比 LayerNorm 少了什么，Llama 为什么用](../../../content/handbooks/us-tech/questions/coding/coding-rmsnorm.md) (`coding-rmsnorm`)
- [白板：GQA 把 KV head repeat 成 query heads，shape 怎么断言](../../../content/handbooks/us-tech/questions/coding/coding-gqa-repeat.md) (`coding-gqa-repeat`)
- [白板：因果、padding、文档边界合成一张注意力 mask](../../../content/handbooks/us-tech/questions/coding/coding-attn-mask.md) (`coding-attn-mask`)
- [白板：sliding window 和因果 mask 合成，prefill 与 decode 的 shape](../../../content/handbooks/us-tech/questions/coding/coding-swa-mask.md) (`coding-swa-mask`)
- [白板：RoPE 对 q/k 旋转，偶数维成对，decode 的 position](../../../content/handbooks/us-tech/questions/coding/coding-rope.md) (`coding-rope`)
- [白板：RoPE 的 cos/sin cache，decode 时怎么 index](../../../content/handbooks/us-tech/questions/coding/coding-rope-cache.md) (`coding-rope-cache`)
- [白板：QK RMSNorm 再 RoPE，Qwen / 部分 Llama 变体怎么写](../../../content/handbooks/us-tech/questions/coding/coding-qk-norm.md) (`coding-qk-norm`)
- [白板：ALiBi 斜率加到 scores 上，decode 用 cache 长度当 query 位](../../../content/handbooks/us-tech/questions/coding/coding-alibi.md) (`coding-alibi`)
- [白板：dropout mask 训练/推理缩放（inverted dropout）](../../../content/handbooks/us-tech/questions/coding/coding-dropout.md) (`coding-dropout`)
- [白板：embedding lookup + padding mask，大词表显存](../../../content/handbooks/us-tech/questions/coding/coding-embedding-lookup.md) (`coding-embedding-lookup`)
- [白板：global norm clip， inf/nan 怎么处理](../../../content/handbooks/us-tech/questions/coding/coding-grad-clip.md) (`coding-grad-clip`)
- [白板：对称 INT8 量化，scale、饱和，以及 dequant GEMM 的形状](../../../content/handbooks/us-tech/questions/coding/coding-int8-symm.md) (`coding-int8-symm`)
- [白板：embedding 与 lm_head 权重共享，梯度怎么流](../../../content/handbooks/us-tech/questions/coding/coding-weight-tying.md) (`coding-weight-tying`)
- [白板：GRPO 的 token loss 怎么聚合成一个数？三种写法的长度偏置](../../../content/handbooks/us-tech/questions/coding/coding-grpo-loss-agg.md) (`coding-grpo-loss-agg`)
- [白板：RLOO 的 leave-one-out baseline，向量化写法和它跟 GRPO 差在哪](../../../content/handbooks/us-tech/questions/coding/coding-rloo-advantage.md) (`coding-rloo-advantage`)
- [白板：GAE 反向递推，done、截断和 value clip 各在哪一行](../../../content/handbooks/us-tech/questions/coding/coding-gae.md) (`coding-gae`)
- [白板：CISPO 和 PPO clip 的区别，clip 的是权重还是梯度](../../../content/handbooks/us-tech/questions/coding/coding-cispo.md) (`coding-cispo`)
- [白板：DPO 的梯度写成加权 logprob，权重是什么，什么时候大](../../../content/handbooks/us-tech/questions/coding/coding-dpo-weighted.md) (`coding-dpo-weighted`)
- [白板：GSPO 的序列级 ratio，写成 token 上的加权 logprob loss](../../../content/handbooks/us-tech/questions/coding/coding-gspo-seq-ratio.md) (`coding-gspo-seq-ratio`)
- [白板：推理引擎的 logprob 和训练端对不上，截断重要性权重怎么加](../../../content/handbooks/us-tech/questions/coding/coding-tis-mismatch.md) (`coding-tis-mismatch`)
- [Fireworks：把 clipped GRPO 写成 SFT 式的加权 logprob loss](../../../content/handbooks/us-tech/questions/coding/fireworks-grpo-sft-loss.md) (`fireworks-grpo-sft-loss`)
- [白板：token 级 KL（策略 vs 参考策略），reduction 和 ignore pad](../../../content/handbooks/us-tech/questions/coding/coding-kl-div.md) (`coding-kl-div`)
- [白板：PaLM z-loss，为什么往 logits 上加这一项](../../../content/handbooks/us-tech/questions/coding/coding-z-loss.md) (`coding-z-loss`)
- [白板：融合 linear 和 cross entropy，不要物化 `[B, T, V]` logits](../../../content/handbooks/us-tech/questions/coding/coding-fused-ce.md) (`coding-fused-ce`)
- [白板：从 logits 取 response 的 token logprob，shift、temperature 和显存](../../../content/handbooks/us-tech/questions/coding/coding-token-logprob.md) (`coding-token-logprob`)
- [白板总览：LLM 训练里常见的 loss，都写成「权重 × logprob」来对照](../../../content/handbooks/us-tech/questions/coding/coding-loss-atlas.md) (`coding-loss-atlas`)
- [白板：BPE 训练一步 merge，词表膨胀；词尾标记写成 endofword 禁止 XML](../../../content/handbooks/us-tech/questions/coding/coding-bpe-merge.md) (`coding-bpe-merge`)
- [白板：packed sequences 的 cu_seqlens 和文档边界 mask](../../../content/handbooks/us-tech/questions/coding/coding-packed-lm.md) (`coding-packed-lm`)
- [白板：FlashAttention 的 online softmax，两遍归约怎么写](../../../content/handbooks/us-tech/questions/coding/coding-online-softmax.md) (`coding-online-softmax`)
- [白板：FlashDecoding 的 split-K，online softmax 怎么沿 KV 切开再合并](../../../content/handbooks/us-tech/questions/coding/coding-flash-decode.md) (`coding-flash-decode`)
- [白板：一步 decode，取 q、concat KV、GQA repeat、出 logits](../../../content/handbooks/us-tech/questions/coding/coding-decode-step.md) (`coding-decode-step`)
- [白板：温度 → top-k → nucleus 的顺序，实现细节](../../../content/handbooks/us-tech/questions/coding/coding-topk-nucleus.md) (`coding-topk-nucleus`)
- [白板：beam search vs greedy vs sampling，长度惩罚](../../../content/handbooks/us-tech/questions/coding/coding-beam-search.md) (`coding-beam-search`)
- [白板：投机解码接受规则，拒绝后从哪一步重采样](../../../content/handbooks/us-tech/questions/coding/coding-spec-accept.md) (`coding-spec-accept`)
- [白板：PagedAttention 的 block table，逻辑页怎么映到物理块，append 一页](../../../content/handbooks/us-tech/questions/coding/coding-paged-table.md) (`coding-paged-table`)

### google

- [Google：用 JAX 写一层 Transformer，shard、scan、remat 怎么摆](../../../content/handbooks/us-tech/questions/google/google-jax-transformer.md) (`google-jax-transformer`)

### nvidia

- [NVIDIA：FlashDecoding split-K，和训练用 FlashAttention 差在哪](../../../content/handbooks/us-tech/questions/nvidia/nvidia-flash-decode.md) (`nvidia-flash-decode`)

### openai

- [OpenAI：noisy 链路上实现 all_gather，轮数 bound 怎么推？](../../../content/handbooks/us-tech/questions/openai/openai-allgather-noise.md) (`openai-allgather-noise`)
- [OpenAI：FlashDecoding 为什么沿 KV 长度做 split-K，decode 时和 FlashAttention 差在哪](../../../content/handbooks/us-tech/questions/openai/openai-flash-decode.md) (`openai-flash-decode`)
