---
id: drustz-fc0b3bfb1bf763449e
section: forum-notes
order: 344
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Basic Store Implementation'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Basic Store Implementation'
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
## Part 1: Basic Store Implementation

### Tools You Are Given

The interviewer gives you this mock code interface:

```python
class FileSystem:
    def save_blob(self, data: bytes) -> None:
        """Save bytes to the file system"""
        pass

    def get_blob(self) -> bytes:
        """Get bytes back from the file system"""
        pass


# Helper functions provided to you
def serialize_int(value: int) -> bytes:
    """Turn an integer into bytes"""
    pass


def deserialize_int(data: bytes) -> int:
    """Turn bytes back into an integer"""
    pass


def serialize_str(value: str) -> bytes:
    """Turn a string into bytes"""
    pass


def deserialize_str(data: bytes) -> str:
    """Turn bytes back into a string"""
    pass
```



### What You Need to Write

You need to write a `KVStore` class with these methods:

```python
class KVStore:
    def __init__(self, file_system: FileSystem):
        """Start with a file system instance"""
        pass

    def put(self, key: str, value: str) -> None:
        """Save a key-value pair in memory"""
        pass

    def get(self, key: str) -> str:
        """Find a value using a key"""
        pass

    def shutdown(self) -> None:
        """Turn the whole store into bytes and save it"""
        pass

    def restore(self) -> None:
        """Load bytes from the file and rebuild the store"""
        pass
```



### How It Should Work

```python
fs = FileSystem()
kv_store = KVStore(fs)

# Save some data
kv_store.put("name", "John:Doe")
kv_store.put("city", "New,York")
kv_store.put("key\nwith\nnewlines", "value=with=equals")

# Save to file system
kv_store.shutdown()

# Make a new instance and load data back
new_kv_store = KVStore(fs)
new_kv_store.restore()

# The data should be exactly the same
assert new_kv_store.get("name") == "John:Doe"
assert new_kv_store.get("city") == "New,York"
assert new_kv_store.get("key\nwith\nnewlines") == "value=with=equals"
```



### Hard Parts to Watch Out For

- **Delimiter Conflicts**: If you separate data with symbols like `:` or `,`, it breaks if your data also contains those symbols.

Example: If you save "key:value", but the key is "time:now", the computer gets confused.
- **Escaping is Hard**: Using backslashes (like `\:`) is messy to code and easy to break.
- **Any Content Allowed**: Keys and values might have:

Symbols (`:`, `,`, `=`)
- New lines (`\n`)
- Quotes
- Null bytes

### The Best Solution: Length-Prefixed Encoding

The safest way to solve this is **length-prefixed encoding**. This means you write the **length** of the data before the data itself.

**The Concept**: `<length>:<data>`

**Examples**:

- String `"a:b"` (3 letters) → `3:a:b`
- String `"hello"` (5 letters) → `5:hello`
**For Key-Value Pairs**: `<keyLen>:<key><valueLen>:<value>`

**Example**:

- `{"ab": "xyz"}` → `2:ab3:xyz`
- `{"key:1": "val=ue"}` → `5:key:16:val=ue`
**Note**: The examples above use text (like "5:") to explain the idea. In your real code, `serialize_int()` will likely create **binary bytes** (like 4 bytes of raw data). It won't look like human-readable text numbers.

Why this is good:

- You know exactly how many bytes to read next.
- You don't need to scan for special characters or use escape codes.
- Real systems like Redis use this logic.

### Edge Cases to Test

- Empty dictionary
- Empty strings for keys or values
- Keys/values with symbols (`:`, `,`, `=`)
- Keys/values with new lines
- Unicode characters (emojis, foreign languages)
- Very long strings
- Saving and loading multiple times

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
