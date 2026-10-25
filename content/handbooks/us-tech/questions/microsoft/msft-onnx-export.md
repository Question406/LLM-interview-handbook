---
id: msft-onnx-export
section: microsoft
order: 8
level: A
title: Microsoft：ONNX / 导出动态轴，训练图和推理图不一致的坑
quick: "导出前先确认是 prefill 还是带 KV cache 的 decode 图，并切到 eval。batch、序列和 cache 过去长度按所用导出 API 声明动态维，再以同 dtype、同输入对比 PyTorch 与 ORT logits。数值和多种形状通过后，再调 EP 与性能。"
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

导出模型要先明确推理时会怎样调用，再定义动态轴，最后验证数值。比如 dummy 是 `[1, 128]`，没有声明 batch 和序列可变，线上 batch 8、长度 512 就可能 shape error，甚至广播错却不报错。

ONNX Runtime / Windows ML 中常见的对齐问题，也来自训练前向与自回归推理用图不同。ORTModule 能运行训练，不代表训练图与推理 ORT session 是同一份文件。

## 先确定形状和前向语义

trace 记录 dummy 走过的算子。老 API 用 `dynamic_axes`，较新的 dynamo 导出用 `dynamic_shapes`，按对应路径选用。NLP 的 `input_ids`、`attention_mask` 以及 logits 都要让维 0 batch、维 1 序列可变；KV cache 还有层、头和过去长度，过去长度写死会让第二步 decode 失败。

CNN 只标 batch 有时足够，Transformer 通常还需序列。动态 shape 推断失败可检查 opset，`reshape` 用输入尺寸表达，避免在 Python 写死 `x.view(1, -1)`。导出前执行 `model.eval()`，dropout 与 BatchNorm 在 train/eval 下行为不同，不能把训练态随机性当作 ORT 数值问题。

训练 teacher forcing 把 `[B, T]` 整段送入，loss 覆盖各位置，不包含逐 token 循环。直接导出 `forward(input_ids)` 仍只是整段前向，最多作为 prefill 基础；decode 需要 KV cache 输入输出，或拆成 prefill / decode 两图，cache 沿长度 concat。

Python `if` 可能把 dummy 分支冻结，变长 decode、early exit、MoE 路由要用 script / dynamo 能捕获的算子或拆图。原地操作和 view 可能不能等价导出；bf16 / fp32 改变也会让 layernorm、softmax 漂移。FlashAttention 未必有对应 ORT EP，退回标准 attention 后需重新测速度。

## 对齐后再启用加速

同一输入、同一 dtype 比较 PyTorch eval 与 ORT logits，容差可先参考 $10^{-4}$～$10^{-3}$，通过后再测 CUDA / TensorRT EP。下面是 batch 与序列都动态的最小导出，先设置 `eval`：

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

动态轴保证形状合法，不保证 4k 下 kernel 已优化，ORT / TRT 仍可能按常见形状特化，所以按线上 shape warmup。权重 tying 也要看导出图，embedding 与 lm_head 若复制成两个 initializer，会增加显存。

## 追问

**causal mask 能直接导出吗？**
可以，但 mask 也要动态，写死 `[1, 1, 32, 32]` 的三角矩阵无法覆盖长序列。

**ONNX 与 TensorRT 怎么衔接？**
TensorRT 可以读取 ONNX，先在 ORT 验证数值，再处理 TRT 的动态维与不支持算子。

**为什么 dummy 32，线上 4k 仍然慢？**
动态形状不代表所有长度都已做性能特化，需要真实形状的 warmup 和压测。
