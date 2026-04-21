---
title: "Merge Sort"
slug: "merge-sort"
tags: ["algorithms", "sorting", "computer-science", "divide-and-conquer"]
summary: "Merge sort is a stable O(n log n) divide-and-conquer sorting algorithm that splits arrays, sorts halves, then merges."
related: ["binary-search"]
updated: "2024-03-01"
---

# Merge Sort

Merge sort divides an array into halves, recursively sorts each half, then merges the sorted halves — achieving $O(n \log n)$ in all cases.

## Merge Sort Complexity Analysis

| Case    | Time          | Space   |
|---------|---------------|---------|
| Best    | $O(n \log n)$ | $O(n)$  |
| Average | $O(n \log n)$ | $O(n)$  |
| Worst   | $O(n \log n)$ | $O(n)$  |

Merge sort is **stable** — equal elements retain their original relative order.

## Merge Sort Implementation

```python
def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### Merge Sort vs Quick Sort

Merge sort guarantees $O(n \log n)$ worst case; quick sort degrades to $O(n^2)$ on sorted input without pivoting tricks. Prefer merge sort when stability or predictable performance is required.
