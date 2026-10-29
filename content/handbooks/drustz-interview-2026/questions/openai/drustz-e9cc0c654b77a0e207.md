---
id: drustz-e9cc0c654b77a0e207
section: openai
order: 126
level: A
title: 'iOS Take-Home: Implement a Sample Project (UIKit/SwiftUI)'
quick: >-
  original-structured-preparation-guide · iOS Take-Home: Implement a Sample
  Project (UIKit/SwiftUI)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/57301c85-b925-4bcf-8609-7c1e87a84a74
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# iOS Take-Home：样例项目实现

> 重要限制：公开页面说明真实要求位于随项目附带的 README，但该 README 没有公开。因此这里不能还原具体功能，也不能伪造“标准答案”。

## 可以确认的任务

候选人会收到一个 Xcode 样例项目，需要使用 UIKit 或 SwiftUI 完成 README 中指定的界面、交互、业务逻辑和验收标准，最后交付一个可运行的项目以及运行说明。

## 通用完成方案

1. **建立基线**：先在指定 Xcode 和 iOS 版本中编译、运行原项目，记录已有失败。
2. **拆解要求**：把 README 的每条要求转成可勾选的验收用例。
3. **组织代码**：用 MVVM 分离 View、页面状态和业务逻辑；避免把网络或存储直接写进 View。
4. **注入依赖**：网络、存储、时钟通过 Protocol 注入，测试时使用 fake implementation。
5. **覆盖测试**：为重要状态转换写单元测试，为主流程写少量 UI 测试。
6. **整理交付**：写明运行方式、架构选择、完成范围、已知限制和后续改进。

## 复杂度

真实复杂度取决于缺失的 README，当前无法给出可靠的时间或空间复杂度。

## 检查清单

- Deployment Target 与依赖版本是否匹配；
- 异步任务能否取消，UI 是否只在主线程更新；
- 离线、空数据、错误和加载状态是否完整；
- 不同屏幕尺寸、深色模式、动态字体和 VoiceOver 是否可用；
- API key、token 等秘密信息是否被错误提交进项目。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/57301c85-b925-4bcf-8609-7c1e87a84a74)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
