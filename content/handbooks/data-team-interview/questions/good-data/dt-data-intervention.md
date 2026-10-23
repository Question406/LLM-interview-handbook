---
id: dt-data-intervention
section: good-data
order: 15
level: S
title: 怎样才算把数据做对：一次干预从假设跑到能不能上 mix？
quick: "先写一个能被推翻的假设，固定评测，一次只改一项数据因素，比如来源、过滤或配比。用同模型、同预算的对照看目标能力和其他能力，再查污染、隐私、许可和版本记录。通过了才进训练 mix，没通过就隔离，记下失败原因。"
companies:
  - apple
tags:
  - Apple
  - Data Flywheel
  - Data Quality
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: Datasheets for Datasets
    url: https://arxiv.org/abs/1803.09010
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "Everyone wants to do the model work, not the data work (CHI 2021)"
    url: https://dl.acm.org/doi/10.1145/3411764.3445518
    type: primary
---

一次数据干预要从「我怀疑问题出在这」走到「实验支不支持、这批数据能不能进训练」。做法是先写一个能被推翻的假设，固定评测，一次只改一项数据因素，用同模型、同预算的对照去检验，查完副作用、记好版本，再决定合并还是隔离。

假设要写得具体。比如：「工具第二次调用失败，是因为 SFT 里没有合法处理失败的分支。」这句话能被实验推翻，比「我们缺数据」有用得多。假设一般从固定评测里的失败模式、WIMBD 式的计数和人工标注争议里找，怎样从评测里诊断出来见 `dt-benchmark-gap`。

一次只改一项，是为了能归因。同时换来源、过滤器和配额，出了问题说不清是哪一项造成的；训练中途不断改过滤规则，再把 loss 下降归功于数据变好，也没法复现。DataComp-LM 固定模型、只改数据，就是这个道理。

## 一轮怎么跑

假设写好后，先把评测固定下来。开发集可以跟着迭代，发布前必须过的检查集在实验期间不动，新标注的参考答案另起一页追加。

然后改那一项：加一个来源、调一个阈值、改一个配额，或者加入验证过的合成数据，效用怎么定义见 `dt-utility-select`。动手之前先确认来源合法、允许用于训练。

接着做对照。固定模型和预算，同时报目标切片和用来看其他能力的锚点指标，见 `dt-hold-model-vary-data`。结果出来后查副作用：评测污染、个人信息（PII）、许可，还有各语言的通过率。如果发现错误已经开始沿处理流程扩散，先停下来往回查，见 `dt-data-cascade`。

最后记录再合并。写清来源、过滤器 git 版本、教师版本和指标变化 $\Delta$，Datasheets 列的字段就是干这个用的。没过检查的数据进隔离区（quarantine），不进训练 mix。

实验失败也有信息量，它告诉你哪句假设不成立、下一步该查什么。HM 问失败的数据尝试时，可以按这个过程讲，见 `dt-failed-data-bet`。整个持续迭代的流程在 `dt-data-flywheel`，这题讲的是其中一轮具体怎么做。

## 追问

**一轮要多久？**
有验证器（verifier）的工具和数学任务可以按周迭代，主观人评按抽检批次来。目标是赶在产品投诉之前发现问题，避开 cascade 里常见的那种延迟。

**许可和隐私在哪一步查？**
在改数据之前，先确认来源能不能合法使用。来源换成许可研究集或合成复现之后，后面的实验和检查照样要做完。

**用当前模型给新数据打标，再看检查集涨没涨，可以吗？**
不行，这会形成自污染。检查集一旦被污染，分数上涨证明不了数据有效，见 `dt-self-improve`。

**新爬取、新分类器、新配额一起上线，省时间行不行？**
省下的时间以后会还回去。Director 问成本收益时，你没法单独删掉其中一项重跑对照，也就答不出哪项值得投入，见 `dt-cost-per-gain`。

**「业界都在做合成」能当假设吗？**
不能，它给不出一个能被实验推翻的具体判断。假设要落到某类失败模式上，比如上面那个工具第二次调用失败的例子。
