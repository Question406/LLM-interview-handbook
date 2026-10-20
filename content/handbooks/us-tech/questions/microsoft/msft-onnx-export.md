---
id: msft-onnx-export
section: microsoft
order: 8
level: A
title: Microsoft：ONNX / 导出动态轴，训练图和推理图不一致的坑
quick: "batch 和序列维要显式声明为动态轴，否则按 dummy 形状写死。训练图是整段 teacher forcing，推理还要 eval 模式和带 KV cache 的 decode 图；先对齐 logits 再谈加速。"
tags:
  - Microsoft
  - ONNX
  - Export
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Export a PyTorch model to ONNX
    url: https://docs.pytorch.org/docs/stable/onnx_export.html
    type: primary
  - title: Convert a PyTorch model to ONNX (Windows ML)
    url: https://learn.microsoft.com/en-us/windows/ai/windows-ml/tutorials/pytorch-convert-model
    type: primary
---

ONNX Runtime / Windows ML / 推理平台岗爱问「为什么导出的模型和 PyTorch 对不齐」。微软是 ONNX 的主推者之一，ORT 又吃训练（ORTModule）和推理两头。题的核心是：**你导出的是哪一张图**。动态轴只是形状问题的一半，另一半是训练时的控制流在推理里根本不存在。

## 动态轴：不声明就冻成 dummy 形状

trace 导出按一次前向记录算子。dummy 若是 `[1, 128]`，图里的 batch 和序列就被写成 1 和 128。线上 batch 8、长度 512 会直接 shape error，或更糟：静默切错广播。必须把可变维标出来。老 API 是 `dynamic_axes`；较新的 dynamo 导出走 `dynamic_shapes`。两者不要混用。

NLP 常见：

- 输入 `input_ids`、`attention_mask`：维 0 batch、维 1 序列。
- 输出 logits：同样两维要动态，否则 ORT 按导出时的词表×长度分配。
- KV cache：维里还有层、头、过去长度。过去长度必须是动态的，否则逐 token 生成（decode）的第二步就会失败。

只标 batch、忘了序列，是最常见的不完整导出。CNN 只标 batch 往往够；Transformer 不够。动态维也不是免费：有的算子 shape 推断会失败，要升 opset，或把 `reshape` 写成由输入尺寸算出来的表达式，不要在 Python 里写死 `x.view(1, -1)`。

导出前 `model.eval()`。文档写得很直：dropout 和 BatchNorm 在 train/eval 行为不同。带着 dropout 导出，推理会随机掉单元，和 eval 数值永远对不齐。这不是 ORT 的 bug。

## 训练图 ≠ 推理图

LLM 训练一步：teacher forcing（训练时用真实的前文预测下一个 token），整段 `[B, T]` 进模型，损失（loss） 对所有位置。图里没有「按 token 循环」，也没有 KV cache。推理是自回归：每步生成一个 token，cache 沿长度维 concat。你把训练用的 `forward(input_ids)` 直接 export，ORT 里仍是 **整段一次前向**。那只能用于输入预填充（prefill，即处理输入并建立缓存），不能当 decode。要 decode 就得导出带 cache 输入输出的图，或拆成 prefill / decode 两份。

其它会静默分叉的点：

- **控制流。** Python `if` 在 trace 里按 dummy 走的那条分支冻住。变长 decode、early exit、MoE 路由要用 script / dynamo 能看见的算子，或拆成多图。
- **原地操作和 view。** 训练能跑，ONNX 图可能非法或和自动微分假设冲突。
- **精度。** 训练 bf16，导出 fp32 或反过来，layernorm 和 softmax 会漂。对齐时用同一 dtype。
- **自定义核。** FlashAttention 在 PyTorch 里，ORT 未必有等价 EP。导出常退回标准 attention，需要重新测量和说明速度。

我会先在 PyTorch eval 和 ORT 上用同一组输入比 logits（允许 $10^{-4}$～$10^{-3}$ 级差），再谈 EP（CUDA / TensorRT）。数值不对就优化，是在优化一张错图。ORTModule 训练走的是训练图，和推理 ORT session 不是同一份文件，别说「我们训练已经用了 ORT 所以导出一定对齐」。

示例：动态轴的最小导出（注意 `eval`，以及 batch/序列都标）：

```python
model.eval()
dummy = (
    torch.randint(0, vocab, (1, 32)),
    torch.ones(1, 32, dtype=torch.long),
)
torch.onnx.export(
    model,
    dummy,
    "model.onnx",
    input_names=["input_ids", "mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch", 1: "seq"},
        "mask": {0: "batch", 1: "seq"},
        "logits": {0: "batch", 1: "seq"},
    },
    opset_version=17,
)
```

## 追问

- **为什么 dummy 长度 32、线上 4k 仍可能慢？** 动态轴只保证合法，不保证 kernel 按 4k 调好。ORT / TRT 仍可能按常见形状特化。要按线上 shape 做 warmup。
- **训练时的 causal mask 能直接导出吗？** 可以，但 mask 形状也要动态。写死 `[1, 1, 32, 32]` 三角会在长序列上错。
- **和 TensorRT 的关系？** TRT 可以吃 ONNX。失败往往在动态维和不支持的 op。先 ORT 对齐，再 TRT。
- **权重共享 / tying？** 导出可能把 embedding 和 lm_head 复制成两份 initializer，显存翻倍。要查图里是否仍是同一份存储。
