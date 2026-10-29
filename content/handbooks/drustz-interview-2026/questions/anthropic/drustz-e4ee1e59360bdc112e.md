---
id: drustz-e4ee1e59360bdc112e
section: anthropic
order: 3
level: A
title: Coding Q6 Tokenizer
quick: locally-saved-topic-editorial · Coding Q6 Tokenizer
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
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
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q6-tokenizer
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Tokenize (Python)

## Part 1: Understanding the Code

You are given two functions: `tokenize` and `detokenize`. Your goal is to:

- **Read the code** and understand what it does.
- **Find the bugs** or logic errors in the tokenization process.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
    return tokens


def detokenize(tokens, vocab: dict):
    text = ""
    reversed_vocab = {value: key for key, value in vocab.items()}
    for token in tokens:
        text += reversed_vocab[token]
    return text
```



**Example:**

```python
vocab = {"a": 1, "b": 2, "cd": 3}

tokens = tokenize("acdebe", vocab)
result = detokenize(tokens, vocab)
```



### Your Task

- **Explain** how this code works to your interviewer.
- **Identify** the problems with this logic.
- **Explain** when this code will fail.

### Questions to Ask Yourself

- How does the code choose which token to pick?
- What happens if the text has a letter that is NOT in the `vocab`?
- What happens to the `key` variable if it never finds a match?
- Does this code pick the best match, or just the first one it sees?

## Part 2: Reviewing a Proposed Fix

Another engineer tried to fix the code. They added a new rule for "unknown" items. Review their code below.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""

    # NEW: Check if there is leftover text at the end
    if key:
        tokens.append(vocab.get("UNK", -1))

    return tokens


vocab = {
    "a": 1,
    "b": 2,
    "cd": 3,
    "UNK": -1,  # NEW: Added UNK (Unknown) token
}
```



**Changes made:**

- Logic added after the loop to check if `key` is empty.
- Added `"UNK": -1` to the dictionary.

### Your Task

Act like a code reviewer. Give feedback, ask questions, and point out concerns.

### Points to Consider

- What is `UNK` used for?
- Does this change actually fix the main problem?
- What happens if the unknown character is in the **middle** of the text, not the end?
- Think about edge cases:

Input text is `"xabc"` (starts with an unknown letter).
- Input text contains the word `"UNK"`.
- Does the logic always find the correct tokens?

## Part 3: Writing a Better Solution

Now, write your own version of the `tokenize` function. It needs to handle characters correctly even if they are not in the vocabulary.

### Requirements

- **Handle unknown characters:** Do not crash if a character is missing from the `vocab`.
- **Stay correct:** Ensure `tokenize` and `detokenize` logic holds up.
- **Use the UNK token:** Replace missing characters with `UNK: -1`.
- **Know the limits:** If the original text actually says "UNK", you won't be able to tell the difference between that and a real unknown character later. This is a known limitation.

### Key Challenges

- When should you stop adding letters to the `key`?
- How do you know if the current string you are building will **never** match a real token?
- Should you check if any word in the `vocab` starts with your current `key`?

### Helpful Context

- **Tokenization:** Breaking text into small chunks (tokens) and giving them numbers (IDs).
- **UNK:** Short for "UNKNOWN". It is a placeholder for data the model hasn't seen before.
- **Greedy Matching:** Taking the first match you find immediately. The original code does this.
- **Prefix Check:** You might need to check if your current string is the start (prefix) of any valid key. If it isn't, you know you won't find a match.

### Example Solution Approach

One way to solve this is to "look ahead." Check if the current `key` could possibly become a match later. If not, treat it as unknown.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
        else:
            # Check: Does any key in vocab start with this string?
            if not any(k.startswith(key) for k in vocab.keys()):
                # No match is possible. Mark as UNK.
                tokens.append(vocab.get("UNK", -1))
                key = ""

    # Handle any leftover text
    if key:
        tokens.append(vocab.get("UNK", -1))

    return tokens
```



This is just one way to do it. Be ready to discuss why this works or if there is a better way.

## Part 4: Follow-Up Questions

Be ready to talk about these topics during the interview:

### 1. Tokenization Strategies

**Question:** What are the different ways to tokenize text? What are the pros and cons?

**Simple Explanation:**

- **Character-level:** Every letter is a token.

*Pro:* Small vocabulary.
- *Con:* Produces very long lists of tokens.
- **Word-level:** Every word is a token.

*Pro:* Easy to understand.
- *Con:* Huge vocabulary; struggles with new words.
- **Subword (BPE, WordPiece):** Breaks words into meaningful chunks (like "ing" or "ed"). This is the standard for modern AI.
- **Byte-level:** Uses raw bytes (UTF-8). No need for `UNK` tokens.

### 2. Algorithm Complexity

**Question:** How fast is your code? Can you make it faster?

**Simple Explanation:**

- **Current speed:** $O(n \times m \times k)$.

$n$ = length of text.
- $m$ = average length of a vocab word.
- $k$ = total number of words in vocab.
- **The Slow Part:** The line `any(k.startswith(key)...)` loops through the whole dictionary every time. This is slow.
- **The Fix:** Use a **Trie** (Prefix Tree). This makes lookups much faster, reducing complexity to $O(n \times m)$.

### 3. Ambiguity and Optimal Tokenization

**Question:** The "greedy" approach (taking the first match) isn't always best. Can you prove it?

**Simple Explanation:**

- Imagine your vocab is `{"ab": 1, "abc": 2, "c": 3}`.
- Your text is `"abc"`.
- **Greedy:** Sees "ab", matches it. Then sees "c", matches it. Result: 2 tokens (`ab`, `c`).
- **Optimal:** Sees "abc", matches it immediately. Result: 1 token (`abc`).
- **Solution:** To find the best path, you would use **Dynamic Programming** or the **Viterbi algorithm**. However, this is slower than the greedy method.

### 4. Handling UNK in Real Systems

**Question:** How do big apps (like ChatGPT or Google Translate) handle unknown words?

**Simple Explanation:**

- **Subwords:** They break the unknown word down. If "microscope" is unknown, they might break it into "micro" and "scope".
- **Character Fallback:** If a word is totally new, they might spell it out letter by letter.
- **Training:** Having too many `UNK` tokens makes the model dumb. Engineers try very hard to avoid them by using better tokenization (like BPE).

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100003*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q6-tokenizer)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
