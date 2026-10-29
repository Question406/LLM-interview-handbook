---
id: drustz-b49d9d32adc1e35e01
section: deepml
order: 90
level: A
title: Implement Compressed Row Sparse Matrix (CSR) Format Conversion
quick: Deep-ML 练习 · Implement Compressed Row Sparse Matrix (CSR) Format Conversion
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/65_implement-compressed-row-sparse-matrix-csr-format-/description.md
    type: primary
---
### description.md

## Task: Convert a Dense Matrix to Compressed Row Sparse (CSR) Format

Your task is to implement a function that converts a given dense matrix into the Compressed Row Sparse (CSR) format, an efficient storage representation for sparse matrices. The CSR format only stores non-zero elements and their positions, significantly reducing memory usage for matrices with a large number of zeros.

Write a function `compressed_row_sparse_matrix(dense_matrix)` that takes a 2D list `dense_matrix` as input and returns a tuple containing three lists:

- **Values array**: List of all non-zero elements in row-major order.
- **Column indices array**: Column index for each non-zero element in the values array.
- **Row pointer array**: Cumulative number of non-zero elements per row, indicating the start of each row in the values array.

    


### example.json

```json
{
  "input": "dense_matrix = [\n    [1, 0, 0, 0],\n    [0, 2, 0, 0],\n    [3, 0, 4, 0],\n    [1, 0, 0, 5]\n]\n\nvals, col_idx, row_ptr = compressed_row_sparse_matrix(dense_matrix)\nprint(\"Values array:\", vals)\nprint(\"Column indices array:\", col_idx)\nprint(\"Row pointer array:\", row_ptr)",
  "output": "Values array: [1, 2, 3, 4, 1, 5]\nColumn indices array: [0, 1, 0, 2, 0, 3]\nRow pointer array: [0, 1, 2, 4, 6]",
  "reasoning": "The dense matrix is converted to CSR format with the values array containing non-zero elements, column indices array storing the corresponding column index, and row pointer array indicating the start of each row in the values array."
}
```




### learn.md


## Understanding the Compressed Row Sparse Matrix Format

The Compressed Row Sparse (CSR) format is a data-efficient representation of sparse matrices, where most of the elements are zero. This format is particularly useful in large-scale scientific computing and machine learning applications, where memory efficiency is critical.

### Concepts

A sparse matrix is a matrix that contains a large number of zero elements. Storing such matrices in their full form can be inefficient, both in terms of memory and computational resources. The CSR format addresses this problem by storing only the non-zero elements and their positions in the matrix. In the CSR format, a matrix is represented by three one-dimensional arrays:

- **Values array**: Contains all the non-zero elements of the matrix, stored row by row.
- **Column indices array**: Stores the column index corresponding to each value in the values array.
- **Row pointer array**: Stores the cumulative number of non-zero elements in each row, allowing quick access to each row's data.

### Structure

Given a matrix:

$$
\begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 2 & 0 & 0 \\
3 & 0 & 4 & 0 \\
1 & 0 & 0 & 5 
\end{bmatrix}
$$

The CSR representation would be:

- **Values array**: [1, 2, 3, 4, 1, 5]
- **Column indices array**: [0, 1, 0, 2, 0, 3]
- **Row pointer array**: [0, 1, 2, 4, 6]

### Explanation:

- The **values array** holds the non-zero elements in the matrix, in row-major order.
- The **column indices array** stores the corresponding column index of each non-zero element.
- The **row pointer array** keeps track of where each row starts in the values array. For example, row 1 starts at index 0, row 2 starts at index 1, row 3 starts at index 2, and so on.

### Applications

The CSR format is widely used in high-performance computing applications such as:

- Finite element analysis (FEA)
- Solving large sparse linear systems (e.g., in numerical simulations)
- Machine learning algorithms (e.g., support vector machines with sparse input)
- Graph-based algorithms where adjacency matrices are often sparse

The CSR format improves both memory efficiency and the speed of matrix operations by focusing only on non-zero elements.


### meta.json

```json
{
  "id": "65",
  "title": "Implement Compressed Row Sparse Matrix (CSR) Format Conversion",
  "difficulty": "easy",
  "category": "Linear Algebra",
  "video": "",
  "likes": "0",
  "dislikes": "0",
  "contributor": [
    {
      "profile_link": "https://github.com/paddywardle",
      "name": "paddywardle"
    }
  ]
}
```




### solution.py

```python
import numpy as np


def compressed_row_sparse_matrix(dense_matrix):
    vals = []
    col_idx = []
    row_ptr = [0]

    for row in dense_matrix:
        for j, val in enumerate(row):
            if val != 0:
                vals.append(val)
                col_idx.append(j)
        row_ptr.append(len(vals))

    return vals, col_idx, row_ptr
```




### starter_code.py

```python
import numpy as np


def compressed_row_sparse_matrix(dense_matrix):
    """
    Convert a dense matrix to its Compressed Row Sparse (CSR) representation.

    :param dense_matrix: 2D list representing a dense matrix
    :return: A tuple containing (values array, column indices array, row pointer array)
    """
    pass
```




### tests.json

```json
[
  {
    "test": "dense_matrix = [\n    [1, 0, 0, 0],\n    [0, 2, 0, 0],\n    [3, 0, 4, 0],\n    [1, 0, 0, 5]\n]\nvals, col_idx, row_ptr = compressed_row_sparse_matrix(dense_matrix)\nprint(\"Values array:\", vals)\nprint(\"Column indices array:\", col_idx)\nprint(\"Row pointer array:\", row_ptr)",
    "expected_output": "Values array: [1, 2, 3, 4, 1, 5]\nColumn indices array: [0, 1, 0, 2, 0, 3]\nRow pointer array: [0, 1, 2, 4, 6]"
  },
  {
    "test": "dense_matrix = [\n    [0, 0, 0],\n    [1, 2, 0],\n    [0, 3, 4]\n]\nvals, col_idx, row_ptr = compressed_row_sparse_matrix(dense_matrix)\nprint(\"Values array:\", vals)\nprint(\"Column indices array:\", col_idx)\nprint(\"Row pointer array:\", row_ptr)",
    "expected_output": "Values array: [1, 2, 3, 4]\nColumn indices array: [0, 1, 1, 2]\nRow pointer array: [0, 0, 2, 4]"
  },
  {
    "test": "dense_matrix = [\n    [0, 0, 3, 0, 0],\n    [0, 4, 0, 0, 0],\n    [5, 0, 0, 6, 0],\n    [0, 0, 0, 0, 0],\n    [0, 7, 0, 0, 8]\n]\nvals, col_idx, row_ptr = compressed_row_sparse_matrix(dense_matrix)\nprint(\"Values array:\", vals)\nprint(\"Column indices array:\", col_idx)\nprint(\"Row pointer array:\", row_ptr)",
    "expected_output": "Values array: [3, 4, 5, 6, 7, 8]\nColumn indices array: [2, 1, 0, 3, 1, 4]\nRow pointer array: [0, 1, 2, 4, 4, 6]"
  }
]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/deepml-problems/questions/65_implement-compressed-row-sparse-matrix-csr-format-/description.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/deepml-problems/questions/65_implement-compressed-row-sparse-matrix-csr-format-/description.md)。Deep-ML：Educational Use Only License。
