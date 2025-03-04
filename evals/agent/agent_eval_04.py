from typing import Callable, List

def sum_of_even_numbers(numbers: List[int]) -> int:
    """
    Calculate the sum of even numbers in a list of integers.

    Args:
        numbers: A list of integers.

    Returns:
        Sum of even integers in the list.
    
    Raises:
        TypeError: If the input is not a list.
    """
    if not isinstance(numbers, list):
        raise TypeError("Input should be a list.")
    
    # Using a generator expression to filter even numbers for memory efficiency
    return sum(num for num in numbers if isinstance(num, int) and num % 2 == 0)

def process_data(
    data: List[int],
    filter_func: Callable[[int], bool],
    agg_func: Callable[[int, int], int],
    init_val: int,
) -> int:
    """
    Processes a list of data using provided filter and aggregation functions.

    Args:
        data: A list of integers.
        filter_func: A function that determines whether an integer should be included.
        agg_func: A function that aggregates the filtered integers.
        init_val: The initial value for aggregation.
    
    Returns:
        The result of aggregating filtered data.
    """
    filtered_data = (num for num in data if filter_func(num))
    return agg_func(filtered_data, init_val)

if __name__ == "__main__":
    data = [1, 2, 3, 4, 5, 6]
    print(sum_of_even_numbers(data))
