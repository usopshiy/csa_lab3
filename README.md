# Лабараоторная работа №3 "Эксперимент"

## Вариант
- Дашкевич Егор Вячеславович P3208
```
asm | risc | harv | hw | instr | struct | stream | mem | cstr | prob1 | cache
```
- Упрощенный вариант

### Расшифровка варианта

- синтаксис языка ***Assembler*** с поддержкой label-ов
- ***RISC*** архитектура процессора
- ***Гарвардский*** тип памяти (память команд и данных раздельно)
- ***HW*** - Control Unit реализуется как часть модели
- Точность модели до ***Инструкций***
- Машинный код представляется в виде ***высокоуровневой структуры данных***
- Ввод-вывод осуществляется как ***поток токенов***
- Порты ввода-вывода отображаются в ***память***
- ***Нуль-терминированые строки*** (cstring)

## Язык программирования
В качестве языка программирования реализовано сокращенное подможество языка Assembler, решающее конкретные задачи.

(см. [Алгоритмы](algorithms))

### Синатксис Языка
```ebnf
program ::= { line }-

line ::= section "\n"
       | label "\n"
       | instr "\n"
       | data "\n"

section ::= "section .data:"
          | "section .text:"

label ::= label_name ":"

data ::= label_name ": " "\"" {<any symbol except ":">} "\0\""

label_name ::= <any symbols except ":">

instr ::= op0
        | op1 label_name
        | op2 reg
        | op3 reg ", " (int | reg)

op0 ::= "hlt"
      | "nop"

op1 ::= "jmp"
      | "jz"
      | "jl"

op2 ::= "in"
      | "out"
      | "inc"
    
op3 ::= "mv"
      | "add"
      | "sub"
      | "ld"
      | "st"
      | "cmp"

reg ::= "x" <any of "0-2">
```

### Семантика
Код выполняется последовательно - строка за строкой

Метки определяются на отдельной строке исходного кода: 
```asm
label:
    word 42 
```
Далее метки могут использоваться в любом месте исходного кода (как до так и после объявления метки)

Метки не чувствительны к регистру, повторение меток недопустимо.
Метки считаются одинаковыми если единственное их различие - регистр символов:
```
"label" == "LaBeL"
```

Использование меток не ограничено по количеству
Транслятор поставит вместо метки адрес команды перед которой она объявлена

Любая программа должна иметь секцию ".text" указывающую на начало инструкций

## Организация памяти
Память построена по Гарвадской модели: память данных и память инструкций разделены

### Регистры
Система основана на RISC архитектуре, поэтому в распоряжении разработчика есть 3 регистра общего пользования
(достаточно для реализации необходимых алгоритмов). 

Помимо этого существуют служебные регистры, прямого доступа к которым нет

Для обеспечения условной адресации существует 2 флага - zf(ноль), nf(отрицательное)

### Память данных
Размер машинного слова не определен - данные хранятся как список строк

Организация памяти:

| Адрес |    Содержимое     |
|:------|:-----------------:|
| 0     |    порт ввода     |
| 1     |    порт вывода    |
| 2     |   переменная #0   |
| ...   |        ...        |
| n     | переменная #(n-2) |
| ...   |        ...        |

* доступ к памяти через любой регистр общего назначения
* ячейки 0 и 1 - выделены под IO
* литералы и константы не поддерживаются

### Память инструкций
Размер машинного слова не определен - инструкции хранятся как высокоуровневоя структура данных

Организация памяти:
* вся память выделена под инструкции, выполнение начинается с 0 адреса
* поддерживается условная и абсолютная адресация
* у разработчика доступ к памяти отсутствует, за исключением меток
* прерывания не поддерживаются

## Система команд 

### Особенности процессора:
* Машинное слово - не определено
* Типы данных - знаковые числа или символы (в модели хранятся в качестве строки длины 1)
* Несколько регистров общего назначения, доступные разработчику + служебные регистры
* Поток управления:
  * Регистр PC инкрементируется после каждой инструкции (кроме переходов)
  * Условные и безусловные переходы

### Набор инструкций
* **hlt** - остановка программы
* **nop** - отстутствие инструкции
* **jmp { program_address }** - абсолютный переход
* **jz { program_address }** - условный переход. Перейти, если результат последней операции равен 0
* **jl { program_address }** - условный переход. Перейти, если результат последней операции меньше 0
* **in { target_register }** - ввести данные с устройства ввода
  * Сокращение команды *ld reg input_port* в языке, в isa только ld
