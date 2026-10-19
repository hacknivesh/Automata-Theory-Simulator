import re
import tkinter as tk
from tkinter import font, ttk

# --- CORE DYNAMIC AUTOMATA LOGIC ---
class DynamicAutomata:
    def __init__(self, pattern, condition):
        self.pattern = pattern
        self.condition = condition
        self.m = len(pattern)
        
        if self.condition == "Starts With":
            self.regex = f"^{re.escape(pattern)}.*"
        elif self.condition == "Ends With":
            self.regex = f".*{re.escape(pattern)}$"
        elif self.condition == "Contains (Substring)":
            self.regex = f".*{re.escape(pattern)}.*"

    def get_next_state(self, state, char):
        if state == -1: 
            return -1 
            
        if self.condition == "Starts With":
            if state == self.m: return self.m 
            if char == self.pattern[state]: return state + 1
            return -1 
            
        elif self.condition == "Contains (Substring)":
            if state == self.m: return self.m 
            s = self.pattern[:state] + char
            for i in range(len(s), 0, -1):
                if self.pattern.startswith(s[-i:]): return i
            return 0
            
        elif self.condition == "Ends With":
            s = self.pattern[:state] + char
            for i in range(len(s), 0, -1):
                if self.pattern.startswith(s[-i:]): return i
            return 0

    def is_accepting(self, state):
        return state == self.m

    def validate_via_regex(self, input_string):
        return bool(re.fullmatch(self.regex, input_string))


