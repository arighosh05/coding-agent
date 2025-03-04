from typing import List, Optional

def binary_search(array: List[int], target: int) -> Optional[int]:
    """
    Performs binary search on a sorted array to find a target element.

    Args:
        array (List[int]): A sorted list of integers.
        target (int): The element to find in the array.

    Returns:
        Optional[int]: The index of the target element if found, otherwise None.

    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    left, right = 0, len(array) - 1

    while left <= right:
        mid = left + (right - left) // 2  # Using integer division for clarity

        if array[mid] == target:
            return mid
        elif array[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return None  # More Pythonic than returning -1


# Example usage and tests
if __name__ == "__main__":
    sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    # Find existing element
    assert binary_search(sorted_array, 11) == 5

    # Edge cases
    assert binary_search(sorted_array, 1) == 0  # First element
    assert binary_search(sorted_array, 19) == 9  # Last element
    assert binary_search(sorted_array, 0) is None  # Element smaller than all elements
    assert binary_search(sorted_array, 20) is None  # Element larger than all elements
    assert binary_search([], 1) is None  # Empty array

    print("All tests passed!")
