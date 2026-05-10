import tkinter as tk
from tkinter import messagebox
import random


class Card:
    def __init__(self, value, bg_color="#93a1a1", fg_color="#1e272e"):
        self.value = value
        self.front_bg = bg_color    
        self.front_fg = fg_color  
        self.back_bg = "#1a1c2c"

class NormalCard(Card):
    def __init__(self, value, emoji_color): 
        
        super().__init__(value, "#f4f4f4", emoji_color)

class HeartCard(Card):
    def __init__(self): super().__init__("❤️", "#ff4757", "#ffffff")
    def activate_effect(self, game):
        game.lives += 1
        game.update_status()

class TornadoCard(Card):
    def __init__(self): super().__init__("🌪️", "#70a1ff", "#ffffff")
    def activate_effect(self, game):
        game.show_alert("🌪️ TORNADO SHUFFLE! 🌪️", "#70a1ff")
        game.animate_tornado(steps=20)

class PeekCard(Card):
    def __init__(self): super().__init__("👁️", "#eccc68", "#ffffff")
    def activate_effect(self, game):
        game.show_alert("👁️ PSYCHIC PEEK... 👁️", "#eccc68")
        game.full_board_peek(3000)

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CHAOS MEMORY v2.1")
        
        
        self.bg_dark = "#0f0f1b"      
        self.panel_bg = "#0a0a0a"  
        self.accent_cyan = "#00ffff" 
        self.accent_blue = "#2e86de"
        self.accent_green = "#2ed573"
        self.accent_red = "#ff4757"
        self.text_main = "#ffffff"

        
        self.emoji_colors = {
            "💎": "#268bd2", "🔥": "#cb4b16", "⚡": "#b58900", "🌈": "#6c71c4", 
            "💀": "#586e75", "👻": "#eee8d5", "🤖": "#2aa198", "🪐": "#cb4b16", 
            "💣": "#dc322f", "🍀": "#859900", "🧿": "#268bd2", "🎸": "#d33682", 
            "🍕": "#cb4b16", "🎭": "#6c71c4", "👑": "#b58900", "🐉": "#859900", 
            "🧬": "#2aa198", "🧪": "#2ed573"
        }
        
        self.root.configure(bg=self.bg_dark)
        self.root.geometry("1280x900")
        
        self.lives = 5
        self.score = 0
        self.level = 1
        self.is_processing = False
        self.first_selection = None
        self.cards = []
        self.buttons = []
        
        self.setup_menu()
        self.main_container = tk.Frame(self.root, bg=self.bg_dark)
        self.main_container.pack(fill="both", expand=True)
        
        self.show_home_page()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        game_menu = tk.Menu(menubar, tearoff=0, bg=self.panel_bg, fg=self.text_main, activebackground=self.accent_blue)
        game_menu.add_command(label="🏠 Back to Home", command=self.show_home_page)
        game_menu.add_command(label="🔄 Restart Level", command=lambda: self.load_level(self.level))
        game_menu.add_separator()
        game_menu.add_command(label="❌ Exit", command=self.root.quit)
        menubar.add_cascade(label="🎮 GAME", menu=game_menu)
        
        level_menu = tk.Menu(menubar, tearoff=0, bg=self.panel_bg, fg=self.text_main)
        level_menu.add_command(label="1️⃣ Level 1", command=lambda: self.start_from_menu(1))
        level_menu.add_command(label="2️⃣ Level 2", command=lambda: self.start_from_menu(2))
        level_menu.add_command(label="3️⃣ Level 3", command=lambda: self.start_from_menu(3))
        menubar.add_cascade(label="🏆 SELECT LEVEL", menu=level_menu)
        self.root.config(menu=menubar)

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_home_page(self):
        self.clear_screen()
        title_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        title_frame.pack(pady=50)
        tk.Label(title_frame, text="CHAOS", font=("Impact", 85), bg=self.bg_dark, fg=self.accent_blue).pack()
        tk.Label(title_frame, text="MEMORY", font=("Impact", 85), bg=self.bg_dark, fg=self.text_main).pack()
        
        selection_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        selection_frame.pack(pady=20)
        levels_data = [("LEVEL 1", self.accent_green, 1), ("LEVEL 2", "#ffa502", 2), ("LEVEL 3", self.accent_red, 3)]

        for title, color, l_num in levels_data:
            f = tk.Frame(selection_frame, bg="#1a1c2c", highlightthickness=2, highlightbackground="#2f3542", padx=20, pady=20)
            f.pack(side="left", padx=20)
            tk.Label(f, text=title, font=("Verdana", 18, "bold"), bg="#1a1c2c", fg=color).pack()
            b = tk.Button(f, text="START", font=("Verdana", 10, "bold"), bg="#2f3542", fg="white", activebackground=color, relief="flat", command=lambda n=l_num: self.start_from_menu(n), cursor="hand2")
            b.pack(pady=10)
            b.bind("<Enter>", lambda e, frame=f, c=color, btn=b: [frame.config(highlightbackground=c), btn.config(bg=c)])
            b.bind("<Leave>", lambda e, frame=f, btn=b: [frame.config(highlightbackground="#2f3542"), btn.config(bg="#2f3542")])

    def start_from_menu(self, lvl):
        self.score = 0
        self.lives = 5
        self.load_level(lvl)

    def setup_game_ui(self):
        self.clear_screen()
        self.header_frame = tk.Frame(self.main_container, bg="#0a0a0a", height=60)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        self.combined_status = tk.Label(self.header_frame, text="",
                                        font=("Courier New", 18, "bold"),
                                        bg="#0a0a0a", fg=self.accent_cyan)
        self.combined_status.pack(expand=True)

        self.alert_label = tk.Label(self.main_container, text="", font=("Verdana", 14, "bold"),
                                   bg=self.bg_dark, fg=self.accent_red)
        self.alert_label.pack(pady=5)

        self.board = tk.Frame(self.main_container, bg=self.bg_dark)
        self.board.pack(expand=True)

        self.progress_frame = tk.Frame(self.main_container, bg="#000", height=5)
        self.progress_frame.pack(fill="x", side="bottom")
        self.progress_bar = tk.Frame(self.progress_frame, bg=self.accent_cyan, width=0)
        self.progress_bar.place(x=0, y=0, relheight=1)

    def update_status(self):
        heart_symbols = "❤ " * self.lives
        status_text = f"LEVEL {self.level} | SCORE {self.score:03d} | LIVES {heart_symbols}"
        self.combined_status.config(text=status_text)

    def load_level(self, lvl):
        self.setup_game_ui()
        self.level = lvl
        config = {1: (42, 18, 7), 2: (48, 21, 8), 3: (54, 24, 9)}
        if lvl not in config:
            messagebox.showinfo("VICTORY", "Game Master status achieved!")
            self.show_home_page(); return

        total, pairs, cols = config[lvl]
        self.current_cols = cols; self.total_pairs = pairs; self.pairs_found = 0
        
        emojis_list = list(self.emoji_colors.keys())
        deck = []
        for i in range(pairs):
            val = emojis_list[i % len(emojis_list)]
            color = self.emoji_colors[val]
            deck.extend([NormalCard(val, color), NormalCard(val, color)])
        
        specials = [HeartCard(), HeartCard(), HeartCard(), PeekCard(), PeekCard(), TornadoCard()]
        deck.extend(specials)
        random.shuffle(deck)
        self.cards = deck
        self.create_grid(cols)
        self.update_progress()
        self.root.after(800, lambda: self.full_board_peek(3000))

    def create_grid(self, cols):
        self.buttons = []
        for i, card in enumerate(self.cards):
            btn = tk.Button(self.board, text="?", width=5, height=2, font=("Segoe UI Emoji", 22, "bold"),
                            bg=card.back_bg, fg="#70a1ff", relief="flat", bd=0, cursor="hand2",
                            activebackground=self.accent_blue, highlightthickness=1, highlightbackground="#2f3542",
                            command=lambda idx=i: self.handle_click(idx))
            btn.grid(row=i//cols, column=i%cols, padx=6, pady=6)
            btn.bind("<Enter>", lambda e, b=btn: self.on_card_hover(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_card_leave(b))
            self.buttons.append(btn)
        self.update_status()

    def on_card_hover(self, btn):
        if btn.cget("state") != "disabled" and btn.cget("text") == "?":
            btn.config(bg="#3d425e", fg="#ffffff", highlightbackground=self.accent_cyan)

    def on_card_leave(self, btn):
        if btn.cget("state") != "disabled" and btn.cget("text") == "?":
            btn.config(bg="#1a1c2c", fg="#70a1ff", highlightbackground="#2f3542")

    def handle_click(self, idx):
        if self.is_processing or self.buttons[idx].cget("state") == "disabled": return
        card = self.cards[idx]; btn = self.buttons[idx]
        btn.config(text=card.value, bg=card.front_bg, fg=card.front_fg)
        if not isinstance(card, NormalCard):
            self.is_processing = True
            self.root.after(300, lambda: self.trigger_special(idx))
        else:
            if self.first_selection is None: self.first_selection = idx
            else:
                if self.first_selection == idx: return
                self.is_processing = True
                self.root.after(400, lambda: self.check_match(idx))

    def check_match(self, second_idx):
        first_idx = self.first_selection
        if self.cards[first_idx].value == self.cards[second_idx].value:
            self.buttons[first_idx].config(bg=self.accent_green); self.buttons[second_idx].config(bg=self.accent_green)
            self.score += 10 * self.level; self.pairs_found += 1
            self.update_progress()
            self.root.after(300, lambda: self.clear_pair(first_idx, second_idx))
        else:
            self.buttons[first_idx].config(bg=self.accent_red); self.buttons[second_idx].config(bg=self.accent_red)
            self.lives -= 1
            self.root.after(500, lambda: self.reset_mismatch(first_idx, second_idx))
            if self.lives <= 0:
                messagebox.showerror("GAME OVER", f"Score: {self.score}"); self.show_home_page()

    def clear_pair(self, i1, i2):
        for i in [i1, i2]: self.buttons[i].config(text="", bg=self.bg_dark, state="disabled")
        active = [i for i, c in enumerate(self.cards) if isinstance(c, NormalCard) and self.buttons[i].cget("state") != "disabled"]
        if not active: self.next_level()
        self.first_selection = None; self.is_processing = False; self.update_status()

    def update_progress(self):
        self.root.update_idletasks()
        progress = (self.pairs_found / self.total_pairs) * self.root.winfo_width()
        self.progress_bar.config(width=progress)

    def reset_mismatch(self, i1, i2):
        for i in [i1, i2]:
            if i < len(self.buttons) and self.buttons[i].cget("state") != "disabled":
                self.buttons[i].config(text="?", bg="#1a1c2c", fg="#70a1ff")
        self.first_selection = None; self.is_processing = False; self.update_status()

    def show_alert(self, message, color):
        self.alert_label.config(text=message, fg=color)
        self.root.after(2000, lambda: self.alert_label.config(text=""))

    def next_level(self):
        self.show_alert("STABILIZING...", self.accent_green)
        self.root.after(1000, lambda: self.load_level(self.level + 1))

    def full_board_peek(self, duration):
        self.is_processing = True
        for i, card in enumerate(self.cards):
            if i < len(self.buttons) and self.buttons[i].cget("state") != "disabled":
                self.buttons[i].config(text=card.value, bg=card.front_bg, fg=card.front_fg)
        self.root.after(duration, self.hide_all)

    def hide_all(self):
        for btn in self.buttons:
            if btn.winfo_exists() and btn.cget("state") != "disabled":
                btn.config(text="?", bg="#1a1c2c", fg="#70a1ff")
        self.is_processing = False

    def trigger_special(self, idx):
        self.buttons[idx].config(text="", bg=self.bg_dark, state="disabled")
        self.cards[idx].activate_effect(self)
        if not isinstance(self.cards[idx], (PeekCard, TornadoCard)): self.is_processing = False
        self.update_status()

    def animate_tornado(self, steps):
        if steps > 0:
            if len(self.cards) < 2: return
            self.cards.insert(0, self.cards.pop()); self.buttons.insert(0, self.buttons.pop())
            for i, btn in enumerate(self.buttons):
                btn.grid(row=i//self.current_cols, column=i%self.current_cols)
                btn.config(command=lambda idx=i: self.handle_click(idx))
            self.root.after(60, lambda: self.animate_tornado(steps - 1))
        else: self.is_processing = False

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()