# DrustZ · AI Interview Prep 2026 导入记录

- Author: Mingrui Zhang / DrustZ
- Repository: https://github.com/DrustZ/ai_interview_prep_2026
- Pinned revision: `04316c111d0e4b75ca2ab8de0e6b42379727946e`
- Import date: 2026-10-28
- Destination: `content/handbooks/drustz-interview-2026/`

## 导入范围

完整盘点 1,808 个 tracked files。作者当前 Markdown、company catalog preparation guides、supplemental research notes、Deep-ML exercises 和 practice implementations 整合为独立题本。长文档按真实的 H2 sections 切分，保留段落与代码的顺序；短文档整篇保留。资料卡数量是阅读单元数量，不等于独立面试题数量。

旧 local_materials.json 的行号与当前源文件不一致，因此 Markdown 从当前文件重新切分；被旧索引截断的 Python 从源文件恢复。Deep-ML 从 description、learn、starter、solution、tests、example、meta 等文件重新组装。原始 forum posts 与第三方 raw articles 仅保留标题与链接。作者个人故事、时间安排、模拟设计不归为用户经历。

`manifest.json` 保存所有 1,808 个文件的 SHA-256、大小、覆盖方式与对应卡片；viewer、crawler 和原始元数据作为基础设施或来源记录，不计为面试题。`oj_original_guides.md` 对应的 212 篇指南已经在 company catalog 中，不重复导入。

## 许可与 attribution

主体材料遵循原仓库 MIT license，保留 `LICENSE`：Copyright (c) 2026 Mingrui Zhang。

Deep-ML 遵循单独的 **Educational Use Only License**，完整保留在 `DEEPML-LICENSE`，用于个人教育学习；不属于 MIT，禁止商业使用及作为 ML training data。原始论坛内容及外部文章的权利属于对应作者，原仓库的 MIT 不覆盖其第三方原文；本次只保存其来源索引。

公开下载位于 `public/materials/drustz-interview-2026/`：代码与测试数据 ZIP、文件覆盖清单、两份 license。ZIP 中保持原有目录，便于查看相对 import 和测试配置。

## Rebuild

```bash
python3 scripts/collect-drustz-materials.py /path/to/ai_interview_prep_2026 /tmp/drustz-import.json
node scripts/import-drustz-materials.mjs /tmp/drustz-import.json
npm run build
```

Collector 要求 pinned revision，一律不运行上游代码。Importer 保留 source links，转换不受支持的 HTML；可解析的代码交给统一 formatter，不完整或不能独立解析的片段按 `text` 保留，不补写算法。`normalization-report.json` 记录这些片段和不支持的 LaTeX。

## Validation

整站 build 验证所有卡片 metadata、Markdown、LaTeX 与代码 formatting；Node tests 包含下载链接 sanitization。另核对所有当前学习文档的覆盖、ZIP 完整性、源文件 SHA-256、company catalog 及 Deep-ML 的数量。导入不宣称所有上游 algorithms / labs 都通过执行验证。
