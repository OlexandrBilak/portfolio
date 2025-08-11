Налаштування фільтрів (config.txt) (у папці dist):

[filters]
city_fb = Місто Facebook
city_kijiji = Місто Kijiji
make = Марка авто
model = Модель авто
year_min = Мінімальний рік пошуку
year_max = Максимальний рік пошуку
price_min = Мінімальна ціна
price_max = Максимальна ціна
facebook_days_filter = Дата розміщення у Facebook ( тільки 4 параметри
    0 - Усі оголошення,
    1 - Останні 24 години,
    7 - Останні 7 днів,
    30 - Останні 30 днів)
max_post_age_hours = Дата розміщення у Kijiji (години)

[settings]
interval = Інтервал пошуку (хвилини)

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Фільтри не працюють:
- Якщо фільтр по місту у facebook не працює:
    Зайти вручну на маркетплейс обрати потрібне місто та скопіювати 3 значення у посиланні
    (https://www.facebook.com/marketplace/Значення)
    Наприклад: (https://www.facebook.com/marketplace/toronto/vehicles/?minPrice...) - копіюємо toronto
    (https://www.facebook.com/marketplace/113816355295121/vehicles/?minPrice...) - копіюємо 113816355295121

- Якщо фільтр по місту у kijiji не працює:
    Зайти вручну на сайт обрати потрібне місто та скопіювати 3 значення у посиланні
    (https://www.kijiji.ca/b-autos-camions/grand-montreal/)
    Наприклад: (https://www.kijiji.ca/b-autos-camions/grand-montreal/volkswagen-golf/201...) - копіюємо grand-montreal

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

