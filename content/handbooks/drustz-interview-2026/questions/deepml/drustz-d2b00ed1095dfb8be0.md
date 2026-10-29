---
id: drustz-d2b00ed1095dfb8be0
section: deepml
order: 92
level: A
title: Implement Efficient Sparse Window Attention
quick: Deep-ML 练习 · Implement Efficient Sparse Window Attention
companies: []
tags:
  - DrustZ
  - Deep-ML 练习
  - Deep-ML · ML Coding
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/131_implement-efficient-sparse-window-attention/description.md
    type: primary
---
### description.md

Create a function named sparse_window_attention that computes sparse attention over long sequences by sliding a fixed-radius window across the sequence.

• The parameter window_size represents the radius w of the window.
- For a token at index i, attend only to tokens whose indices are within max(0, i - w) through min(seq_len - 1, i + w), inclusive.
- Tokens near the beginning or end of the sequence simply have smaller windows; no padding is added.

• Inputs
- Q, K, V: NumPy arrays with shapes (seq_len,  $d_k$ ) for Q and K, and (seq_len,  $d_v$ ) for V.
- window_size: integer window radius.
- scale_factor (optional): value used to scale dot-product scores; if None, default to sqrt( $d_k$ ).

• Output
- A NumPy array of shape (seq_len,  $d_v$ ) containing the attention results.


### example.json

```json
{
  "input": "import numpy as np\nQ = np.array([[1.0], [1.0], [1.0]])\nK = np.array([[1.0], [1.0], [1.0]])\nV = np.array([[1.0], [2.0], [3.0]])\nprint(sparse_window_attention(Q, K, V, 1))",
  "output": "[[1.5] [2. ] [2.5]]",
  "reasoning": "The sparse_window_attention function processes each query in the input Q by computing attention scores only with keys in K within a window of size 1 (i.e., the current position and one adjacent position on each side), then applies softmax to these scores to derive weights for the corresponding values in V. For the given input arrays, this results in the output where the first element is the weighted average of V[0] and V[1] (yielding 1.5), the second is the average of all elements in V (yielding 2.0), and the third is the average of V[1] and V[2] (yielding 2.5)."
}
```




### learn.md

## Sparse Window Attention

Sparse window attention is a technique used in sequence processing models to efficiently focus on relevant parts of the data. It limits the model's attention to a local neighborhood around each position, reducing computational demands while maintaining effectiveness for tasks involving long sequences.

### 1. Understanding Attention Mechanisms

Attention mechanisms enable a model to weigh the importance of different elements in a sequence when generating an output. At its core, attention computes a set of weights that indicate how much each element should contribute to the result for a given position. These weights are derived from the similarity between a query representing the current position and keys, which represent other positions. The final output is a combination of values associated with those positions, scaled by the weights.

For instance, imagine reading a sentence: your brain focuses more on nearby words to understand the current word, rather than scanning the entire sentence. Mathematically, this process involves calculating similarities and producing a weighted average of the values.

### 2. The Challenge with Full Attention

In traditional attention, every position in a sequence interacts with every other position, leading to high computational costs. This approach scales poorly for long sequences, as the number of interactions grows quadratically with the sequence length. To address this, sparse attention introduces restrictions, allowing the model to ignore distant or irrelevant positions.

By focusing only on a subset of the sequence, sparse attention maintains accuracy for local dependencies 2014such as in language where words often relate to their immediate neighbors while drastically reducing the resources needed.

### 3. Defining the Window in Sparse Attention

Sparse window attention defines a fixed neighborhood, or "window," around each position. For a given position, the model considers only the elements within a specified radius on either side. This radius, often called the window size, determines how far the attention extends.

For example, if the window size is 2, a position at index 5 would attend to positions 3, 4, 5, 6, and 7 (assuming those exist in the sequence). This sliding window approach ensures that attention is local and efficient, capturing patterns that are typically short-range while discarding long-range interactions that may not be necessary.

The key benefit here is efficiency: by limiting the scope, the overall process avoids examining the entire sequence, much like how a person might skim a text by focusing on paragraphs rather than every line.

### 4. Computing the Attention Scores

Once the window is defined, attention scores are calculated to measure the relevance of each element within that window. These scores are based on the dot product between the query and the keys in the window, which quantifies their similarity.

The formula for the scores is given by:

$$
\text{scores} = \frac{Q K^T}{\sqrt{d_k}}
$$

Here, $Q$ represents the query vector for the current position, $K$ is the matrix of key vectors within the window, and $K^T$ is its transpose. The term $d_k$ denotes the dimensionality of the keys, and dividing by $\sqrt{d_k}$ scales the scores to prevent them from becoming too large, which could destabilize the process.

