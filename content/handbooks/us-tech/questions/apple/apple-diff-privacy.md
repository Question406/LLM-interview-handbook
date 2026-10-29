---
id: apple-diff-privacy
section: apple
order: 5
level: S
title: Apple：differential privacy 在个性化语言模型里怎么讲 ε，和「数据不出设备」的关系？
quick: >-
  数据不出设备说明这条路径没有发布数据，本身没有一个可报的 $\varepsilon$。DP 约束的是发布结果对单条记录的敏感度；个性化上下文优先留在
  on-device，只有发布人群统计时再讨论噪声、每日条数和合成预算。
tags:
  - Apple
  - Differential Privacy
  - On-device
  - Personalization
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Learning with Privacy at Scale
    url: 'https://machinelearning.apple.com/research/learning-with-privacy-at-scale'
    type: primary
  - title: Differential Privacy
    url: 'https://machinelearning.apple.com/research/diff-privacy'
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

## 可以这样回答

“数据不出设备”和 differential privacy 解决不同环节：前者让私有上下文留在本地，后者约束发布结果能透露多少个体信息。比如让 Siri 回答下周的会议，可以用本地证据；要统计大家常用哪个 emoji，才需要讨论上传的加噪统计和 $\varepsilon$。

Apple 2017 的 Learning with Privacy at Scale 讲本地 DP 频率统计，2024 foundation model 材料讲训练不用用户私有数据，Exponent MLE 指南也提到隐私和 on-device。回答时要把这些公开声明的范围分清楚。

## 技术备查

“数据不出设备”和 differential privacy 解决不同环节：前者让私有上下文留在本地，后者约束发布结果能透露多少个体信息。比如让 Siri 回答下周的会议，可以用本地证据；要统计大家常用哪个 emoji，才需要讨论上传的加噪统计和 $\varepsilon$。

Apple 2017 的 Learning with Privacy at Scale 讲本地 DP 频率统计，2024 foundation model 材料讲训练不用用户私有数据，Exponent MLE 指南也提到隐私和 on-device。回答时要把这些公开声明的范围分清楚。

## 先解释预算约束什么

机制 $M$ 满足 $\varepsilon$-DP，是指对至多差一条记录的邻居 $D,D'$ 和任意可测集合 $S$，都有

$$
\Pr[M(D)\in S] \le e^{\varepsilon}\Pr[M(D')\in S].
$$

它限制一条记录变化能给输出分布带来多大差别。$\varepsilon$ 越小通常要更大噪声，隐私越强；$\varepsilon=0$ 是输出与数据独立，$\varepsilon\to\infty$ 就没有 DP 承诺。本地 DP（LDP）在设备先随机化，服务器从未看见真值，不需要信任 curator；中心 DP 先收真值再加噪，需要更大的信任面。Apple 键盘、Safari 分析用 LDP。

公开 emoji 用例采用 Count Mean Sketch，$\varepsilon=4$、$m=1024$、$k=2^{16}$，词典约 2600；高耗电域名的 Hadamard CMS 同样 $\varepsilon=4$，每条记录可只发 1 bit。CMS 把 one-hot 哈希后，每个坐标以 $1/(e^{\varepsilon/2}+1)$ 翻转，单条像噪声，大量用户聚合后才能估频率。哈希碰撞有额外工程余量，但不能替代 $\varepsilon$ 的保证。

这些是事件预算，另有每日条数上限。同一用户提交 $n$ 次，最坏合成 $\varepsilon_{\mathrm{tot}}\le\sum\varepsilon_i$，还得考虑跨天累加。只报单次预算会漏掉持续采集的风险。

## 放回个性化语言模型里

on-device 推理读取邮件、日历或屏幕，条件是 $(q,E_{\mathrm{local}})$，用本地检索或 adapter 保留证据，评测答案是否被本地事实支持。没有上传的路径就不虚构 $\varepsilon$。quantization 和 on-device 推理也能帮助上下文留在设备。

PCC 把请求交给 Apple silicon 服务器，公开叙述是无持久化、无苹果可读日志，用来补 on-device 3B 能力。这属于机密计算，没有 DP 的 $\varepsilon$。DP 遥测则上传加噪的人群统计，用来学新词、新槽或 UI 模式；设计上要有事件级 LDP、条数限制、去标识，emoji 与 Safari 等用例分仓、不在服务端拼接。

改进全球 QuickType 或发现新俚语，可用 CMS / SFP，报告 per-event $\varepsilon$、每日 $n$ 和 opt-in。SFP 在未知词典拼出高频新词，仍是频率统计。foundation model 公开原则是不使用私有个人数据或交互训练基础模型，不能把它解释成上传邮件再训 AFM。

$\varepsilon=4$ 的 CMS 也不意味着八千字邮件加一点高斯噪声就能上传训练。长文本、高维 gradient 的 LDP 效用通常很差，DP-SGD、中心 DP、安全聚合需要另行设计；公开键盘系统没有宣称在训练 LLM。若讨论上传用户 adapter，可选择设备训练、设备存储，或者假设另做 gradient DP-SGD 并按用户合成预算。预算按用户级报告，按 token 报会漏掉长对话累积；公开 AFM 叙述没有这条上传路径，要明确这是假设方案。

## 追问

**PCC 算 DP 吗？**
不算。PCC 控制谁能看明文，DP 控制输出分布对记录的敏感度，两者可同时使用，但要分别解释。

**$\varepsilon=4$ 算大吗？**
学术讨论常认为偏松，尤其缺少生命周期合成时。可以引用 Apple 公开用例，同时交代 composition 和攻击面，不能用 2017 参数替现代 LLM 作担保。

**opt-in 失败怎么办？**
保持不采集。DP 不会替代用户同意。

**联邦学习就有 DP 吗？**
没有。无噪声 gradient 平均仍可能被成员推断，需要另加 DP 或安全聚合，预算另算。

相关：`apple-personalize`、`apple-siri-grounded`、`apple-ondevice-quant`
