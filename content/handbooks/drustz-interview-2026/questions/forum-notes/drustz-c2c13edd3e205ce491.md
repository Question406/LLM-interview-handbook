---
id: drustz-c2c13edd3e205ce491
section: forum-notes
order: 284
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Counting Backward'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Counting Backward'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Part 2: Counting Backward

Update your class (or make a new one) to support **reverse iteration**.

### Requirements

- Start with an IPv4 address.
- Count backwards (decrease the IP address).
- Stop after `0.0.0.0` (raise `StopIteration`).
- Use a flag or parameter to choose the direction.

### Example Usage

```python
ip = IPV4Iterator("0.0.0.5", reverse=True)
for i in ip:
    print(i)

# Output:
# 0.0.0.5
# 0.0.0.4
# 0.0.0.3
# 0.0.0.2
# 0.0.0.1
# 0.0.0.0
```



### Solution Approach

You can change the logic to handle a `reverse` flag:

```python
class IPV4Iterator:
    def __init__(self, start_ip: str, reverse: bool = False):
        self.current = self._ip_to_int(start_ip)
        self.reverse = reverse
        self.max_ip = (256**4) - 1  # 255.255.255.255
        self.min_ip = 0  # 0.0.0.0

    def __iter__(self):
        return self

    def __next__(self):
        if self.reverse:
            if self.current < self.min_ip:
                raise StopIteration
            result = self._int_to_ip(self.current)
            self.current -= 1
        else:
            if self.current > self.max_ip:
                raise StopIteration
            result = self._int_to_ip(self.current)
            self.current += 1

        return result

    # ... helper methods same as Part 1
```



### Tricky Cases

- Starting from `0.0.0.0` in reverse (should stop immediately).
- Starting from the max IP in reverse.
- Handling number underflow (like `192.168.1.0` becoming `192.168.0.255`).

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
