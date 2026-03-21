import sys
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QPushButton, QMessageBox, QLineEdit, QTextEdit,
    QGroupBox, QStyle
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

# Класс для создания элементов UI 
class WidgetFactory:
    @staticmethod
    def create_label(text: str, parent: QWidget) -> QLabel:
        return QLabel(text, parent)

    @staticmethod
    def create_radio_button(text: str, parent: QWidget) -> QRadioButton:
        return QRadioButton(text, parent)

    @staticmethod
    def create_line_edit(title: str, parent: QWidget) -> QLineEdit:
        line_edit = QLineEdit(parent)
        line_edit.setPlaceholderText(title)
        return line_edit

    @staticmethod
    def create_button(
        text: str, 
        parent: QWidget, 
        icon: QStyle.StandardPixmap = None,
        slot = None,
        tip: str = ''
        ) -> QPushButton:
        button = QPushButton(text, parent)
        if icon:
            button.setIcon(parent.style().standardIcon(icon))
        if slot:
            button.clicked.connect(slot)
        if tip:
            button.setToolTip(tip)
        return button

    @staticmethod
    def create_text_edit(parent: QWidget, is_read_only: bool = False) -> QTextEdit:
        text_edit = QTextEdit(parent)
        text_edit.setReadOnly(is_read_only)
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
        self.category_selector.set_default_category(category="Продукты")
    
    def init_ui(self):
        self.title_label = WidgetFactory.create_label(text="Ежедневный учет расходов", parent=self)
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
        
        self.amount_input = WidgetFactory.create_line_edit(title="Введите сумму расхода", parent=self)

        category_group = QGroupBox(title="Выберите категорию расхода", parent=self)
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
            radio_button = WidgetFactory.create_radio_button(text=category, parent=self)
            self.category_buttons[category] = radio_button
            category_layout.addWidget(radio_button)
        
        category_group.setLayout(category_layout)
        
        self.add_button = WidgetFactory.create_button(
            text="Добавить расход", 
            icon=QStyle.StandardPixmap.SP_DialogApplyButton,
            parent=self,
            slot=self.add_expense,
            tip="Нажмите Enter, чтобы добавить расход"
        )
        self.show_total_button = WidgetFactory.create_button(
            text="Показать общую сумму",
            icon=QStyle.StandardPixmap.SP_MessageBoxInformation,
            parent=self,
            slot=self.show_total_expenses,
            tip="Нажмите Alt, чтобы показать общую сумму"
        )
        self.clear_button = WidgetFactory.create_button(
            text="Очистить все расходы", 
            icon=QStyle.StandardPixmap.SP_DialogResetButton,
            parent=self,
            slot=self.clear_all_expenses,
            tip="Нажмите Ctrl, чтобы очистить все расходы"
        )
        
        self.display_area = WidgetFactory.create_text_edit(parent=self, is_read_only=True)
        self.display_area.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)
        
        self.update_display()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        
        input_layout = QHBoxLayout()
        amount_label = WidgetFactory.create_label("Сумма (руб.):", self)
        input_layout.addWidget(amount_label)
        input_layout.addWidget(self.amount_input)
        main_layout.addLayout(input_layout)
        
        main_layout.addWidget(category_group)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.show_total_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(self.display_area)
        
        self.setLayout(main_layout)
        self.setWindowTitle("510З_Ларионов_НЮ_вариант_№12_2_Вариант__Калькулятор_расходов")
        self.setMinimumSize(500, 600)
        
        self.amount_input.setFocus()
    
    def add_expense(self):
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
        total = self.expense_manager.get_total_expenses()
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Общая сумма расходов")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText(f"Общая сумма всех расходов: {total:.2f} руб.")
        message_box.exec()
    
    def clear_all_expenses(self):
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы уверены, что хотите очистить все расходы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for category in self.expense_manager.expenses:
                self.expense_manager.expenses[category] = 0.0
            self.update_display()
            QMessageBox.information(self, "Успешно", "Все расходы очищены!")
    
    def update_display(self):
        """Обновление текстового поля с расходами"""
        summary = self.expense_manager.get_expenses_summary()
        self.display_area.clear()
        self.display_area.append(summary)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.add_expense()
        elif event.key() == Qt.Key.Key_Alt:
            self.show_total_expenses()
        elif event.key() == Qt.Key.Key_Control:
            self.clear_all_expenses()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExpenseTrackerApp()
    window.show()
    sys.exit(app.exec())
