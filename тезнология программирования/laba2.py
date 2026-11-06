# Задача 1
def convert_types(data):
    result = []
    for item in data:
        if isinstance(item, (int, float)):
            result.append(str(item))
        elif isinstance(item, str):
            try:
                result.append(int(item))
            except ValueError:
                try:
                    result.append(float(item))
                except ValueError:
                    result.append(item)
        else:
            result.append(str(item))
    return result


# Задача 2
def swap_values(a, b):
    a, b = b, a
    return a, b


# Задача 3
def bool_transform(value):
    if value:
        return True
    return False


# Задача 4
def compound_operations(a, b):
    results = []

    value = a
    value += b
    results.append(value)

    value = a
    value -= b
    results.append(value)

    value = a
    value *= b
    results.append(value)

    value = a
    value /= b
    results.append(value)

    value = a
    value //= b
    results.append(value)

    value = a
    value %= b
    results.append(value)

    value = a
    value **= b
    results.append(value)

    return results


# Задача 5
def check_type(value, expected_type):
    return type(value).__name__ == expected_type


# Задача 6
def logical_and(a, b, c):
    if a:
        if b:
            if c:
                return True
    return False


# Задача 7
def logical_or(a, b, c):
    if a:
        return True
    if b:
        return True
    if c:
        return True
    return False


# Задача 8
def is_between(value, low, high):
    if value >= low and value <= high:
        return True
    return False


# Задача 9
def print_even_numbers(n):
    for number in range(2, n + 1, 2):
        print(number)


# Задача 10
def countdown_while(n):
    while n >= 1:
        print(n)
        n -= 1


# Задача 11
def skip_multiples(n, multiple):
    for number in range(1, n + 1):
        if number % multiple == 0:
            continue
        print(number)


# Задача 12
def if_elif_else_chain(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"


# Задача 13
def abs_value(x):
    if x < 0:
        return -x
    return x


# Задача 14
def binary_representation(n):
    if n == 0:
        return "0"

    negative = n < 0
    if negative:
        n = -n

    result = ""
    while n > 0:
        result = str(n % 2) + result
        n //= 2

    if negative:
        return "-" + result
    return result


# Задача 15
def custom_round(number, ndigits):
    factor = 10 ** ndigits
    scaled = number * factor

    if scaled >= 0:
        rounded = int(scaled + 0.5)
    else:
        rounded = int(scaled - 0.5)

    return rounded / factor


# Задача 16
def find_max_min(numbers):
    iterator = iter(numbers)
    try:
        first = next(iterator)
    except StopIteration:
        raise ValueError("Список не должен быть пустым")

    maximum = first
    minimum = first
    for number in iterator:
        if number > maximum:
            maximum = number
        if number < minimum:
            minimum = number

    return maximum, minimum


# Задача 17
def all_true(iterable):
    for item in iterable:
        if not item:
            return False
    return True


# Задача 18
def any_true(iterable):
    for item in iterable:
        if item:
            return True
    return False


# Задача 19
def custom_enumerate(sequence, start=0):
    result = []
    index = start
    for item in sequence:
        result.append((index, item))
        index += 1
    return result


# Задача 20
def custom_filter(func, iterable):
    result = []
    for item in iterable:
        if func(item):
            result.append(item)
    return result


# Задача 21
def custom_map(func, iterable):
    result = []
    for item in iterable:
        result.append(func(item))
    return result


# Задача 22
def custom_zip(list1, list2):
    result = []
    length = min(len(list1), len(list2))
    for index in range(length):
        result.append((list1[index], list2[index]))
    return result


# Задача 23
def custom_reversed(sequence):
    result = []
    for index in range(len(sequence) - 1, -1, -1):
        result.append(sequence[index])
    return result


# Задача 24
def custom_sorted(iterable, reverse=False):
    items = list(iterable)

    for end in range(len(items) - 1, 0, -1):
        for index in range(end):
            left = items[index]
            right = items[index + 1]
            need_swap = left < right if reverse else left > right
            if need_swap:
                items[index], items[index + 1] = right, left

    return items


# Задача 25
def sum_digits(n):
    if n < 0:
        n = -n

    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total


# Задача 26
def count_vowels(text):
    vowels = "aeiou"
    count = 0
    for letter in text.lower():
        if letter in vowels:
            count += 1
    return count


# Задача 27
def power(base, exp):
    if exp < 0:
        positive_result = power(base, -exp)
        return 1 / positive_result

    result = 1
    for _ in range(exp):
        result *= base
    return result


# Задача 28
def is_prime(n):
    if n < 2:
        return False

    limit = int(n ** 0.5)
    for divisor in range(2, limit + 1):
        if n % divisor == 0:
            return False
    return True


# Задача 29
def factorial(n):
    if n < 0:
        raise ValueError("Факториал определён только для неотрицательных чисел")

    result = 1
    for number in range(2, n + 1):
        result *= number
    return result


# Задача 30
def fibonacci(n):
    if n < 0:
        raise ValueError("Индекс Фибоначчи не может быть отрицательным")

    previous = 0
    current = 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


# Проверка работы функций
def main():
    print("Задача 1 -", convert_types([1, "2", "hello", 3.5]))
    print("Задача 2 -", swap_values(5, 10))
    print("Задача 3 -", bool_transform(5), bool_transform(0))
    print("Задача 4 -", compound_operations(10, 3))
    print("Задача 5 -", check_type(5, "int"), check_type("5", "int"))
    print("Задача 6 -", logical_and(True, 5, "x"),
          logical_and(True, 0, "x"))
    print("Задача 7 -", logical_or(0, "", False),
          logical_or(0, 5, False))
    print("Задача 8 -", is_between(5, 1, 10),
          is_between(15, 1, 10))

    print("Задача 9 -")
    print_even_numbers(10)

    print("Задача 10 -")
    countdown_while(5)

    print("Задача 11 -")
    skip_multiples(10, 3)

    print(
        "Задача 12 -",
        if_elif_else_chain(5),
        if_elif_else_chain(-3),
        if_elif_else_chain(0),
    )
    print("Задача 13 -", abs_value(-5), abs_value(3))
    print("Задача 14 -", binary_representation(10),
          binary_representation(0))
    print("Задача 15 -", custom_round(3.14159, 2),
          custom_round(2.5, 0))
    print("Задача 16 -", find_max_min([3, 7, 1, 9, 2]))
    print("Задача 17 -", all_true([1, 2, 3]), all_true([1, 0, 3]))
    print("Задача 18 -", any_true([0, "", False]),
          any_true([0, 5, False]))
    print("Задача 19 -", custom_enumerate(["a", "b", "c"], start=1))
    print(
        "Задача 20 -",
        custom_filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]),
    )
    print("Задача 21 -", custom_map(lambda x: x * 2, [1, 2, 3]))
    print("Задача 22 -", custom_zip([1, 2, 3], ["a", "b", "c"]))
    print("Задача 23 -", custom_reversed([1, 2, 3, 4]))
    print("Задача 24 -", custom_sorted([3, 1, 4, 1, 5]))
    print("Задача 25 -", sum_digits(1234), sum_digits(99))
    print("Задача 26 -", count_vowels("Hello World"),
          count_vowels("Python"))
    print("Задача 27 -", power(2, 5), power(3, 3))
    print("Задача 28 -", is_prime(17), is_prime(18))
    print("Задача 29 -", factorial(5), factorial(0))
    print("Задача 30 -", fibonacci(10), fibonacci(0), fibonacci(1))


if __name__ == "__main__":
    main()