* **out { source_register }** - вывести данные на устройство вывода
  * Сокращение команды *st output_port* в языке, в isa только st
* **inc { register }** - увеличить значение на 1
* **mv { target_register } { source_register | int }** - операция перемещения данных между регистрами
* **add { target_register } { source_register | int }** - операция сложения
* **sub { target_register } { source_register | int }** - операция вычитания
* **ld { target_register } { memory_address }** - выгрузить значение из памяти
* **st { source_register } { memory_address }** - загрузить значение в память
* **cmp { register } { register | int }** - сравнить числа (zf = 1 если равны)

Обозначения: 
* program_address - адрес в памяти инструкций, обычно является меткой
* register - регистр общего назначения
* int - целочисленное знаковое число
* memory_address - адрес в памяти данных, обычно является меткой

### Кодирование инструкций
Инструкции заданы высокоуровневой структурой данных. Для записи машинного кода используется json

## Транслятор
**Использование:** ``./src/translator.py <asm_file> <data_out_file> <instr_out_file>``

Транслятор языка работает в 3 этапа:
* **Препроцессинг** - разбивает файл на значащие линии, убирает пустые строки и лишние пробелы
* **Первый проход** - транслирует память данных и память инструкций. Создает словарь метка:адрес. 
Также на этом этапе происходит трансляция команд *in* и *out* в инструкции *ld* и *st*
* **Второй проход** - заменяет метки в памяти инструкций на адреса, согласно словарю метка:адрес

## Модель процессора
**Запуск:**

``./src/machine.py <machine_code_file> <data_memory_file> <input_buffer_file>``

### Data Path

![Data Path](resources/DP.png)

Реализован в классе DataPath 

Сигналы:
* ``alu_op`` - сигнал операции алу
* ``control`` - сигналы контроля памяти (запись, вывод)
* ``latch_reg`` - сигналы защелкивания конкретного регистра

``input, output`` - вход и выход внешнего устройства (запись перезватывается при обращении на порт)
``ZF, NF`` - флаги результата операции
### Control Unit

Реализован в классе ControlUnit

![Control Unit](resources/CU.png)

Сигналы:
* ``signals`` - управляющие сигналы, идущие на DataPath
* ``latch_pc`` - защелкивание счетчика программы (инструкции)

``sel_args`` - обрезает инструкцию до её аргумента (адресса перехода) для команд перехода
``step counter`` - счетчик тактов, необходим для правильной работы инструкций, занимающих несколько тактов
``flags`` - флаги операции с алу, необходимы для условных переходов

## Тестирование
**Запуск тестов**: ``poetry run pytest . -v``

Конфигурация голден тестов находится в директории [golden](golden)

Настройки голден тестов: [test_golden.py](test_golden.py)

### Тестовое покрытие
* ``cat`` - повторяет поток ввода на поток вывода
* ``hello_world`` - выводит "Hello, world!\n" в поток вывода
* ``hello_user`` - выводит в поток вывода приветствие пользователя
* ``prob1`` - сумма чисел, кратных 3 или 5, но меньших 1000

### Конфигурация CI с помощью GitHub Actions
Находится в файле [python.yml](.github/workflows/python.yaml):
```yml
name: Python CI/CD

on:
  push:
    branches:
      - master
  pull_request:
    branches:
      - master

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.10.8

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Run tests and collect coverage
        run: |
          poetry run coverage run -m pytest .
          poetry run coverage report -m
        env:
          CI: true

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.10.8

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: echo Ok

      - name: Run Ruff linters
        run: poetry run ruff check .
```
**Пример работы тестового покрытия**:
```
poetry run pytest . -v

=============================================================================== test session starts =============================================================================== 
platform win32 -- Python 3.10.8, pytest-7.4.4, pluggy-1.5.0 -- C:\Users\Пользователь\AppData\Local\pypoetry\Cache\virtualenvs\csa-lab3-j1K-f4Cs-py3.10\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Пользователь\PycharmProjects\csa_lab3
configfile: pyproject.toml
plugins: golden-0.2.2
platform win32 -- Python 3.10.8, pytest-7.4.4, pluggy-1.5.0 -- C:\Users\Пользователь\AppData\Local\pypoetry\Cache\virtualenvs\csa-lab3-j1K-f4Cs-py3.10\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Пользователь\PycharmProjects\csa_lab3
configfile: pyproject.toml
plugins: golden-0.2.2
collected 4 items

test_golden.py::test_bar[golden/cat.yml] PASSED                                                                                                                              [ 25%] 
test_golden.py::test_bar[golden/hello_user.yml] PASSED                                                                                                                       [ 50%] 
test_golden.py::test_bar[golden/hello_world.yml] PASSED                                                                                                                      [ 75%] 
test_golden.py::test_bar[golden/prob1.yml] PASSED                                                                                                                            [100%] 

================================================================================ 4 passed in 0.38s ================================================================================ 
```

