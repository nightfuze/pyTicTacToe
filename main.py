import tkinter as tk
from enum import Enum
from tkinter import ttk


class ModeState(Enum):
    computer = "Против компьютера"
    player = "Против игрока"


class TicTacToe:
    def __init__(self, size=15, mode: ModeState = ModeState.computer):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.current_player = 1
        self.winning_length = 5
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        self.mode = mode
        self.game_over = False

    def make_move(self, row, col) -> bool:
        """Сделать ход."""
        if self.game_over:
            return False
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player
            self.current_player = -self.current_player
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
                1: 50 if not current_player else 100000000,     # Один открытый конец
                2: 500000 if not current_player else 100000000  # Два открытых конца
            },
            # 3 фигуры в ряд
            3: {
                1: 5 if not current_player else 7,           # Один открытый конец
                2: 50 if not current_player else 10000       # Два открытых конца
            },
            # 2 фигуры в ряд
            2: {
                1: 2,   # Один открытый конец
                2: 5    # Два открытых конца
            },
            # 1 фигура в ряд
            1: {
                1: 0.5,  # Один открытый конец
                2: 1     # Два открытых конца
            }
        }

        if consecutive >= 5:
            # Выигрышная последовательность
            return 200000000

        return scores.get(consecutive, {}).get(open_ends, 0)

    def analyze_direction(self, row, col, direction, player):
        """Анализирует линию в заданном направлении для подсчета очков."""
        consecutive = 0     # Счетчик последовательных фигур
        open_ends = 0       # Счетчик открытых концов
        score = 0           # Оценка линии

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

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] != 0:
                    player = self.board[row][col]
                    for direction in self.directions:
                        score += self.analyze_direction(row, col, direction, player) * player

        return score

    def get_valid_moves(self):
        """Получает список возможных ходов, приоритизируя ходы рядом с существующими фигурами."""
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0 and self.has_neighbor(row, col):
                    valid_moves.append((row, col))
        return valid_moves if valid_moves else [(self.size // 2, self.size // 2)]

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

    def minimax(self, depth, alpha, beta, maximizing_player):
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
        _, move = self.minimax(2, float('-inf'), float('inf'), True)
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


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-Нолики до 5 в ряд")

        self.game = TicTacToe()
        self.cell_size = 40
        self.game_mode = ModeState.computer

        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.mode_var = tk.StringVar(value=ModeState.computer.value)
        self.mode_label = tk.Label(self.control_frame, text="Режим игры:")
        self.mode_label.grid(row=0, column=0, padx=(0, 10))

        self.mode_menu = ttk.OptionMenu(
            self.control_frame,
            self.mode_var,
            ModeState.computer.value,
            *[mode.value for mode in ModeState],
            command=self.change_mode
        )
        self.mode_menu.grid(row=0, column=1)

        self.reset_button = tk.Button(self.control_frame, text="Новая игра", command=self.reset_game)
        self.reset_button.grid(row=0, column=2, padx=(20, 0))

        self.status_var = tk.StringVar(value="X - ход")
        self.status_label = tk.Label(self.control_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=3, padx=(20, 0))

        canvas_size = self.cell_size * self.game.size
        self.canvas = tk.Canvas(
            self.main_frame,
            width=canvas_size,
            height=canvas_size,
            bg="white"
        )
        self.canvas.grid(row=1, column=0)
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

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
            self.draw_board()
            if self.game.check_winner(1):
                x, y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
                self.canvas.create_text(x, y, text="Крестики победили!", font="Arial 32")
            elif self.game.check_winner(-1):
                x, y = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
                self.canvas.create_text(x, y, text="Нолики победили!", font="Arial 32")

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
        self.status_var.set("X - ход")

    def update_status(self):
        """Обновление состояния игры."""
        if self.game.game_over:
            winner = "X" if self.game.current_player == -1 else "O"
            self.status_var.set(f"{winner} победили!")
        else:
            current = "X" if self.game.current_player == 1 else "O"
            self.status_var.set(f"{current} - ход")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    app.run()