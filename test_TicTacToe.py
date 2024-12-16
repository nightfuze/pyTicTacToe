import os
import unittest

from main import TicTacToe, ModeState, AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.auth_service = AuthService()
        self.test_users_file = "test_users.json"
        self.auth_service.users_file = self.test_users_file

    def tearDown(self):
        # Удаляем тестовый файл после тестов
        if os.path.exists(self.test_users_file):
            os.remove(self.test_users_file)

    def test_register(self):
        # Тест успешной регистрации
        success, message = self.auth_service.register("testuser", "password123", "password123")
        self.assertTrue(success)
        self.assertEqual(message, "Успешная регистрация")

        # Тест регистрации существующего пользователя
        success, message = self.auth_service.register("testuser", "password123", "password123")
        self.assertFalse(success)

        # Тест регистрации с несовпадающими паролями
        success, message = self.auth_service.register("newuser", "pass1", "pass2")
        self.assertFalse(success)

    def test_login(self):
        # Регистрируем тестового пользователя
        self.auth_service.register("testuser", "password123", "password123")

        # Тест успешного входа
        success, message = self.auth_service.login("testuser", "password123")
        self.assertTrue(success)

        # Тест входа с неверным паролем
        success, message = self.auth_service.login("testuser", "wrongpass")
        self.assertFalse(success)

        # Тест входа несуществующего пользователя
        success, message = self.auth_service.login("nonexistent", "password123")
        self.assertFalse(success)

    def test_password_hashing(self):
        # Тест хеширования пароля
        password = "testpass123"
        hashed = AuthService.hash_password(password)
        self.assertTrue(AuthService.verify_password(password, hashed))
        self.assertFalse(AuthService.verify_password("wrongpass", hashed))

    def test_save_load_users(self):
        # Тест сохранения и загрузки пользователей
        self.auth_service.register("testuser", "password123", "password123")
        self.auth_service.save_users()

        # Создаем новый экземпляр сервиса для загрузки данных
        new_service = AuthService()
        new_service.users_file = self.test_users_file
        new_service.load_users()

        self.assertIn("testuser", new_service.users)


class TestTicTacToe(unittest.TestCase):
    def setUp(self):
        # Создаем две игры с разными режимами для тестирования
        self.game_vs_computer = TicTacToe(mode=ModeState.computer)
        self.game_vs_player = TicTacToe(mode=ModeState.player)

    def test_initialization(self):
        """Тест инициализации игры"""
        # Проверка режима против компьютера
        self.assertEqual(self.game_vs_computer.size, 10)
        self.assertEqual(self.game_vs_computer.current_player, 1)
        self.assertEqual(self.game_vs_computer.winning_length, 5)
        self.assertEqual(self.game_vs_computer.mode, ModeState.computer)
        self.assertFalse(self.game_vs_computer.game_over)
        self.assertEqual(self.game_vs_computer.moves, 0)

        # Проверка режима против игрока
        self.assertEqual(self.game_vs_player.size, 10)
        self.assertEqual(self.game_vs_player.current_player, 1)
        self.assertEqual(self.game_vs_player.mode, ModeState.player)
        self.assertFalse(self.game_vs_player.game_over)

    def test_make_move_vs_computer(self):
        """Тест ходов в режиме против компьютера"""
        # Ход игрока
        self.assertTrue(self.game_vs_computer.make_move(0, 0))
        self.assertEqual(self.game_vs_computer.board[0][0], 1)

        # Проверка, что после хода игрока компьютер сделал свой ход
        computer_moved = False
        for row in self.game_vs_computer.board:
            if -1 in row:
                computer_moved = True
                break
        self.assertTrue(computer_moved)

        # Попытка хода в занятую клетку
        self.assertFalse(self.game_vs_computer.make_move(0, 0))

    def test_make_move_vs_player(self):
        """Тест ходов в режиме против игрока"""
        # Ход первого игрока
        self.assertTrue(self.game_vs_player.make_move(0, 0))
        self.assertEqual(self.game_vs_player.board[0][0], 1)
        self.assertEqual(self.game_vs_player.current_player, -1)

        # Ход второго игрока
        self.assertTrue(self.game_vs_player.make_move(0, 1))
        self.assertEqual(self.game_vs_player.board[0][1], -1)
        self.assertEqual(self.game_vs_player.current_player, 1)

    def test_check_winner_horizontal(self):
        """Тест проверки победителя по горизонтали"""
        # Создаем выигрышную комбинацию по горизонтали
        for i in range(5):
            self.game_vs_player.board[0][i] = 1
        self.assertTrue(self.game_vs_player.check_winner(1))

    def test_check_winner_vertical(self):
        """Тест проверки победителя по вертикали"""
        # Создаем выигрышную комбинацию по вертикали
        for i in range(5):
            self.game_vs_player.board[i][0] = 1
        self.assertTrue(self.game_vs_player.check_winner(1))

    def test_check_winner_diagonal(self):
        """Тест проверки победителя по диагонали"""
        # Создаем выигрышную комбинацию по диагонали
        for i in range(5):
            self.game_vs_player.board[i][i] = 1
        self.assertTrue(self.game_vs_player.check_winner(1))

    def test_check_winner_reverse_diagonal(self):
        """Тест проверки победителя по обратной диагонали"""
        # Создаем выигрышную комбинацию по обратной диагонали
        for i in range(5):
            self.game_vs_player.board[i][4 - i] = 1
        self.assertTrue(self.game_vs_player.check_winner(1))

    def test_is_moves_left(self):
        """Тест проверки оставшихся ходов"""
        # Заполняем все поле
        for i in range(self.game_vs_player.size):
            for j in range(self.game_vs_player.size):
                self.game_vs_player.board[i][j] = 1
        self.assertTrue(self.game_vs_player.is_moves_left())

    def test_computer_strategy(self):
        """Тест стратегии компьютера"""
        # Создаем ситуацию, где компьютер должен заблокировать победу игрока
        for i in range(4):
            self.game_vs_computer.board[0][i] = 1

        # Делаем ход и проверяем, что компьютер заблокировал победу
        self.game_vs_computer.current_player = -1
        self.game_vs_computer.make_computer_move()
        blocked = False
        if self.game_vs_computer.board[0][4] == -1:
            blocked = True
        self.assertTrue(blocked)

    def test_game_over_state(self):
        """Тест состояния окончания игры"""
        # Создаем победную комбинацию
        for i in range(5):
            self.game_vs_player.board[0][i] = 1

        # Делаем ход и проверяем, что игра завершилась
        self.game_vs_player.make_move(1, 0)
        self.assertTrue(self.game_vs_player.game_over)

    def test_evaluate_position(self):
        """Тест оценки позиции"""
        # Проверяем начальную позицию
        self.assertEqual(self.game_vs_computer.evaluate_position(), 0)

        # Создаем преимущество для игрока
        for i in range(3):
            self.game_vs_computer.board[0][i] = 1
        self.assertNotEqual(self.game_vs_computer.evaluate_position(), 0)

    def test_get_valid_moves(self):
        """Тест получения возможных ходов"""
        # Проверяем количество возможных ходов в начале игры
        moves = self.game_vs_computer.get_valid_moves()
        self.assertEqual(len(moves), 1)  # В начале игры предлагается ход в центр

        # Делаем ход и проверяем, что появились новые возможные ходы
        self.game_vs_computer.make_move(5, 5)
        moves = self.game_vs_computer.get_valid_moves()
        self.assertTrue(len(moves) > 1)


if __name__ == '__main__':
    unittest.main()