# --- GUI IMPLEMENTATION WITH VISUAL DIAGRAM ---
class AutomataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic DFA Visualizer")
        self.root.geometry("600x850")
        self.root.configure(bg="#2b2b2b")
        
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=11)
        self.mono_font = font.Font(family="Consolas", size=10)

        # 1. Configuration Section
        config_frame = tk.LabelFrame(root, text=" 1. Define Automata ", font=self.normal_font, bg="#2b2b2b", fg="#00e676", padx=10, pady=10)
        config_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(config_frame, text="Condition:", font=self.normal_font, bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.condition_var = tk.StringVar(value="Ends With")
        self.condition_menu = ttk.Combobox(config_frame, textvariable=self.condition_var, state="readonly", width=25, font=self.normal_font)
        self.condition_menu['values'] = ("Starts With", "Ends With", "Contains (Substring)")
        self.condition_menu.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(config_frame, text="Target Substring:", font=self.normal_font, bg="#2b2b2b", fg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.pattern_var = tk.StringVar(value="ab")
        tk.Entry(config_frame, textvariable=self.pattern_var, font=self.normal_font, width=27).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # 2. Testing Section
        test_frame = tk.LabelFrame(root, text=" 2. Test String ", font=self.normal_font, bg="#2b2b2b", fg="#00e676", padx=10, pady=10)
        test_frame.pack(fill="x", padx=20, pady=5)

        self.test_var = tk.StringVar()
        self.test_entry = tk.Entry(test_frame, textvariable=self.test_var, font=self.normal_font, width=40, justify="center")
        self.test_entry.pack(pady=10, ipady=4)
        self.test_entry.bind("<Return>", lambda e: self.start_validation())

        self.validate_btn = tk.Button(test_frame, text="Simulate DFA", font=self.normal_font, bg="#007acc", fg="white",
                                      activebackground="#005999", relief="flat", cursor="hand2", command=self.start_validation)
        self.validate_btn.pack(pady=5, ipadx=10, ipady=2)

        # 3. Visual Diagram Section (Canvas)
        diag_frame = tk.LabelFrame(root, text=" 3. Live DFA Diagram ", font=self.normal_font, bg="#2b2b2b", fg="#00e676", padx=10, pady=10)
        diag_frame.pack(fill="x", padx=20, pady=5)
        
        self.canvas = tk.Canvas(diag_frame, height=150, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="x", pady=5)
        self.node_ids = {} # Stores canvas IDs for state circles

        # 4. Console & Results
        res_frame = tk.LabelFrame(root, text=" 4. Execution Log ", font=self.normal_font, bg="#2b2b2b", fg="#00e676", padx=10, pady=10)
        res_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.console = tk.Text(res_frame, height=6, bg="#1e1e1e", fg="#d4d4d4", font=self.mono_font, state="disabled", wrap="word")
        self.console.pack(fill="both", expand=True, pady=5)

        self.final_label = tk.Label(root, text="Awaiting Input...", font=font.Font(family="Segoe UI", size=14, weight="bold"), bg="#2b2b2b", fg="#aaaaaa")
        self.final_label.pack(pady=10)

    def draw_dfa_graph(self):
        self.canvas.delete("all")
        self.node_ids.clear()
        
        m = self.automata.m
        spacing = 80
        start_x = 60
        y = 75
        r = 22 # radius
        
        # Start Arrow
        self.canvas.create_line(10, y, start_x - r, y, arrow=tk.LAST, fill="white", width=2)
        
        # Draw Nodes and Forward Transitions
        for i in range(m + 1):
            x = start_x + (i * spacing)
            
            # Forward Transition Arrow (except last node)
            if i < m:
                next_x = start_x + ((i + 1) * spacing)
                self.canvas.create_line(x + r, y, next_x - r, y, arrow=tk.LAST, fill="#aaaaaa", width=2)
                # Transition Label
                char = self.automata.pattern[i]
                self.canvas.create_text((x + next_x)//2, y - 10, text=char, fill="#ffcc00", font=("Consolas", 12, "bold"))
            
            # State Circle
            circle = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#3c3f41", outline="white", width=2)
            self.node_ids[i] = circle
            
            # Accept State (Double Circle)
            if i == m:
                self.canvas.create_oval(x - r + 4, y - r + 4, x + r - 4, y + r - 4, outline="white", width=2)
                
            # State Label
            self.canvas.create_text(x, y, text=f"q{i}", fill="white", font=("Consolas", 10, "bold"))

        # Dead State (for Starts With)
        if self.automata.condition == "Starts With":
            dead_x = start_x + ((m * spacing) // 2)
            dead_y = 135
            circle = self.canvas.create_oval(dead_x - r, dead_y - r, dead_x + r, dead_y + r, fill="#3c3f41", outline="red", width=2)
            self.node_ids[-1] = circle
            self.canvas.create_text(dead_x, dead_y, text="Dead", fill="red", font=("Consolas", 9, "bold"))

    def highlight_state(self, state):
        # Reset all nodes to default color
        for s, oval_id in self.node_ids.items():
            self.canvas.itemconfig(oval_id, fill="#3c3f41")
            
        # Highlight current state
        if state in self.node_ids:
            color = "#F44336" if state == -1 else "#4CAF50" # Red for dead, Green for active
            self.canvas.itemconfig(self.node_ids[state], fill=color)

    def log_console(self, msg):
        self.console.config(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.see("end")
        self.console.config(state="disabled")

    def start_validation(self):
        pattern = self.pattern_var.get()
        condition = self.condition_var.get()
        self.test_string = self.test_var.get()
        
        if not pattern: return

        self.automata = DynamicAutomata(pattern, condition)
        self.draw_dfa_graph()
        
        self.validate_btn.config(state="disabled")
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.config(state="disabled")
        self.final_label.config(text="Simulating...", fg="#ffcc00")

        self.log_console(f"--- Initialization ---")
        self.log_console(f"Pattern: '{pattern}' | Logic: {condition}")
        self.log_console(f"Traversing String: '{self.test_string}'\n")
        
        self.current_state = 0
        self.char_index = 0
        self.highlight_state(self.current_state)
        
        self.root.after(500, self.animate_step)

    def format_state(self, s):
        return f"q{s}" if s != -1 else "Dead State"

    def animate_step(self):
        if self.char_index < len(self.test_string):
            char = self.test_string[self.char_index]
            next_state = self.automata.get_next_state(self.current_state, char)
            
            s_curr = self.format_state(self.current_state)
            s_next = self.format_state(next_state)
            
            self.log_console(f"Read '{char}': {s_curr} \u2192 {s_next}")
            
            self.current_state = next_state
            self.char_index += 1
            self.highlight_state(self.current_state)
            
            if self.current_state == -1 and self.automata.condition == "Starts With":
                self.log_console("Dead State reached. Machine halted.")
                self.root.after(400, self.finish_validation)
            else:
                self.root.after(700, self.animate_step) 
        else:
            self.finish_validation()

    def finish_validation(self):
        dfa_accept = self.automata.is_accepting(self.current_state)
        regex_accept = self.automata.validate_via_regex(self.test_string)
        
        self.log_console(f"\n--- Final Output ---")
        self.log_console(f"End State: {self.format_state(self.current_state)}")
        
        if dfa_accept and regex_accept:
            self.final_label.config(text="FINAL VERDICT: ACCEPTED", fg="#4CAF50")
        else:
            self.final_label.config(text="FINAL VERDICT: REJECTED", fg="#F44336")
            
        self.validate_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomataGUI(root)
    root.mainloop()