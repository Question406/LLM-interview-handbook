---
id: drustz-fe34af801efed21dce
section: openai
order: 117
level: A
title: 'Jetpack Compose: Build a UI Similar to Google Translate Home Screen'
quick: >-
  original-structured-preparation-guide · Jetpack Compose: Build a UI Similar to
  Google Translate Home Screen
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
      https://www.1point3acres.com/interview/problems/ecec4fb8-cd2f-4da0-9620-145885b2aa3f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Jetpack Compose：仿 Google Translate 首页

> 内容定位：公开描述给出了页面组件，但不要求接入真实翻译服务。下面是一套原创、可运行方向的实现说明。

## 题目要做什么

实现一个类似 Google Translate 首页的 Compose 页面：

- 顶部工具栏；
- 来源语言、目标语言和交换按钮；
- 点击语言后可从至少 10 种语言中选择；
- 文本输入最多 5,000 个字符；
- 有输入时显示模拟翻译结果和清空按钮；
- 正确管理语言、输入内容和弹窗状态。

## 状态设计

```kotlin
data class TranslateUiState(
    val sourceLanguage: Language,
    val targetLanguage: Language,
    val input: String = "",
    val picker: Picker? = null
)
```



模拟翻译结果是输入内容的派生值，不必在状态里重复保存。语言列表可以用 `Dialog` 或 `ModalBottomSheet` 配合 `LazyColumn` 展示。

## 实现步骤

1. 点击来源或目标语言时，把 `picker` 设为对应类型。
2. 用户选择语言后更新该字段并关闭弹窗。
3. 交换按钮一次性互换两个语言，避免出现只更新一边的中间状态。
4. `onValueChange` 中截断超过 5,000 字符的输入。
5. 输入为空时隐藏结果区和清空按钮；点击清空只重置文本。
6. 若要求旋转后恢复，可使用 `ViewModel` 与 `SavedStateHandle`。

## 复杂度

设文本长度为 `L`、语言数为 `K`。处理输入或生成模拟结果为 `O(L)`；扫描语言列表为 `O(K)`；空间为 `O(L + K)`。

## 容易踩坑

- 来源语言和目标语言相同；
- 5,000 字符按 UTF-16 code unit 还是 Unicode code point 计算；
- 交换语言时选择弹窗仍然打开；
- 输入只有空白；
- 小屏幕、动态字体和无障碍点击区域。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ecec4fb8-cd2f-4da0-9620-145885b2aa3f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
