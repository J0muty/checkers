import pygame
import sys
from pygame.locals import *
import tkinter as tk
from tkinter import ttk

pygame.init()


WIDTH, HEIGHT = 600, 600
CELL_SIZE = 75
ROWS, COLS = 8, 8
PIECE_SIZE = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 66, 66)
GREEN = (0, 255, 0)  # Цвет дамки

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers Game')

black_pieces = [{'position': pos, 'king': False} for pos in [
    (0, 1), (0, 3), (0, 5), (0, 7),
    (1, 0), (1, 2), (1, 4), (1, 6),
    (2, 1), (2, 3), (2, 5), (2, 7)
]]

white_pieces = [{'position': pos, 'king': False} for pos in [
    (5, 0), (5, 2), (5, 4), (5, 6),
    (6, 1), (6, 3), (6, 5), (6, 7),
    (7, 0), (7, 2), (7, 4), (7, 6)
]]

selected_piece = None
player_turn = WHITE

def draw_board():
    window.fill(RED)
    for row in range(ROWS):
        for col in range(row % 2, COLS, 2):
            pygame.draw.rect(window, BLACK, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_pieces():
    for piece in white_pieces + black_pieces:
        row, col = piece['position']
        color = WHITE if piece in white_pieces else BLACK
        pygame.draw.circle(window, color,
                           (int(col * CELL_SIZE + CELL_SIZE / 2), int(row * CELL_SIZE + CELL_SIZE / 2)),
                           PIECE_SIZE // 2)
        if piece['king']:
            pygame.draw.circle(window, GREEN,
                               (int(col * CELL_SIZE + CELL_SIZE / 2), int(row * CELL_SIZE + CELL_SIZE / 2)),
                               PIECE_SIZE // 2 - 10)

def check_pieces_left(color):
    if color == WHITE:
        return len([piece for piece in white_pieces if not piece.get('removed', False)])
    elif color == BLACK:
        return len([piece for piece in black_pieces if not piece.get('removed', False)])
    return 0
def get_clicked_cell(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def can_move(piece_dict, to_pos):
    from_pos, is_king = piece_dict['position'], piece_dict['king']

    # Проверка, что конечная позиция находится в пределах доски
    if to_pos[0] < 0 or to_pos[0] >= ROWS or to_pos[1] < 0 or to_pos[1] >= COLS:
        return False, []  # Конечная позиция вне доски

    occupied_positions = [p['position'] for p in white_pieces + black_pieces]
    if to_pos in occupied_positions:
        return False, []  # Клетка уже занята

    fr, fc = from_pos
    tr, tc = to_pos
    move_rows = abs(tr - fr)
    move_cols = abs(tc - fc)

    if move_rows != move_cols:
        return False, []  # Ход не по диагонали

    step_r = 1 if tr > fr else -1
    step_c = 1 if tc > fc else -1
    r, c = fr, fc

    opponents_captured = []
    meet_opponent = False
    while (r + step_r, c + step_c) != (tr, tc):
        r += step_r
        c += step_c
        if (r, c) in occupied_positions:
            piece_at_pos = next((p for p in white_pieces + black_pieces if p['position'] == (r, c)), None)
            if piece_at_pos and piece_at_pos in (white_pieces if player_turn == BLACK else black_pieces):
                if meet_opponent:  # Второй оппонент встреченный на пути не допустим
                    return False, []
                meet_opponent = True
                opponents_captured.append(piece_at_pos)
            else:
                return False, []  # Путь блокирован

    # Проверка движения для обычных шашек (не королей)
    if not is_king:
        direction_correct = (player_turn == WHITE and fr > tr) or (player_turn == BLACK and fr < tr)
        valid_normal_move = move_rows == 1 and direction_correct
        valid_capture_move = move_rows == 2 and len(opponents_captured) == 1

        if not valid_normal_move and not valid_capture_move:
            return False, []

    if len(opponents_captured) > 1:
        return False, []

    return True, opponents_captured

player_turn = WHITE  # WHITE - белые шашки, BLACK - черные шашки

def switch_player_turn():
    global player_turn
def move_piece(piece_dict, end_pos):
    global player_turn

    move_possible, captured_pieces = can_move(piece_dict, end_pos)

    if (player_turn == WHITE and move_possible) or (player_turn == BLACK and move_possible):
        start_pos = piece_dict['position']
        pieces = white_pieces if piece_dict in white_pieces else black_pieces
        index = [p['position'] for p in pieces].index(start_pos)
        pieces[index]['position'] = end_pos
        piece_dict['position'] = end_pos  # Обновление положения пешки в piece_dict



        # Превращение в дамку
        if (pieces == white_pieces and end_pos[0] == 0) or (pieces == black_pieces and end_pos[0] == ROWS - 1):
            pieces[index]['king'] = True

        # Удаление съеденных шашек
        for piece in captured_pieces:
            if piece in white_pieces:
                white_pieces.remove(piece)
            elif piece in black_pieces:
                black_pieces.remove(piece)

        switch_player_turn()  # После успешного хода меняем активного игрока
        return True

    return False

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    global selected_piece, player_turn
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_clicked_cell(*event.pos)
                if player_turn == WHITE:
                    for piece in white_pieces:
                        if piece['position'] == (row, col):
                            selected_piece = piece
                else:
                    for piece in black_pieces:
                        if piece['position'] == (row, col):
                            selected_piece = piece

            if event.type == pygame.MOUSEBUTTONUP:
                if selected_piece:
                    row, col = get_clicked_cell(*event.pos)
                    if move_piece(selected_piece, (row, col)):
                        player_turn = WHITE if player_turn == BLACK else BLACK
            if check_pieces_left(BLACK) == 0:
                wait_for_enter("Победили белые", screen)
                break
            elif check_pieces_left(WHITE) == 0:
                wait_for_enter("Победили черные", screen)
                break

        def check_any_valid_moves(player_pieces, opponent_pieces):
            for piece in player_pieces:
                possible_moves = [
                    (piece['position'][0] + i, piece['position'][1] + j)
                    for i in (-1, 1)
                    for j in (-1, 1)
                ]
                for move in possible_moves:
                    valid_move, _ = can_move(piece, move)
                    if valid_move:
                        return True  # Найден хотя бы один допустимый ход
            return False  # Нет возможных ходов, проигрыш

        def game_loop():
            global player_turn
            player_pieces = white_pieces if player_turn == WHITE else black_pieces
            opponent_pieces = black_pieces if player_turn == WHITE else white_pieces

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                    if event.type == pygame.MOUSEBUTTONUP:
                        if selected_piece:
                            row, col = get_clicked_cell(*event.pos)
                            if move_piece(selected_piece, (row, col)):
                                # Проверка окончания хода и возможности следующего хода
                                player_turn = WHITE if player_turn == BLACK else BLACK
                                next_player_pieces = white_pieces if player_turn == WHITE else black_pieces
                                next_opponent_pieces = black_pieces if player_turn == WHITE else white_pieces
                                if not check_any_valid_moves(next_player_pieces, next_opponent_pieces):
                                    winner = "белые" if player_turn == BLACK else "черные"
                                    wait_for_enter(f"Победили {winner}", screen)
                                    return  # Завершаем игру
                if __name__ == "__main__":
                    game_loop()

                draw_board()
                draw_pieces()
                pygame.display.flip()
            # Здесь задаётся текущий игрок и его шашки, а также шашки противника
        player_pieces = white_pieces if player_turn == WHITE else black_pieces
        opponent_pieces = black_pieces if player_turn == WHITE else white_pieces

        # Проверка на наличие возможных ходов
        if not check_any_valid_moves(player_pieces, opponent_pieces):
            print(f"Игрок {'WHITE' if player_turn == WHITE else 'BLACK'} проиграл, так как не имеет допустимых ходов.")
            break

        draw_board()
        draw_pieces()
        pygame.display.flip()

        def wait_for_enter(message, screen):
            font = pygame.font.Font(None, 56)  # Устанавливаем размер шрифта 36
            text = font.render(message, True, (255, 255, 255))  # Устанавливаем белый цвет текста

            text_rect = text.get_rect()
            text_rect.center = (WIDTH // 2, HEIGHT // 2)

            screen.fill((0, 0, 0))  # Очищаем экран
            screen.blit(text, text_rect)
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting = False







# Создам главное окно



def setup_game():
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 35))

    label = ttk.Label(root)
    label.pack(pady=120)

    start_button = ttk.Button(root, text="Начать игру", command=start_game, style='TButton', width=50)
    start_button.pack(side='top', pady=20, anchor='center')

    settings_button = ttk.Button(root, text="Настройки", command=show_settings, style='TButton', width=50)
    settings_button.pack(side='top', pady=20, anchor='center')

    rules_button = ttk.Button(root, text="Правила", command=show_rules, style='TButton', width=50)
    rules_button.pack(side='top', pady=20, anchor='center')

    exit_button = ttk.Button(root, text="Выход из игры", command=exit_game, style='TButton', width=50)
    exit_button.pack(side='top', pady=20, anchor='center')

    root.mainloop()
def toggle_sound():
    global is_sound_on, sound_button
    is_sound_on = not is_sound_on
    sound_button.config(text="Включить звук" if is_sound_on else "Выключить звук")
    print("Звук", "включен" if is_sound_on else "выключен")

def toggle_music():
    global is_music_on, music_button
    is_music_on = not is_music_on
    music_button.config(text="Включить музыку" if is_music_on else "Выключить музыку")
    print("Музыка", "включена" if is_music_on else "выключена")

def start_game():
    global root
    root.destroy()

    draw_board()
    draw_pieces()
    pygame.display.update()

def show_settings():
    global is_settings_open, sound_button, music_button, back_button
    if not is_settings_open:
        sound_button = ttk.Button(root, text="Включить звук", command=toggle_sound, style='TButton', width=50)
        sound_button.pack()

        music_button = ttk.Button(root, text="Включить музыку", command=toggle_music, style='TButton', width=50)
        music_button.pack()

        back_button = ttk.Button(root, text="Назад", command=hide_settings, style='TButton', width=50)
        back_button.pack()

        is_settings_open = True
    else:
        hide_settings()


    root.mainloop()


    root.mainloop()
def hide_settings():
    global is_settings_open, sound_button, music_button, back_button
    sound_button.pack_forget()
    music_button.pack_forget()
    back_button.pack_forget()

    is_settings_open = False
def show_rules():
    global is_rules_open, rules_label
    if not is_rules_open:
        rules_text = "Ваши правила сюда"
        rules_label = tk.Label(root, text=rules_text)
        rules_label.pack()
        is_rules_open = True
    else:
        rules_label.pack_forget()
        is_rules_open = False
def exit_game():
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Шашки")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry("{0}x{1}+0+0".format(screen_width, screen_height))

    is_settings_open = False
    is_rules_open = False
    is_sound_on = True
    is_music_on = True
    rules_label = None

def hide_settings():
    global is_settings_open
    global sound_button
    global music_button
    global back_button

    sound_button.pack_forget()
    music_button.pack_forget()
    back_button.pack_forget()

    is_settings_open = False
def show_rules():
    global is_rules_open
    global rules_label
    if not is_rules_open:
        rules_text = ("Правила шашек:\n 1. В шашках играют на доске 8х8 клеток, где черные клетки остаются пустыми."
                      "\n 2. Играют два игрока — белые и чёрные."
                      "\n 3. Игроки ставят фишки на клетки доски по диагонали, на своей стороне игрового поля"
                      "\n 3. Фишка может ходить на одну клетку вперед по диагонали на свою свободную клетку"
                      "\n 3. Если на пути стоит фишка противника, можно взятие — прыжок через фишку противника на свободную клетку. Фишка противника убирается с поля"
                      "\n 3. Когда фишка дойдет до противоположного края доски, она становится дамкой. Дамка может двигаться по диагонали на любое количество пустых клеток"
                      "\n 3. Выигрывает игрок, который либо заберет все фишки соперника, либо заступит их ходы")
        rules_label = tk.Label(root, text=rules_text)
        rules_label.pack()
        is_rules_open = True
    else:
        rules_label.pack_forget()
        is_rules_open = False
def exit_game():
    sys.exit()


setup_game()








if __name__ == '__main__':
    main()