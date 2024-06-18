# Chess Application

## Introduction
This application allows users to play chess against each other over a network. 

## Usage
1. First Version
    1. **Starting the Server and Connecting Clients and Playing the game**: 
       - Read [V1](V1/README.md)
    
2. Second version
    1. **Starting the Server and Connecting Clients and Playing the game**: 
       - Read [V2](V2/README.md)

## Current Status
- Implemented features: 
  - Client-server communication
  - Client vs bot
  - Basic chess gameplay functionality
- Known issues: 
  - The Player against Human button does not work as it doesn't create the correct game mode as the server does not understand it correctly.
  - The Client vs Client game functionality does not work right now, but I am going to continue working on it even after submission.
  - Occasionally, the server disconnects unexpectedly.


## Decomposition

### Chess Game with Client-Server Architecture

This is a simple implementation of a chess game with a client-server architecture. The server uses the Stockfish chess engine to play against the client. The client is a graphical user interface (GUI) built with Tkinter, allowing the user to play against the server.

### Overview
- `client.py`: Contains the implementation of the client GUI and logic for handling user input and communicating with the server.
- `server.py`: Contains the implementation of the server logic, including handling client connections, managing the game state, and using the Stockfish engine to generate moves.
- `protocol.py`: Contains helper functions for encoding and decoding chess moves.

### How to Run

1. Make sure you have Python and Tkinter installed on your system.
2. Run the `server.py` file to start the server.
3. Run the `client.py` file to start the client GUI.
4. In the client GUI, choose your opponent (bot or human).
5. In the client GUI, choose your color (white or black) and click the "Submit" button.
6. The game will start, and you can make moves by clicking on the squares on the board.

### Method Decomposition

### `client.py`

1. `ChessGUI` class:
   - `__init__(self, root, server_socket, client_color)`: Initializes the GUI, loads piece images, draws the board, and sets up event handlers.
   - `load_images(self)`: Loads the piece images from the corresponding directories.
   - `draw_board(self)`: Clears the canvas and draws the board with pieces.
   - `on_square_click(self, event)`: Handles the square click event, allowing the user to make moves.
   - `receive_moves(self)`: Receives moves from the server and updates the board.
   - `resign(self)`: Handles the resign button click event, sending a "resign" message to the server.

2. `main()` function:
   - Creates a window for the user to choose their color.
   - Establishes a connection with the server.
   - Sends the user's color choice to the server.
   - Creates an instance of the `ChessGUI` class with the server socket and user's color.
   - Starts the main event loop for the GUI.

### `server.py`

1. `ChessServer` class:
   - `__init__(self, host, port)`: Initializes the server with the specified host and port, and creates a Stockfish engine instance.
   - `handle_client(self, client_socket, client_color)`: Handles the game logic for a client connection, including receiving moves, making engine moves, and checking for checkmate.
   - `start(self)`: Starts the server, listens for incoming client connections, and creates a new thread for each client.

### `protocol.py`

1. `encode_move(move)`: Encodes a chess move as a string.
2. `decode_move(encoded_move)`: Decodes an encoded move string (not used in the current implementation). 
- Note: I was originally going to make the protocol encode the move into binary, and decode from binary, but I was too stuck with GUI implementation so that idea is for future.

## Test Cases Output
- Screenshots of various test cases showing the application in action are in [here](documentation/screenshots).

## Requirements and Design Documents
 - [Documentation](documentation/documentation.pdf)
 - [Self-Reflection](documentation/self_reflection_template_CSC450_V2.doc)

## Future Enhancements
- Implement time controls for games to choose different options to play a 3min/5min/10min games.
- Add support for player ratings and rankings (leaderboard).
- Make the leaderboard synchronized through synchronized methods.
- Improve the user interface for a better gaming experience and make it like an actual desktop application.
- Fix any known issues above.
