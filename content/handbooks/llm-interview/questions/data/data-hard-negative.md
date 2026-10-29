---
id: data-hard-negative
section: data
order: 2
level: S
title: Preference Data 怎么构造 Hard Negative？
quick: >-
  好的 rejected 看起来合理，只在一个关键点上出错，比如推理错一步、单位偏了、工具参数错了。尽量让它只在这一个维度上比 chosen
  差，并控制两者的长度和风格，模型才会学到 correctness criteria，不会只学会偏好更长或更客气的回答。
tags:
  - Preference Data
  - Hard Negative
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: 'https://arxiv.org/abs/2204.05862'
    type: primary
---

Hard negative 要看着像样、只错一处：rejected 只在一个关键维度上比 chosen 差，长度和风格尽量匹配。最容易造的 negative 是 chosen 完整正确、rejected 写一句「我不知道」，这种 pair 只教模型少说废话，学不到 correctness criteria。DPO 或 RM 在一堆「一眼假」的 rejected 上训，表面 loss 很低，上线后照样分不清细微的错。

比如一道换算题，chosen 最后的单位是公里，rejected 推理步骤一模一样，只是把单位写成了米。两条长度、语气都一样，模型想分对，只能去看那个单位。Anthropic HH 的价值也在这类 borderline comparisons 上，像「有帮助但略越界」和「无害但没用」，光有正确和胡话的对比不够。

## 只改一个关键维度

有效的构造往往只改一处：推理链错一步；主体、时间、单位稍微偏了；代码整体能跑但 edge cases 错；工具选对了但 argument 错了；内容对但违反了格式或安全约束；Agent 轨迹只在一个决策上选错文件或者过早 terminate。对照尽量 length-matched、风格相近，否则模型学到的是「长=好」，或者变成一个 style classifier。再配上多维 rubric，按 pair 难度分组统计，你才知道自己在学习哪项 decision criterion，不会到头来发现所有 hard pair 其实都是「更短所以输」。

如果所有 chosen 都更长、更客气，梯度就会跑到这些无关因素（nuisance）上。办法是长度匹配、加对调风格的 counterexample pair、先分维度打分再合成偏好。

## 太难的 pair 怎么办

标注员在极难的 pair 上分歧很大时，别强行二值化，保留 tie、软概率，或者降权。Hard 过了头，人和 judge 自己都抖，就成了 label noise，会污染 reward model（RM）的训练数据。所以要同时看 pair margin、annotator agreement 和验证器（verifier）confidence，三个都低，这条就不该进硬偏好，见 `data-annotator-agreement`。

Easy negative 也有用，少量「别胡说」能稳住底线。配比上先 easy，再逐步提高 hard 的比例，hard 最后应该占偏好集的主体，但每个桶都留一点 easy，防止模型忘了「胡话也是错」。全是 hard 又没有 calibration，梯度噪声会很大。

## Agent 轨迹上的 hard negative

做法是从成功轨迹复制一份，只替换一个关键 action，再在真实环境里把后面的失败跑出来，让 credit 集中在那一步。整条随机打乱就成了「轨迹不像」，模型学不到「这个决策错了」。失败后缀一般不当 SFT 的正例：错误步做 rejected，有 recovery 的话 recovery 做正例。这和 `arl-trajectories` 是同一个思路在 pair 构造上的落地。

挖掘来源也别只靠手写。线上的错误、judge 和人类判断不一致的 pair、模型高置信但 verifier 判失败的样本，都是现成的 hard negative。过滤还是那三关：只差一个维度、长度风格匹配、人能稳定分出来。发布时按难度分组报 win-rate，只报总体赢面，会掩盖模型还抓不住细错。

## 追问

**Agent trajectory 的 negative 怎么构造？**
复制成功轨迹，只改一个关键 action（错 repo 文件、错 tool 参数、过早结束），在真实环境里执行出后续的 failure。前后上下文保持相似，credit 才会集中在那一步。

**Hard negative 太难会怎样？**
人和 judge 自己都拿不准，就引入了 label noise，RM 拟合的是争吵。用 pair margin、annotator agreement、verifier confidence 三项筛选标准，过不了的降权或者当 tie。

**和 easy negative 怎么配比？**
先用少量 easy 稳住「别胡说」，再提高 hard 的比例。全是 hard 又没有 calibration，loss 会抖，模型也会忘了底线。
