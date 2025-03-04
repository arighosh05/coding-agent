def efficient_sort(arr):
    """
    Sorts an array of numbers in ascending order, removing any duplicates.
    
    Parameters:
    arr (list): A list of numbers to be sorted.

    Returns:
    list: A sorted list with duplicates removed.

    Raises:
    ValueError: If the input is not a list of numbers.
    """
    
    # Ensure the input is a list and contains only numeric elements
    if not isinstance(arr, list):
        raise ValueError("Input must be a list.")
    
    # Remove any None values from the list
    arr = [x for x in arr if x is not None]

    # Ensure all elements are numbers
    if not all(isinstance(x, (int, float)) for x in arr):
        raise ValueError("All elements must be numbers.")
    
    # Use set to remove duplicates and then sort the result
    unique_sorted_arr = sorted(set(arr))
    
    return unique_sorted_arr

# Example usage:
# sorted_numbers = efficient_sort([3, 1, 2, 3, 4, None, 2])
# print(sorted_numbers)  # Output: [1, 2, 3, 4]
