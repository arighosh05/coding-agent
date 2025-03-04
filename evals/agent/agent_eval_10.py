class Solution:
    def grayCode(self, n):
        """
        Generates an n-bit Gray code sequence.
        
        Args:
            n (int): The number of bits in the Gray code.
            
        Returns:
            List[int]: A list representing the n-bit Gray code sequence.
            
        Raises:
            ValueError: If n is not a non-negative integer.
        """
        # Input validation to ensure n is a non-negative integer
        if not isinstance(n, int) or n < 0:
            raise ValueError("Input must be a non-negative integer.")
        
        # Gray code sequence generation using the iterative approach
        result = []
        for i in range(1 << n):  # Iterate from 0 to 2^n - 1
            # Using the formula i ^ (i >> 1) to generate the Gray code
            gray_code = i ^ (i >> 1)
            result.append(gray_code)
            # Each gray_code is the result after bit manipulation

        return result

# The iterative approach is beneficial, especially for larger values of n, reducing the risk of stack overflow
# by avoiding the depth of recursive calls.
