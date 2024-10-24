## Известно, что X кг шоколадных конфет стоит A рублей, а Y кг ирисок
## стоит B рублей. Определить, сколько стоит 1 кг шоколадных конфет, 1 кг ирисок, а также
## во сколько раз шоколадные конфеты дороже ирисок.

# Ввод данных
a = int(input("Введите стоимость шоколадных конфет: "))
x = int(input("Введите вес шоколадных конфет: "))
b = int(input("Введите стоимость ирисок: "))
y = int(input("Введите вес ирисок: "))

# Расчёт цены за 1 кг
price_per_kg_chocolate = a / x
price_per_kg_caramels = b / y

# Расчёт, во сколько раз шоколадные конфеты дороже ирисок
if price_per_kg_caramels != 0:
    price_factor = price_per_kg_chocolate / price_per_kg_caramels
else:
    price_factor = None # Если цена ирисок равна нулю

# Вывод результатов
print(f"Цена 1 кг шоколадных конфет: {price_per_kg_chocolate} рублей")
print(f"Цена 1 кг ирисок: {price_per_kg_caramels} рублей")

if price_factor is not None:
    print(f"Шоколадные конфеты дороже ирисок в {price_factor} раз.")
else:
    print("Цена ирисок равна нулю, невозможно рассчитать.")
