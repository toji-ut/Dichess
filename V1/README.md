## Chess Game through Computer Networks

### Prerequisites
- Python 3
- Python chess library
- Stockfish chess engine

### How to Use
1. **Download the Project**: Clone or download the project repository to your local machine.

2. **Install Python Packages**: Open your terminal and navigate to the project directory. Use pip to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. **Install Stockfish Chess Engine**: Install the Stockfish chess engine. You can use Homebrew on macOS:

    ```bash
    brew install stockfish
    ```

4. **Run the Server and Client**: Open two separate terminal tabs or windows.

    - In the first tab, navigate to the `server` directory and run the following command to start the server:

        ```bash
        python3 server.py
        ```

    - In the second tab, navigate to the `client` directory and run the following command to start the client:

        ```bash
        python3 client.py
        ```

5. **Play the Game**: Once the server and client are running, follow the prompts on the client to choose your color (white or black). Then, start playing the game by making moves on the graphical user interface (GUI) board.

6. **Game Interface**:
   - **Choose Your Color**: Upon starting the client, the user will be prompted to choose their color (white or black) using buttons labeled "White" and "Black".
   - **Submit Button**: After selecting the color, the user should click the "Submit" button to confirm their choice.
   - **Resign Button**: During gameplay, the user can resign by clicking the "Resign" button. This ends the game and concedes victory to the opponent.
   - **Game Board**: The GUI board will display the chessboard and pieces. Clicking on a piece selects it, and clicking on a destination square moves the piece to that square. Only legal moves are allowed.
   - **Server Messages**: Throughout the game, the client will receive messages from the server indicating game status, such as "Checkmate" or "Invalid move". These messages will be displayed in the terminal where the client was started.

Enjoy playing chess against the computer with this server-client setup!
