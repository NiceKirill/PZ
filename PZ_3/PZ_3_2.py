## 2. При открытии вклада в банке установлены следующие годовые проценты: при
## вкладе до 50000р. процент составит 4%; при вкладе от 50000р. до 100000р. процент
## составит 5%; при вкладе от 100000р. до 150000р. скидка составит 6%; при вкладе от
## процентной ставки в зависимости от вносимой суммы.

def get_interest_rate(deposit):
    if deposit < 50000:
        return 4
    elif deposit < 100000:
        return 5
    elif deposit < 150000:
        return 6
    elif deposit < 200000:
        return 7
    return None

deposit = float(input("Введите сумму вашего вклада: "))
interest_rate = get_interest_rate(deposit)

if interest_rate is not None:
    print(f"Процентная ставка для вклада {deposit} рублей составляет {interest_rate}%.")
else:
    print("Для сумм свыше 200000 рублей процентная ставка не установлена.")1
