import tkinter as tk
from tkinter import messagebox
import random


class Card:
    def __init__(self, value, is_special=False, color_override=None):
        self.value = value
        self.is_special = is_special
        self.back_bg = "#1a1c2c"
        self.is_matched = False  
        self.is_flipped = False  
        
        if is_special:
            self.front_bg = color_override 
            self.front_fg = "#ffffff"     
        else:
            self.front_bg = "#f4f4f4"     
            self.front_fg = color_override 

class NormalCard(Card):
    def __init__(self, value, emoji_color):
        super().__init__(value, is_special=False, color_override=emoji_color)

class SpecialCard(Card):
    def __init__(self, value, card_color):
        super().__init__(value, is_special=True, color_override=card_color)
    def activate_effect(self, game): pass

class HeartCard(SpecialCard):
    def __init__(self): super().__init__("❤️", "#ff4757")
    def activate_effect(self, game): 
        game.lives += 1
        game.update_status()
        game.is_processing = False

class TornadoCard(SpecialCard):
    def __init__(self): super().__init__("🌪️", "#70a1ff")
    def activate_effect(self, game):
        game.show_alert("🌪️ TORNADO SHUFFLE!", "#70a1ff")
        if game.first_selection is not None:
            game.cards[game.first_selection].is_flipped = False
            game.first_selection = None
        game.animate_tornado(25) 

class PeekCard(SpecialCard):
    def __init__(self): super().__init__("👁️", "#eccc68")
    def activate_effect(self, game):
        game.show_alert("👁️ PSYCHIC PEEK...", "#eccc68")
        game.root.after(400, lambda: game.full_board_peek(3000))


