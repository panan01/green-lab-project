"""
This is a pure Python implementation of the merge sort algorithm.

For doctests run following command:
python -m doctest -v merge_sort.py
or
python3 -m doctest -v merge_sort.py

For manual testing run:
python merge_sort.py --size small
python merge_sort.py --size large
"""
import random
import argparse


def merge_sort(collection: list) -> list:
    """
    Sorts a list using the merge sort algorithm.

    :param collection: A mutable ordered collection with comparable items.
    :return: The same collection ordered in ascending order.

    Time Complexity: O(n log n)
    Space Complexity: O(n)

    Examples:
    >>> merge_sort([0, 5, 3, 2, 2])
    [0, 2, 2, 3, 5]
    >>> merge_sort([])
    []
    >>> merge_sort([-2, -5, -45])
    [-45, -5, -2]
    >>> merge_sort([5, 4, 3, 2, 1])
    [1, 2, 3, 4, 5]
    >>> merge_sort([1, 2, 3, 4, 5])
    [1, 2, 3, 4, 5]
    """

    def merge(left: list, right: list) -> list:
        """
        Merge two sorted lists into a single sorted list.

        :param left: Left collection
        :param right: Right collection
        :return: Merged result
        """
        result = []
        i, j = 0, 0
        
        # G3: Store loop end conditions in variables to avoid re-evaluating len()
        # This is part of a larger G3 optimization to avoid list.pop(0)
        # by using indices, which is a significant performance improvement.
        left_len, right_len = len(left), len(right)
        
        while i < left_len and j < right_len:
            # G1: Assign list elements to variables to avoid multiple lookups.
            left_val = left[i]
            right_val = right[j]
            
            if left_val <= right_val:
                result.append(left_val)
                i += 1
            else:
                result.append(right_val)
                j += 1
        
        # Extend the result with the remaining elements from either list.
        # Slicing is efficient for capturing the rest of the list.
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    if len(collection) <= 1:
        return collection
        
    mid_index = len(collection) // 2
    left_half = merge_sort(collection[:mid_index])
    right_half = merge_sort(collection[mid_index:])

    # G2: Avoid redundant merge operation if the collection is already sorted.
    # If the last element of the left half is already less than or equal to
    # the first element of the right half, the halves are already in order.
    if left_half and right_half and left_half[-1] <= right_half[0]:
        return left_half + right_half

    return merge(left_half, right_half)


def main(size: str) -> None:
    """
    Generates a list of a specified size, sorts it using merge sort,
    and prints a confirmation message.

    :param size: A string, either 'small' or 'large', determining the list size.
    """
    print(f"Selected data size: '{size}'")

    # Define the scale for small and large tests
    # 为小规模和大规模测试定义数据量
    size_mapping = {
        "small": 10_000,    # 1万个元素
        "large": 2_000_000  # 200万个元素
    }
    num_elements = size_mapping[size]

    print(f"Generating a list with {num_elements:,} random integers...")
    # Generate a list of random integers between 0 and a large number
    # 生成一个包含随机整数的列表，范围从0到一个大数
    unsorted_list = [random.randint(0, num_elements * 10) for _ in range(num_elements)]
    
    print("Sorting the list using merge sort...")
    sorted_list = merge_sort(unsorted_list)
    
    print("Sorting complete.")
    # We avoid printing the large list to the console as it would be very slow.
    # 我们避免在控制台打印大型列表，因为这会非常慢。
    # You can verify the first and last elements to get a sense of the result.
    # 你可以验证第一个和最后一个元素来感受排序结果。
    if sorted_list:
        print(f"Verification: First element is {sorted_list[0]}, Last element is {sorted_list[-1]}")


if __name__ == "__main__":
    # Run doctests to verify correctness of the algorithm
    # 运行文档测试以验证算法的正确性
    import doctest
    doctest.testmod()

    # Set up argument parser
    # 设置参数解析器
    parser = argparse.ArgumentParser(
        description="A script to test the performance of the merge sort algorithm.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--size",
        choices=["small", "large"],
        required=True,
        help=(
            "Select the size of the dataset to sort:\n"
            "'small': A small dataset (10,000 elements) for quick tests.\n"
            "'large': A large dataset (2,000,000 elements) for performance/energy tests."
        )
    )

    args = parser.parse_args()
    main(args.size)