This equation produces a set of numbers indicating how aligned the query is with each key. A higher score means greater similarity, reflecting a stronger influence on the output.

### 5. Applying the Softmax and Weighted Sum

After obtaining the scores, they are normalized to create probabilities using the softmax function. This step ensures that the weights sum to 1, turning the raw scores into a distribution.

The softmax operation is defined as:

$$
\text{attention weights} = \frac{\exp(\text{scores})}{\sum \exp(\text{scores})}
$$

Each element in the attention weights represents the relative importance of the corresponding key in the window. Finally, the output for the current position is computed as a weighted sum of the values in the window:

$$
\text{output} = \text{attention weights} \cdot V
$$

In this expression, $V$ is the matrix of value vectors within the window. The result is a single vector that combines the values based on their computed importance, effectively summarizing the relevant information from the local context.

### 6. Example Walkthrough

---

Consider a simple sequence of five numbers: [1, 2, 3, 4, 5]. Suppose the window size is 1, meaning each position attends to itself and its immediate neighbors.

For the position of the number 3 (at index 2), the window includes indices 1, 2, and 3 corresponding to the numbers 2, 3, and 4. The model would compute similarities between the query for index 2 and the keys for indices 1, 2, and 3. It then assigns weights to 2, 3, and 4 based on these similarities and produces an output as a weighted combination of these numbers.

This illustrates how sparse window attention efficiently captures local relationships, such as how 3 might relate more to 2 and 4 than to distant numbers like 1 or 5.


### meta.json

```json
{
  "id": "131",
  "title": "Implement Efficient Sparse Window Attention",
  "difficulty": "medium",
  "category": "Machine Learning",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/moe18",
      "name": "Moe"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def sparse_window_attention(Q, K, V, window_size, scale_factor=None):
    """
    Computes sparse attention with a sliding window mask to efficiently handle longer context lengths.
    This implementation uses a loop over the sequence to compute attention only within the specified window,
    reducing memory usage compared to dense attention.

    Args:
        Q (np.ndarray): Query matrix of shape (seq_len, d_k)
        K (np.ndarray): Key matrix of shape (seq_len, d_k)
        V (np.ndarray): Value matrix of shape (seq_len, d_v)
        window_size (int): The radius of the attention window (attends to window_size positions on each side).
        scale_factor (float, optional): Scaling factor for the dot product. If None, uses sqrt(d_k).

    Returns:
        np.ndarray: Attention output of shape (seq_len, d_v)
    """
    seq_len = Q.shape[0]
    d_k = Q.shape[1]
    if scale_factor is None:
        scale_factor = np.sqrt(d_k).astype(float)
    output = np.zeros((seq_len, V.shape[1]), dtype=V.dtype)
    for i in range(seq_len):
        start = max(0, i - window_size)
        end = min(seq_len, i + window_size + 1)
        local_Q = Q[i : i + 1]
        local_K = K[start:end]
        local_V = V[start:end]
        scores = np.dot(local_Q, local_K.T) / scale_factor
        max_score = np.max(scores, axis=1, keepdims=True)
        exp_scores = np.exp(scores - max_score)
        sum_exp = np.sum(exp_scores, axis=1, keepdims=True)
        attention_weights = exp_scores / sum_exp
        output[i] = np.dot(attention_weights, local_V)
    return output
```




### starter_code.py

```python
import numpy as np


def sparse_window_attention(Q, K, V, window_size, scale_factor=None):
    # Your code here
    pass
```




### tests.json

```json
[
  {
    "test": "import numpy as np\nQ = np.array([[1.0], [1.0], [1.0]])\nK = np.array([[1.0], [1.0], [1.0]])\nV = np.array([[1.0], [2.0], [3.0]])\nprint(sparse_window_attention(Q, K, V, 1))",
    "expected_output": "[[1.5], [2.], [2.5]]"
  },
  {
    "test": "import numpy as np\nQ = np.array([[4.0]])\nK = np.array([[4.0]])\nV = np.array([[5.0]])\nprint(sparse_window_attention(Q, K, V, 0))",
    "expected_output": "[[5.]]"
  },
  {
    "test": "import numpy as np\nQ = np.array([[0.0], [1.0], [0.0],[2.0], [0.0], [7.0]])\nK = np.array([[1.0], [2.0], [3.0], [0.0], [6.0], [0.0]])\nV = np.array([[10.0], [20.0], [30.0],[12.0], [23.0], [70.0]])\nprint(sparse_window_attention(Q, K, V, 2))",
    "expected_output": "[[20. ], [25.31123059], [19. ], [23.01651938], [33.75 ], [23. ]]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/131_implement-efficient-sparse-window-attention/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/131_implement-efficient-sparse-window-attention/description.md)。Deep-ML：Educational Use Only License。
