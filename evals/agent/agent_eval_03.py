import concurrent.futures
import logging
from functools import partial

# Configure logging for better debugging and error tracking
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def process(number):
    """
    Process a given number by performing some computation or transformation.
    The sample processing here squares the input number.

    :param number: Integer, expected to be an element from the dataset.
    :return: The result of processing the input number, typically another integer.
    """
    try:
        # Basic processing operation (can be replaced with more complex logic)
        result = number ** 2
        logging.debug(f"Processed number {number} to {result}.")
        return result
    except Exception as e:
        # Error handling to ensure the function doesn't fail silently
        logging.error(f"Error processing number {number}: {e}")

def get_large_dataset():
    """
    Generate a large dataset consisting of a range of numbers.
    
    :return: A generator over a range of numbers up to 1,000,000 to save memory.
    """
    return (i for i in range(1000000))

def main():
    """
    Main function to handle the processing of a large dataset using parallel execution.
    """
    dataset = get_large_dataset()

    # Use ThreadPoolExecutor for lighter tasks or ProcessPoolExecutor for CPU-bound tasks
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Mapping process to each item in the dataset concurrently
        # Using a list to consume the generator and trigger processing
        list(executor.map(process, dataset))

    logging.info("Completed processing of the large dataset.")

if __name__ == "__main__":
    main()
