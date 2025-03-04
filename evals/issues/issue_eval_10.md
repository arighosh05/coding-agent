### code

```
class Solution:
    def __init__(self):
        self.nextNum = 0

    def grayCode(self, n):
        self.result = []
        self.grayCodeHelper(n)
        return self.result

    def grayCodeHelper(self, n):
        if n == 0:
            self.result.append(self.nextNum)
            return
        self.grayCodeHelper(n - 1)
        # Flip the bit at (n - 1)th position from right
        self.nextNum = self.nextNum ^ (1 << (n - 1))
        self.grayCodeHelper(n - 1)
```

### context

```
An n-bit gray code sequence is a sequence of 2n integers where:

Every integer is in the inclusive range [0, 2n - 1],
The first integer is 0,
An integer appears no more than once in the sequence,
The binary representation of every pair of adjacent integers differs by exactly one bit, and
The binary representation of the first and last integers differs by exactly one bit.

Given an integer n, the code returns any valid n-bit gray code sequence.
```
