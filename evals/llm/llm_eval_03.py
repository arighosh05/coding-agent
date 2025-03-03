from concurrent.futures import ThreadPoolExecutor

def process(number):
    """Dummy processing function for demonstration."""
    pass  # Replace with actual processing logic

def process_large_dataset():
    """Efficiently processes a large dataset using multi-threading."""
    dataset = range(1000000)  # Efficient iterator

    with ThreadPoolExecutor() as executor:
        executor.map(process, dataset)

if __name__ == "__main__":
    process_large_dataset()
