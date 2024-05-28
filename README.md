# Архитектура компьютера. Лабораторная работа №3

- Балин Артем Алексеевич, P3212
- alg| acc | harv | hw | instr | struct | stream | port | cstr | prob1 |
- Базовый вариант (без усложнения)

## Язык программирования

Синтаксис в расширенной БНФ.

```ebnf
program ::= sentence { sentence }

sentence ::= simple_sentence
        | while_block
        | if_block
        | comment

simple_sentence ::= print_sentence
                    | declare_and_assign
                    | assign

assign ::= char_assign | int_assign

char_assign ::= variable_name "=input()"

int_assign ::= variable_name "=" math_equathion

print_sentence ::= print_string | print_char

print_string ::= "print(" string ")"

string ::= "\"" { <any symbol except "\t \n"> } "\""
         | "\'" { <any symbol except "\t \n"> } "\'"

print_char ::= "print(" variable_name ")"

comment ::= "//" { <any symbol except "\n"> }

variable_name ::= variable_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

math_equation ::= term { ("+" | "-") term }

term ::= factor { ("*" | "/" | "%") factor }

factor ::= variable_name | integer | "(" math_equation ")"

integer ::= digit { digit }
            | "-" integer

digit ::= <any of "0-9">

declare_and_assign ::= "int" int_assign
                     | "char" char_assign

while_block ::= "while(" condition ")" "{" program "}"

if_block ::= "if(" condition ")" "{" program "}"

condition ::= math_equation
            | "!" math_equation

```

Команды:

- `add` -- сумма значений на левом и правом входе АЛУ записывается в аккумулятор
- `sub` -- значение на правом входе АЛУ вычитается из значения левого входа и записывается в аккумулятор
- `mul` -- произведение значений на левом и правом входе АЛУ записывается в аккумулятор
- `div` -- значение на левом входе АЛУ делится нацело на значение на правом входе, результат записывается в аккумулятор
- `mod` -- остаток от деления значения на левом входе АЛУ на значение на правом входе записывается в аккумулятор
- `inc` -- инкрементированное значение аккумулятора записывается в аккумулятор
- `dec` -- декрементированное значение аккумулятора записывается в аккумулятор
- `ld` -- загрузка значения из памяти/константы в аккумулятор
- `st` -- загрузка значения из аккумулятора в память по указанному адресу
- `jump` -- безусловный переход по метке
- `jz` -- переход по метке, если флаг `z-flag` установлен в 1
- `jnz` -- переход по метке, если флаг `z-flag` установлен в 0
- `halt` -- команда останова
- `in` -- загрузка одного значения из порта 0 в аккумулятор
- `out` -- загрузка значения аккумулятора в порт 1

Для команд, реализующих арифметику (первые 5), доступно два режима адресации: абсолютная из памяти данных и прямая загрузка операнда по аргументу.

Команда `ld` имеет три режима адресации:

- Абсолютная - загружает значение из памяти данных по адресу, указанному в аргументе
- Прямая загрузка операнда - загружает значение напрямую из аргумента команды
- Относительная - загружает значение по адресу, который лежит в памяти по адресу аргумента команды

Остальные команды безадресные или с абсолютной адресацией.

## Организация памяти

- Память соответствует Гарвардской архитектуре
- Размер машинного слова - 32 бита
- Адресация - абсолютная/относительная

Память данных изначально инициализируется нулями. Выделение памяти под переменные и строки происходит последовательно с начала памяти. Для вычисления математических выражений память с конца начинает использоваться как стек.

Под число отводиться 1 ячейка памяти, под строку длиной `n` - `n+1`, вместе со строкой в начале хранится её размер

## Система команд

### Особенности процессора:

- Машинное слово - 32 бита, знаковое
- Память:
  - адресуется через регистр `AR`, для относительной адресации - через `DR`
  - может быть прочитана в регистр `DR`
  - можно записать в память значение по адресу из `ACC`
- ALU:
  - операции: сложение, вычитание, деление, умножение, деление с остатком, прямая загрузка из правого/левого входа `ALU`
  - на левый вход `ACC`/`INPUT`
  - на правый вход `DR`/`Direct load`
- `PC` - счётчик команд, адресует память команд, увеличивается на 1 по умолчанию, может изменяться аргументами команд ветвления
- Прерываний нет
- Ввод/вывод реализован в закрытом виде: есть двумерный массив, 0 представляет из себя буфер с данными на ввод, 1 - буфер с данными на вывод, управляется управляющим сигналом из `Control Unit`

### Набор инструкций

