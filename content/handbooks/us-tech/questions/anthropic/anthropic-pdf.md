---
id: anthropic-pdf
section: anthropic
order: 27
level: A
title: Anthropic：PDF 是页图还是文本层？引用怎么落到页？
quick: >-
  原生 PDF 每页同时进一张图和抽出来的文本。图保版面、表、章；文本层才是 citations 能指的句子。扫描件几乎没有文本层，页码引用会空或假。无引事实句不要展示。不要自己编页码。
tags:
  - Anthropic
  - PDF
  - Vision
  - Citations
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PDF support (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/pdf-support
    type: primary
  - title: Citations (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/citations
    type: primary
---

企业文档岗会把「把合同丢给 Claude 并点回原页」当成系统设计。官方路径是 `document` 块，类型为 PDF，不是你先 OCR 再糊进 user 散文。Citations 打开后，PDF 的指针带从 1 计的页码。我会把页图、文本层、引用三件事对齐 `anthropic-citations`。

## 混合编码：每页 = 图 + 字

发送 PDF 之后，服务端大致做两步：

1. 每一页渲染成图，走和 `anthropic-vision` 同一套视觉 token（约 $\lceil W/28\rceil\times\lceil H/28\rceil$，再受长边上限约束）；
2. 抽取该页 PDF 文本层，按句切开，和页图一起进模型。

所以 token 是文本 token 加页图 token，不是二选一。文档给过数量级：文本大约每页一千五到三千；三页带视觉理解大约七千 token 量级（Bedrock Converse 上他们拿「纯抽文本约一千 / 开视觉约七千」对比过）。密表、小字、嵌图会先撑爆窗口，再碰到页数上限。上限大约：整请求几十 MB；页数在普通窗口约 100，百万 token 窗口可以到数百。密 PDF 往往窗口先满。大文件用 Files API 只传 `file_id`。

三条产品路不要混：

| 路径 | 模型看见什么 | 适合 |
| --- | --- | --- |
| 只抽文本（或 Converse 未开 citations 的回退） | 字，没图 | 条款检索、纯文本合同 |
| 原生 PDF / 页图+文本 | 版面 + 字 | 表、章、印章、多栏 |
| 自己截成多张 `image` | 只有像素 | 扫描件；但 citations 指不到句 |

扫描件、拍照件常常没有文本层。视觉仍可能读字，但 citations 文档写死：目前只能引文本，不能引 PDF 里的图。没有文本层就没有可引用 span。此时要么先 OCR 做成 custom content 块，要么 UI 只给「模型看见图，未接地」的弱提示，不要假装有页内高亮。

Bedrock Converse 的坑：不开 citations 会退回纯文本抽取，模型「看不见」图和表。这是网关行为，不是 Claude 突然不会看图。面试要说清平台差。

## 引用落到页，不落到幻觉页码

PDF citations 的形状：起始/结束页码（从 1 计）加 `cited_text`。指针保证落在你提供的文件里，不保证论断被这段支持。合规产品我仍用 `anthropic-citations` 那条政策：无 citation 的经验句丢掉或改成「文档未覆盖」。

扫描件 + 开 citations 的失败模式：模型用视觉读到数字，却编一个看起来像的页码；或者引到页眉页脚。评测要抽查：高亮文本是否真支持该句，页码是否和 PDF viewer 的逻辑页一致。文档建议 prompt 里用 viewer 的逻辑页号，并先把页旋转正。

```python
def show_claim(block):
    if not block.citations:
        return hedge(block.text)  # 无引则降级，不展示为事实
    for c in block.citations:
        ui.link(page=c.start_page_number, quote=c.cited_text)
```

不要用 prompt 求「请列出第几页」：那是 `anthropic-eval-honesty` 会抓的编造。API 路径至少堵死「指向未提供文档」；错配 span、未引事实仍要产品挡。

## 和缓存、长窗口、注入

长合同跨多次问答：document 块放消息最前，`cache_control` 打在文档末，问题放后缀，见 `anthropic-prompt-cache`。文档建议 PDF 放在提问文本之前。离线对账走 `anthropic-batch-api`。窗口预算和针测见 `anthropic-long-context` / `anthropic-needle`——页图把 $T_{\mathrm{vis}}$ 算进同一条 $T$。

外部 PDF 零信任：条款、页脚、「忽略系统提示」都是注入，见 `anthropic-prompt-injection`。像素里的指令见 `anthropic-mm-harm`。不要把下载来的年报当已授权系统提示。

错法：为了省视觉 token 只贴 OCR、表对不齐还怪模型；开了 citations 却只渲染 `text`、丢掉页码；一百页一次塞进 200k 窗口；用 `context` 字段塞真正要引的条款（引不到）。

## 追问

- **为什么不全部自己 OCR？** OCR 丢版面和章。原生混合少一座级联。扫描件例外：没有文本层时，OCR 成 custom 块才能引句。
- **引用能证明没幻觉吗？** 不能。只能证明字来自该页文本层。图里的趋势线目前引不到。
- **加密 PDF？** 官方不支持带密码的文件。先在可信侧解密，不要把口令交给模型。
- **和 tool 检索怎么接？** 先按段召回，再把命中页做成短 PDF 或 custom 块开 citations。整本塞进去是在赌窗口，不是检索。
