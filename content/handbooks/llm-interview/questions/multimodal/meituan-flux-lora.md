---
id: meituan-flux-lora
section: multimodal
order: 181
level: A
title: 美团秋招二面：FLUX 怎么工作，LoRA 在这里起什么作用？
quick: "FLUX 是潜空间上的 flow matching Transformer：文本条件进调制，模型按时间步回归速度场、一步步去噪，最后由 VAE 解码出图。LoRA 挂在注意力和 MLP 的线性层上，用低秩残差改风格或主体，不重训整网；上线可以 merge，但要防小数据过拟合和多 LoRA 冲突。"
tags:
  - Meituan
  - FLUX
  - LoRA
  - Diffusion
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法二面-秋招面经
    url: https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177
    type: candidate-first-hand
  - title: FLUX official repo
    url: https://github.com/black-forest-labs/flux
    type: primary
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：“FLUX的工作原理，LoRA在这个地方起到了什么作用？”

FLUX.1 是潜空间上的 rectified flow / flow matching Transformer：文本条件进网络，模型沿时间步学一个速度场，把噪声一步步推成图像潜变量，再由 VAE 解码。LoRA 在这里是挂在线性层上的低秩残差，用很少的数据改风格或主体，不用重训 12B 的基座；它改的是外观分布，提高不了基座的物理真实度。

常见的错答一是把 FLUX 背成「就是 Stable Diffusion」，二是把 LoRA 说成能提升透视、手部这类能力。面试不要求背发布会上的层数，要说清两件事：条件怎么进网络，时间步在回归什么。

## FLUX 怎么工作

整条链是：文本编码（T5 / CLIP 一类）→ 条件注入 → 在 VAE 潜空间里按时间步预测速度 / 去噪 → 解码。公开实现先双流再单流：Double Stream 对图、文各用一套权重，注意力在拼接后的序列上混合；之后 Single Stream 把图文 token 拼在一起继续做。时间步和 guidance 经过 MLP 打进调制。

训练目标是 flow matching：沿 $x_t=(1-t)x_0+t\varepsilon$ 一类直线路径，回归速度 $v_\theta(x_t,t,c)\approx\varepsilon-x_0$（写法随参数化略有变化）。和 SD 的 U-Net 去噪比，这里是 Transformer 序列 + 流匹配。采样就是沿学到的速度场积分，步数少的时候也要锁随机种子做回归，否则「这次手好看」不代表模型变强了。白板上能画出「文本条件进调制 → 潜空间速度场 → VAE 出图」就够了，double/single block 的数目不用背。

## LoRA 在这里起什么作用

$$
W'=W+\frac{\alpha}{r}BA,\quad B\in\mathbb{R}^{d\times r},\;A\in\mathbb{R}^{r\times k},\;r\ll d.
$$

LoRA 挂在注意力和 MLP 的线性层上，官方的 `FluxLoraWrapper` 会替换 `nn.Linear`。和业务的关系在于品牌、人物、菜品的一致性，单靠基座加输入提示（prompt）往往不够。数据少、显存紧的时候，就把品牌色、人物脸、店铺画风落到低秩残差上。透视、手部解剖、物理真实度是基座能力，LoRA 改不了。

放到美团的场景里说：门店装修风、菜品摆盘、品牌吉祥物，训练集往往只有几十到几百张，全参微调容易连背景的桌子和拍摄角度一起过拟合。LoRA 把可更新的自由度压到 $r(d+k)$，相当于只允许模型沿低维的外观方向改。数据要做主体分离，同一道菜换不同的盘子和光照，否则残差学到的是「永远这张桌子」。

推理时 $\alpha/r$ 是强度旋钮，开太大和 CFG 叠加会过饱和、出现畸形。上线可以 merge 进 $W$，没有额外延迟，也没有额外算子。风险主要有四个：过拟合训练集里的姿势和背景，和基座的 CFG / guidance 打架，多个 LoRA 叠加时权重冲突，把训练集的水印学进去。多品牌别一股脑叠一堆 LoRA，先分模块（只挂 attn，或只挂单流块），再做 A/B。

文字是另一个坑。菜单、价格、店名仍然是生成模型的弱项，LoRA 学的是纹理，排版它管不了；要可读的文字就走后处理或专门的文字层，指望再调 $r$ 没用。所以评测要看同一输入提示下的主体一致率、畸形率和文字可读性（菜单 / 价签），只刷美学分不够。

## 追问

**$r$ 越大越好吗？**
不是。太大接近全参微调，失去 LoRA 的正则作用；太小又拟合不动主体。先扫 $r\in\{8,16,32,64\}$，看验证集上的畸形率。

**能替代 ControlNet 吗？**
不能。LoRA 改的是外观分布，深度、姿态、版式这类空间条件仍要靠条件分支或 in-context 编辑。

**flow 和 DDPM 的损失有什么区别？**
都是在噪声轨迹上做回归。flow 常用直线路径和速度目标，采样步数往往更少，但这谈不上无损压缩。

**多个 LoRA 怎么控？**
分尺度、分模块，或者一次只 merge 一个。出现冲突时，看是哪一层在抢同一个 $W$。

**和 LLM 上的 LoRA 一样吗？**
公式一样，挂的层和过拟合的症状不同：扩散模型更常出现人体结构和纹理错误，LLM 更常出现格式和事实错误。
