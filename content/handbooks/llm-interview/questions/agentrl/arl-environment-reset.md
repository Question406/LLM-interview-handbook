---
id: arl-environment-reset
section: agentrl
order: 17
level: S
title: Agent RL 里的 Environment Reset 为什么比普通文本 RL 更难？
quick: >-
  因为网页、数据库、文件和外部 API 都有状态，Agent 会下单、写文件、改权限。reset 不彻底，下一个 episode
  会看到上一条轨迹留下的订单、缓存或权限，奖励分数（reward）和 observation 都被污染，训练和 eval
  不再可比。要隔离状态、记录随机性、处理副作用，并在开局断言环境干净。
tags:
  - Agent RL
  - Environment
  - Reproducibility
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: WebArena
    url: 'https://arxiv.org/abs/2307.13854'
    type: primary
  - title: OSWorld
    url: 'https://arxiv.org/abs/2404.07972'
    type: primary
---

因为 Agent 会改环境。文本 completion 基本可以当独立样本，换一条 prompt，世界不会留下上一句的副作用；Agent 却会下单、写文件、改权限、改 cookie。reset 不彻底，下一个 episode 的初始状态就依赖上一条轨迹，奖励和观察都被污染，训练曲线和评测分数也就没法比了。

举个例子：上一条轨迹在购物网站上创建了一个订单，下一条轨迹的任务恰好是「帮我下这个订单」，它一进来发现订单已经在了，直接拿到奖励。离线分数很高，换一台干净机器立刻失效。Reset 定义的是 MDP 的初始状态分布 $p(s_0)$，属于问题定义的一部分。面试时别答成「多开几个 docker」，先说状态泄漏怎么破坏 on-policy 学习，再说隔离、断言脏状态、并行独立副本。

## 有状态世界把 episode 耦合在一起

网页、数据库、文件系统、云 API 都有跨 episode 存活的状态。典型的泄漏有三种：上一条轨迹创建的订单、账号、文件，被下一条当成「已经存在」的捷径；浏览器缓存、登录 cookie、localStorage、没提交的草稿；配额、限流、异步 job 在 episode 结束后才写完。这样一来，观察已经不是当前策略在标准 $s_0$ 下的结果，奖励可能来自前一个 Agent 做完的工作，策略学到的是部署不了的捷径。WebArena 把可复现的网站快照当作任务定义的一部分，OSWorld 对桌面应用也要求从已知镜像启动，原因就在这里：任务定义包含初始世界，光有自然语言指令不够。

评测也会受影响。同一个 checkpoint 跑两遍，环境没复位的话，第二遍会受第一遍留下的状态影响，测出来的方差里混进了环境残留，你分不清是模型变强了还是环境变容易了。没有干净的 $s_0$，成功率就失去了比较基础。训练环比评测更危险，成千上万个 episode 累积脏状态，策略会把泄漏当技能。通常是这样发现的：换一台机器分数腰斩，或者单 worker 分数高于多 worker，后者强烈提示并行污染。

## Reset 要隔离状态、记录随机性、处理副作用

先隔离状态：每个 episode 用独立的账号、目录、数据库 snapshot，或者能原子恢复到同一个镜像；共享 staging 站点又不做租约，等于没 reset。再控制随机性：记录 seed、任务版本、工具版本、网络 mock 和 observation 的截止时间。完全 deterministic 也不等于真实，生产有延迟和失败，评测要的是可复现的随机性，别假装世界是静态的。最后处理副作用：写操作要 cleanup 或回滚，真发邮件、真扣款这类不可逆的外部行为走 sandbox 或 human gate，别在训练环里打到生产。

Reset 失败时光重跑不够，要能检测脏状态：episode 开始时断言购物车为空、工作目录哈希等于基线、没有残留进程。这类断言比一句「我们 reset 了」靠得住。并行 worker 还要防互相污染，两个 sampling 轨迹（rollout）写同一个用户名，reset 脚本会删掉别人的 episode。超时也要定义清楚：页面没加载完，算不算合法的 $s_0$？把超时样本当失败奖励，模型会学到「环境一慢就放弃」；当成功跳过，又会漏训。Reset 本身要进监控，看成功率、耗时、断言失败类型，环境工程的 oncall 指标不比 GPU 利用率次要。文本 RL 几乎没有对应的东西，这就是它「更难」的地方。

## 脏 reset 会让 RL 优化错误的 MDP

On-policy RL 假设轨迹来自当前的 $\pi$ 和固定的 $p(s_0)$。$s_0$ 被前面的轨迹推着走，等于环境跟着策略一起非平稳变化，advantage estimation、组内 normalization、成功率曲线全都偏掉。更糟的是模型可能学会「第一局故意留后门，第二局领奖励」，这在干净部署里根本不存在。

所以 snapshot 粒度、reset 超时、失败重试算不算同一个 episode，都会改变有效 horizon 和奖励稀疏度，环境工程是算法的一部分。报告结果时要写明：是不是每个 episode 都从同一个镜像启动、外部 API 有没有 mock、reset 失败的轨迹丢没丢，否则别人复现不了，你自己也没法做 ablation。脏 reset 下学到的策略，在干净评测上会表现得像「不会用工具」，其实它依赖的是上一个 episode 留下的文件，训练 MDP 和部署 MDP 已经是两个了。先保证 $p(s_0)$ 一致，再谈算法，否则 GRPO / PPO 的曲线没有解释力。

## 追问

**文本 RLHF 为什么不太谈 reset？**
因为那里的环境近似无状态，下一个 prompt 不依赖上一条回复改过的外部世界。一旦工具能写文件、调 API，这个假设就失效了，Agent 的 $s_0$ 是一个世界快照。

**Reset 失败了，轨迹丢掉还是继续用？**
丢。脏 $s_0$ 上的 reward 会把捷径写进策略。要统计 reset 失败率，高了先修环境再训；把失败的 reset 当普通失败奖励，模型会学到环境的故障模式。

**环境必须 deterministic 吗？**
评测要对齐 seed 和镜像；训练可以保留受控的随机（页面延迟、检索抖动），但要能记录下来。把随机当 bug 全关掉，会 overfitting 到单一 DOM。

**和并行 rollout 是什么关系？**
每条并行轨迹都要有独立的世界副本。后端是共享可变的时候，隔离和锁比「多开几个浏览器」重要。多 worker 分数高于单 worker 时，优先查污染。
