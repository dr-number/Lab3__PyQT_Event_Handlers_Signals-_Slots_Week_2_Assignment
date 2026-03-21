import sys
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QPushButton, QMessageBox, QLineEdit, QTextEdit,
    QButtonGroup, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QIcon, QKeyEvent
import os

# Класс для создания элементов UI 
class WidgetFactory:
    @staticmethod
    def create_label(text: str, parent: QWidget) -> QLabel:
        return QLabel(text, parent)

    @staticmethod
    def create_radio_button(text: str, parent: QWidget) -> QRadioButton:
        radio_button = QRadioButton(text, parent)
        return radio_button

    @staticmethod
    def create_line_edit(parent: QWidget) -> QLineEdit:
        line_edit = QLineEdit(parent)
        line_edit.setPlaceholderText("Введите сумму расхода")
        return line_edit

    @staticmethod
    def create_button(text: str, parent: QWidget) -> QPushButton:
        button = QPushButton(text, parent)
        return button

    @staticmethod
    def create_text_edit(parent: QWidget) -> QTextEdit:
        text_edit = QTextEdit(parent)
        text_edit.setReadOnly(True)
        return text_edit

# Класс для управления категориями расходов
class ExpenseManager:
    def __init__(self):
        self.expenses: Dict[str, float] = {
            "Продукты": 0.0,
            "Транспорт": 0.0,
            "Развлечения": 0.0,
            "Коммунальные услуги": 0.0,
            "Другое": 0.0
        }
    
    def add_expense(self, category: str, amount: float) -> bool:
        if category in self.expenses and amount > 0:
            self.expenses[category] += amount
            return True
        return False
    
    def get_total_expenses(self) -> float:
        return sum(self.expenses.values())
    
    def get_expenses_summary(self) -> str:
        summary = "=== Расходы по категориям ===\n\n"
        for category, amount in self.expenses.items():
            if amount > 0:
                summary += f"{category}: {amount:.2f} руб.\n"
            else:
                summary += f"{category}: 0.00 руб.\n"
        summary += f"\nОбщая сумма расходов: {self.get_total_expenses():.2f} руб."
        return summary

# Класс для выбора категории
class CategorySelector:
    def __init__(self, radio_buttons: Dict[str, QRadioButton]):
        self.radio_buttons = radio_buttons
        self.selected_category = None
    
    def get_selected_category(self) -> Optional[str]:
        for category, button in self.radio_buttons.items():
            if button.isChecked():
                self.selected_category = category
                return category
        return None
    
    def set_default_category(self, category: str):
        if category in self.radio_buttons:
            self.radio_buttons[category].setChecked(True)

# Основное окно приложения
class ExpenseTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.expense_manager = ExpenseManager()
        self.init_ui()
        self.category_selector = CategorySelector(self.category_buttons)
        self.category_selector.set_default_category("Продукты")
    
    def init_ui(self):
        # Создание элементов интерфейса через фабрику
        # Заголовок с CSS стилями
        self.title_label = WidgetFactory.create_label("Ежедневный учет расходов", self)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                text-align: center;
            }
        """)
        
        # Поле для ввода суммы с иконкой
        self.amount_input = WidgetFactory.create_line_edit(self)
        
        # Группа для категорий
        category_group = QGroupBox("Выберите категорию расхода", self)
        category_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        category_layout = QVBoxLayout()
        categories = ["Продукты", "Транспорт", "Развлечения", "Коммунальные услуги", "Другое"]
        self.category_buttons = {}
        
        for category in categories:
            radio_button = WidgetFactory.create_radio_button(category, self)
            self.category_buttons[category] = radio_button
            category_layout.addWidget(radio_button)
        
        category_group.setLayout(category_layout)
        
        # Кнопка добавления расхода с иконкой
        self.add_button = WidgetFactory.create_button("Добавить расход", self)
        # Установка иконки (используем стандартную иконку из PyQt6)
        self.add_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogContentsView')))
        self.add_button.clicked.connect(self.add_expense)
        
        # Кнопка показа общей суммы
        self.show_total_button = WidgetFactory.create_button("Показать общую сумму", self)
        self.show_total_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
        self.show_total_button.clicked.connect(self.show_total_expenses)
        
        # Текстовое поле для отображения расходов
        self.display_area = WidgetFactory.create_text_edit(self)
        self.display_area.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)
        
        # Обновление отображения
        self.update_display()
        
        # Настройка компоновки
        main_layout = QVBoxLayout()
        
        # Верхняя часть
        main_layout.addWidget(self.title_label)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        amount_label = WidgetFactory.create_label("Сумма (руб.):", self)
        input_layout.addWidget(amount_label)
        input_layout.addWidget(self.amount_input)
        main_layout.addLayout(input_layout)
        
        # Категории
        main_layout.addWidget(category_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.show_total_button)
        main_layout.addLayout(buttons_layout)
        
        # Область отображения
        main_layout.addWidget(self.display_area)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Учет ежедневных расходов")
        self.setMinimumSize(500, 600)
        
        # Установка фокуса на поле ввода
        self.amount_input.setFocus()
    
    def add_expense(self):
        """Добавление расхода"""
        try:
            amount_text = self.amount_input.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "Предупреждение", "Введите сумму расхода!")
                return
            
            amount = float(amount_text)
            if amount <= 0:
                QMessageBox.warning(self, "Предупреждение", "Сумма должна быть положительной!")
                return
            
            selected_category = self.category_selector.get_selected_category()
            if not selected_category:
                QMessageBox.warning(self, "Предупреждение", "Выберите категорию расхода!")
                return
            
            # Добавление расхода
            if self.expense_manager.add_expense(selected_category, amount):
                QMessageBox.information(
                    self, 
                    "Успешно", 
                    f"Расход {amount:.2f} руб. добавлен в категорию '{selected_category}'"
                )
                self.amount_input.clear()
                self.update_display()
                self.amount_input.setFocus()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить расход!")
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму (число)!")
    
    def show_total_expenses(self):
        """Отображение общей суммы расходов"""
        total = self.expense_manager.get_total_expenses()
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Общая сумма расходов")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"Общая сумма всех расходов: {total:.2f} руб.")
        message_box.exec()
    
    def update_display(self):
        """Обновление текстового поля с расходами"""
        summary = self.expense_manager.get_expenses_summary()
        self.display_area.clear()
        self.display_area.append(summary)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Добавление расхода по нажатию Enter
            self.add_expense()
        elif event.key() == Qt.Key.Key_T:
            # Показать общую сумму по нажатию 'T'
            self.show_total_expenses()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExpenseTrackerApp()
    window.show()
    sys.exit(app.exec())