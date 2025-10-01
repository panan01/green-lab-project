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
    """

    def merge(left: list, right: list) -> list:
        """
        Merge two sorted lists into a single sorted list.

        :param left: Left collection
        :param right: Right collection
        :return: Merged result
        """
        result = []
        while left and right:
            result.append(left.pop(0) if left[0] <= right[0] else right.pop(0))
        result.extend(left)
        result.extend(right)
        return result

    # G1: The expression 'len(collection)' was used multiple times.
    # It's now stored in a variable to avoid redundant computation.
    collection_len = len(collection)
    if collection_len <= 1:
        return collection
    mid_index = collection_len // 2
    return merge(merge_sort(collection[:mid_index]), merge_sort(collection[mid_index:]))


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
        "large": 2_00_000  # 20万个元素
    }
    num_elements = size_mapping[size]

    print(f"Generating a list with {num_elements:,} random integers...")
    # Generate a list of random integers between 0 and a large number
    # 生成一个包含随机整数的列表，范围从0到一个大数

    # G1: Assign the expression for the random range's upper bound to a variable.
    # This improves readability by giving the calculation a descriptive name.
    random_range_upper_bound = num_elements * 10
    unsorted_list = [random.randint(0, random_range_upper_bound) for _ in range(num_elements)]
    
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
            "'large': A large dataset (2,000,00 elements) for performance/energy tests."
        )
    )

    args = parser.parse_args()
    main(args.size)