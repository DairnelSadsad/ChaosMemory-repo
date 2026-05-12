import tkinter as tk
from tkinter import messagebox
import random

# --- CARD CLASSES ---
class Card:
    def __init__(self, value, is_special=False, color_override=None):
        self.value = value
        self.is_special = is_special
        self.back_bg = "#1a1c2c" # Dark blue card back
        
        # When flipped, special cards get a bright color background.
        # Normal cards get a standard light background.
        if is_special:
            self.front_bg = color_override # Bright color for card face
            self.front_fg = "#ffffff"     # White emoji to pop out
        else:
            self.front_bg = "#f4f4f4"     # Neutral light background
            self.front_fg = color_override # Colored emoji on neutral background

class NormalCard(Card):
    def __init__(self, value, emoji_color):
        super().__init__(value, is_special=False, color_override=emoji_color)

class SpecialCard(Card):
    def __init__(self, value, card_color):
        super().__init__(value, is_special=True, color_override=card_color)
        
    def activate_effect(self, game): pass

class HeartCard(SpecialCard):
    def __init__(self): super().__init__("❤️", "#ff4757") # Red Card
    def activate_effect(self, game): 
        game.lives += 1
        game.update_status()

class TornadoCard(SpecialCard):
    def __init__(self): super().__init__("🌪️", "#70a1ff") # Blue Card
    def activate_effect(self, game):
        game.show_alert("🌪️ TORNADO SHUFFLE!", "#70a1ff")
        game.animate_tornado(20)

class PeekCard(SpecialCard):
    def __init__(self): super().__init__("👁️", "#eccc68") # Gold Card
    def activate_effect(self, game):
        game.show_alert("👁️ PSYCHIC PEEK...", "#eccc68")
        game.full_board_peek(3000)

