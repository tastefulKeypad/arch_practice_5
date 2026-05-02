# Домашнее задание 05: Оптимизация производительности через кеширование и rate limiting

Цель работы: Получить практические навыки проектирования систем с учетом производительности, реализации кеширования и rate limiting.

Вариант 21: Система управления арендой автомобилей https://www.hertz.com/

## Структура проекта
```
arch_practice_5
├── api
│   ├── db        - Содержит модели объектов для БД и файл инициализации БД
│   ├── endpoints - Содержит endpoint'ы API
│   └── schemas   - Содержит схемы объектов для валидации pydantic
```
# Запуск проекта
```
git clone https://github.com/tastefulKeypad/arch_practice_5.git
cd arch_practice_5
docker-compose up -d --build
```

# Полная очистка проекта
```
docker-compose down -v 
docker rmi arch_practice_5_image:latest
```

## Примеры использования
После запуска на ```localhost:8000/docs``` будет доступна интерактивная OPENAPI документация проекта.

Чтобы инициализировать бд пользователями и автомобилями используйте endpoint 'populate_db', после чего можно будет авторизироваться как администратор:

email: admin@example.com

pass:  admin 

Или как обычный пользователь:

email: user1@example.com 

pass:  user
