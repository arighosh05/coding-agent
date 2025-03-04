from abc import ABC, abstractmethod


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, array, target):
        pass


class BinarySearch(SearchStrategy):
    @staticmethod
    def binary_search(array, target):
        """
        Performs binary search on a sorted array to find a target element.
        
        Args:
            array (list): A sorted list of comparable elements
            target: The element to find in the array
            
        Returns:
            int: The index of the target element if found, otherwise -1
        
        Raises:
            TypeError: If the array or target is None, or if elements are non-comparable.
            ValueError: If the input array is not sorted.

        Example:
            >>> BinarySearch.binary_search([1, 3, 5, 7, 9], 5)
            2
        
        Time Complexity: O(log n)
        Space Complexity: O(1)
        """
        # Input validation
        if array is None or target is None:
            raise TypeError("The array and target must be non-None.")
        if not isinstance(array, list):
            raise TypeError("The array must be a list.")

        # Check that array is sorted
        if any(array[i] > array[i + 1] for i in range(len(array) - 1)):
            raise ValueError("The input array must be sorted in non-decreasing order.")

        left, right = 0, len(array) - 1

        while left <= right:
            mid = (left + right) // 2  # Midpoint calculation for clarity

            try:
                if array[mid] == target:
                    return mid
                elif array[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1
            except TypeError:
                raise TypeError("Array elements must be comparable with the target.")

        return -1


# Example usage
if __name__ == "__main__":
    sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    
    # Find existing element
    assert BinarySearch.binary_search(sorted_array, 11) == 5
    
    # Edge cases
    assert BinarySearch.binary_search(sorted_array, 1) == 0  # First element
    assert BinarySearch.binary_search(sorted_array, 19) == 9  # Last element
    assert BinarySearch.binary_search(sorted_array, 0) == -1  # Element smaller than all elements
    assert BinarySearch.binary_search(sorted_array, 20) == -1  # Element larger than all elements
    assert BinarySearch.binary_search([], 1) == -1  # Empty array

    try:
        BinarySearch.binary_search(None, 1)
    except TypeError as e:
        assert str(e) == "The array and target must be non-None."

    try:
        BinarySearch.binary_search("not_a_list", 1)
    except TypeError as e:
        assert str(e) == "The array must be a list."
    
    try:
        BinarySearch.binary_search([3, 2, 1], 1)
    except ValueError as e:
        assert str(e) == "The input array must be sorted in non-decreasing order."
    
    # Non-comparable elements test
    try:
        BinarySearch.binary_search([1, 2, 'a', 3], 2)
    except TypeError as e:
        assert str(e) == "Array elements must be comparable with the target."

    print("All tests passed!")
