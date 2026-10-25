---
id: sys-elastic-resume-reshard
section: systems
order: 269
level: A
title: 弹性扩缩容后如何 Resume，并对模型状态 Reshard？
quick: "弹性恢复要先等通信结束，保存一致的 checkpoint，再按新 TP/PP/EP/DP 布局重切状态并重建通信组。Checkpoint 应按逻辑参数 ID 存，Adam 动量和数据位置也要一起映射。恢复后检查 loss 是否连续；RL 还要对齐 `policy_version` 并清掉旧 KV。"
tags:
  - Elastic Training
  - Reshard
  - Checkpoint
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: PyTorch Distributed Elastic
    url: https://pytorch.org/docs/stable/distributed.elastic.html
    type: primary
  - title: PyTorch Distributed Checkpoint
    url: https://pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html
    type: primary
---

扩缩容后，要先结束当前通信并保存一致的 checkpoint，再按新的并行布局 reshard 状态、重建通信组。比如旧 checkpoint 里的 `rank=3, shard=2`，换了 world size 后就不再代表同一段参数，不能直接交给新 rank。PyTorch Elastic 管 rendezvous 和进程生命周期，DCP 管逻辑状态读写；恢复需要把两者接起来，并选用已经完整落盘的版本，落盘语义见 `sys-async-checkpoint`。

恢复过程可以写成：排空 $\to$ 一致 ckpt $\to$ 按新并行计划 reshard $\to$ 重建通信组。

## 按参数逻辑位置重切状态

存盘不要以 `rank=3, shard=2` 当主键。DCP / `torch_dist` 按 FQN 存完整逻辑张量的分片元数据，load 时用 **当前** TP/PP/EP/DP 再切。旧格式 `mp_rank_*` 绑定了保存时的并行布局，换 TP 必须离线重切，见 slime 的 `torch` vs `torch_dist`。Reshard 可以写成

$$
\mathrm{shard}_{r}^{\mathrm{old}}(W)\;\xrightarrow{\mathrm{plan}}\;\mathrm{shard}_{r'}^{\mathrm{new}}(W),\qquad r\lt R_{\mathrm{old}},\; r'\lt R_{\mathrm{new}}.
$$

$R$ 变了，$r$ 号文件不能直接 memcpy 到新 rank。

并行维度难度不同：

**DP 变大 / 变小。**
数据副本增减，参数布局往往不变（纯 DDP）或 FSDP shard 变细/变粗。最常见的弹性，也最好测。
**TP 变。**
矩阵按列/行重切，attention head 数必须能整除新 TP，否则 张量形状会不匹配。
**EP 变。**
Expert 从一张卡搬到另一张，路由表和 all-to-all 组成员全换。比 DP 难一个数量级；专家数还要对齐新 EP，见 `sys-expert-parallel`。

优化器状态必须跟权重同一套 plan 切：Adam 的 $m,v$ 与 $\theta$ 逐元素对齐。只 reshard 权重、动量仍按旧 rank 摆，下一步就会更新错切片。RNG 无法在不同 worker 数下逐比特复现，验收允许种子差，但 **损失应在噪声范围内连续**，不能跳一个数量级。

## 在安全边界重建训练与采样进程

运行中改拓扑前，必须排空 in-flight NCCL：没有正在进行的 all-reduce / all-to-all / pipeline send。通常在 step 边界、ckpt 栅栏之后再杀进程或加进程。中途插入 rank，集合通信的参与者集合不一致，典型症状是 hang，见分布式 hang 题。梯度桶、CUDA graph、bucket 大小都要按新 world 重建，不要复用旧指针。

RL 集群还要重建 生成训练轨迹的 rollout worker 的路由：哪组 GPU 跑 generate、哪组跑 trainer、weight sync 的 collective 是谁。HybridEngine 同卡方案改的是卡数与布局，分卡方案改的是两池比例，见 `sys-verl-hybridengine`、`sys-rl-dataplane-controlplane`。Resume 后 rollout 必须加载 **同一 `policy_version`**，并 清空 KV 缓存，否则旧策略生成的轨迹会混进第一步。弹性不是只把 trainer 拉起来。

恢复以后，先验证计算是否接上：新并行下 forward 一张固定 batch 的 loss 与参考实现同量级；optimizer step 一次后范数正常；EP 变了则每 expert 的参数和旧 ckpt 对得上（允许排列）。进程都 alive 不够。弹性失败常见是 ckpt 绑死 rank、没有等全部通信结束、只恢复 $\theta$ 没恢复 $m,v$。先修这三件，再谈自动扩缩策略。DP 变了还要重切数据：同一份全局 batch 按新 rank 划分，否则有的样本会重复、有的永远看不到。dataloader 位点若按旧 world 存的绝对 index，resume 后要对新切分做一次映射，不能原样 seek。这和权重 reshard 是同一类「逻辑坐标 vs 物理 rank」问题。

## 追问

**为什么不能热加卡接着训？**
飞行中的 collective 不知道新成员；分片边界也变了。必须先结束通信，再重新切分状态。
**DP 和 EP 哪个更怕弹性？**
EP。Expert 布局和不规则 all-to-all 组成员都变。DP 多半只改副本数。
**数值对不齐就算失败吗？**
RNG 与数据切分变了，允许小差。损失突然大幅变化、某层 shape 错、某 expert 全零才是失败。
**和 async ckpt 什么关系？**
弹性切点必须是已成功的完整且一致的检查点版本。上传到一半的目录不能拿来 reshard。
**RL 只扩 trainer 行不行？**
行，但要改 sync 协议和路由表；rollout 池的 KV 容量与 $n$ 也要一起重估。
---
