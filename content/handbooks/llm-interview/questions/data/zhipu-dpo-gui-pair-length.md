---
id: zhipu-dpo-gui-pair-length
section: data
order: 105
level: S
title: 智谱 Agent 算法：GUI 长轨迹 DPO 正负样本长度不一有什么影响？
quick: "DPO 的序列 log-prob 是各 token 对数概率之和，GUI 里正负轨迹的长度往往和对错一起变，长度、EOS 和 observation 的 token 数就混进了偏好间隔，模型可能只学会把输出变长或变短，表现为早停或死循环。对策是构造同前缀、只在关键 action 分叉的反事实 pair，mask 掉 observation，统一终止格式，按长度差分组评测；删长轨迹解决不了。"
tags:
  - Zhipu
  - GUI Agent
  - DPO
  - Preference Data
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 智谱大模型agent算法面经 好细啊（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/24952c828c59435abd3c302c97fa358d
    type: candidate-first-hand
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

## 真题记录

- 公司：智谱（Zhipu）
- 团队 / 岗位：大模型 Agent 算法
- 届别 / 流程：原帖未披露；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-02-13
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“长链路GUI下正负样本长度不一有啥影响？原因是啥？”**

长度不一的影响是：DPO 的序列 log-prob 是各 token 对数概率之和，正负轨迹长度不同，长度本身、EOS 和无关 token 的数量都会混进偏好间隔，模型可能只学到「输出更短」或「更长」，没学会点对控件。偏差的方向取决于数据里成功轨迹是不是总更长或总更短，并不单调，「长的 log-prob 更小所以总是输」这个说法不对。靠删掉长轨迹也解决不了，真实的 GUI 任务本来就长。

先看长度怎么进到 DPO 的间隔里。直接偏好优化（DPO）的偏好间隔来自

$$
\beta\Big(\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big).
$$

$\log\pi(y\mid x)$ 是 token 条件对数概率之和，$y$ 每多一个 token，就多一项 $\log\pi(t_i\mid\cdot)$，通常是负的。长度会同时进入 chosen、rejected 和 $\pi_{\mathrm{ref}}$。成功轨迹总更长时（多走几步才点对、含详细 thought），chosen 的 sum log-prob 更小，模型可能学成「宁愿短、早停」，表现为 premature stop。失败轨迹总更长时（乱点、循环），模型可能学成「越短越好」，把必要的确认、滚动、重试都当负例。EOS、工具调用格式、把整页 HTML 塞进序列，都会按 token 数加权，跟「这一步决策对不对」无关。

有 $\beta$、有 $\pi_{\mathrm{ref}}$ 也抵消不了。只要两边长度系统性不同，多出来那些 token 的 $\log(\pi_\theta/\pi_{\mathrm{ref}})$ 还在间隔里。Reference 同样对长序列求和，它只能改变偏差的符号和大小，消不掉长度偏好。

GUI 长轨迹特别容易出这个问题，因为网页和桌面轨迹的长短往往来自任务结构，并不随机。比如订一张机票，成功的那条多了几步正确的 recovery：弹窗出来后点关闭、等页面加载、切回正确的窗口；失败的那条可能在错误菜单里一直打转，也可能很早点错就结束了。observation 有时长有时短，DOM dump 的 token 数可以压过真正的 action token。pair 要是按「同一任务的整段成功轨迹对整段失败轨迹」来配，长度就和对错高度共线，模型不用学 grounding，只要学会生成更长或更短的 action 序列，DPO loss 就能降。这和纯文本的 length hacking 是一类问题，在 GUI 上还会表现为 endless-action（为了凑长度反复滑动）或者过早 `terminate`。

所以 pair 要这样构造：同一任务、相近 state，尽量共享同一前缀，只在关键 action 或 recovery 处分叉，这样长度差来自那几步 recovery，和整段 DOM 有没有被序列化无关。每个 pair 记一个原因标签（点错坐标、选错控件、该停不停），事后可以切片：要是只有「失败更长」的循环类 pair 在拉动 loss，说明你在惩罚探索，没在惩罚点错。无效的 observation 和截图描述 mask 掉，让 loss 主要落在 action 和终止格式上。终止 token 的监督两边要一致，免得一边学到规范的 EOS、另一边学到截断。GUI 数据少、长轨迹贵，pair 质量比数量重要，整段成功对整段失败硬配，是最容易把长度当标签的写法。

要不要换成 length-normalized 目标（对 $|y|$ 取平均）？可以试，但它是另一个目标，算不上「同一个 DPO 更稳」，换了就要在 GUI 成功率上重新评。直觉上，sum 目标把「每多说一个 token」写进了偏好，而 GUI 里多出来的往往是 observation 回放或无意义的 hover；平均目标会把「每步都很自信的短错」抬高，可能鼓励过早 terminate。两种目标都可能 length hack，只是方向不同，所以只能用任务成功来选，DPO 损失（loss）选不出来。和 SimPO 一类平均对数概率目标比较时，也把 GUI 成功当金标，只看偏好 acc 不够。

评测上，按 chosen / rejected 的长度差 $\Delta |y|$ 分组，看 success、step count、premature stop 和 endless-action rate。如果只在 $\Delta |y|$ 很大的桶上「DPO 很有效」，长度接近的桶上成功率不动，就是在学长度。另外看平均步数是不是单调变短或变长、任务成功率却不升，以及同一初始 state 的对照 pair（长度接近、只改一个 action）上胜率有没有一起升。汇报时同时给总体成功率、按 $\Delta |y|$ 分组的成功率、早停率、平均步数；四项里只有总体成功率好看，就要怀疑 length hacking。长度应该当切片来看，别当删除条件。

智谱这一问想听的是因果：log-prob 求和让长度成了假标签，长样本本身没有错。把 GUI 特有的 observation 膨胀和早停、死循环的评测带上，才像做过 agent 数据。

## 追问

**为什么 reference 消不掉长度？**
两边都对序列求和，多出来的 token 仍然贡献 $\log(\pi_\theta/\pi_{\mathrm{ref}})$。只有额外 token 上两者 log-ratio 的期望为 0 时才近似无关，GUI 的观察串通常不满足。

**换成平均 log-prob 就公平了吗？**
它削弱了「越长越罚」，但目标也变了，短而错的高置信序列可能被抬高。要用 success、早停率、死循环率验收，见 `baidu-simpo-vs-dpo-length` 一类对照。

**observation 要不要进 DPO？**
进了就会按 token 数主导 margin。更稳的做法是 mask 掉不可控的观察，只在 agent action 上算 preference。截图描述尤其长，最容易把长度变成标签。

**pair 一定要等长吗？**
不必逐 token 等长，但要在同一任务、相近步数、同一终止协议下比，关键分歧越局部，长度的伪相关越弱。删长轨迹会让模型没见过真实任务，解决不了问题。
