---
id: sys-async-checkpoint
section: systems
order: 268
level: A
title: 异步落盘 Checkpoint 如何保证可恢复一致性？和 activation checkpointing 差在哪？
quick: >-
  这不是重算激活。同步 ckpt 让 GPU 空等存储；异步先在步边界做一致快照（权重、优化器、RNG、DP
  shard），后台再上传。必须版本栅栏 + 齐套清单 + 原子 rename，崩溃不得留下「半旧半新」可读成功标记。
tags:
  - Checkpoint
  - Async IO
  - Training Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: PyTorch Distributed Checkpoint
    url: https://pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html
    type: primary
---

陷阱是看见 checkpoint 就答「重算激活省显存」。那是 `sys-checkpoint`：activation / gradient checkpointing，卖的是 HBM，FLOPs 增加。本题是 **权重异步落盘**：把 $(\theta,m,v,\mathrm{RNG},\mathrm{step})$ 写到磁盘或对象存储，训练尽量不停。两个英文词撞车，面试先划清。PyTorch DCP 的对象是按逻辑名切的 stateful shard，能在不同 world size 上再读；它不管你前向丢不丢激活。

## 一致快照：在飞梯度、优化器、RNG、分片

异步的正确顺序是：**步边界栅栏 $\to$ 快照 $\to$ 训练继续 $\to$ 后台上传 $\to$ 齐套才标成功**。快照必须发生在 `optimizer.step()` 之后、下一步 `backward` 之前，否则会出现「权重已更新、Adam 一阶矩还是上一步」或「梯度只写完一半 rank」。在飞梯度不能进盘：要么 step 完清掉，要么明确不存 grad、恢复时从下一 forward 重算。

同一逻辑版本 $t$ 要齐套：

$$
S_t=\big(\theta_t,\; m_t,\; v_t,\; \mathrm{RNG}_t,\; \mathrm{step}=t\big).
$$

缺任何一项，恢复后 loss 会跳、dropout 会换序列、DP 会各训各的。RNG 包括 CPU、CUDA per-device、dataloader worker；只存 `torch.get_rng_state()` 不够。DP / FSDP / ZeRO 分片必须属于 **同一个 $t$**：rank 0 写完新 $\theta$、rank 7 还是 $t-1$，就是半旧半新。DCP 用 planner 按 FQN 写 shard，读时再按当前并行拼回来，见弹性恢复 `sys-elastic-resume-reshard`。手写 IO 的清单与校验见 `code-sharded-checkpoint-io`。

快照实现常见双缓冲或 copy-on-write：GPU 把状态拷到 pinned 缓冲或 CPU 镜像，拷完即可发下一 step 的计算；上传走独立流。拷贝窗口要短，且这段窗口内禁止改被拷对象。不要在 all-reduce 中途拍快照。FSDP / ZeRO-3 若在 all-gather 权重的窗口里拷贝，盘上可能混入「本 rank 分片 + 临时整模」，恢复时 shape 对不上。正确切点是参数重新 scatter 回分片、优化器 step 完成之后。频率上，拷贝气泡大约是一次 HBM 到 CPU 的状态体积；百亿参数加 Adam 状态往往是权重的数倍，ckpt 太密会把 async 的「不停步」红利吃光。

## 失败语义：临时目录、原子 rename、最后一致

后台上传会在进程崩溃时留下残文件。成功标记只能在 **清单里列出的所有 shard 校验通过之后** 出现：先写 `tmp/`，再原子 rename 目录或把 `MANIFEST.json.tmp` rename 成 `MANIFEST.json`。没有清单的目录等于不存在，恢复程序不得加载。校验和按 shard；缺文件、digest 不对，整版作废，回退上一成功版本。

RL 还要同步 env / episode 计数、dataloader 位点、rollout 的 `policy_version`。只恢复 $\theta$ 会让 verifier 进度和策略对不上。控制面触发 ckpt（见 `sys-rl-dataplane-controlplane`），数据面 rank 各自写 shard；触发频率是吞吐税：太密则拷贝气泡打满，太疏则故障窗口大。面试报的是「步边界一致快照 + 齐套才成功」，不是「开了 async 所以更快」。Activation checkpointing 省的是这一 step 的激活；落盘 checkpoint 保的是下一小时还能 resume。两味药对两类病。

## 追问

- **和 `sys-checkpoint` 怎么一句话分清？** 那题重算激活换显存；本题异步写权重换容错。一个不落盘，一个必须齐套落盘。
- **为什么不能边 backward 边存？** 梯度与 $\theta$ 不同步，恢复后优化器状态对不上，可能 NaN。必须步边界。
- **只存权重不存优化器？** 能 resume 但 Adam 动量归零，等效换优化器，loss 会抖。生产要齐套。
- **DCP 和每 rank 一个 `mp_rank_*` 文件差在哪？** DCP 按逻辑张量存，可读入新并行；绑死 rank 文件换 world size 就要重切，见 `sys-elastic-resume-reshard`。
- **async 失败了训练要停吗？** 不必停计算，但不得覆盖上一成功版本。失败重试上传，成功才移动清单。
---