| Инструкция | Кол-во тактов |
| :--------- | ------------- |
| add        | 1             |
| sub        | 1             |
| mul        | 1             |
| div        | 1             |
| mod        | 1             |
| inc        | 1             |
| dec        | 1             |
| ld         | 1 или 2       |
| st         | 1             |
| in         | 1             |
| out        | 1             |
| jump       | 1             |
| jz         | 1             |
| jnz        | 1             |
| halt       | 1             |

Примечание: в этой модели я предполагаю:

- чтение данных из памяти и выполнение над ними операций в АЛУ можно уложить в 1 такт, читая данные на подъёме сигнала тактового генератора и выполняя операции на спаде сигнала
- Данные из памяти действительно можно загрузить с необходимой скоростью (что не работает в реальности)

### Кодирование команд

Команды хранятся как структуры.

Пример команды:

```json
{ "opcode": "load", "arg": 5, "addressing_mode": "direct", "index": 2 }
```

где

- `opcode` - название команды
- `index` - её номер в памяти команд (скорее для отладки)
- `arg` - аргумент (если есть)
- `addressing_mode` - тип адресации (если есть)

## Транслятор

Реализовано в модуле: [translator.py](./translator.py)

Интерфейс командной строки: `python3 translator.py <input_file> <target_file>`

Этапы трансляции:

- выделяем массив из `sentence` в соответствии с БНФ
- `if` и `while` `_statement`\`ы транслируются в набор команд ветвления и `simple_statement`\`ов, которые находятся внутри блока или являются условием `condition`
- `simple_statement` транслируется согласно БНФ в `assign`, `declare` или `print`
- `print_string` аллоцирует `n+1` ячейку, начиная с первой свободной, под строку
- `assign` аллоцирует 1 ячейку памяти под переменную, сохраняя в словарь по ключу "название переменной" метку (номер ячейки памяти), далее процесс выполняется как `declare`
- `declare`, зная метку переменной, транслирует `math_equathion` в набор инструкций, после чего использует `ld` и `st` команды для сохранения в нужную ячейку
- `math_equathion` - происходит трансляция выражения в обратную польскую нотацию с сохранением приоритета математических операций. Зная, где сейчас находится вершина стека и текущую операцию, над двумя значениями из стека выполняется операция и кладётся обратно на стек. Используются команды арифметики и `ld`/`st`

В сформированном файле хранятся команды в структурном представлении, а также словарём хранится номер ячейки и данные в ней для каждой аллоцированной строки.

Стоит заметить, что изначально память данных всюду 0, кроме ячеек со строками, поэтому даже такой код

```js
int a = 5;
```

после трансляции будет выглядит примерно так:

```
{"opcode": "load", "arg": 5, "addressing_mode": "direct", "index": 1}
{"opcode": "store", "arg": 4095, "index": 2}
{"opcode": "load", "arg": 4095, "addressing_mode": "absolute", "index": 3}
{"opcode": "store", "arg": 1, "index": 4}
```

Из-за отсутствия констант, даже `5` считается математическим выражением, требующим записи на стек.

## Модель процессора

Реализовано в модуле: [machine.py](./machine.py)

Интерфейс командной строки: `python3 machine.py <code_file> <input_file>`

### DataPath

<img src="./media/DP.svg">

Реализован в классе `DataPath`

`ALU`, `IO` и `DataMemory` также реализованы в соответствующих классах (являются полями `DataPath`)

Управление сигналами происходит в методах класса:

- `latch acc` - защёлкнуть значение в `ACC`
- `latch DR` - защёлкнуть значение в `Data register`
- `latch AR` - защёлкнуть значение в `Address register`
- `re/wr` - управление памятью: записать значение из `ACC` или прочитать в `DR` по адресу
- `select port` - управление IO: выбранный порт 0 возвращает значение на `MUX` левого входа `ALU`; выбранный порт 1 записывает в буфер значение из `ACC`
- `left_in` и `right_in` определяют, какое из двух значений пройдёт через мультиплексор на входы `ALU`
- `alu_op` - определяет операцию в `ALU` (из-за `hardware` реализации сигнал представлен просто строкой, например, `"++"` и `"+"` для `inc` и `add` соответственно)
- `sel addr` определяет, каким значением будет адресовываться память `Data Memory`

Флаг `z_flag` устанавливается после каждой операции в `ALU`, отображает нулевое значение в аккумуляторе

По умолчанию, все регистры хранят 0

### ControlUnit

<img src="./media/CU.svg">

Реализовано в классе `ControlUnit`.

- `Hardwared` (реализовано полностью на Python)
- `decode_and_execute_instruction` - для декодирования инструкции, то есть подаче нужных управляющих сигналов, значений (`direct load` и `program counter` при необходимости) в сам `Control Unit` и `DataPath
- `tick` для подсчёта количества тактов

