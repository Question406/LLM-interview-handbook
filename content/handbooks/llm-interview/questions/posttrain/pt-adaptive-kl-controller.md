---
id: pt-adaptive-kl-controller
section: posttrain
order: 225
level: A
title: 自适应 KL controller 在做什么，比固定 $\beta$ 好在哪？
quick: >-
  自适应 KL controller 把目标 KL 当设定点，按实测 $\widehat{\mathrm{KL}}$ 调惩罚系数 $\beta_t$，让策略既不死贴 $\pi_{\mathrm{ref}}$、也不漂走。固定 $\beta$ 在奖励尺度和批次难度变化时，有效约束会跟着变，很难跨阶段保持同一个工作点。
tags:
  - KL
  - PPO
  - Controllers
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

自适应 KL controller 把惩罚系数 $\beta_t$ 当成一个旋钮，按实测的 KL 去调，让策略离参考模型的距离一直停在目标附近。它比固定 $\beta$ 好在钉住的是工作点：奖励尺度变了、批次难度变了，约束强度还是那么大。它保证不了回答更好、更安全，平均 KL 进了目标带，也只说明距离控制住了。

举个例子。训练中途换了一个打分更激进的奖励模型，奖励整体被放大，固定的小 $\beta$ 就显得太弱，策略很快漂远；反过来奖励变弱，固定的大 $\beta$ 会把策略按死在 监督微调（SFT） 附近。系数一直没动，实际约束却已经松了或者掐死了。

## Controller 在调什么

InstructGPT 一类流水线每步估计 $\widehat{\mathrm{KL}}_t=\mathbb{E}[\log\pi_\theta-\log\pi_{\mathrm{ref}}]$，比目标 $KL_{\mathrm{target}}$ 高就把 $\beta$ 调大，低就调小。这是反馈控制，优化目标没变，还是奖励减 $\beta\,\mathrm{KL}$。

实现时先给 $\beta$ 做平滑、加上下限，免得单步估计的噪声把系数打飞。KL 的估计要和训练用同一种 reduction、同一个 mask：要是把 prompt 也算进 KL，controller 会把「读懂问题」当成偏离来罚。它和 PPO clip 是分工的，clip 管相对 $\pi_{\mathrm{old}}$ 的一步比率，controller 管相对 $\pi_{\mathrm{ref}}$ 的累积漂移，两层同时猛调，就看不清是谁在起作用。

固定 $\beta$ 默认损失尺度全程不变。实际上 强化学习（RL） 前半段 reward 噪声大、策略还贴着参考，小 $\beta$ 就够了；后半段策略方差上升、实测 KL 冲高，需要自动加罚，免得突然变成长篇空话。换奖励、换难度、换组大小的时候，controller 能维持同一个有效约束，不同阶段的曲线也能放在一起比。你钉住的是工作点，那个和 reward 归一化绑在一起的系数交给它自己去调。

代价是滞后和振荡。$\beta$ 调晚了，策略先漂出去一截；调猛了，系数来回抽，所以要和 PPO clip、学习率一起调。目标带本身也得选对：目标 KL 太小，学不动，像在 SFT 附近微调；太大，会出现奖励 hacking、风格崩、安全回退。controller 只是省掉了手工改系数，目标带选错和固定 $\beta$ 选错是一回事。$\beta$ 顶到上限还压不住 KL，就该回头查奖励尺度，别再把目标调大。

## 监控看分位数和切片

汇报时把 reward、KL、$\beta_t$ 三条曲线画在一起。均值达标的时候，长尾题的 KL 分位数可能已经爆了。再按题型切片：简单题 KL 很小、难题 KL 很大，说明 controller 在用同一个 $\beta$ 折中两类题，这可能掩盖了 reward 标定错误。长度单独看，reward 和长度一起涨、人评不动，先当 length hacking 处理，controller 加罚只能治标。

验收标准可以写成：KL 进了目标带，同时分位数、切片、安全和能力回退都能接受。这和「KL 太大 / 太小」那张卡用的是同一组画像，贴死参考对应目标过小，刷奖励写空话对应目标过大。

## 追问

**目标 KL 怎么选？**
先找 SFT 附近还能学得动的最小带，再看 reward 曲线和安全回退慢慢放宽，没有全局标准数。目标过小相当于「$\beta$ 太大」，目标过大相当于「$\beta$ 太小」。

**clip 和 controller，谁管一步、谁管全程？**
clip 管相对 $\pi_{\mathrm{old}}$ 的一步比率，controller 管相对 $\pi_{\mathrm{ref}}$ 的累积漂移。只留一个，会漏掉另一种失败。

**能不能关掉 controller，只留固定 $\beta$？**
尺度稳定的短实验可以。换奖励或加难度以后，有效约束会漂，越是长跑、换阶段，越应该钉住工作点。

**平均 KL 达标就能上线吗？**
还不行，要看分位数、切片和安全 / 能力回退，controller 可能正在掩盖标定错误。$\beta$ 顶死了仍压不住，先修奖励，再改目标。
