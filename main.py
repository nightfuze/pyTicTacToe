import hashlib
import json
import os
import time
import tkinter as tk
from enum import Enum
from tkinter import ttk, messagebox


class ModeState(Enum):
    computer = "Против компьютера"
    player = "Против игрока"


class TicTacToe:
    def __init__(self, size=10, mode: ModeState = ModeState.computer):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.current_player = 1
        self.winning_length = 5
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        self.mode = mode
        self.game_over = False
        self.moves = 0

    def is_moves_left(self) -> bool:
        """Проверка, на оставшиеся ходы"""
        for row in self.board:
            if row.count(0):
                return False
        return True

    def make_move(self, row, col) -> bool:
        """Сделать ход."""
        if self.game_over:
            return False
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player
            self.current_player = -self.current_player
            self.moves += 1
            if self.mode == ModeState.computer and self.current_player == -1:
                self.make_computer_move()
            if self.check_winner(1) or self.check_winner(-1):
                self.game_over = True
            return True
        return False

    def make_computer_move(self):
        """Сделать ход компьютера."""
        row, col = self.get_best_move()
        self.make_move(row, col)

    def evaluate_shape(self, consecutive, open_ends, current_player):
        """Оценивает комбинацию на основе последовательных фигур и открытых концов."""
        if open_ends == 0 and consecutive < 5:
            # Если нет открытых концов и менее 5 в ряд - комбинация бесполезна
            return 0

        scores = {
            # 4 фигуры в ряд
            4: {
                1: 50 if not current_player else 100000000,  # Один открытый конец
                2: 500000 if not current_player else 100000000  # Два открытых конца
            },
            # 3 фигуры в ряд
            3: {
                1: 5 if not current_player else 7,  # Один открытый конец
                2: 50 if not current_player else 10000  # Два открытых конца
            },
            # 2 фигуры в ряд
            2: {
                1: 2,  # Один открытый конец
                2: 5  # Два открытых конца
            },
            # 1 фигура в ряд
            1: {
                1: 0.5,  # Один открытый конец
                2: 1  # Два открытых конца
            }
        }

        if consecutive >= 5:
            # Выигрышная последовательность
            return 200000000

        return scores.get(consecutive, {}).get(open_ends, 0)

    def analyze_direction(self, row, col, direction, player):
        """Анализирует линию в заданном направлении для подсчета очков."""
        consecutive = 0  # Счетчик последовательных фигур
        open_ends = 0  # Счетчик открытых концов
        score = 0  # Оценка линии

        # Проверка открытого конца сзади
        prev_row = row - direction[0]
        prev_col = col - direction[1]
        if (0 <= prev_row < self.size and
                0 <= prev_col < self.size and
                self.board[prev_row][prev_col] == 0):
            open_ends += 1

        # Подсчет последовательных фигур
        while (0 <= row < self.size and
               0 <= col < self.size and
               self.board[row][col] == player):
            consecutive += 1
            row += direction[0]
            col += direction[1]

        # Проверка открытого конца спереди
        if (0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == 0):
            open_ends += 1

        if consecutive > 0:
            # Если есть последовательные фигуры, тогда оцениваем комбинацию на основе последовательных фигур и открытых концов
            score = self.evaluate_shape(consecutive, open_ends, player == self.current_player)

        return score

    def evaluate_position(self):
        """Оценка всех позиций."""
        score = 0
        checked_lines = set()

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] != 0:
                    player = self.board[row][col]
                    for direction in self.directions:
                        line_key = (row, col, direction[0], direction[1])
                        if line_key not in checked_lines:
                            checked_lines.add(line_key)
                            score += self.analyze_direction(row, col, direction, player) * player

        return score

    def get_valid_moves(self):
        """Получает список возможных ходов с приоритизацией и исключением бесполезных ходов"""
        moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    priority = 0
                    # Проверяем соседние клетки в радиусе 2
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            r, c = row + dr, col + dc
                            if 0 <= r < self.size and 0 <= c < self.size:
                                if self.board[r][c] != 0:
                                    # Ближайшие соседи имеют больший вес
                                    priority += 3 if abs(dr) <= 1 and abs(dc) <= 1 else 1

                    if priority > 0:
                        moves.append((priority, row, col))

        moves.sort(reverse=True)
        return [(row, col) for _, row, col in moves] if moves else [(self.size // 2, self.size // 2)]

    def has_neighbor(self, row, col):
        """Проверка, есть ли рядом фигура."""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if (0 <= r < self.size and
                        0 <= c < self.size and
                        self.board[r][c] != 0):
                    return True
        return False

    def minimax(self, depth, alpha=float('-inf'), beta=float('inf'), maximizing_player=False):
        """Минимакс алгоритм для выбора наилучшего хода."""
        if depth == 0:
            return self.evaluate_position(), None

        valid_moves = self.get_valid_moves()
        print(len(valid_moves))
        if not valid_moves:
            return 0, None

        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                self.board[move[0]][move[1]] = 1
                eval_score, _ = self.minimax(depth - 1, alpha, beta, False)
                self.board[move[0]][move[1]] = 0

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                self.board[move[0]][move[1]] = -1
                eval_score, _ = self.minimax(depth - 1, alpha, beta, True)
                self.board[move[0]][move[1]] = 0

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_best_move(self):
        """Вычисление лучшего хода для компьютера."""
        _, move = self.minimax(2)
        return move

    def check_winner(self, player):
        """Проверка выиграл ли игрок."""
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:
                    for direction in self.directions:
                        count = 1
                        r, c = row + direction[0], col + direction[1]

                        while (0 <= r < self.size and
                               0 <= c < self.size and
                               self.board[r][c] == player):
                            count += 1
                            if count == self.winning_length:
                                return True
                            r += direction[0]
                            c += direction[1]
        return False


class AuthService:
    def __init__(self):
        self.users_file = "users.json"
        self.users = {}
        self.load_users()

    def login(self, username, password):
        if username not in self.users:
            return False, "Неверное имя пользователя"

        if AuthService.verify_password(password, self.users[username]):
            return True, "Успешный вход"

        return False, "Неверный пароль"

    def register(self, username, password, confirm_password):
        if username in self.users:
            return False, "Такое имя пользователя уже зарегистрировано"

        if password != confirm_password:
            return False, "Пароли не совпадают"

        self.users[username] = AuthService.hash_password(password)
        self.save_users()

        return True, "Успешная регистрация"

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed_password):
        return AuthService.hash_password(password) == hashed_password

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f)

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                self.users = json.load(f)


class AuthWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.transient(root)

        self.auth_service = AuthService()

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        self.fields = {}

    def create_field(self, label, field):
        frame = tk.Frame(self.main_frame)
        frame.pack(fill=tk.X, pady=10)

        label = tk.Label(frame, text=label)
        label.pack(anchor=tk.W)

        entry = tk.Entry(frame)
        entry.pack(fill=tk.X, expand=True)

        error_label = tk.Label(frame, text="", fg="red")
        error_label.pack(anchor=tk.W)

        self.fields[field] = (entry, error_label)

    def get_field(self, field):
        return self.fields[field][0].get()

    def hide_input(self, field):
        self.fields[field][0].config(show="*")

    def show_input(self, field):
        self.fields[field][0].config(show="")

    def show_error(self, field, message):
        self.fields[field][1].config(text=message)

    def clear_error(self, field):
        self.fields[field][1].config(text="")


class LoginWindow(AuthWindow):
    def __init__(self, root, on_success=None):
        super().__init__(root)
        self.title("Авторизация")
        self.geometry("300x300")

        self.create_field("Имя пользователя:", "username")
        self.create_field("Пароль:", "password")
        self.hide_input("password")
        self.on_success = on_success

        show_password_var = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(
            self.main_frame,
            text="Показать пароль",
            variable=show_password_var,
            command=lambda: self.toggle_password_visibility(show_password_var.get())
        )
        show_password_checkbox.pack(anchor=tk.W, pady=10)

        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=20)

        self.login_button = tk.Button(buttons_frame, text="Войти", command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        self.register_button = tk.Button(buttons_frame, text="Регистрация",
                                         command=self.show_register)
        self.register_button.pack(side=tk.LEFT, padx=5)

    def toggle_password_visibility(self, show_password):
        if show_password:
            self.show_input("password")
        else:
            self.hide_input("password")

    def login(self):
        username = self.get_field("username")
        password = self.get_field("password")

        self.clear_error("username")
        self.clear_error("password")

        if not username:
            self.show_error("username", "Введите имя пользователя")
            return
        if not password:
            self.show_error("password", "Введите пароль")
            return

        success, message = self.auth_service.login(username, password)
        if success:
            if self.on_success:
                self.on_success(username)
            self.destroy()
        else:
            if "пользователя" in message:
                self.show_error("username", message)
            else:
                self.show_error("password", message)

    def show_register(self):
        self.destroy()
        RegisterWindow(self.root, self.on_success)


class RegisterWindow(AuthWindow):
    def __init__(self, root, on_success=None):
        super().__init__(root)
        self.title("Регистрация")
        self.geometry("300x400")
        self.on_success = on_success

        self.create_field("Имя пользователя:", "username")
        self.create_field("Пароль:", "password")
        self.create_field("Подтвердите пароль:", "confirm_password")

        self.hide_input("password")
        self.hide_input("confirm_password")

        show_password_var = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(
            self.main_frame,
            text="Показать пароль",
            variable=show_password_var,
            command=lambda: self.toggle_password_visibility(show_password_var.get())
        )
        show_password_checkbox.pack(anchor=tk.W, pady=10)

        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=20)

        self.register_button = tk.Button(buttons_frame, text="Зарегистрироваться", command=self.register_user)
        self.register_button.pack(padx=5)

        self.back_button = tk.Button(buttons_frame, text="Назад", command=self.back_to_login)
        self.back_button.pack(padx=5)

    def toggle_password_visibility(self, show_password):
        if show_password:
            self.show_input("password")
            self.show_input("confirm_password")
        else:
            self.hide_input("password")
            self.hide_input("confirm_password")

    def register_user(self):
        username = self.get_field("username")
        password = self.get_field("password")
        confirm_password = self.get_field("confirm_password")

        for field in self.fields:
            self.clear_error(field)

        if not username:
            self.show_error("username", "Введите имя пользователя")
            return
        if len(username) < 3:
            self.show_error("username", "Имя пользователя должно быть не менее 3 символов")
            return

        if not password:
            self.show_error("password", "Введите пароль")
            return
        if len(password) < 6:
            self.show_error("password", "Пароль должен быть не менее 6 символов")
            return

        if not confirm_password:
            self.show_error("confirm_password", "Подтвердите пароль")
            return

        success, message = self.auth_service.register(username, password, confirm_password)
        if success:
            messagebox.showinfo("Успех", message)
            self.back_to_login()
        else:
            if "пользователя" in message:
                self.show_error("username", message)
            elif "Пароли" in message:
                self.show_error("confirm_password", message)
            else:
                self.show_error("password", message)

    def back_to_login(self):
        self.destroy()
        LoginWindow(self.root, self.on_success)


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-Нолики до 5 в ряд")

        self.game = TicTacToe()
        self.cell_size = 65
        self.game_mode = ModeState.computer
        self.start_time = None
        self.timer_id = None

        self.sidebar_frame = tk.Frame(self.root, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        settings_frame = tk.LabelFrame(self.sidebar_frame, text="Настройки игры", padx=10, pady=5)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        self.mode_label = tk.Label(settings_frame, text="Режим игры:")
        self.mode_label.pack(anchor=tk.W, pady=(5, 0))

        self.mode_var = tk.StringVar(value=ModeState.computer.value)
        self.mode_menu = ttk.OptionMenu(
            settings_frame,
            self.mode_var,
            ModeState.computer.value,
            *[mode.value for mode in ModeState],
            command=self.change_mode
        )
        self.mode_menu.pack(fill=tk.X, pady=(0, 10))

        control_frame = tk.LabelFrame(self.sidebar_frame, text="Управление", padx=10, pady=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.reset_button = tk.Button(control_frame, text="Новая игра", command=self.reset_game)
        self.reset_button.pack(fill=tk.X, pady=5)

        stats_frame = tk.LabelFrame(self.sidebar_frame, text="Статистика", padx=10, pady=5)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_var = tk.StringVar(value="Ход: X")
        self.status_label = tk.Label(stats_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W, pady=5)

        self.moves_var = tk.StringVar(value="Ходов: 0")
        self.moves_label = tk.Label(stats_frame, textvariable=self.moves_var)
        self.moves_label.pack(anchor=tk.W, pady=5)

        self.time_var = tk.StringVar(value="Время: 00:00")
        self.time_label = tk.Label(stats_frame, textvariable=self.time_var)
        self.time_label.pack(anchor=tk.W, pady=5)

        player_frame = tk.LabelFrame(self.sidebar_frame, text="Игрок", padx=10, pady=5)
        player_frame.pack(fill=tk.X, padx=5, pady=5)

        self.player_name_var = tk.StringVar(value="Гость")
        self.player_label = tk.Label(player_frame, textvariable=self.player_name_var)
        self.player_label.pack(anchor=tk.W, pady=5)

        self.logout_button = tk.Button(player_frame, text="Выйти", command=self.logout)
        self.logout_button.pack(fill=tk.X, pady=5)

        canvas_size = self.cell_size * self.game.size
        self.canvas = tk.Canvas(
            self.main_frame,
            width=canvas_size,
            height=canvas_size,
            bg="white"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

        LoginWindow(self.root, self.on_login)

    def draw_board(self):
        """Отрисовка игрового поля."""
        self.canvas.delete("all")

        for i in range(self.game.size + 1):
            self.canvas.create_line(
                i * self.cell_size, 0,
                i * self.cell_size, self.game.size * self.cell_size,
                fill="gray"
            )
            self.canvas.create_line(
                0, i * self.cell_size,
                   self.game.size * self.cell_size, i * self.cell_size,
                fill="gray"
            )

        for row in range(self.game.size):
            for col in range(self.game.size):
                if self.game.board[row][col] == 1:
                    self.draw_player(row, col)
                elif self.game.board[row][col] == -1:
                    self.draw_opponent(row, col)

    def draw_player(self, row, col):
        """Отрисовка фигуры игрока."""
        x = col * self.cell_size
        y = row * self.cell_size
        padding = self.cell_size * 0.2
        color = "blue"
        thickness = 2
        self.canvas.create_line(
            x + padding, y + padding,
            x + self.cell_size - padding, y + self.cell_size - padding,
            width=thickness,
            fill=color
        )
        self.canvas.create_line(
            x + self.cell_size - padding, y + padding,
            x + padding, y + self.cell_size - padding,
            width=thickness,
            fill=color
        )

    def draw_opponent(self, row, col):
        """Отрисовка фигуры противника."""
        x = col * self.cell_size
        y = row * self.cell_size
        padding = self.cell_size * 0.2
        color = "red"
        thickness = 2
        self.canvas.create_oval(
            x + padding, y + padding,
            x + self.cell_size - padding, y + self.cell_size - padding,
            width=thickness,
            outline=color
        )

    def on_click(self, event):
        """Обработчик нажатия на игровое поле."""
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if self.game.make_move(row, col):
            self.moves_var.set(f"Ходов: {self.game.moves}")
            self.draw_board()
            if self.game.check_winner(1):
                # x, y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
                # self.canvas.create_text(x, y, text="Крестики победили!", font="Arial 32")
                messagebox.showinfo("Победа!", "Крестики победили!")
            elif self.game.check_winner(-1):
                # x, y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
                # self.canvas.create_text(x, y, text="Нолики победили!", font="Arial 32")
                messagebox.showinfo("Поражение!", "Нолики победили!")
            elif self.game.is_moves_left():
                messagebox.showinfo("Ничья!", "Ничья!")

    def change_mode(self, event):
        """Обработчик изменения режима игры."""
        print(self.mode_var.get())
        self.game_mode = ModeState(self.mode_var.get())
        self.reset_game()

    def change_size(self):
        """Обработчик изменения размера игрового поля."""
        self.game_size = self.size_var.get()
        self.reset_game()

    def reset_game(self):
        """Сброс игры."""
        self.game = TicTacToe(mode=self.game_mode)
        self.draw_board()
        self.moves_var.set(f"Ходов: {self.game.moves}")
        self.time_var.set(f"Время: 00:00")
        self.status_var.set("X - ход")
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        """Обновление таймера."""
        if self.start_time is None:
            self.start_time = time.time()

        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.time_var.set(f"Время: {minutes:02d}:{seconds:02d}")

        if not self.game.game_over:
            self.timer_id = self.root.after(1000, self.update_timer)

    def update_status(self):
        """Обновление состояния игры."""
        if self.game.game_over:
            winner = "X" if self.game.current_player == -1 else "O"
            self.status_var.set(f"{winner} победили!")
        else:
            current = "X" if self.game.current_player == 1 else "O"
            self.status_var.set(f"{current} - ход")

    def logout(self):
        self.player_name_var.set("Гость")
        LoginWindow(self.root, self.on_login)

    def on_login(self, username):
        self.player_name_var.set(username)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    app.run()