Особенности работы модели:

- Остановка моделирования осуществляется при:
  - превышении лимита выполненных инструкций
  - исключении `StopIteration` -- если выполнена инструкция `halt`
  - `EOFException` = при ошибке `Buffer is empty`
- Для журнала состояний процессора используется модуль `logging`
- Шаг моделирования соответствует одной инструкции с выводом состояния в журнал
- Количество инструкций для моделирования ограниченино hardcode-константой

## Тестирование

- Тестирование осуществляется при помощи golden test`ов
- Конфигурация тестов [здесь](./golden/)
- Настройка тестирования [здесь](./golden_alg_test.py)

CI на GitHub:

```yml
name: Python CI

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.8

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
          python-version: 3.8
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: poetry run ruff format --check .

      - name: Run Ruff linters
        run: poetry run ruff check .
```

где:

- `poetry` -- управления зависимостями для языка программирования Python.
- `coverage` -- формирование отчёта об уровне покрытия исходного кода.
- `pytest` -- утилита для запуска тестов.
- `ruff` -- утилита для форматирования и проверки стиля кодирования.

Пример использования журнала работы на примере `cat`:

```bash
PS F:\git\Alg-acc-machine> cat ./examples/cat_alg.js
char c = input();
while (c){
    print(c);
    c = input();
}
PS F:\git\Alg-acc-machine> cat ./examples/cat_input.txt
ITMO
PS F:\git\Alg-acc-machine> python translator.py ./examples/cat_alg.js ./examples/cat_alg_out.txt
source LoC: 6 code instr: 14
PS F:\git\Alg-acc-machine> cat ./examples/cat_alg_out.txt
{"opcode": "input", "index": 0}
{"opcode": "store", "arg": 0, "index": 1}
{"opcode": "load", "arg": 0, "addressing_mode": "absolute", "index": 2}
{"opcode": "store", "arg": 4095, "index": 3}
{"opcode": "load", "arg": 4095, "addressing_mode": "absolute", "index": 4}
{"opcode": "jz", "index": 5, "arg": 13}
{"opcode": "load", "arg": 0, "addressing_mode": "absolute", "index": 6}
{"opcode": "store", "arg": 4095, "index": 7}
{"opcode": "load", "arg": 4095, "addressing_mode": "absolute", "index": 8}
{"opcode": "output", "index": 9}
{"opcode": "input", "index": 10}
{"opcode": "store", "arg": 0, "index": 11}
{"opcode": "jump", "arg": 2, "index": 12}
{"opcode": "halt", "index": 13}

