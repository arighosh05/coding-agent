def sum_even_numbers(numbers: list[int]) -> int:
    """
    Returns the sum of all even numbers in the given list.

    :param numbers: List of integers
    :return: Sum of even integers
    """
    return sum(i for i in numbers if i % 2 == 0)

# Example usage
data = [1, 2, 3, 4, 5, 6]
print(sum_even_numbers(data))
