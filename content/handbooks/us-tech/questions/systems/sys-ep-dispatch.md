---
id: sys-ep-dispatch
section: systems
order: 29
level: S
title: 系统：MoE expert parallel 的 token dispatch 负载
quick: >-
  Router 之后 all-to-all 把 token 送到持有该 expert 的卡。一步墙钟等于收 token 最多的那张卡，不是均值。
  Prefill 走吞吐型 dispatch，decode 消息又短又要低延迟，不能共用一条核。负载靠容量、bias、EPLB，不是再喊一次 aux loss。
tags:
  - DeepSeek
  - NVIDIA
  - MoE
  - Expert Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
  - title: deepseek-ai/DeepEP
    url: https://github.com/deepseek-ai/DeepEP
    type: primary
  - title: deepseek-ai/EPLB
    url: https://github.com/deepseek-ai/EPLB
    type: secondary
  - title: Switch Transformers — Scaling to Trillion Parameter Models
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

## 题怎么来的

`sys-expert-parallel` 讲 EP 切的是专家、搬的是 token。本题把镜头推到 dispatch 这一跳的负载：直方图一歪，all-to-all 和 expert GEMM 一起歪。DeepSeek-V3 报告、开源 DeepEP / EPLB，以及 NVIDIA grouped GEMM，都是公开材料。xAI 岗也会从 decode 碎片问过来，见 `xai-moe-decode`。不要把未开源的内部 dispatch 讲成自己写过。

## Dispatch 在干什么

我会按一步 MoE 把账摊开：

1. 本卡 router 对每个 token 出 top-$k$ expert id。
2. **Dispatch all-to-all：** hidden（可已是 FP8）按目的 rank 搬走。消息长度随该 rank 被打中的 token 数变。
3. 本地 grouped GEMM，见 `nvidia-moe-gemm`、`sys-fp8-gemm`。
4. **Combine all-to-all：** 输出送回 token 原 rank，按门控加权。

通信量粗算 $2k\cdot T\cdot d$ 量级。均值好看没用：令 $c_r$ 为 rank $r$ 收到的 token 数，

$$
t_{\mathrm{step}}\propto \max_r c_r,
$$

因为集合通信等最慢那条边，GEMM 等最热那个 expert。Switch 的容量因子 $C$：每个 expert 只收约 $C\cdot T/E$ 个 token，超出 drop 或溢出。$C$ 太小伤质量，$C$ 太大热点照样在。Aux loss、DeepSeek 公开的 expert bias 修正、EPLB（把热专家复制到多个 rank、按历史负载摆专家），目的都是让 $\{c_r\}$ 的 $\max/\mathrm{mean}$ 接近 1。面试要说到这是 P99 通信优化，不是训练曲线装饰。

```python
counts = torch.bincount(expert_ids.flatten(), minlength=E)
per_rank = counts.view(ep_size, E // ep_size).sum(dim=1)
# 调度和核都按这个 max 走；均值 MFU 会撒谎
hot = int(per_rank.max())
```

Decode 时 $T$ 变成在飞 batch 那么点 token，$k \gt 1$，all-to-all 退化成小消息延迟墙。Prefill 的 $T$ 大，走带宽。DeepEP 公开 README 把两条路写死了：高吞吐核给训练和 inference prefill；低延迟核给 inference decode；原生 FP8 dispatch；还能控占用多少 SM，好和 GEMM overlap。同一套 NCCL all-to-all 硬套到 decode 上，尾延迟会很难看。这也是「训练拓扑不要原样搬 serving」的具体落点。

## 负载从哪来、怎么叠并行

Router 塌缩：少数 expert 吃掉大部分 token。预训练 aux 再好，推理分布也可能漂（用户话术、工具 JSON、代码）。Serving 可以：

- **静态复制热专家**（EPLB 一类）：多占显存，换 $\max c_r$ 下降。
- **运行时 bias：** 把打满的 expert 略压低，下一微批更平。改的是负载，原则上不该偷偷改训练时的路由定义；若改了，要当质量风险说出来。
- **Drop：** 实现简单，shape 每步变，CUDA graph 和 overlap 都痛，见 `sys-expert-parallel`。

和 DP / TP 叠：DP 会把不同 replica 的 token 汇总到同一 expert 持有者，热点可能被放大；TP 切单个 expert 内部矩阵，通信规则，适合 NVLink。EP 的不规则 all-to-all 更常跨节点。节点内 TP$\times$EP、跨节点 DP 是常见公开拓扑。EP 再加能放下更多 expert，但消息更碎；expert GEMM 已经很小、通信占比过半时，再加 EP 吞吐掉。

Overlap：同批 dispatch 的输出是该批 GEMM 的输入，同微批叠不上。要切微批或像 DualPipe / DeepEP 那样把通信核占用的 SM 限住，让下一微批的 MMA 还能跑。面试说「我们 overlap 了」要能指出重叠的是下一微批，不是因果上的同一批。

错误说法：EP 均衡了所以 all-to-all 和 dense all-reduce 一样齐；decode 继续用 prefill 的大吞吐核；只看平均 tokens/s。直方图、P99 步时、每 expert 的 $c_e$ 才是体检。

PD 分离时 prefill / decode 用不同 EP 度是合理的：prefill 吃吞吐 dispatch，decode 复制 expert 换通信。KV 布局和 expert 布局是两件事，见 `sys-prefill-decode-disagg`。

## 追问

- **热点卡在等通信还是在等 GEMM？** 都可能。先看 $\max c_r$：大且 GEMM SOL 高，是算；大且 NCCL / RDMA SOL 高，是搬。DeepEP 把两条拆开正是因为阶段不同。
- **为什么 decode 要单独的低延迟核？** 每步 token 少，启动和 RTT 主导。吞吐核按大 $T$ 优化，小消息上更亏。
- **FP8 dispatch 图什么？** 体积减半，GEMM 直接吃 FP8，少一次 cast。Scale 要和 `sys-fp8-gemm` 的 tile 对齐。
- **EPLB 和 aux loss 谁在推理生效？** Aux 是训练目标。推理时专家位置和复制是 EPLB / 部署表。只报「训过 aux」不够。
- **Token drop 和 CUDA graph？** 每步 $c_r$ 变，静态图难捕获。低延迟 decode 更爱固定容量 padding，用计算换可预测延迟。
- **和 TP all-reduce 一句话差在哪？** TP 尺寸固定、对端固定；EP dispatch 变长、目的随 router 变，尾部由热点 expert 决定。
