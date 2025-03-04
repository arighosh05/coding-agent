class Solution:
    def isMatch(self, text: str, pattern: str) -> bool:
        """
        Determine if the text matches the pattern, which can include
        '.' for any single character and '*' for zero or more of 
        the preceding element.

        Args:
        text (str): The input string to match.
        pattern (str): The pattern against which the string is matched.

        Returns:
        bool: True if the text matches the pattern, False otherwise.
        """
        # dp[i][j] will be True if text[i:] matches pattern[j:]
        dp = [[False] * (len(pattern) + 1) for _ in range(len(text) + 1)]
        dp[len(text)][len(pattern)] = True  # Base case: "" matches ""
        
        # Iterate over the text and pattern in reverse order
        for i in range(len(text), -1, -1):
            for j in range(len(pattern) - 1, -1, -1):
                # Check if current positions match
                first_match = i < len(text) and (pattern[j] in {text[i], '.'})
                
                if j + 1 < len(pattern) and pattern[j + 1] == '*':
                    # If '*' follows, you can either ignore the pattern part or use it
                    dp[i][j] = dp[i][j + 2] or (first_match and dp[i + 1][j])
                else:
                    # Otherwise, proceed if current positions match
                    dp[i][j] = first_match and dp[i + 1][j + 1]
        
        # Return whether the entire string matches the entire pattern
        return dp[0][0]


# Sample unit test cases
import unittest

class TestRegexMatching(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def test_basic(self):
        self.assertTrue(self.solution.isMatch("aa", "a*"))
        self.assertTrue(self.solution.isMatch("ab", ".*"))
        self.assertFalse(self.solution.isMatch("aa", "a"))

    def test_empty_text(self):
        self.assertTrue(self.solution.isMatch("", ".*"))
        self.assertTrue(self.solution.isMatch("", "a*"))
        self.assertFalse(self.solution.isMatch("", "a"))

    def test_empty_pattern(self):
        self.assertFalse(self.solution.isMatch("a", ""))
        self.assertTrue(self.solution.isMatch("", ""))

    def test_complex_patterns(self):
        self.assertFalse(self.solution.isMatch("abc", "a.c"))
        self.assertTrue(self.solution.isMatch("mississippi", "mis*is*p*."))

    def test_edge_cases(self):
        self.assertFalse(self.solution.isMatch("a", "ab*a"))
        self.assertTrue(self.solution.isMatch("aab", "c*a*b"))

# Run tests
if __name__ == "__main__":
    unittest.main()
