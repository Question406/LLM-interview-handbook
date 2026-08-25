---
id: zhipu-dpo-gui-pair-length
section: data
order: 105
level: S
title: 智谱 Agent 算法：GUI 长轨迹 DPO 正负样本长度不一有什么影响？
quick: >-
  sequence log-prob 是 token 和，长短 pair 会把长度、EOS 与无关 token 数混进 preference margin，模型可能只学「更短」或「更长」。需在 pair 构造、长度归一化 / 目标定义、终止 token 与 per-slice eval 上显式控制，不能靠删长轨迹解决。
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

别答「长的 log-prob 更小所以总是输」。DPO 比较的是 **相对参考的序列和**，长度会同时进入 chosen、rejected 和 $\pi_{\mathrm{ref}}$，偏差方向取决于数据里「成功是否总更长 / 更短」，不是单调的。GUI 长轨迹里 observation、重复点击、EOS 格式都会变成假偏好信号。删掉长轨迹只会让模型没见过真实任务，不是解。Sequence log-prob 是 token 和，长短 pair 会把长度、EOS 与观察串混进 preference margin，模型可能只学更短或更长。必须在 pair 构造、是否长度归一化、终止格式和按长度切片的成功率上显式控制，而不是靠过滤长轨迹。

## 长度怎样混进 DPO margin

DPO 的偏好间隔来自

$$
\beta\Big(\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big).
$$

$\log\pi(y\mid x)$ 是 token 条件对数概率之和。$y$ 多一个 token，就多一项 $\log\pi(t_i\mid\cdot)$，通常为负。于是：

- 成功轨迹总更长（多步才点对、含详细 thought）时，chosen 的 sum log-prob 更小，模型可能学「宁愿短、早停」，表现为 premature stop；
- 失败轨迹总更长（乱点、循环）时，模型可能学「越短越好」，把必要的确认、滚动、重试当负例；
- EOS、工具调用格式、把整页 HTML 塞进序列，都会按 token 数加权，而不是按「这一步决策对不对」加权。

即使除以 $\beta$、即使有 $\pi_{\mathrm{ref}}$，只要两边长度系统不同，**多出来的那些 token 的 $\log(\pi_\theta/\pi_{\mathrm{ref}})$ 仍在间隔里**。Reference 同样对长序列求和，不能自动消去长度偏好，只能改变偏差的符号和大小。Length-normalized 目标（对 $|y|$ 取平均）是另一种目标，不是「同一个 DPO 更稳」，换了就应在 GUI 成功率上重评。直觉上：sum 目标把「每多说一个 token」写进偏好；GUI 里多说的往往是 observation 回放或无意义的 hover，不是更好的决策。平均目标把「每步都非常自信的短错」抬高，可能鼓励过早 terminate。两种目标都可能 length hack，只是方向不同，所以必须用任务成功来选，不能用 DPO loss 来选。

## GUI 长链路为什么特别容易中招

网页 / 桌面轨迹不是对称的对话 pair。正负样本长度不一往往来自任务结构，而不是随机：

- 成功路径包含正确 recovery：多几步点击、等待、回到正确窗口；
- 失败路径在错误菜单里打转，或很早点错就结束；
- observation 有时长有时短，DOM dump 的 token 数可以压过真正的 action token。

若 pair 构造是「同一任务的成功 vs 失败整段轨迹」，长度与对错高度共线。模型不必学会 grounding，只要学会「生成更长 / 更短的 action 序列」就能降低 DPO loss。这和纯文本 length hacking 同类，但 GUI 上还会表现为 endless-action（为凑长度重复滑）或过早 `terminate`。

优先构造 **同任务、相近 state、只在关键 action 或 recovery 处分歧** 的 counterfactual pair，并记录原因标签（点错坐标、选错控件、该停不停）。对无效 observation / 截图描述做 mask，让 loss 主要落在 action 与终止格式上。终止 token 的监督要两边一致，避免一边学到规范 EOS、另一边学到截断。Counterfactual 的意思是：尽量共享同一前缀，只在决策点分叉，这样长度差来自那几步 recovery，而不是整段 DOM 是否被序列化。原因标签事后还能做切片：若只有「失败更长」的循环类 pair 在拉动 loss，说明你在惩罚探索而不是惩罚点错。GUI 数据少、长轨迹贵，pair 质量比数量更重要；用整段成功 vs 整段失败硬配，是最容易把长度当标签的写法。

## 用切片 eval 抓 length hacking，别凭感觉删数据

按 chosen / rejected 长度差 $\Delta |y|$ 分桶，看 success、step count、premature stop 与 endless-action rate。若只在 $\Delta |y|$ 很大的桶上「DPO 很有效」，而长度接近的桶上成功率不动，就是在学长度。还要看：

- 平均步数是否单调变短或变长，而任务成功率不升；
- 同一初始 state 的对照 pair（长度接近、只改一个 action）上胜率是否也升。

对比 sum 与 length-normalized log-prob、SimPO 一类平均对数概率目标时，把 GUI 成功当金标，不要只看偏好 acc。不能靠过滤长轨迹解决问题：真实 GUI 任务就是长的；该做的是 pair 对齐、mask、终止格式控制，以及把长度当切片而不是当删除条件。汇报时建议同时给出：总体成功率、按 $\Delta |y|$ 分桶的成功率、早停率、平均步数。四条里只有总体成功率很好看，就要怀疑 length hacking。原因可以收成一句：**sequence-level 目标把 token 数写进 margin，而 GUI 正负样本的 token 数往往与对错共线。** 影响是模型学到长度策略；对策是构造局部反事实 pair、mask 观察串、用任务切片而不是用删数据来「解决」长轨迹。

智谱这问要的是因果：不是「长样本不好」，而是 log-prob 求和让长度成为假标签。把 GUI 特有的 observation 膨胀和早停 / 死循环评测带上，才像做过 agent 数据，而不是把普通 DPO 长度偏差复读一遍。GUI 长轨迹里 observation、重复点击和终止格式都会按 token 数进入 sequence log-prob，正负样本长度一旦与成败共线，DPO 就会学到「更短」或「更长」而不是正确点击。对策是局部反事实 pair、对观察串 mask、统一终止协议，并按长度差分桶看成功率、早停和死循环。删掉长轨迹只会让模型没见过真实任务，不能当解。

## 追问

- **为什么 reference 消不掉长度？** 两边都对序列求和，多出来的 token 仍贡献 $\log(\pi_\theta/\pi_{\mathrm{ref}})$。只有当额外 token 上两者 log-ratio 期望为 0 时才近似无关，GUI 观察串通常不满足。
- **平均 log-prob 就公平了吗？** 它削弱「越长越罚」，但会改目标：短而错的高置信序列可能被抬高。必须用 success / 早停 / 死循环率验收，见 `baidu-simpo-vs-dpo-length` 一类对照。换目标就要重评，不能当同一 DPO 的稳定版。
- **observation 要不要进 DPO？** 进了就按 token 数主导 margin。更稳的是 mask 掉不可控观察，只在 agent action 上算 preference。截图描述尤其长，最容易把长度写成标签。
- **pair 一定要等长吗？** 不必逐 token 等长，但应在同一任务、相近步数、同一终止协议下对比；关键分歧越局部，长度伪相关越弱。删长轨迹会让模型没见过真任务，不是解。
