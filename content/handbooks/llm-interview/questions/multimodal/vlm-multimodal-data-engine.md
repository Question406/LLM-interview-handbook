---
id: vlm-multimodal-data-engine
section: multimodal
order: 203
level: A
title: 多模态数据引擎应具备哪些阶段（collection、filtering、annotation、feedback incorporation）？
quick: >-
  数据引擎是一个 feedback loop：采集、质量和安全过滤、自动加人工标注、训练、按失败类型挖掘再入库。每个阶段有量化
  threshold，数据集、过滤规则和标注指南都版本化，不然加了数据也说不清是哪批起的作用。
tags:
  - Data Engine
  - Multimodal
  - Pipeline
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: >-
      Learning Transferable Visual Models From Natural Language Supervision
      (CLIP)
    url: 'https://arxiv.org/abs/2103.00020'
    type: primary
---

多模态数据引擎是一个 feedback loop：采集 $\to$ 质量 / 安全过滤 $\to$ 自动加人工标注 $\to$ 训练 $\to$ 错误挖掘再入库。每个阶段有量化 threshold，产物都版本化。只讲爬虫和标注员人数答不到点上，堆更多图文对也不等于有了数据引擎。

为什么必须 feedback loop：没有 failure-driven data updates，易例可能把离线定位分数抬上去，线上图标和扫描件的错误却一直没解决。为什么要版本化：数据集 digest、过滤规则版本、标注指南版本少一个，「加了数据」就没法归因。CLIP 一类工作已经说明，规模有效的前提是过滤、对齐和版本化，网图原样入库不行。

采集阶段记来源、许可、时间、语言、分辨率，光有 URL 不够。许可证和版权来源写进 provenance，训不进的数据不要「先用着再补协议」。过滤至少处理模糊 / 过压缩、图文低相关、近重复、PII、有害、水印广告，以及 caption 和像素明显不匹配。相关度可以用 CLIP 分数设下限 $s(I,T)\ge\tau$，但$\tau$ 不能当唯一 quality criterion，高分也可能是模板水印配万能文案。过严的话有效规模会塌：若过滤后 $|D'| \lt \beta |D|$ 且下游召回不升，说明 $\tau$ 切掉的是长尾不是垃圾，该改规则，别继续加严。安全过滤和质量过滤分开报，有害漏放率和低相关删除率都要有，合成一个「清洗率」会把漏放藏起来。PII 走检测加人工抽检，caption 里没有名字，不代表像素里也没有。

标注按任务拆开，别一张图配一个万能 caption：grounding 框、OCR、UI 动作、文档 layout、视频关键帧状态，各有各的指南和 IAA。动作轨迹和 OCR 的错误模式不同，混成 caption 就没法重新加入具体的模型头。做法是自动预标加人工 calibration，争议样本进黄金集。每个阶段的 threshold 都量化：近重复率、有害漏放率、框交并比（IoU，即两个区域的交集与并集之比）、OCR 字段 F1、动作轨迹可执行率。

训练之后按 failure type 补充下一轮训练数据：grounding 偏、OCR 串行、图标无文本、扫描倾斜，别再堆「好看」的自然图。feedback-data proportion 要有下限，比如失败挖掘 $\ge \alpha$ 的新数据，不然引擎会退化成易例工厂。度量盯下游的 grounding 召回、有害漏放、近重复，光盯数据条数没意义。

版本化落到每次训练，都要声明数据 digest、过滤配置、标注指南 commit。换了指南却沿用旧 id，评测会把标注漂移当成模型提升。黄金集冻结，过滤规则一变就重跑漏放。这套和文本数据引擎一样，只是多了像素级近重复和跨模态相关度。

容易误导的做法有：拿合成的规整 UI 当唯一来源；过滤只删模糊、不删注入图；新增数据只包含模型已经会的类别；没有数据集 digest。CLIP 的经验是过滤改变有效规模，GUI / 文档数据也一样，未过滤的百万对，可能不如经过 failure-driven data updates 的十万对。面试时讲清 $\tau$、漏放率和 feedback-data inclusion rate，「爬了多少站点」当不了主答案。

## 追问

**CLIP 分数够不够当唯一的过滤？**
不够。它不测 PII、版权、注入和图标无文本，只能当相关度下限。

**为什么 feedback data 必须包含失败 case？**
只加易例可能提高离线分，线上长尾任务却改善不了；失败挖掘才会推动 frontier。

**近重复怎么算？**
感知哈希加嵌入近邻。跨分辨率的截图也要算重复，不然 GUI 数据会被同一个页面刷爆。