{"data": []}
PS F:\git\Alg-acc-machine> python machine.py ./examples/cat_alg_out.txt ./examples/cat_input.txt
DEBUG:root:TICK:   0 PC:   0 AR: 0 DR: 0 ACC:0  input
DEBUG:root:TICK:   1 PC:   1 AR: 0 DR: 0 ACC:73         store 0
DEBUG:root:TICK:   2 PC:   2 AR: 0 DR: 0 ACC:73         load 0
DEBUG:root:TICK:   3 PC:   3 AR: 0 DR: 73 ACC:73        store 4095
DEBUG:root:TICK:   4 PC:   4 AR: 4095 DR: 73 ACC:73     load 4095
DEBUG:root:TICK:   5 PC:   5 AR: 4095 DR: 73 ACC:73     jz 13
DEBUG:root:TICK:   6 PC:   6 AR: 4095 DR: 73 ACC:73     load 0
DEBUG:root:TICK:   7 PC:   7 AR: 0 DR: 73 ACC:73        store 4095
DEBUG:root:TICK:   8 PC:   8 AR: 4095 DR: 73 ACC:73     load 4095
DEBUG:root:TICK:   9 PC:   9 AR: 4095 DR: 73 ACC:73     output
DEBUG:root:TICK:  10 PC:  10 AR: 4095 DR: 73 ACC:73     input
DEBUG:root:TICK:  11 PC:  11 AR: 4095 DR: 73 ACC:84     store 0
DEBUG:root:TICK:  12 PC:  12 AR: 0 DR: 73 ACC:84        jump 2
DEBUG:root:TICK:  13 PC:   2 AR: 0 DR: 73 ACC:84        load 0
DEBUG:root:TICK:  14 PC:   3 AR: 0 DR: 84 ACC:84        store 4095
DEBUG:root:TICK:  15 PC:   4 AR: 4095 DR: 84 ACC:84     load 4095
DEBUG:root:TICK:  16 PC:   5 AR: 4095 DR: 84 ACC:84     jz 13
DEBUG:root:TICK:  17 PC:   6 AR: 4095 DR: 84 ACC:84     load 0
DEBUG:root:TICK:  18 PC:   7 AR: 0 DR: 84 ACC:84        store 4095
DEBUG:root:TICK:  19 PC:   8 AR: 4095 DR: 84 ACC:84     load 4095
DEBUG:root:TICK:  20 PC:   9 AR: 4095 DR: 84 ACC:84     output
DEBUG:root:TICK:  21 PC:  10 AR: 4095 DR: 84 ACC:84     input
DEBUG:root:TICK:  22 PC:  11 AR: 4095 DR: 84 ACC:77     store 0
DEBUG:root:TICK:  23 PC:  12 AR: 0 DR: 84 ACC:77        jump 2
DEBUG:root:TICK:  24 PC:   2 AR: 0 DR: 84 ACC:77        load 0
DEBUG:root:TICK:  25 PC:   3 AR: 0 DR: 77 ACC:77        store 4095
DEBUG:root:TICK:  26 PC:   4 AR: 4095 DR: 77 ACC:77     load 4095
DEBUG:root:TICK:  27 PC:   5 AR: 4095 DR: 77 ACC:77     jz 13
DEBUG:root:TICK:  28 PC:   6 AR: 4095 DR: 77 ACC:77     load 0
DEBUG:root:TICK:  29 PC:   7 AR: 0 DR: 77 ACC:77        store 4095
DEBUG:root:TICK:  30 PC:   8 AR: 4095 DR: 77 ACC:77     load 4095
DEBUG:root:TICK:  31 PC:   9 AR: 4095 DR: 77 ACC:77     output
DEBUG:root:TICK:  32 PC:  10 AR: 4095 DR: 77 ACC:77     input
DEBUG:root:TICK:  33 PC:  11 AR: 4095 DR: 77 ACC:79     store 0
DEBUG:root:TICK:  34 PC:  12 AR: 0 DR: 77 ACC:79        jump 2
DEBUG:root:TICK:  35 PC:   2 AR: 0 DR: 77 ACC:79        load 0
DEBUG:root:TICK:  36 PC:   3 AR: 0 DR: 79 ACC:79        store 4095
DEBUG:root:TICK:  37 PC:   4 AR: 4095 DR: 79 ACC:79     load 4095
DEBUG:root:TICK:  38 PC:   5 AR: 4095 DR: 79 ACC:79     jz 13
DEBUG:root:TICK:  39 PC:   6 AR: 4095 DR: 79 ACC:79     load 0
DEBUG:root:TICK:  40 PC:   7 AR: 0 DR: 79 ACC:79        store 4095
DEBUG:root:TICK:  41 PC:   8 AR: 4095 DR: 79 ACC:79     load 4095
DEBUG:root:TICK:  42 PC:   9 AR: 4095 DR: 79 ACC:79     output
DEBUG:root:TICK:  43 PC:  10 AR: 4095 DR: 79 ACC:79     input
WARNING:root:Input buffer is empty
INFO:root:output_buffer: 'ITMO'
ITMO
instr_counter:  43 ticks: 43
```

Пример проверки исходного кода:

```
PS F:\git\Alg-acc-machine> poetry run pytest . -v
=========================================================================================================== test session starts ============================================================================================================
platform win32 -- Python 3.10.5, pytest-7.4.4, pluggy-1.5.0 -- C:\Users\art\AppData\Local\pypoetry\Cache\virtualenvs\alg-machine-pNfafQNh-py3.10\Scripts\python.exe
cachedir: .pytest_cache
rootdir: F:\git\Alg-acc-machine
configfile: pyproject.toml
plugins: golden-0.2.2
collected 4 items

golden_alg_test.py::test_translator_and_machine[golden/cat_alg.yml] PASSED                                                                                                                                                            [ 25%]
golden_alg_test.py::test_translator_and_machine[golden/hello_alg.yml] PASSED                                                                                                                                                          [ 50%]
golden_alg_test.py::test_translator_and_machine[golden/hello_user_alg.yml] PASSED                                                                                                                                                     [ 75%]
golden_alg_test.py::test_translator_and_machine[golden/prob1_alg.yml] PASSED                                                                                                                                                          [100%]

============================================================================================================ 4 passed in 0.30s =============================================================================================================
PS F:\git\Alg-acc-machine> poetry run ruff check .                                                                                                                                                                                           
PS F:\git\Alg-acc-machine> poetry run ruff format .                                                                                                                                                                                          
4 files left unchanged        
```