**Пример запуска и работы (алгоритм cat)**:
```
./translator.py ../algorithms/cat.asm ../data.txt ../instr.txt
Output files:  ../data.txt ../instr.txt

Process finished with exit code 0

./machine.py ./instr.txt ./data.txt ./input.txt
csa
DEBUG   machine:simulate      TICK 0
 REGS: [0: 0 1: 0 2: 0]
 ld ['x0', '0']
DEBUG   machine:simulate      TICK 3
 REGS: [0: 99 1: 0 2: 0]
 cmp ['x0', '0']
DEBUG   machine:simulate      TICK 7
 REGS: [0: 99 1: 0 2: 0]
 jz ['6']
DEBUG   machine:simulate      TICK 9
 REGS: [0: 99 1: 0 2: 0]
 st ['x0', '1']
DEBUG   machine:simulate      TICK 11
 REGS: [0: 99 1: 0 2: 0]
 ld ['x0', '0']
DEBUG   machine:simulate      TICK 14
 REGS: [0: 115 1: 0 2: 0]
 jmp ['1']
DEBUG   machine:simulate      TICK 15
 REGS: [0: 115 1: 0 2: 0]
 cmp ['x0', '0']
DEBUG   machine:simulate      TICK 19
 REGS: [0: 115 1: 0 2: 0]
 jz ['6']
DEBUG   machine:simulate      TICK 21
 REGS: [0: 115 1: 0 2: 0]
 st ['x0', '1']
DEBUG   machine:simulate      TICK 23
 REGS: [0: 115 1: 0 2: 0]
 ld ['x0', '0']
DEBUG   machine:simulate      TICK 26
 REGS: [0: 97 1: 0 2: 0]
 jmp ['1']
DEBUG   machine:simulate      TICK 27
 REGS: [0: 97 1: 0 2: 0]
 cmp ['x0', '0']
DEBUG   machine:simulate      TICK 31
 REGS: [0: 97 1: 0 2: 0]
 jz ['6']
DEBUG   machine:simulate      TICK 33
 REGS: [0: 97 1: 0 2: 0]
 st ['x0', '1']
DEBUG   machine:simulate      TICK 35
 REGS: [0: 97 1: 0 2: 0]
 ld ['x0', '0']
DEBUG   machine:simulate      TICK 38
 REGS: [0: 0 1: 0 2: 0]
 jmp ['1']
DEBUG   machine:simulate      TICK 39
 REGS: [0: 0 1: 0 2: 0]
 cmp ['x0', '0']
DEBUG   machine:simulate      TICK 43
 REGS: [0: 0 1: 0 2: 0]
 jz ['6']
DEBUG   machine:simulate      TICK 45
 REGS: [0: 0 1: 0 2: 0]
 hlt []
DEBUG   machine:simulate      TICK 45
 REGS: [0: 0 1: 0 2: 0]
 hlt []
```
### Статистика
| ФИО                        | алг         | LoC | code байт | code инстр. | инстр. | такт | вариант                                                                                   | 
|----------------------------|-------------|-----|-----------|-------------|--------|------|-------------------------------------------------------------------------------------------|
| Дашкевич Егор Вячеславович | сat         | 10  | -         | 7           | 20     | 45   | asm   \| risc \| harv \| hw \| instr \| struct \| stream \| mem \| cstr \| prob1 \| cache |
| Дашкевич Егор Вячеславович | hello_world | 15  | -         | 9           | 91     | 241  | asm   \| risc \| harv \| hw \| instr \| struct \| stream \| mem \| cstr \| prob1 \| cache |
| Дашкевич Егор Вячеславович | hello_user  | 57  | -         | 42          | 243    | 659  | asm   \| risc \| harv \| hw \| instr \| struct \| stream \| mem \| cstr \| prob1 \| cache |
| Дашкевич Егор Вячеславович | prob1       | 34  | -         | 26          | 136    | 428  | asm   \| risc \| harv \| hw \| instr \| struct \| stream \| mem \| cstr \| prob1 \| cache |
