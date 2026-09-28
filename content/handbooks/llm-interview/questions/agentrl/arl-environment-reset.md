---
id: arl-environment-reset
section: agentrl
order: 17
level: S
title: Agent RL 里的 Environment Reset 为什么比普通文本 RL 更难？
quick: >-
  网页、数据库、文件和外部 API 都是有状态的。若 reset 不彻底，后一个 episode 会看到前一个轨迹留下的订单、缓存或权限，reward 和
  observation 被污染，训练与 eval 都不再可比较。
tags:
  - Agent RL
  - Environment
  - Reproducibility
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: WebArena
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: OSWorld
    url: https://arxiv.org/abs/2404.07972
    type: primary
---

文本 completion 通常可近似成独立样本：换一条 prompt，世界不会留下上一句的副作用。Agent episode 会改环境：下单、写文件、改权限、进 cookie。Reset 定义的是 MDP 初始状态分布 $p(s_0)$，不是测试脚手架。Reset 不彻底，$s_0$ 依赖上一条轨迹，奖励和观察被污染，训练曲线与评测分数都不可比。面试别答成「多 docker 一下」：先说状态泄漏怎样破坏 on-policy 学习，再谈隔离、断言脏状态、并行独立副本。

## 有状态世界把 episode 耦合在一起

网页、数据库、文件系统、云 API 都有跨 episode 存活的状态。典型泄漏：

- 上一条轨迹创建的订单 / 账号 / 文件，下一条当「已经存在」的捷径；
- 浏览器缓存、登录 cookie、localStorage、未提交草稿；
- 配额、限流、异步 job 在 episode 结束后才写完。

于是观察不再是当前策略在标准 $s_0$ 下的结果，reward 可能来自「捡到上一个 agent 的战利品」。策略会学到不可部署的捷径：离线分数很高，换一台干净机器立刻失效。WebArena、OSWorld 一类基准把可复现的站点 / 桌面快照当作题目的一部分，原因正在这里：任务定义包含初始世界，而不只是自然语言指令。

Eval 同样被毁。同一 checkpoint 跑两遍，若环境未复位，第二次吃第一次的副作用，方差里混进了「世界脏了多少」。你无法区分模型变强和环境变容易。WebArena 把可复现的网站快照当作任务定义的一部分，OSWorld 对桌面应用同样要求从已知镜像启动。没有干净 $s_0$ 就没有可比较的成功率，不是「benchmark 爱干净」。训练环比评测更危险：成千上万 episode 累积脏状态，策略会把泄漏当技能。发现方式往往是「换一台机器分数腰斩」或「单 worker 分数高于多 worker」。后者强烈提示并行污染。

## Reset 要隔离状态、记录随机性、处理不可逆副作用

工程上至少三件事：

- **隔离状态：** 每个 episode 独立账号 / 目录 / 数据库 snapshot，或能原子恢复到同一镜像。共享 staging 站点而不做租约，等于没有 reset。
- **控制随机性：** 记录 seed、任务版本、工具版本、网络 mock 与 observation 截止时间。完全 deterministic 不等于真实：生产有延迟和失败；评测要的是可复现的随机性，不是假装世界是静态的。
- **处理副作用：** 写操作必须 cleanup 或回滚。不可逆的外部行为（真发邮件、真扣款）应走 sandbox 或 human gate，不要在训练环里打到生产。

Reset 失败时不要只重跑。要能检测脏状态：episode 开始时断言「购物车为空、工作目录哈希等于基线、无残留进程」。检测比「我们 reset 了」的口头保证更接近事故现场。并行 worker 还要防止互相污染：两个 rollout 写同一用户名，reset 脚本会删掉别人的 episode。超时也要定义：页面没加载完就算不算合法 $s_0$？把超时样本当失败奖励，模型会学到「环境一慢就放弃」；把超时当成功跳过，又会漏训。Reset 本身应进监控：成功率、耗时、断言失败类型。环境工程的 oncall 指标不亚于 GPU 利用率。文本 RL 几乎没有对应物，这正是「更难」的要点。

## 脏 reset 会让 RL 优化错误的 MDP

On-policy RL 假设轨迹来自当前 $\pi$ 与固定 $p(s_0)$。若 $s_0$ 被前序轨迹推动，等于环境在跟策略一起非平稳变化。优势估计、组内归一化、成功率曲线全部偏掉。更糟的是模型可以学「第一局故意留下后门、第二局领取奖励」，这在干净部署里不存在。

所以 Agent RL 的环境工程是算法的一部分：snapshot 粒度、reset 超时、失败重试是否算同一 episode，都会改有效 horizon 和奖励稀疏度。报告结果时应写明：是否每 episode 从同一镜像启动、外部 API 是否 mock、失败 reset 是否丢弃轨迹。否则别人无法复现，你自己也没法做 ablation。脏 reset 下学到的策略，在干净评测上会表现得像「不会用工具」，其实它依赖的是「上一个 episode 留下的文件」。这不是泛化失败，是训练 MDP 和部署 MDP 根本不是同一个。先把 $p(s_0)$ 钉住，再谈算法；否则 GRPO / PPO 的曲线没有解释力。

## 追问

- **文本 RLHF 为什么不太谈 reset？** 因为环境近似无状态，下一 prompt 不依赖上一回复的外部世界。一旦工具能写文件或调 API，这条假设立刻失效。Agent 的 $s_0$ 是世界快照，不是句子。Reset 属于 MDP 定义。
- **Reset 失败该丢轨迹还是继续？** 丢。脏 $s_0$ 的 reward 会把捷径写进策略。应计失败 reset 率，高了先修环境再训。把失败 reset 当普通失败奖励，模型会学到环境故障模式。
- **Deterministic 是否必须？** 评测要对齐 seed 与镜像；训练可以保留受控随机（页面延迟、检索抖动），但必须可记录。把随机当 bug 关掉，会过拟合到单一 DOM。
- **和并行 rollout 的关系？** 每条并行轨迹需要独立世界副本。共享可变后端时，隔离与锁比「多开几个浏览器」更关键。多 worker 分数高于单 worker 时，优先查污染。Reset 属于算法假设，不是运维边角。
