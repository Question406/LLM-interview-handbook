---
id: drustz-cb7aa2ec33e9521c60
section: forum-notes
order: 283
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Counting Forward'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Counting Forward'
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
## Part 1: Counting Forward

Create a class called `IPV4Iterator`. It must have `__init__` and `__next__` methods to loop through IPv4 addresses starting from a specific IP.

### Problem Requirements

- Start with an IPv4 address string (like `"255.255.255.250"`).
- Use the Python iterator protocol (`__iter__` and `__next__`).
- Count up from the starting IP until you reach `255.255.255.255`.
- Raise `StopIteration` when you go past the last valid IP.

### Example Usage

```python
ip = IPV4Iterator("255.255.255.250")
for i in ip:
    print(i)

# Output:
# 255.255.255.250
# 255.255.255.251
# 255.255.255.252
# 255.255.255.253
# 255.255.255.254
# 255.255.255.255
```



### Tricky Cases

- Starting from `0.0.0.0`.
- Starting from `255.255.255.255` (should stop immediately).
- Handling numbers that roll over (like `192.168.0.255` becoming `192.168.1.0`).
- Invalid input (optional).

### Solution Code

```python
class IPV4Iterator:
    def __init__(self, start_ip: str):
        self.current = self._ip_to_int(start_ip)
        self.max_ip = (256**4) - 1  # This is 255.255.255.255 as an integer

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.max_ip:
            raise StopIteration

        result = self._int_to_ip(self.current)
        self.current += 1
        return result

    def _ip_to_int(self, ip: str) -> int:
        """Convert IP string to 32-bit integer"""
        octets = [int(octet) for octet in ip.split('.')]
        return (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]

    def _int_to_ip(self, num: int) -> str:
        """Convert 32-bit integer to IP string"""
        return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
