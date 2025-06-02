import streamlit as st
import random
from typing import List
from abc import ABC, abstractmethod

###NON IMPLEMENTIAMO IA

# --- Costanti ---
ROWS = 6
COLUMNS = 7

# --- Modello ---
class Piece:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_symbol(self) -> str:
        return self.symbol

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]

    def drop_piece(self, column: int, symbol: str) -> bool:
        for row in reversed(range(ROWS)):
            if self.grid[row][column] is None:
                self.grid[row][column] = Piece(symbol)
                return True
        return False

    def is_column_full(self, column: int) -> bool:
        return self.grid[0][column] is not None

    def is_full(self) -> bool:
        return all(self.is_column_full(c) for c in range(COLUMNS))

    def check_win(self, symbol: str) -> bool:
        # Controllo orizzontale
        for row in range(ROWS):
            for col in range(COLUMNS - 3):
                if all(self.grid[row][col + i] and self.grid[row][col + i].get_symbol() == symbol for i in range(4)):
                    return True
        # Controllo verticale
        for col in range(COLUMNS):
            for row in range(ROWS - 3):
                if all(self.grid[row + i][col] and self.grid[row + i][col].get_symbol() == symbol for i in range(4)):
                    return True
        # Controllo diagonale \
        for row in range(ROWS - 3):
            for col in range(COLUMNS - 3):
                if all(self.grid[row + i][col + i] and self.grid[row + i][col + i].get_symbol() == symbol for i in range(4)):
                    return True
        # Controllo diagonale /
        for row in range(3, ROWS):
            for col in range(COLUMNS - 3):
                if all(self.grid[row - i][col + i] and self.grid[row - i][col + i].get_symbol() == symbol for i in range(4)):
                    return True
        return False

    def get_grid(self):
        return self.grid

# --- Player ---
class Player(ABC):
    def __init__(self, name: str, symbol: str):
        self.name = name
        self.symbol = symbol

    def get_name(self) -> str:
        return self.name

    def get_symbol(self) -> str:
        return self.symbol

    @abstractmethod
    def get_move(self, board: Board) -> int:
        pass

class HumanPlayer(Player): 
    def get_move(self, board: Board) -> int:
        raise NotImplementedError("HumanPlayer.get_move() deve essere gestito via UI")

class BotPlayer(Player):
    def get_move(self, board: Board, difficulty: str) -> int:
        available = [i for i in range(COLUMNS) if not board.is_column_full(i)]

        if difficulty == "Facile":
            return random.choice(available)

        elif difficulty == "Medio":
            # Cerca una mossa vincente per il bot
            for col in available:
                temp_board = Board()
                temp_board.grid = [row[:] for row in board.grid] # Copia profonda della griglia
                if temp_board.drop_piece(col, self.symbol):
                    if temp_board.check_win(self.symbol):
                        return col
            # Se non c'è una mossa vincente immediata, gioca a caso
            return random.choice(available)

        elif difficulty == "Difficile":
            # 1. Cerca una mossa vincente per il bot
            for col in available:
                temp_board = Board()
                temp_board.grid = [row[:] for row in board.grid]
                if temp_board.drop_piece(col, self.symbol):
                    if temp_board.check_win(self.symbol):
                        return col
            
            # 2. Blocca una mossa vincente dell'avversario
            opponent_symbol = "X" if self.symbol == "O" else "O" # Assumiamo l'avversario sia l'altro simbolo
            for col in available:
                temp_board = Board()
                temp_board.grid = [row[:] for row in board.grid]
                if temp_board.drop_piece(col, opponent_symbol):
                    if temp_board.check_win(opponent_symbol):
                        return col
            
            # 3. Se non ci sono mosse vincenti o da bloccare, gioca al centro o a caso
            # Preferisce le colonne centrali per una migliore strategia
            central_columns = [3, 2, 4, 1, 5, 0, 6] # Ordine di preferenza
            for col in central_columns:
                if col in available:
                    return col
            
            # Fallback: gioca a caso se tutte le altre logiche falliscono
            return random.choice(available)

# --- Nuova classe Game ---
class Game:
    def __init__(self, player_name: str, difficulty: str):
        self.board = Board()
        self.player = HumanPlayer(player_name, "X")
        self.bot = BotPlayer("Bot", "O")
        self.turn = "X"
        self.difficulty = difficulty
        self.winner = None
        self.error_message = ""

    def play_move(self, column: int) -> bool:
        if self.winner is not None:
            self.error_message = "La partita è già terminata."
            return False

        if self.turn == "X":
            if self.board.is_column_full(column):
                self.error_message = "Colonna piena! Scegli un'altra colonna."
                return False
            self.board.drop_piece(column, "X")
            if self.board.check_win("X"):
                self.winner = f"{self.player.get_name()} ha vinto! 🏆"
            elif self.board.is_full():
                self.winner = "Pareggio! 🤝"
            else:
                self.turn = "O"
            return True
        else:
            self.error_message = "Non è il turno del giocatore umano."
            return False

    def bot_move(self):
        if self.winner is not None:
            return
        if self.turn == "O":
            col = self.bot.get_move(self.board, self.difficulty)
            self.board.drop_piece(col, "O")
            if self.board.check_win("O"):
                self.winner = "Il Bot ha vinto! 🤖"
            elif self.board.is_full():
                self.winner = "Pareggio! 🤝"
            else:
                self.turn = "X"

    def get_grid(self):
        return self.board.get_grid()

# --- Streamlit UI ---
if "page" not in st.session_state:
    st.session_state.page = "start"
if "game" not in st.session_state:
    st.session_state.game = None

# --- UI Start ---
if st.session_state.page == "start":
    st.title("🟡🔴 Forza 4")
    name = st.text_input("Inserisci il tuo nome:", "")
    level = st.selectbox("Scegli la difficoltà:", ["Facile", "Medio", "Difficile"])

    if st.button("Gioca"):
        player_name = name or "Giocatore"
        difficulty = level
        st.session_state.game = Game(player_name, difficulty)
        st.session_state.page = "game"
        st.rerun()

# --- UI Game ---
elif st.session_state.page == "game":
    game: Game = st.session_state.game

    st.title("🟡🔴 Forza 4")
    st.markdown(f"**Giocatore:** {game.player.get_name()} (🟡)  vs  Bot (🔴) | Difficoltà: {game.difficulty}")

    if game.error_message:
        st.error(game.error_message)
        game.error_message = ""

    # Mostra la griglia
    for row in game.get_grid():
        cols = st.columns(COLUMNS)
        for i, cell in enumerate(row):
            symbol = cell.get_symbol() if cell else " "
            color = "🟡" if symbol == "X" else "🔴" if symbol == "O" else "⬜"
            cols[i].markdown(f"<div style='text-align:center; font-size:30px'>{color}</div>", unsafe_allow_html=True)

    if not game.winner:
        if game.turn == "X":
            cols = st.columns(COLUMNS)
            for i in range(COLUMNS):
                if cols[i].button("⬇", key=f"col_{i}"):
                    if game.play_move(i):
                        if not game.winner and game.turn == "O":
                            game.bot_move()
                    st.rerun()
        else:
            # Se è il turno del bot ma non è ancora stato giocato, lo facciamo giocare
            game.bot_move()
            st.rerun()
    else:
        st.success(game.winner)

    col1, col2 = st.columns(2)
    if col1.button("🔁 Nuova partita"):
        st.session_state.game = Game(game.player.get_name(), game.difficulty)
        st.rerun()

    if col2.button("🏠 Menu iniziale"):
        st.session_state.page = "start"
        st.rerun()