
# 2.1. Создание односвязного списка

def pair(head, tail):
    return lambda f: f(head, tail)


def head(lst):
    return lst(lambda h, t: h)


def tail(lst):
    return lst(lambda h, t: t)


# 2.2. Создание списка из аргументов

def make_list(*args):
    result = None

    for value in reversed(args):
        result = pair(value, result)

    return result


# 2.3. Преобразование списка в строку

def list_to_string(lst):
    result = []
    
    while lst is not None:
        result.append(str(head(lst)))
        lst = tail(lst)

    return "[" + ", ".join(result) + "]"


# 2.4. Создание списка чисел от low до high

def list_range(low, high):
    result = None

    for number in range(high, low - 1, -1):
        result = pair(number, result)

    return result


# 2.5. Свертка слева

def foldl(func, lst, acc):
    while lst is not None:
        acc = func(acc, head(lst))
        lst = tail(lst)

    return acc


# 2.6. Сумма элементов списка

def list_sum(lst):
    return foldl(lambda acc, x: acc + x, lst, 0)


# 2.7. Вычисление факториала

def fact(n):
    return foldl(lambda acc, x: acc * x,
                 list_range(1, n), 1)


# 2.8. Преобразование в обычный список Python

def list_to_py(lst):
    return foldl(lambda acc, x: acc + [x], lst, [])


# 2.9. Разворот списка

def list_reverse(lst):
    return foldl(lambda acc, x: pair(x, acc), lst, None)


# 2.10. Свертка справа

def foldr(func, lst, acc):
    return foldl(lambda result, x: pair(x, result),
                 list_reverse(lst), acc) if lst is not None else acc


# 2.11. Применение функции к каждому элементу

def list_map(func, lst):
    return foldr(lambda x, acc: pair(func(x), acc), lst, None)


# 2.12. Фильтрация элементов

def list_filter(pred, lst):
    return foldr(
        lambda x, acc: pair(x, acc) if pred(x) else acc,
        lst,
        None
    )


# 2.13. Сумма квадратов нечетных чисел

def sum_odd_squares(lst):
    odd_numbers = list_filter(lambda x: x % 2 != 0, lst)
    squares = list_map(lambda x: x ** 2, odd_numbers)
    return list_sum(squares)


# 2.14. Соединение двух списков

def list_concat(lst1, lst2):
    return foldr(lambda x, acc: pair(x, acc), lst1, lst2)


# 2.15. Замена элемента по индексу

def list_replace(lst, index, value):
    if index < 0:
        raise IndexError("Индекс не может быть отрицательным")

    def replace_recursive(current, i):
        if current is None:
            raise IndexError("Индекс выходит за границы списка")

        if i == 0:
            return pair(value, tail(current))

        return pair(head(current), replace_recursive(tail(current), i - 1))

    return replace_recursive(lst, index)


# Проверка работы всех функций

numbers = make_list(1, 2, 3, 4, 5)

print("Original list:", list_to_string(numbers))
print("Head:", head(numbers))
print("Tail:", list_to_string(tail(numbers)))
print("Range:", list_to_string(list_range(1, 5)))
print("Sum:", list_sum(numbers))
print("Factorial 5:", fact(5))
print("Python list:", list_to_py(numbers))
print("Reversed list:", list_to_string(list_reverse(numbers)))
print("Foldr:", foldr(lambda x, acc: x - acc, numbers, 0))
print("Multiply by 2:", list_to_string(list_map(lambda x: x * 2, numbers)))
print("Even numbers:", list_to_string(list_filter(lambda x: x % 2 == 0, numbers)))
print("Sum of odd squares:", sum_odd_squares(numbers))
print("Concatenation:", list_to_string(list_concat(numbers, make_list(6, 7))))
print("Replace element:", list_to_string(list_replace(numbers, 2, 100)))