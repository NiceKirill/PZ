## Дан список размера N. Найти номера тех элементов список, которые больше своего
## левого соседа, и количество таких элементов. Найденные номера выводить в
## порядке их убывания.

def find_greater_elements(lst):

    # Проверка на длину списка
    if len(lst) < 2:
        raise ValueError("Список должен содержать хотя бы два элемента.")

    # Список для хранения индексов элементов, которые больше своих левых соседей
    greater_indices = []

    for i in range(1, len(lst)):
        if lst[i] > lst[i - 1]:
            greater_indices.append(i)

    # Сортируем найденные индексы в порядке убывания
    greater_indices.sort(reverse=True)

    return greater_indices, len(greater_indices)


# Пример использования функции
lst = [3, 2, 7, 5, 6, 4]
indices, count = find_greater_elements(lst)
print("Индексы:", indices)
print("Количество:", count)