class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CHAOS MEMORY v3.0")
        self.root.geometry("1280x950")
        
        self.bg_dark = "#0f0f1b"
        self.panel_bg = "#0a0a0a"
        self.accent_cyan = "#00ffff"
        self.accent_red = "#ff4757"
        self.accent_green = "#2ed573"
        self.root.configure(bg=self.bg_dark)

        self.emoji_pool = {
            "💎": "#268bd2", "🔥": "#cb4b16", "⚡": "#b58900", "🌈": "#6c71c4",
            "💀": "#586e75", "🤖": "#2aa198", "💣": "#dc322f", "🍀": "#859900",
            "🎸": "#d33682", "🍕": "#cb4b16", "🎭": "#6c71c4", "👑": "#b58900",
            "🧬": "#2aa198", "🧪": "#2ed573", "🧿": "#268bd2", "🪐": "#cb4b16",
            "👻": "#9ea1a3", "🍦": "#ff7f50", "🚀": "#00a8ff", "🛸": "#9c88ff",
            "🍄": "#ff4d4d", "🌙": "#f1c40f", "🌊": "#1e90ff", "🥑": "#44bd32"
        }

        self.setup_menu()
        self.main_container = tk.Frame(self.root, bg=self.bg_dark)
        self.main_container.pack(fill="both", expand=True)
        
        self.level = 1
        self.show_home_page()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        game_menu = tk.Menu(menubar, tearoff=0, bg=self.panel_bg, fg="white")
        game_menu.add_command(label="🏠 Home", command=self.show_home_page)
        game_menu.add_command(label="🔄 Restart", command=lambda: self.start_game(self.level))
        menubar.add_cascade(label="🎮 GAME", menu=game_menu)
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
            tk.Label(f, text=text, font=("Verdana", 14, "bold"), bg="#1a1c2c", fg=color).pack()
            btn = tk.Button(f, text="START", font=("Verdana", 10, "bold"), bg="#2f3542", fg="white", relief="flat", command=lambda n=num: self.start_game(n))
            btn.pack(pady=10)

    def start_game(self, lvl):
        for w in self.main_container.winfo_children(): w.destroy()
        self.level, self.lives, self.score, self.pairs_found = lvl, 5, 0, 0
        self.is_processing, self.first_selection = False, None
        
        self.header = tk.Frame(self.main_container, bg=self.panel_bg, height=70)
        self.header.pack(fill="x")
        
        self.status_label = tk.Label(self.header, text="", font=("Courier New", 18, "bold"), bg=self.panel_bg, fg=self.accent_cyan)
        self.status_label.pack(side="left", padx=30, expand=True)

        self.alert_label = tk.Label(self.main_container, text="", font=("Verdana", 14, "bold"), bg=self.bg_dark, fg=self.accent_red)
        self.alert_label.pack(pady=5)

        self.board = tk.Frame(self.main_container, bg=self.bg_dark)
        self.board.pack(expand=True, pady=10)

        config = {1: (18, 7), 2: (21, 8), 3: (24, 9)}
        num_pairs, self.cols = config.get(lvl, (24, 9))
        self.total_pairs = num_pairs

        all_emojis = list(self.emoji_pool.items())
        selected_emojis = all_emojis[:num_pairs]
        
        deck = []
        for emoji, color in selected_emojis:
            deck.extend([NormalCard(emoji, color), NormalCard(emoji, color)])
        
        specials = [HeartCard() for _ in range(3)] + [PeekCard() for _ in range(2)] + [TornadoCard()]
        deck.extend(specials)
        
        random.shuffle(deck)
        self.cards = deck
        self.buttons = []
        
        for i in range(len(self.cards)):
            btn = tk.Button(self.board, text="?", width=5, height=2, font=("Segoe UI Emoji", 18, "bold"),
                            bg="#1a1c2c", fg="#70a1ff", relief="flat")
            btn.config(command=lambda idx=i: self.handle_click(idx))
            btn.grid(row=i // self.cols, column=i % self.cols, padx=3, pady=3)
            self.buttons.append(btn)
        
        self.update_status()
        self.root.after(500, lambda: self.full_board_peek(2500))

    def update_status(self):
        status = f"LEVEL {self.level} | SCORE {self.score:03d} | LIVES {'❤ ' * self.lives}"
        self.status_label.config(text=status)

    def handle_click(self, idx):
        if self.is_processing or self.cards[idx].is_matched: return
        card, btn = self.cards[idx], self.buttons[idx]
        
        card.is_flipped = True
        btn.config(text=card.value, bg=card.front_bg, fg=card.front_fg)

        if isinstance(card, SpecialCard):
            self.is_processing = True
            if self.first_selection is not None:
                self.cards[self.first_selection].is_flipped = False
                self.first_selection = None
                self.hide_all()
            self.root.after(300, lambda: self.trigger_special(idx))
        elif self.first_selection is None:
            self.first_selection = idx
        elif self.first_selection != idx:
            self.is_processing = True
            self.root.after(400, lambda: self.check_match(idx))

    def check_match(self, s_idx):
        f_idx = self.first_selection
        if f_idx is not None and self.cards[f_idx].value == self.cards[s_idx].value:
            self.score += 10 * self.level
            self.pairs_found += 1
            self.cards[f_idx].is_matched = True
            self.cards[s_idx].is_matched = True
            self.buttons[f_idx].config(bg=self.accent_green, fg="white")
            self.buttons[s_idx].config(bg=self.accent_green, fg="white")
            self.root.after(400, lambda: self.clear_pair(f_idx, s_idx))
        else:
            self.lives -= 1
            if f_idx is not None:
                self.buttons[f_idx].config(bg=self.accent_red, fg="white")
                self.buttons[s_idx].config(bg=self.accent_red, fg="white")
                self.root.after(500, lambda: self.reset_cards(f_idx, s_idx))
        
        self.first_selection, self.is_processing = None, False
        self.update_status()
        if self.lives <= 0: self.game_over()

    def clear_pair(self, i1, i2):
        for i in (i1, i2): 
            self.buttons[i].config(text="", bg=self.bg_dark, state="disabled")
        if self.pairs_found >= self.total_pairs: self.start_game(self.level + 1)

    def reset_cards(self, i1, i2):
        for i in (i1, i2): 
            self.cards[i].is_flipped = False
            self.buttons[i].config(text="?", bg="#1a1c2c", fg="#70a1ff")

    def trigger_special(self, idx):
        self.cards[idx].is_matched = True 
        self.buttons[idx].config(state="disabled", text="", bg=self.bg_dark)
        self.cards[idx].activate_effect(self)
        self.update_status()

    def full_board_peek(self, duration):
        self.is_processing = True
        for i, btn in enumerate(self.buttons):
            if not self.cards[i].is_matched:
                c = self.cards[i]
                btn.config(text=c.value, bg=c.front_bg, fg=c.front_fg)
        self.root.after(duration, self.hide_all)

    def hide_all(self):
        for i, btn in enumerate(self.buttons):
            if not self.cards[i].is_matched and not self.cards[i].is_flipped:
                btn.config(text="?", bg="#1a1c2c", fg="#70a1ff")
        self.is_processing = False

    def animate_tornado(self, steps):
        if steps > 0:
            self.is_processing = True
            self.cards.insert(0, self.cards.pop())
            for i, btn in enumerate(self.buttons):
                card = self.cards[i]
                if card.is_matched:
                    btn.config(text="", bg=self.bg_dark, state="disabled")
                elif card.is_flipped:
                    btn.config(text=card.value, bg=card.front_bg, fg=card.front_fg, state="normal")
                else:
                    btn.config(text="?", bg="#1a1c2c", fg="#70a1ff", state="normal")
                btn.config(command=lambda idx=i: self.handle_click(idx))
            self.root.after(60, lambda: self.animate_tornado(steps - 1))
        else: 
            self.is_processing = False

    def show_alert(self, msg, color):
        self.alert_label.config(text=msg, fg=color)
        self.root.after(2000, lambda: self.alert_label.config(text=""))

    def game_over(self):
        messagebox.showerror("GAME OVER", f"Final Score: {self.score}")
        self.show_home_page()

if __name__ == "__main__":
    root = tk.Tk()
    MemoryGame(root)
    root.mainloop()
