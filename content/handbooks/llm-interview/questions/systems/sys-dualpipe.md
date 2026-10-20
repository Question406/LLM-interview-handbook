---
id: sys-dualpipe
section: systems
order: 271
level: A
title: DualPipe 如何压 PP bubble？和 1F1B 差在哪？
quick: >-
  气泡来自 PP 依赖：后排等前排的激活，前排等后排的梯度。1F1B 用交替 F/B 压激活峰值，warmup / cooldown 仍空。DualPipe
  从两端对向灌 microbatch，并把 PP 通信、EP all-to-all 叠进对面的 GEMM。我会先画空格子，不会只报名。
tags:
  - Pipeline Parallelism
  - DualPipe
  - DeepSeek
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

`sys-parallel` 的追问只点到「加 microbatch、1F1B」。本题要能**画出空等从哪来**，再说 DualPipe 填的是哪一段。这块容易背「DeepSeek 用 DualPipe」却说不清气泡。

## 气泡从哪来

$P$ 个 stage 把层切开。前向激活必须 $0\to 1\to\cdots\to P-1$，反向梯度必须 $P-1\to\cdots\to 0$。一张卡只有拿到上游结果才能算，算完才能发给下游。

朴素地一整批只走一遍：任意时刻大约只有 $1/P$ 的卡在算，其余在等。这就是 bubble。GPipe 把 global batch 切成 $M$ 个 microbatch 灌进去，稳态利用率上去，但头尾仍有 $(P-1)$ 个槽位的空等。粗算空闲比例

$$
\frac{P-1}{M+P-1}.
$$

$M\gg P$ 时比例变小，但激活要存更多份前向，显存先爆。把 $P=4$ 画成时间表：第 0 拍只有 stage 0 在 F，第 1 拍 stage 0 和 1，直到第 $P-1$ 拍才全员有活。前面那些空格子就是气泡。我会先画这条依赖，再谈调度；先报产品名等于没答。

## 1F1B 填了什么

1F1B（one-forward-one-backward）在 warmup 灌满流水线之后，每张卡交替做一次 F 和一次 B：刚算完的前向立刻给更早的 microbatch 做反向，激活不用攒到全部 F 结束。相对 GPipe，峰值激活从大约「$M$ 份」降到大约「$P$ 份」。

它没有取消依赖链。warmup 时后排仍在等第一波 F；cooldown 时前排在等最后一波 B。时间上的气泡仍约 $(P-1)$ 个 F/B 槽，只是被 $M$ 摊薄。通信（PP 的 P2P 送激活 / 收梯度）往往还暴露在关键路径上：GEMM 结束，卡还在等下一跳。MoE 再叠一层不规则 all-to-all 时，这段等待更明显，见 `sys-expert-parallel`。

## DualPipe：对向灌入 + 通信重叠

DeepSeek-V3 的 DualPipe 做两件事，不要并成一句「更好的 1F1B」。

**对向流水。** 一组 microbatch 仍从 stage $0$ 流向 $P-1$；另一组从 $P-1$ 流向 $0$。1F1B 里 stage $0$ 在 cooldown 的空档，现在可以吃反向流水的前向（或反向）。两端同时是「头」，warmup / cooldown 的空槽被对面那条管道填掉，气泡比单向 1F1B 更短。负载也更匀：不再总是第 $0$ 张先忙、第 $P-1$ 张后忙。

**把通信藏进对面的计算。** V3 把一层拆成 Attention GEMM、EP dispatch、专家 MLP、EP combine，以及 PP 的 send/recv。调度上让**这一条的 GEMM 覆盖另一条的 PP 通信和 all-to-all**。单向 1F1B 很难同时藏住两种通信；对向之后，两条管道的计算与通信相位错开，才有可重叠的窗口。MoE 通信如何与计算叠，见 `sys-moe-alltoall-overlap`。

代价是在途激活更多：两条方向都要留中间结果，显存高于同 $M$ 的 1F1B，常要重计算或更细的切块来换。EP 负载不均时，对向也藏不住热点卡的尾部等待。那是路由均衡问题，再换一个 schedule 名字也消不掉。

1F1B 换的是激活生命周期；DualPipe 换的是方向和通信相位。先画 $P$ 段依赖，再画两端对向灌入，最后说 overlap。缺第一张图，DualPipe 只是个名字。

## 追问

- **和 `sys-parallel` 那句 1F1B 差在哪？** 那题是五维对照，PP 只点到 bubble。本题要画空等，并说出对向流水和 comm-compute overlap。
- **加 $M$ 能不能代替 DualPipe？** $M$ 摊薄比例，但激活涨、调度碎。DualPipe 针对的是 $P$ 大、且 PP 与 EP 通信都在关键路径上的 MoE 大模型。
- **气泡为零了吗？** 没有。依赖还在，只是空槽被对向工作和重叠通信填掉大部分。负载不均、kernel 切不细、流同步过重，气泡会重新露出来。
- **显存呢？** 对向在途更多，往往高于 1F1B。省实际耗时、费激活，和 checkpoint 是同一类交换。
- **没有 MoE 还有没有用？** 对向仍能填 PP warmup。V3 的点是 **PP P2P 和 EP all-to-all 一起藏进 GEMM**，稠密模型收益主要在 PP 通信。
