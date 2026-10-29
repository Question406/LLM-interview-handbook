---
id: drustz-630fdde7a0cf8ce952
section: anthropic
order: 62
level: A
title: File Deduplication (find duplicate files)
quick: >-
  original-structured-preparation-guide · File Deduplication (find duplicate
  files)
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
      https://www.1point3acres.com/interview/problems/42afe615-f6b2-494c-807f-37c309841f8b
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# File Deduplication：基础可运行版本

## 题目与接口

输入一个文件夹，访问它及所有子目录中的普通文件，把二进制内容一致的路径分组；唯一文件不输出，也不需要实际删除。

```python
def find_duplicate_files(root_path: str) -> list[list[str]]: ...
```



若 `docs/a.txt` 与 `backup/a.txt` 都是 `hello`，而 `b.txt` 是 `world`，应返回前两个路径组成的一组。面试环境可能要求自己创建临时目录和测试文件。

## 直接解法

用 `os.walk(root_path)` 递归枚举；每个文件以 `rb` 打开，循环读取固定大小块并更新 SHA-256，然后加入 `digest -> paths`。最后过滤长度小于 2 的桶并排序。为防极小概率 hash 碰撞，可把 `(size,digest)` 当候选键，再对同桶文件逐块比较；读取失败应记录或上报，不能当作空文件。

一个清楚的测试顺序是：先验证遍历器确实发现嵌套文件，再验证相同内容进入同一桶，最后验证唯一文件被过滤。这样若输出不对，可以立刻区分是漏遍历、读取方式错误，还是分组逻辑错误，而不必在一个大函数里排查。

## 复杂度与边界

设文件数为 `N`、总字节数为 `S`，完整扫描时间 `O(N+S)`，路径索引 `O(N)`，缓冲区 `O(B)`。测试应覆盖嵌套目录、两个空文件、二进制内容、无权限文件、断开的链接和空目录。默认不跟随目录 symlink 可避免环；若扫描时文件被修改，可比较读取前后的 size/mtime 并重试。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/42afe615-f6b2-494c-807f-37c309841f8b)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