# --- MAIN GAME ---
class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CHAOS MEMORY v2.1")
        self.root.geometry("1280x900")
        
        self.bg_dark = "#0f0f1b"
        self.panel_bg = "#0a0a0a"
        self.accent_cyan = "#00ffff"
        self.accent_red = "#ff4757"
        self.root.configure(bg=self.bg_dark)

        # Standard emoji palette (distinct colors)
        self.emoji_colors = {
            "💎": "#268bd2", "🔥": "#cb4b16", "⚡": "#b58900", "🌈": "#6c71c4",
            "💀": "#586e75", "🤖": "#2aa198", "💣": "#dc322f", "🍀": "#859900",
            "🎸": "#d33682", "🍕": "#cb4b16", "🎭": "#6c71c4", "👑": "#b58900",
            "🧬": "#2aa198", "🧪": "#2ed573", "🧿": "#268bd2", "🪐": "#cb4b16"
        }

        self.setup_menu()
        self.main_container = tk.Frame(self.root, bg=self.bg_dark)
        self.main_container.pack(fill="both", expand=True)
        
        self.level, self.lives, self.score = 1, 5, 0
        self.show_home_page()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        game_menu = tk.Menu(menubar, tearoff=0, bg=self.panel_bg, fg="white", activebackground="#2e86de")
        game_menu.add_command(label="🏠 Home", command=self.show_home_page)
        game_menu.add_command(label="🔄 Restart", command=lambda: self.start_game(self.level))
        game_menu.add_separator()
        game_menu.add_command(label="❌ Exit", command=self.root.quit)
        menubar.add_cascade(label="🎮 GAME", menu=game_menu)

        lvl_menu = tk.Menu(menubar, tearoff=0, bg=self.panel_bg, fg="white")
        for i in range(1, 4):
            lvl_menu.add_command(label=f"Level {i}", command=lambda n=i: self.start_game(n))
        menubar.add_cascade(label="🏆 SELECT LEVEL", menu=lvl_menu)
        self.root.config(menu=menubar)

    def show_home_page(self):
        for w in self.main_container.winfo_children(): w.destroy()
        tk.Label(self.main_container, text="CHAOS", font=("Impact", 85), bg=self.bg_dark, fg="#2e86de").pack(pady=(50,0))
        tk.Label(self.main_container, text="MEMORY", font=("Impact", 85), bg=self.bg_dark, fg="white").pack()

        card_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        card_frame.pack(pady=40)

        lvls = [("LEVEL 1", "#2ed573", 1), ("LEVEL 2", "#ffa502", 2), ("LEVEL 3", "#ff4757", 3)]
        for text, color, num in lvls:
            f = tk.Frame(card_frame, bg="#1a1c2c", highlightthickness=2, highlightbackground="#2f3542", padx=20, pady=20)
            f.pack(side="left", padx=20)
            tk.Label(f, text=text, font=("Verdana", 18, "bold"), bg="#1a1c2c", fg=color).pack()
            btn = tk.Button(f, text="START", font=("Verdana", 10, "bold"), bg="#2f3542", fg="white", 
                            relief="flat", cursor="hand2", command=lambda n=num: self.start_game(n))
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, frame=f, c=color, b=btn: [frame.config(highlightbackground=c), b.config(bg=c)])
            btn.bind("<Leave>", lambda e, frame=f, b=btn: [frame.config(highlightbackground="#2f3542"), b.config(bg="#2f3542")])

    def start_game(self, lvl):
        for w in self.main_container.winfo_children(): w.destroy()
        self.level, self.lives, self.score, self.pairs_found = lvl, 5, 0, 0
        self.is_processing, self.first_selection = False, None
        
        self.header = tk.Frame(self.main_container, bg=self.panel_bg, height=60)
        self.header.pack(fill="x")
        self.status_label = tk.Label(self.header, text="", font=("Courier New", 18, "bold"), bg=self.panel_bg, fg=self.accent_cyan)
        self.status_label.pack(expand=True)

        self.alert_label = tk.Label(self.main_container, text="", font=("Verdana", 14, "bold"), bg=self.bg_dark, fg=self.accent_red)
        self.alert_label.pack(pady=5)

        self.board = tk.Frame(self.main_container, bg=self.bg_dark)
        self.board.pack(expand=True)

        # Config: Pairs, Columns
        config = {1: (18, 7), 2: (21, 8), 3: (24, 9)}
        num_pairs, self.cols = config.get(lvl, (24, 9))
        self.total_pairs = num_pairs

        # Fill deck with standard pairs
        emoji_keys = list(self.emoji_colors.keys())
        deck = []
        for i in range(num_pairs):
            val = emoji_keys[i % len(emoji_keys)]
            color = self.emoji_colors[val]
            deck.extend([NormalCard(val, color), NormalCard(val, color)])
        
        # Inject exact special card counts
        specials = [HeartCard() for _ in range(3)] + [PeekCard() for _ in range(2)] + [TornadoCard()]
        deck.extend(specials)
        
        random.shuffle(deck)
        self.cards = deck
        
        self.buttons = []
        for i, card in enumerate(self.cards):
            btn = tk.Button(self.board, text="?", width=5, height=2, font=("Segoe UI Emoji", 22, "bold"),
                            bg=card.back_bg, fg="#70a1ff", relief="flat", command=lambda idx=i: self.handle_click(idx))
            btn.grid(row=i // self.cols, column=i % self.cols, padx=5, pady=5)
            self.buttons.append(btn)
        
        self.update_status()
        # Initial peek
        self.root.after(800, lambda: self.full_board_peek(3000))

    def update_status(self):
        status = f"LEVEL {self.level} | SCORE {self.score:03d} | LIVES {'❤ ' * self.lives}"
        self.status_label.config(text=status)

    def handle_click(self, idx):
        if self.is_processing or self.buttons[idx].cget("state") == "disabled": return
        card, btn = self.cards[idx], self.buttons[idx]
        
        # Now uses the card class's intrinsic front face definitions.
        btn.config(text=card.value, bg=card.front_bg, fg=card.front_fg)

        if isinstance(card, SpecialCard):
            self.is_processing = True
            # Short delay allows special card to pop visually before triggering effect.
            self.root.after(350, lambda: self.trigger_special(idx))
        elif self.first_selection is None:
            self.first_selection = idx
        elif self.first_selection != idx:
            self.is_processing = True
            self.root.after(400, lambda: self.check_match(idx))

    def check_match(self, second_idx):
        f_idx = self.first_selection
        # All Normal Cards get plain backgrounds to blend in. Match confirmation is subtle green.
        if self.cards[f_idx].value == self.cards[second_idx].value:
            self.score += 10 * self.level
            self.pairs_found += 1
            # Temporary "found" confirmation
            self.buttons[f_idx].config(bg="#2ed573")
            self.buttons[second_idx].config(bg="#2ed573")
            self.root.after(300, lambda: self.clear_pair(f_idx, second_idx))
        else:
            self.lives -= 1
            # Mismatch highlight
            for i in (f_idx, second_idx): self.buttons[i].config(bg=self.accent_red)
            self.root.after(500, lambda: self.reset_cards(f_idx, second_idx))
        
        self.first_selection, self.is_processing = None, False
        self.update_status()
        if self.lives <= 0: self.game_over()

    def clear_pair(self, i1, i2):
        for i in (i1, i2):
            self.buttons[i].config(state="disabled", text="", bg=self.bg_dark)
        # Advance level if all normal cards are cleared
        active_normals = [c for c in self.cards if not c.is_special and self.buttons[self.cards.index(c)].winfo_exists() and self.buttons[self.cards.index(c)].cget("state") != "disabled"]
        if not active_normals:
             self.start_game(self.level + 1)

    def reset_cards(self, i1, i2):
        for i in (i1, i2):
            if i < len(self.buttons):
                self.buttons[i].config(text="?", bg="#1a1c2c", fg="#70a1ff")

    def trigger_special(self, idx):
        # Special card is self-clearing, it just provides its bonus.
        self.buttons[idx].config(state="disabled", text="", bg=self.bg_dark)
        self.cards[idx].activate_effect(self)
        # Peeks and Tornados require special processing, others can release immediately.
        if not isinstance(self.cards[idx], (PeekCard, TornadoCard)): 
            self.is_processing = False
        self.update_status()

    def full_board_peek(self, duration):
        self.is_processing = True
        for i, btn in enumerate(self.buttons):
            if btn.winfo_exists() and btn.cget("state") != "disabled":
                card = self.cards[i]
                # Power-up card definitions apply here too, making them easy to spot during peek.
                btn.config(text=card.value, bg=card.front_bg, fg=card.front_fg)
        self.root.after(duration, self.hide_all)

    def hide_all(self):
        for btn in self.buttons:
            if btn.winfo_exists() and btn.cget("state") != "disabled":
                btn.config(text="?", bg="#1a1c2c", fg="#70a1ff")
        self.is_processing = False

    def animate_tornado(self, steps):
        if steps > 0:
            # Shift lists internally
            self.cards.insert(0, self.cards.pop())
            self.buttons.insert(0, self.buttons.pop())
            # Re-grid to make visual
            for i, btn in enumerate(self.buttons):
                btn.grid(row=i // self.cols, column=i % self.cols)
                btn.config(command=lambda idx=i: self.handle_click(idx))
            self.root.after(60, lambda: self.animate_tornado(steps - 1))
        else: self.is_processing = False

    def show_alert(self, msg, color):
        self.alert_label.config(text=msg, fg=color)
        self.root.after(2000, lambda: self.alert_label.config(text=""))

    def game_over(self):
        messagebox.showerror("GAME OVER", f"Score: {self.score}")
        self.show_home_page()

if __name__ == "__main__":
    root = tk.Tk()
    MemoryGame(root)
    root.mainloop()
