from collections import deque

numbers = deque()
for i in range(10000):
    numbers.appendleft(i)  # O(1) insert operation
