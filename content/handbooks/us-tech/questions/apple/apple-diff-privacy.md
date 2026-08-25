---
id: apple-diff-privacy
section: apple
order: 5
level: S
title: Apple：差分隐私在个性化语言模型里怎么讲 ε，和「数据不出设备」的关系？
quick: >-
  「不出设备」是数据最小化，没有 $\varepsilon$。DP 是：即使加噪后的统计离开设备，邻居数据集的输出仍
  $e^{\varepsilon}$-不可区分。个性化 LM 的私有上下文应留在端上做检索 / adapter；只有要学人群规律时才花
  $\varepsilon$。不要把 PCC、本地 DP、训练数据三者说成一件事。
tags:
  - Apple
  - Differential Privacy
  - On-device
  - Personalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Learning with Privacy at Scale
    url: https://machinelearning.apple.com/research/learning-with-privacy-at-scale
    type: primary
  - title: Differential Privacy
    url: https://machinelearning.apple.com/research/diff-privacy
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Apple MLE 基础轮会把隐私问得很死，Exponent 指南也点了 data privacy 和 on-device。这题容易答成口号。个性化语言模型要把三个机制拆开，再决定 $\varepsilon$ 花在哪。Apple 2017 的 Learning with Privacy at Scale 讲的是本地 DP 做频率统计；2024 的 foundation model 文讲的是训练不用用户私有数据。面试里两篇都要能指到，不要混成「Apple 有 DP 所以模型是私密的」。

## $\varepsilon$ 在说什么

机制 $M$ 满足 $\varepsilon$-DP：对至多差一条记录的邻居 $D,D'$，以及对任意可测集合 $S$，

$$
\Pr[M(D)\in S] \le e^{\varepsilon}\Pr[M(D')\in S].
$$

$\varepsilon$ 越小噪声越大、隐私越强。$\varepsilon=0$ 是输出与数据独立；$\varepsilon\to\infty$ 没有 DP 承诺。本地 DP（LDP）在设备上先随机化再上传，服务器自始至终看不到真值，不信任 curator。中心 DP 是服务器先收齐再加噪，信任面更大。Apple 键盘 / Safari 分析走的是 LDP。

公开参数可以举他们自己的例子：流行 emoji 的 Count Mean Sketch，$\varepsilon=4$，$m=1024$，$k=2^{16}$，词典约 2600；高耗电域名的 Hadamard CMS，$\varepsilon=4$，每条记录可以只发 1 bit。这是按事件的 $\varepsilon$，外加每日条数上限。追问 composition：同一用户 $n$ 次提交，最坏 $\varepsilon_{\mathrm{tot}}\le\sum\varepsilon_i$。只报 per-event $\varepsilon$、不提每日上限和跨天累加，会被认为没读过定义。

CMS 的直觉：one-hot 哈希之后，每个坐标以 $1/(e^{\varepsilon/2}+1)$ 翻转。单条记录像噪声，海量用户平均出频率。哈希碰撞额外给了一点否认能力，但那是工程余量，不要说碰撞可以替代 $\varepsilon$。

## 三件不是一回事

端侧推理：数据不离开设备，没有 $\varepsilon$，用来读邮件、日历、屏幕并生成答案。

Private Cloud Compute：请求到 Apple silicon 服务器，公开叙述是无持久化、无苹果可读日志。这是机密计算，不是 DP，没有 $\varepsilon$。用来补端上 3B 不够的大模型。

本地 DP 遥测：加噪统计上传，有 $\varepsilon$。用来学「大家常用哪个 emoji」，不是学「你的邮件写了什么」。

Foundation model 公开原则：不用用户私有个人数据或交互来训练基础模型。所以个性化默认不是把你的邮件送去再训一版 AFM。端上能完成的，用本地检索或本地 adapter，见 `apple-personalize`。只有当你设计的是从人群里学新词、新槽、新 UI 模式，才进入 DP：事件级 LDP、条数上限、去标识、按用例拆仓（emoji 记录和 Safari 记录在服务端不拼接）。

常见错答：「数据不出设备，所以 $\varepsilon$ 很小。」不出设备意味着这条路径没有发布函数，谈 $\varepsilon$ 没有意义。另一错答：「我们上了 DP，所以可以把原文上传。」$\varepsilon=4$ 的 CMS 保护的是频率估计，不是把八千字邮件加一点高斯噪声当训练集。高维梯度 / 长文本的 LDP 效用通常烂掉，那是 DP-SGD 加中心 DP 或安全聚合的另一题，Apple 公开键盘系统没有声称在训 LLM。

## 个性化 LM 里 $\varepsilon$ 怎么开口

产品目标若是「Siri 知道我下周的会」：证据留在设备，生成条件是 $(q,E_{\mathrm{local}})$，评测接地，见 `apple-siri-grounded`。没有上传，就不编一个 $\varepsilon$。

产品目标若是「改进全球 QuickType / 发现新俚语」：沿用 CMS / SFP，报告 per-event $\varepsilon$、每日 $n$、opt-in。SFP 用来在未知词典里拼高频新词，仍然是频率，不是把用户句子原文送去 SFT。

若有人逼问「用户 adapter 能不能上传」：要么完全不上（设备侧训、设备侧存），要么对梯度做 DP-SGD 并按用户合成预算。$\varepsilon$ 要按用户级不是按 token 级报，否则长对话把预算打爆。Apple 公开 AFM 训练叙述里没有这条路径，面试里把它标成「若做，约束是这些」，不要假装已经上线。

和 `apple-ondevice-quant` 连一句：量化、端侧推理是为了让个性化上下文根本不必离开设备；DP 是为了那些你**决定发布**的聚合统计。两条杠杆，不要用一条口号代替。

## 追问

- **PCC 算 DP 吗？** 不算。PCC 限制的是谁能看见明文；DP 限制的是输出分布对单条数据的敏感度。可以同时有，但回答必须拆。
- **$\varepsilon=4$ 算不算大？** 学术界常觉得偏松，尤其是只按天、不按生命周期合成。面试答：报 Apple 公开用例的数，同时承认 composition 和攻击面，不要替 2017 的参数做现代 LLM 的担保。
- **opt-in 失败了怎么办？** 系统保持不采集。DP 不是绕过同意的许可证。
- **和联邦学习？** FL 本身不是 DP。无噪声的梯度平均会被成员推断。要保护个体，仍然要 DP 或安全聚合，预算另算。
