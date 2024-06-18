import tkinter as tk
from PIL import Image, ImageTk
import chess
import socket
import threading


class ChessGUI:
    def __init__(self, root, server_socket, client_color):
        # initialize the GUI class with the main window, server socket, and client color
        self.root = root
        self.server_socket = server_socket
        self.client_color = client_color
        self.root.title("Chess Game")

        self.board = chess.Board()
        self.board_canvas = tk.Canvas(self.root, width=400, height=400)
        self.board_canvas.pack()

        self.load_images()  # load the piece images
        self.draw_board()  # draw the initial board

        self.board_canvas.bind("<Button-1>",
                               self.on_square_click)  # bind the left mouse click event to handle square clicks

        threading.Thread(target=self.receive_moves).start()  # start a new thread for receiving moves from the server

        self.resign_button = tk.Button(self.root, text="Resign", command=self.resign)

        self.resign_button.pack()

    def load_images(self):
        # load the piece images from the corresponding directories
        self.piece_images = {}
        for piece_type in ['r', 'n', 'b', 'q', 'k', 'p']:
            white_image = Image.open(f"../whitePieces/{piece_type.upper()}.png")
            white_image = white_image.resize((50, 50), resample=Image.BILINEAR)
            self.piece_images[piece_type.upper()] = ImageTk.PhotoImage(white_image)

            black_image = Image.open(f"../blackPieces/{piece_type}.png")
            black_image = black_image.resize((50, 50), resample=Image.BILINEAR)
            self.piece_images[piece_type] = ImageTk.PhotoImage(black_image)

    def draw_board(self):
        # clear the canvas and draw the board with pieces
        self.board_canvas.delete("all")
        square_size = 50
        colors = ["white", "gray"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x0, y0 = col * square_size, row * square_size
                x1, y1 = x0 + square_size, y0 + square_size
                self.board_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_symbol = piece.symbol()
                    image = self.piece_images.get(piece_symbol)
                    if image:
                        self.board_canvas.create_image((x0 + x1) // 2, (y0 + y1) // 2, image=image)

    def on_square_click(self, event):
        # handle the square click event
        col = event.x // 50
        row = 7 - (event.y // 50)
        square = chess.square(col, row)
        piece = self.board.piece_at(square)
        if piece and piece.color == (chess.WHITE if self.client_color == "white" else chess.BLACK):
            self.selected_square = square
        elif hasattr(self, 'selected_square'):
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.draw_board()
                move_str = move.uci()
                print("Sending move:", move_str)
                try:
                    self.server_socket.send(move_str.encode())
                except BrokenPipeError:
                    print("Server connection closed.")
                    self.root.quit()
            delattr(self, 'selected_square')

    def receive_moves(self):
        # receive moves from the server and update the board
        while True:
            data = self.server_socket.recv(1024)
            if not data:
                print("Server disconnected.")
                break
            move_str = data.decode()
            if len(move_str) == 4 or len(move_str) == 5:
                move = chess.Move.from_uci(move_str)
                self.board.push(move)
                self.draw_board()
                print("Received move:", move_str)
            else:
                print("Received message:", move_str)

    def resign(self):
        # handle resign button click event
        self.server_socket.send("resign".encode())
        self.root.quit()


def main():
    root = tk.Tk()
    color_choice = tk.StringVar()
    color_choice.set("white")

    def on_button_click(color):
        color_choice.set(color)

    label = tk.Label(root, text="Choose your color:")
    label.pack()

    white_button = tk.Button(root, text="White", command=lambda: on_button_click("white"))
    white_button.pack()

    black_button = tk.Button(root, text="Black", command=lambda: on_button_click("black"))
    black_button.pack()

    submit_button = tk.Button(root, text="Submit", command=root.quit)
    submit_button.pack()

    root.mainloop()  # start the main event loop for color choice window

    label.destroy()
    white_button.destroy()
    black_button.destroy()
    submit_button.destroy()

    host = 'localhost'
    port = 5555
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((host, port))

    client_color = color_choice.get()
    server_socket.send(client_color.encode())
    print("Sent color:", client_color)

    gui = ChessGUI(root, server_socket, client_color)
    gui.root.mainloop()


if __name__ == "__main__":
    main()
