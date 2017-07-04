import math
import sys
import random

from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit,
                             QPushButton, QGridLayout, QApplication)
from PyQt5.QtCore import QCoreApplication, Qt

EPSILON = 1e-9          # Заданая точность.
PRECISION = '10'        # Точность вывода результата.
MAX = 100               # [-MAX;MAX] --- интервал поиска корней.
STEP = 0.5


class BadEquationError(Exception):
    """Исключение, возникающее при неправильном вводе уравнения."""
    pass


class Equation:
    # Строка, содержащая функцию.
    _function = ''

    def set_function(self, func):
        """Проверка и установка функции."""
        result = []
        # Словарь: ключь --- то, что ввёл пользователь,
        #          значение --- во, что его преобразовать.
        correct_words = {'+': '+', '-': '-', '*': '*', '/': '/', '^': '**',
                         '(': '(', ')': ')', 'x': 'x', 'sin': 'math.sin',
                         'cos': 'math.cos', 'tg': 'math.tan',
                         'ctg': 'math.cot', '.': '.'
                         }
        if len(func) == 0:
            raise BadEquationError('Введите уравнение.')
        i = 0
        while i < len(func):
            # В уравнении могут быть: цифры,
            if func[i].isdigit():
                result.append(func[i])
                i += 1
                continue
            # символы из correct_words,
            elif func[i] in correct_words:
                result.append(correct_words[func[i]])
                i += 1
                continue
            # и слова из correct_words.
            elif func[i].isalpha():
                word = ''
                while i < len(func) and func[i].isalpha():
                    word += func[i]
                    i += 1
                if word in correct_words:
                    result.append(correct_words[word])
                    continue
            # Иначе это не уравнение.
            raise BadEquationError('Уравнение введено неверно.')
        self._function = ''.join(result)
        # Пробуем посчитать f(0). Если неполучается, то вызываем исключение.
        try:
            self.f(0)
        except Exception:
            raise BadEquationError('Ошибка!')

    def f(self, x):
        """Посчитать функцию в точке."""
        # Выполняет строку кода (функцию).
        return eval(self._function)

    def diff(self, x):
        """Посчитать производную функции в точке."""
        return (self.f(x + EPSILON) - self.f(x - EPSILON)) / (2 * EPSILON)

    def separate_roots(self):
        """
        Найти корни отделения.

        Результат --- список кортежей (a, b).

        """
        result = []
        x_1 = -MAX
        x_2 = x_1 + STEP
        while x_2 < MAX:
            temp = self.f(x_1) * self.f(x_2)
            # Если разные знаки, то добавляем в result.
            if temp <= 0:
                result.append((x_1, x_2))
            # Если x_i = 0, то пропускаем следующий отрезок, что бы не
            # было двух одинаковых корней в ответе.
            if temp == 0:
                x_1, x_2 = x_2, x_1 + STEP
            x_1, x_2 = x_2, x_1 + STEP
        self.sep_seg = result

    def solve(self):
        """
        Решить уравнение методом простых итераций.

        Возвращает список корней.

        """
        self.separate_roots()
        result = []
        # Для каждого отрезка отделения.
        for seg in self.sep_seg:
            # a = seg[0]; b = seg[1]
            # m --- максимум по модулю производной.
            m = self.diff(seg[0])
            temp = self.diff(seg[1])
            if abs(temp) > abs(m):
                m = temp
            # L --- лямбда.
            if m > 0:
                L = random.uniform(-2 / m, 0)
            else:
                L = random.uniform(0, -2 / m)

            # prev --- предыдущее значение c.
            prev = seg[0]
            while True:
                c = prev + L * self.f(prev)
                if abs(c - prev) < EPSILON:
                    break
                prev = c
            result.append(c)
        self.solutions = result


class EqSolver(QWidget):
    """Класс для работы с GUI."""
    def __init__(self):
        super().__init__()
        self.equation = Equation()
        self._init_ui()

    def _init_ui(self):
        description = QLabel(
            'Эта программа решает нелинейное уравнение f(x) = 0 методом простых итераций'
        )
        input_request = QLabel('f(x) = ')
        self.formulae = QLineEdit()
        roots = QLabel('Корни уравнения: ')
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        solve_button = QPushButton('Решить')
        solve_button.setShortcut(Qt.Key_Return)
        solve_button.clicked.connect(self._solve_button_clicked)
        exit_button = QPushButton('Выход', self)
        exit_button.setShortcut(Qt.Key_Escape)
        exit_button.clicked.connect(QCoreApplication.instance().quit)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(description, 1, 0, 1, 3)
        grid.addWidget(input_request, 2, 0)
        grid.addWidget(self.formulae, 2, 1, 1, 2)
        grid.addWidget(roots, 3, 0)
        grid.addWidget(self.output, 3, 1, 1, 2)
        grid.addWidget(solve_button, 4, 1)
        grid.addWidget(exit_button, 4, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 100)
        self.setFixedSize(450, 170)
        self.setWindowTitle('EqSolver')
        self.show()
        self.formulae.setFocus()

    def _solve_button_clicked(self):
        """Слот, обрабатывающий нажатие кнопки 'Решить'."""
        # Обработка исключения BadEquationError.
        try:
            self.equation.set_function(self.formulae.text())
        except BadEquationError as exc:
            self.output.setText(str(exc))
        # Если исключения не было.
        else:
            self.equation.solve()
            output = ''
            for solution in self.equation.solutions:
                output += ('{: .' + PRECISION + '}\n').format(solution)
            self.output.setText(output)


# Если скрипт запущен как программа.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    eqSolver = EqSolver()
    sys.exit(app.exec_())
