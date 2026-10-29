---
id: drustz-0aa0235bb7a921df43
section: forum-notes
order: 212
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Followers & Following Lists'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Followers & Following Lists'
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
## Part 2: Followers & Following Lists

### New Requirement: Get Lists

The interviewer now asks: "Update the snapshot class so we can see the full list of followers."

Add these methods:

```python
class Snapshot:
    # ... (Part 1 methods) ...

    def get_following(self, user_id: str) -> list[str]:
        """
        Get a list of people that `user_id` follows.
        """
        pass

    def get_followers(self, user_id: str) -> list[str]:
        """
        Get a list of people who follow `user_id`.
        """
        pass
```



### Example Usage

```python
network = SocialNetwork()

# Setup users and follows...
network.add_user("A")
network.add_user("B")
network.add_user("C")
network.add_user("D")

network.follow("A", "B")
network.follow("A", "C")
network.follow("B", "C")
network.follow("D", "A")

snapshot = network.create_snapshot()

print(snapshot.get_following("A"))  # ["B", "C"]
print(snapshot.get_followers("C"))  # ["A", "B"]
```



### Solution for Part 2

```python
class Snapshot:
    def __init__(self, follows: dict[str, set[str]]):
        self._follows = {user: set(followees) for user, followees in follows.items()}
        # Build reverse index for efficient follower lookups
        self._followers = {}
        for user, followees in self._follows.items():
            for followee in followees:
                if followee not in self._followers:
                    self._followers[followee] = set()
                self._followers[followee].add(user)

    def is_following(self, follower: str, followee: str) -> bool:
        return followee in self._follows.get(follower, set())

    def get_following(self, user_id: str) -> list[str]:
        return list(self._follows.get(user_id, set()))

    def get_followers(self, user_id: str) -> list[str]:
        return list(self._followers.get(user_id, set()))
```



**Time and Space Complexity:**

| Method | Time | Space |
| --- | --- | --- |
| `Snapshot.__init__` | O(U + E) | O(U + E) |
| `get_following` | O(F) | O(F) |
| `get_followers` | O(F) | O(F) |

Here, F is the number of friends found.

**Design Choice:** We build a reverse list (`_followers`) immediately when we create the snapshot. This uses more memory O(E), but it makes `get_followers` very fast O(F). This is a good trade-off because we create the snapshot once, but we might read from it many times.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
