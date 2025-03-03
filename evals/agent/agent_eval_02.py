from abc import ABC, abstractmethod
from collections import deque

# Abstract class defining a Strategy interface for different data structure operations.
class DataStructureStrategy(ABC):
    @abstractmethod
    def insert(self, elem):
        """Inserts an element according to the specific strategy."""
        pass

# Deque-based implementation of the strategy that allows efficient O(1) insertion at the start.
class DequeStrategy(DataStructureStrategy):
    def __init__(self):
        self.data = deque()  # Initialize an empty deque.

    def insert(self, elem):
        self.data.appendleft(elem)  # Insert element at the beginning.

# Context class that uses a strategy to handle data insertions.
class DataHandler:
    def __init__(self, strategy: DataStructureStrategy):
        self.strategy = strategy

    def insert_elements(self, n):
        """Insert elements from 0 to n-1 using the current strategy."""
        for i in range(n):
            self.strategy.insert(i)

# Usage example
handler = DataHandler(DequeStrategy())
handler.insert_elements(10000)  # Efficiently inserts 10,000 elements using DequeStrategy.
