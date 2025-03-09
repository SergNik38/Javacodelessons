def search(array: list[int], number: int) -> bool:
    left, right = 0, len(array) - 1
    while left <= right:
        middle = (left + right) // 2
        if array[middle] == number:
            return True
        elif array[middle] < number:
            left = middle + 1
        else:
            right = middle - 1
    return False


if __name__ == "__main__":
    array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    number = 3
    print(search(array, number))
