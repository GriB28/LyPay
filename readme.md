<div align="center">

# [github.com/GriB28/LyPay](https://github.com/GriB28/LyPay)
## [<img src="https://www.svgrepo.com/show/452115/telegram.svg" alt="tg" height=20 />`Telegram-боты`](https://core.telegram.org/bots) для [`Благотворительной Ярмарки`](https://t.me/fairL2SH) Лицея "Вторая школа"

</div>

#
### ⬇️ Установка и настройка (Windows 10+)

1. Скачайте архив с исходным кодом со [страницы последнего релиза](https://github.com/GriB28/LyPay/releases/latest) и распакуйте его
2. Установите интерпретатор Python
    * Официальный сайт: [python.org](https://python.org/downloads)
    * При установке обязательно запишите значение директории интерпретатора в переменную среды `Path` (есть соответствующая настройка в установщике)
    * _При желании_ так же можно вручную установить зависимости из файла [`.req`](./.req) (каждый раз при запуске сборки проверка и, если необходимо, установка библиотек будет происходить автоматически)
3. Необходимо перенести базу данных и ключ `.env` или воспользоваться тестовыми пустыми шаблонами
    * В директории [`.examples`](./.examples) находятся пустой файл `.env`, который необходимо заполнить, и шаблонная база данных
    * Ключ и базу данных необходимо переместить в корневую папку проекта

#
### ☑️ Запуск и команды лаунчера
Сборка запускается через скрипт [`startup.bat`](./startup.bat)

#### ⚙️ Основные команды лаунчера
- **launch** – стандартный запуск (эквивалентен `start all`)
- **start** \<name\> – запуск одного бота/скрипта
- **shutdown** – стандартное завершение работы (эквивалентно `off all`)
- **off** \<name\> – завершение работы одного бота/скрипта
- **restart** \<name\> – перезапуск одного бота/скрипта
- **settings** read | r – чтение сохранённых настроек
- **settings** current | c – чтение текущих настроек
- **settings** set \<key\> \<new_value\> – перезаписывание настроек по ключу
- **help** – список всех команд и их аргументов

#
## Создатели и разработчики
[`github.com/GriB28`](https://github.com/GriB28),
[`github.com/GregorBag`](https://github.com/GregorBag)

[![Contributors](https://contrib.rocks/image?repo=GriB28%2FLyPay)](https://github.com/GriB28/LyPay/graphs/contributors)

Особая благодарность:
[`github.com/NikitaMulyar`](https://github.com/NikitaMulyar),
[`github.com/Mathew5555`](https://github.com/Mathew5555)
