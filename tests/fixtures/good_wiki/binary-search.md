---
title: "Binary Search"
slug: "binary-search"
tags: ["algorithms", "searching", "computer-science"]
summary: "Binary search finds a target in a sorted array in O(log n) time by halving the search space each step."
related: ["hash-table", "merge-sort"]
updated: "2024-01-15"
---

# Binary Search

Binary search is a divide-and-conquer algorithm that locates a target value in a **sorted** array by repeatedly halving the search space.

## Binary Search Algorithm Steps

1. Set `low = 0`, `high = len(array) - 1`.
2. While `low <= high`: compute `mid = (low + high) // 2`.
3. If `array[mid] == target`, return `mid`.
4. If `array[mid] < target`, set `low = mid + 1`.
5. If `array[mid] > target`, set `high = mid - 1`.
6. Return -1 if not found.

## Binary Search Time Complexity

- **Best case:** $O(1)$ — target at midpoint.
- **Average/Worst case:** $O(\log n)$ — halving each iteration.
- **Space:** $O(1)$ iterative, $O(\log n)$ recursive.

### Binary Search Iterative vs Recursive

The iterative form avoids call-stack overhead; use it in production. The recursive form is cleaner for teaching.

```python
def binary_search(arr: list[int], target: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
