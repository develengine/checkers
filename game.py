#!/usr/bin/env python3

import tkinter as tk

window_size = 720
unit = window_size // 8
piece_size = 0.8

root = tk.Tk()
root.resizable(width = False, height = False)

canvas = tk.Canvas(root, width = window_size, height = window_size)
canvas.pack()

board = [ ]
player = True
selected = None
must_jump = False
protected = None
reserved = None
use_reserved = False

for _ in range(8):
    board.append([''] * 8)

for i in range(0, 8, 2):
    board[i][0] = 'bp'
for i in range(1, 8, 2):
    board[i][1] = 'bp'
for i in range(0, 8, 2):
    board[i][6] = 'wp'
for i in range(1, 8, 2):
    board[i][7] = 'wp'
# board[6][6] = 'wq'
# board[3][3] = 'bp'
# board[1][3] = 'bp'
# board[5][5] = 'bp'
# board[1][5] = 'bp'
# board[3][5] = 'bp'
# board[2][6] = ''

def callback(event):
    global selected
    global must_jump
    global player
    global protected
    global reserved
    global use_reserved

    def redraw_all():
        clear_canvas()
        draw_pieces()

    def is_clear(x, y, dx, dy, n):
        for i in range(n):
            if board[x + dx * i][y + dy * i] != '':
                return False
        return True

    def can_jump(x, y):
        global reserved
        global use_reserved

        piece = board[x][y]
        if piece[1] == 'q':
            for i in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                enemy = False
                xp = x + i[0]
                yp = y + i[1]
                while -1 < xp < 8 and -1 < yp < 8:
                    on_piece = board[xp][yp]
                    if use_reserved and reserved != None and xp == reserved[0] and yp == reserved[1]:
                        break
                    if on_piece == '':
                        if enemy:
                            return True
                    elif on_piece[0] == piece[0]:
                        break
                    elif enemy:
                        break
                    else:
                        enemy = True
                    xp += i[0]
                    yp += i[1]
        else:
            f = -1 if piece[0] == 'w' else 1
            for i in [(1 * f, 1 * f), (-1 * f, 1 * f)]:
                if -1 < x + i[0] < 8 and -1 < y + i[1] < 8:
                    on_piece = board[x + i[0]][y + i[1]]
                    if on_piece == '' or on_piece[0] == piece[0]:
                        continue
                    elif -1 < (x + i[0] * 2) < 8 and -1 < (y + i[1] * 2) < 8 and board[x + i[0] * 2][y + i[1] * 2] == '':
                        if use_reserved and reserved != None and x + i[0] * 2 == reserved[0] and y + i[1] * 2 == reserved[1]:
                            continue
                        return True
        return False

    def swap_sides():
        global player
        global must_jump
        global protected
        global reserved

        use_reserved = True

        kills = [ ]
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] != '' and (board[x][y][0] == 'w') == player and can_jump(x, y):
                    kills.append((x, y))

        for i in kills:
            if protected == None or not (protected[0] == i[0] and protected[1] == i[1]):
                board[i[0]][i[1]] = ''

        use_reserved = False
        protected = None
        reserved = None

        player = not player


    x = event.x // unit
    y = event.y // unit
    piece = board[x][y]

    if selected == None:
        if piece == '':
            redraw_all()
            return
        elif (piece[0] == 'w') == player:
            selected = (x, y)
            if can_jump(x, y):
                draw_highlight(x, y, "red")
            else:
                draw_highlight(x, y, "blue")
            return
        else:
            redraw_all()
            return

    vx = x - selected[0]
    vy = y - selected[1]
    dir_x = vx // abs(vx) if vx != 0 else 0
    dir_y = vy // abs(vy) if vy != 0 else 0
    selected_piece = board[selected[0]][selected[1]]
    forward = -1 if selected_piece[0] == 'w' else 1
    behind = board[x - dir_x][y - dir_y]

    if piece != '':
        if (piece[0] == 'w') == player:
            if not must_jump:
                selected = (x, y)
                redraw_all()
                if can_jump(x, y):
                    draw_highlight(x, y, "red")
                else:
                    draw_highlight(x, y, "blue")
            return
        else:
            if not must_jump:
                selected = None
                redraw_all()
            return
    if abs(vx) != abs(vy) or (selected_piece[1] == 'p' and dir_y != forward):
        if not must_jump:
            selected = None
            redraw_all()
        return
    if dir_x == vx:
        if not must_jump:
            if can_jump(selected[0], selected[1]):
                selected = None
                redraw_all()
                return
            new_piece = selected_piece
            if selected_piece[1] == 'p' and (y == 0 or y == 7):
                new_piece = selected_piece[0] + 'q'
            board[x][y] = new_piece
            board[selected[0]][selected[1]] = ''
            reserved = selected
            selected = None
            protected = (x, y)
            swap_sides()
            redraw_all()
        return

    if behind == '':
        if not must_jump:
            if selected_piece[1] == 'q' and is_clear(selected[0] + dir_x, selected[1] + dir_y, dir_x, dir_y, abs(vx) - 2):
                board[x][y] = selected_piece
                board[selected[0]][selected[1]] = ''
                protected = (x, y)
                swap_sides()
            selected = None
            redraw_all()
    elif behind[0] == selected_piece[0]:
        if not must_jump:
            selected = None
            redraw_all()
    else:
        if selected_piece[1] == 'p':
            if abs(vx) == 2:
                new_piece = selected_piece
                if selected_piece[1] == 'p' and (y == 0 or y == 7):
                    new_piece = selected_piece[0] + 'q'
                board[x][y] = new_piece
                board[selected[0]][selected[1]] = ''
                board[x - dir_x][y - dir_y] = ''
                if not must_jump:
                    reserved = selected
                must_jump = can_jump(x, y)
                if new_piece[1] == 'q':
                    must_jump = False
                if must_jump:
                    selected = (x, y)
                    redraw_all()
                    draw_highlight(x, y, "red");
                else:
                    swap_sides()
                    redraw_all()
                    selected = None
            else:
                if not must_jump:
                    selected = None
                    redraw_all()
        elif is_clear(selected[0] + dir_x, selected[1] + dir_y, dir_x, dir_y, abs(vx) - 2):
            board[x][y] = selected_piece
            board[selected[0]][selected[1]] = ''
            board[x - dir_x][y - dir_y] = ''
            if not must_jump:
                reserved = selected
            must_jump = can_jump(x, y)
            if must_jump:
                selected = (x, y)
                redraw_all()
                draw_highlight(x, y, "red");
            else:
                swap_sides()
                redraw_all()
                selected = None
        else:
            if not must_jump:
                selected = None
                redraw_all()

