# Учебный прокат

Локальное приложение для бронирования учебного оборудования.

## Запуск

Требуется Python 3.13.5. Из корня проекта на новой базе выполните:

```sh
python -m pip install -r requirements.txt
python -m src.equipment --db demo.sqlite3 catalog
python -m src.equipment --db demo.sqlite3 book --student 7 --equipment 1
python -m src.equipment --db demo.sqlite3 my-bookings --student 7
```

Каталог показывает проектор, микрофон и ноутбук. Бронирование возвращает бронь № 1 со статусом `reserved`, а последняя команда показывает её для студента 7.

15.11.2026 Codex повторил проверку в чистом контейнере Debian GNU/Linux 12 с Python 3.13.5. Каталог, бронирование и просмотр брони прошли успешно.

[Паспорт проекта](docs/00-project.md)

15.11.2026 Codex проверил команды на Windows с Python 3.13.5 и новым файлом SQLite.
