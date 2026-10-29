---
id: drustz-165cfcb462c27a039f
section: anthropic
order: 92
level: A
title: Find Duplicate Files
quick: original-structured-preparation-guide · Find Duplicate Files
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/b38dbdc7-ff57-4c09-b92b-2054b2f5e5a4
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Find Duplicate Files：把目录遍历与内容分组拆开

## 题目

给定目录，找出全部重复文件并按内容分组。这个版本重点把“发现文件”和“判断内容”分层，便于在 Python、Java 或面试平台里测试。

```text
walk_files(root) -> Iterator[path]
find_duplicates(paths) -> List[List[path]]
```



目录 `root/x/a.txt` 与 `root/y/b.txt` 内容相同，即使文件名不同也属于一组；同名但内容不同不能归组。

## 实现

`walk_files` 用显式栈或语言自带的递归遍历，产出普通文件，默认不跟随 symlink。`find_duplicates` 先读取 size，再对有竞争者的桶分块计算 digest，最后过滤单元素组。生成器让遍历不必先保存全部目录项；但最终为了返回所有路径，索引仍通常需要 `O(N)`。测试时用临时目录创建嵌套文件，不依赖机器上已有路径，并在 teardown 清理。

分层还有一个好处：遍历器可以替换成对象存储、压缩包或测试用内存列表，而分组算法无需改动。若要求边扫描边输出，要注意某个候选组在扫描结束前仍可能增加成员，因此通常只能输出增量事件，不能过早宣布最终结果。

## 正确性、复杂度与边界

不同 size 必不相同；相同内容会进入相同 size 与 digest 桶。若必须绝对准确，再逐块比较候选。设访问 `N` 个文件、实际读取 `R` 字节，时间 `O(N+R)`，空间 `O(N)`。覆盖空根目录、根路径不存在、目录内文件消失、permission error、二进制和 Unicode 文件名、符号链接环，以及结果顺序；异常策略应由接口约定为跳过并报告或立即失败。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b38dbdc7-ff57-4c09-b92b-2054b2f5e5a4)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