canvas.bind("<Button-1>", callback)

def clear_canvas():
    canvas.delete("all")
    color = False
    for i in range(8):
        for j in range(8):
            x = j * unit
            y = i * unit
            canvas.create_rectangle(x, y, x + unit, y + unit, fill = '#ffe5af' if color else '#877a65', width = 0)
            color = not color
        color = not color

def draw_piece(x, y, white, queen):
    filler = '#deb45d' if white else '#3d301c'
    outer = '#000000'
    extent = (window_size / 8) * piece_size
    padding = unit - extent
    coord = x * unit, y * unit, x * unit + extent, y * unit + extent
    f = canvas.create_rectangle if queen else canvas.create_oval
    f(x * unit + padding, y * unit + padding, x * unit + extent, y * unit + extent, fill = filler, outline = outer, width = 0)

def draw_pieces():
    for i in range(len(board)):
        for j in range(len(board[i])):
            color = True
            queen = True
            if board[i][j] == '':
                continue
            if board[i][j][0] == 'b':
                color = False
            if board[i][j][1] == 'p':
                queen = False
            draw_piece(i, j, color, queen)

def draw_highlight(x, y, color):
    extent = (window_size / 8) * piece_size
    padding = unit - extent
    coord = x * unit, y * unit, x * unit + extent, y * unit + extent
    canvas.create_oval(x * unit + padding, y * unit + padding, x * unit + extent, y * unit + extent, outline = color, width = 5)
    

clear_canvas()
draw_pieces()

root.mainloop()

