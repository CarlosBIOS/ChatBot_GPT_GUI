from PyQt6.QtWidgets import QMainWindow, QApplication, QTextEdit, QLineEdit, QPushButton, QMessageBox, QStatusBar
from PyQt6.QtGui import QAction
import sys
from os import getenv
from groq import Groq
import threading


class ChatBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chatbot = ChatBot()

        self.setWindowTitle('ChatBot')

        help_menu_item = self.menuBar().addMenu('&Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        # Add chat area widget:
        self.chat_area = QTextEdit(self)
        font = self.chat_area.font()
        font.setPointSize(20)
        self.chat_area.setFont(font)
        self.chat_area.setReadOnly(True)
        # 10 significa o padx, ou seja, distância da borda no x e do y. 480 de 700 e 320 de 500
        self.chat_area.setGeometry(40, 50, 1450, 700)

        # Add the input field widget
        self.input_field = QLineEdit(self)
        font = self.input_field.font()
        font.setPointSize(23)  # Altere o tamanho da fonte aqui (por exemplo, 16)
        self.input_field.setFont(font)
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setGeometry(40, 770, 1350, 60)

        # Add the button
        self.button = QPushButton('Send', self)
        self.button.setGeometry(1400, 770, 90, 60)
        self.button.clicked.connect(self.send_message)

        self.showFullScreen()  # Usamos este método quando não existe setCenterWidget, como foi no student management

    def send_message(self):
        user_input: str = self.input_field.text().strip()
        if user_input.casefold() == 'clear':
            self.chat_area.clear()
        elif user_input.casefold() == 'exit':
            sys.exit(app.exec())
        else:
            self.chat_area.append(f'<p style="color:#008000">Me: {user_input}</p>')

            thread = threading.Thread(target=self.get_bot_response, args=(user_input, ))
            thread.start()

        self.input_field.clear()

    def get_bot_response(self, user_input):
        response = self.chatbot.get_response(user_input).replace('\n\n', '\n')

        for paragraph in response.split("\n"):
            self.chat_area.append(f'<p style="color:#FFD700; background-colour: #E9E9E9">{paragraph}</p>')
        else:
            self.chat_area.append('<p style="color:#FFD700; background-colour: #E9E9E9">\n</p>')

    @staticmethod
    def about():
        about = AboutDialog()
        about.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        content: str = ("This application was created to assist you. It's inspired by "
                        "ChatGPT and allows you to interact in a natural language way.\n\n"
                        "**Features:**\n"
                        "- Ask questions and receive informative responses.\n"
                        "- Clear the chat history by typing 'clear'.\n"
                        "- Exit the program by typing 'exit'.\n\n"
                        "Developed by: Carlos Monteiro\n"
                        "Version: 1.0\n")
        self.setText(content)


class ChatBot:
    def __init__(self):
        self.client = Groq(
            api_key=getenv("key_grog"),
        )
        self.system_prompt = {
            "role": "system",
            "content": "You are a helpful assistant."
        }
        self.chat_history = [self.system_prompt]

    def get_response(self, user_input: str):
        # Append the user input to the chat history
        self.chat_history.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(model="llama3-70b-8192", messages=self.chat_history,
                                                       max_tokens=1000, temperature=1.2)
        # Append the response to the chat history
        self.chat_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        return "Assistant: " + response.choices[0].message.content


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ChatBotWindow()
    sys.exit(app.exec())
