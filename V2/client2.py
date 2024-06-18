import tkinter as tk
from PIL import Image, ImageTk
import socket
import threading
import chess


class ChessClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Client")

        self.choice_frame = tk.Frame(self.root)
        self.choice_frame.pack()

        self.bot_button = tk.Button(self.choice_frame, text="Play Against Bot", command=self.start_bot_game)
        self.bot_button.pack(side=tk.LEFT)

        self.client_button = tk.Button(self.choice_frame, text="Play Against Human", command=self.start_client_game)
        self.client_button.pack(side=tk.RIGHT)

    def start_bot_game(self):
        self.choice_frame.destroy()
        self.start_game("bot")

    def start_client_game(self):
        self.choice_frame.destroy()
        self.start_game("human")

    def start_game(self, opponent_type):
        self.opponent_type = opponent_type
        self.color_choice = tk.StringVar()
        self.color_choice.set("white")

        label = tk.Label(self.root, text="Choose your color:")
        label.pack()

        self.white_button = tk.Button(self.root, text="White", command=lambda: self.on_button_click("white"))
        self.white_button.pack()

        self.black_button = tk.Button(self.root, text="Black", command=lambda: self.on_button_click("black"))
        self.black_button.pack()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.connect_to_server)
        self.submit_button.pack()

    def on_button_click(self, color):
        self.color_choice.set(color)

    def connect_to_server(self):
        self.white_button.destroy()
        self.black_button.destroy()
        self.submit_button.destroy()

        host = 'localhost'
        port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((host, port))

        acknowledgment = self.server_socket.recv(1024).decode()
        if acknowledgment != "Ready":
            print("Server did not acknowledge.")
            self.root.quit()
            return

        self.server_socket.send(self.opponent_type.encode())

        if self.opponent_type == "human":
            acknowledgment = self.server_socket.recv(1024).decode()
            if acknowledgment != "Accepted":
                print("Server did not accept the opponent type.")
                self.root.quit()
                return

        client_color = self.color_choice.get()
        self.server_socket.send(client_color.encode())

        self.gui = ChessGUI(self.root, self.server_socket, client_color)
        self.root.mainloop()


class ChessGUI:
    def __init__(self, root, server_socket, client_color):
        self.root = root
        self.server_socket = server_socket
        self.client_color = client_color
        self.root.title("Chess Game")

        self.board = chess.Board()
        self.board_canvas = tk.Canvas(self.root, width=400, height=400)
        self.board_canvas.pack()

        self.load_images()
        self.draw_board()

        self.board_canvas.bind("<Button-1>", self.on_square_click)

        threading.Thread(target=self.receive_moves).start()

        self.resign_button = tk.Button(self.root, text="Resign", command=self.resign)
        self.resign_button.pack()

    def load_images(self):
        self.piece_images = {}
        for piece_type in ['r', 'n', 'b', 'q', 'k', 'p']:
            white_image = Image.open(f"../whitePieces/{piece_type.upper()}.png")
            white_image = white_image.resize((50, 50), resample=Image.BILINEAR)
            self.piece_images[piece_type.upper()] = ImageTk.PhotoImage(white_image)

            black_image = Image.open(f"../blackPieces/{piece_type}.png")
            black_image = black_image.resize((50, 50), resample=Image.BILINEAR)
            self.piece_images[piece_type] = ImageTk.PhotoImage(black_image)

    def draw_board(self):
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
        self.server_socket.send("resign".encode())
        self.root.quit()


if __name__ == "__main__":
    client = ChessClient()
    client.root.mainloop()