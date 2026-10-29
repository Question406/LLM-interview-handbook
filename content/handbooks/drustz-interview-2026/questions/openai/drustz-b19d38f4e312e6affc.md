---
id: drustz-b19d38f4e312e6affc
section: openai
order: 162
level: A
title: Implement Node and Function Classes with Type Inference
quick: >-
  original-structured-preparation-guide · Implement Node and Function Classes
  with Type Inference
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
      https://www.1point3acres.com/interview/problems/a425b87b-b53c-40ae-9683-57d3e32491ee
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Node / Function 类型树与泛型推断

## 证据边界

当前标题与本地同题族完整资料一致确认：实现 `Node`、`Function`、字符串表示及泛型返回类型推断。primitive 的精确集合在不同记录中略有差异，因此应由构造器传入或固定为题目所给集合；不能仅凭“大写就是 generic”猜测。下面是结构化重述，不是会员页逐字原文。

## 可读题面、接口与例子

`Node` 是 primitive/generic 叶子或有序 tuple 子节点；`Function(parameters, output_type)` 表示签名。实现：

```python
def get_return_type(actual: list[Node], fn: Function) -> Node: ...
```



字符串格式为 `[int,T1]` 与 `(T1,int,T1) -> [T1,float]`。调用后者的实际类型 `[str,int,str]`，结果为 `[str,float]`；若最后一项改为 float，同一个 T1 被迫绑定 str 与 float，应报 generic conflict。实际参数保证为 concrete，返回新 Node，不能修改函数定义。

## 解法与关键数据结构

用不可变 tagged tree `Node(kind,name,children)`，结构相等不能靠对象 identity。`bind(pattern,actual,env)`：generic 叶首次写入哈希表，重复时做整棵树结构相等；primitive 要求名称相同；tuple 要求实际也是 tuple、长度相同，再逐子节点递归。全部参数绑定成功后，`substitute(fn.output,env)` 深拷贝返回树并替换 generic。若返回类型出现未绑定 generic，应按题意报错，而非把占位符静默留下。

## 复杂度与边界测试

设所有被访问类型树节点总数为 `M`、最大深度 `H`，绑定、替换和格式化均为 `O(M)` 时间，环境与新树 `O(M)`，递归栈 `O(H)`。测试零参数、空 tuple、primitive mismatch、tuple 长度错、嵌套 generic、generic 绑定整个 tuple、重复绑定一致/冲突、返回未绑定变量、函数多次调用的 env 泄漏、原 AST 未被修改，以及极深类型树改显式栈。`__str__` 还要覆盖无尾逗号和规定空格。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a425b87b-b53c-40ae-9683-57d3e32491ee)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
