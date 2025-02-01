## Дана строка, содержащая латинские буквы и круглые скобки. Если скобки
## расставлены правильно (то есть каждой открывающей соответствует одна
## закрывающая), то вывести число 0. В противном случае вывести или номер позиции,
## в которой расположена первая ошибочная закрывающая скобка, или, если
## закрывающих скобок не хватает, число —1.

def check_brackets(string):
    stack = []

    for i, char in enumerate(string):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if not stack:
                return i + 1
            else:
                stack.pop()

    if stack:
        return -1
    else:
        return 0


# Пример использования
string = "((a+b)*(c-d))"
print(check_brackets(string))  # Ожидаемый результат: 0

string = "(a+b)*)"
print(check_brackets(string))  # Ожидаемый результат: 7

string = "((a+b"
print(check_brackets(string))  # Ожидаемый результат: -1

