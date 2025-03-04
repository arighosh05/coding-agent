### code

```
def binary_search(array, target):
    """
    Performs binary search on a sorted array to find a target element.
    
    Args:
        array: A sorted list of comparable elements
        target: The element to find in the array
        
    Returns:
        int: The index of the target element if found, otherwise -1
        
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    left, right = 0, len(array) - 1
    
    while left <= right:
        # Use bitwise shift to avoid potential overflow in large arrays
        # and it's computationally more efficient than division
        mid = left + ((right - left) >> 1)
        
        if array[mid] == target:
            return mid
        elif array[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1


# Example usage
if __name__ == "__main__":
    sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    
    # Find existing element
    assert binary_search(sorted_array, 11) == 5
    
    # Edge cases
    assert binary_search(sorted_array, 1) == 0  # First element
    assert binary_search(sorted_array, 19) == 9  # Last element
    assert binary_search(sorted_array, 0) == -1  # Element smaller than all elements
    assert binary_search(sorted_array, 20) == -1  # Element larger than all elements
    assert binary_search([], 1) == -1  # Empty array
    
    print("All tests passed!")
```

### context

```
a python script that implements binary search algorithm
```
