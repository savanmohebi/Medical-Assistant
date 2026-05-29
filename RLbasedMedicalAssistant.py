import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import json
import os

# ==========================================
# DATABASE LOADING PROTOCOL
# ==========================================
def load_database(filename="medical_database.json"):
    """Reads the JSON database using an absolute path relative to this script."""
    # 1. Find the exact absolute folder path where gui_app.py lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Safely join that folder path with our database filename
    filepath = os.path.join(script_dir, filename)
    
    # 3. Check if it exists
    if not os.path.exists(filepath):
        messagebox.showerror(
            "Database Error", 
            f"Cannot find the database at:\n{filepath}\n\nPlease ensure the file is named exactly '{filename}'."
        )
        return []
        
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Success: Loaded {len(data)} diseases into memory from {filepath}")
            return data
    except json.JSONDecodeError:
        messagebox.showerror("Database Error", "The JSON file is corrupted or incorrectly formatted.")
        return []

diseases = load_database()


# ==========================================
# ADVANCED WEIGHTED DIAGNOSIS ALGORITHM
# ==========================================

def diagnose(selected_symptoms):
    """Calculates match percentage using a weighted score algorithm."""
    results = []
    
    for d in diseases:
        disease_symptoms = d["symptoms"] # Dictionary of {symptom: weight}
        
        match_weight = 0
        total_weight = sum(disease_symptoms.values())
        
        # Calculate how much weight the user's selected symptoms cover
        for s in selected_symptoms:
            if s in disease_symptoms:
                match_weight += disease_symptoms[s]
                
        if match_weight > 0:
            # Score formula: (Matched Weights / Total Weights) * 100
            score = (match_weight / total_weight) * 100
            results.append((score, d))
            
    # Sort by highest score first (Descending order)
    results.sort(key=lambda x: x[0], reverse=True)
    return results


# ==========================================
# MAIN APPLICATION GUI
# ==========================================

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Savan Medical Aid Clinic")
        self.root.geometry("1250x780")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#eef4fb")

        self.symptom_vars = {}
        self.selected_count_var = tk.StringVar(value="Selected symptoms: 0")

        self.setup_styles()
        self.build_header()
        self.build_layout()
        self.setup_universal_scrolling()

    # ---------------- STYLES ----------------

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Vertical.TScrollbar",
            gripcount=0,
            background="#c7d7ee",
            darkcolor="#c7d7ee",
            lightcolor="#c7d7ee",
            troughcolor="#f4f8fd",
            bordercolor="#f4f8fd",
            arrowcolor="#355c7d"
        )

        style.configure(
            "Blue.Horizontal.TProgressbar",
            troughcolor="#e3edf9",
            background="#0d6efd",
            bordercolor="#e3edf9",
            lightcolor="#0d6efd",
            darkcolor="#0d6efd",
            thickness=14
        )

    # ---------------- HEADER ----------------

    def build_header(self):
        header = tk.Frame(self.root, bg="#0b5ed7", height=90)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🏥 Savan Medical Aid Clinic",
            font=("Segoe UI", 24, "bold"),
            bg="#0b5ed7",
            fg="white"
        ).pack(pady=(14, 2))

        tk.Label(
            header,
            text="Smart weighted symptom-based medical assistant",
            font=("Segoe UI", 11),
            bg="#0b5ed7",
            fg="#dbe9ff"
        ).pack()

    # ---------------- MAIN LAYOUT ----------------

    def build_layout(self):
        main = tk.Frame(self.root, bg="#eef4fb")
        main.pack(fill="both", expand=True, padx=18, pady=18)

        self.build_symptoms_panel(main)
        self.build_result_panel(main)

    # ---------------- LEFT PANEL (SYMPTOMS) ----------------

    def build_symptoms_panel(self, parent):
        left = tk.Frame(parent, bg="white", bd=0, highlightthickness=1, highlightbackground="#d7e3f2")
        left.pack(side="left", fill="y", padx=(0, 14))
        left.pack_propagate(False)
        left.configure(width=400)

        top_box = tk.Frame(left, bg="white")
        top_box.pack(fill="x", padx=18, pady=(18, 10))

        tk.Label(
            top_box, text="🤒 Select Symptoms", font=("Segoe UI", 17, "bold"), bg="white", fg="#1f2d3d"
        ).pack(anchor="w")

        tk.Label(
            top_box, text="Choose all symptoms that match the patient's condition.",
            font=("Segoe UI", 10), bg="white", fg="#6c7a89", wraplength=340, justify="left"
        ).pack(anchor="w", pady=(4, 8))

        tk.Label(
            top_box, textvariable=self.selected_count_var, font=("Segoe UI", 10, "bold"),
            bg="#eef5ff", fg="#0b5ed7", padx=10, pady=6
        ).pack(anchor="w")

        search_frame = tk.Frame(left, bg="white")
        search_frame.pack(fill="x", padx=18, pady=(0, 10))

        tk.Label(search_frame, text="🔎 Search symptom", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w", pady=(0, 4))

        search_input_frame = tk.Frame(search_frame, bg="white")
        search_input_frame.pack(fill="x")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_symptoms())

        search_entry = tk.Entry(search_input_frame, textvariable=self.search_var, font=("Segoe UI", 11), relief="solid", bd=1)
        search_entry.pack(side="left", fill="x", expand=True, ipady=6)

        tk.Button(
            search_input_frame, text="✖", font=("Segoe UI", 9), bg="#f1f5f9", fg="#64748b",
            relief="flat", command=lambda: self.search_var.set(""), cursor="hand2"
        ).pack(side="right", padx=(5, 0), ipadx=5, ipady=4)

        list_container = tk.Frame(left, bg="#f8fbff", bd=0, highlightthickness=1, highlightbackground="#e2ebf5")
        list_container.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.symptom_canvas = tk.Canvas(list_container, bg="#f8fbff", highlightthickness=0)
        self.symptom_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.symptom_canvas.yview, style="Custom.Vertical.TScrollbar")
        self.symptoms_frame = tk.Frame(self.symptom_canvas, bg="#f8fbff")
        self.symptom_canvas_window = self.symptom_canvas.create_window((0, 0), window=self.symptoms_frame, anchor="nw")

        self.symptoms_frame.bind("<Configure>", lambda e: self.symptom_canvas.configure(scrollregion=self.symptom_canvas.bbox("all")))
        self.symptom_canvas.bind("<Configure>", lambda e: self.symptom_canvas.itemconfig(self.symptom_canvas_window, width=e.width))

        self.symptom_canvas.configure(yscrollcommand=self.symptom_scrollbar.set)
        self.symptom_canvas.pack(side="left", fill="both", expand=True)
        self.symptom_scrollbar.pack(side="right", fill="y")

        self.all_symptoms = self.get_all_symptoms()
        self.refresh_symptoms()

    # ---------------- RIGHT PANEL (RESULTS) ----------------

    def build_result_panel(self, parent):
        right = tk.Frame(parent, bg="#eef4fb")
        right.pack(side="left", fill="both", expand=True)

        top = tk.Frame(right, bg="#eef4fb")
        top.pack(fill="x")

        tk.Label(top, text="🔬 Diagnosis Results", font=("Segoe UI", 20, "bold"), bg="#eef4fb", fg="#1f2d3d").pack(anchor="w")
        tk.Label(top, text="Analyze selected symptoms and review likely conditions.", font=("Segoe UI", 10), bg="#eef4fb", fg="#6c7a89").pack(anchor="w", pady=(3, 12))

        btn_frame = tk.Frame(right, bg="#eef4fb")
        btn_frame.pack(anchor="w", pady=(0, 12))

        tk.Button(
            btn_frame, text="🧠 Analyze", font=("Segoe UI", 12, "bold"), bg="#0d6efd", fg="white",
            activebackground="#0b5ed7", activeforeground="white", relief="flat", bd=0, padx=20, pady=10,
            cursor="hand2", command=self.analyze
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="♻ Reset", font=("Segoe UI", 12), bg="white", fg="#2c3e50",
            activebackground="#f1f5f9", relief="flat", bd=0, padx=20, pady=10, cursor="hand2", command=self.reset
        ).pack(side="left")

        result_container = tk.Frame(right, bg="white", highlightthickness=1, highlightbackground="#d7e3f2")
        result_container.pack(fill="both", expand=True)

        self.result_canvas = tk.Canvas(result_container, bg="white", highlightthickness=0)
        result_scrollbar = ttk.Scrollbar(result_container, orient="vertical", command=self.result_canvas.yview, style="Custom.Vertical.TScrollbar")
        self.result_frame = tk.Frame(self.result_canvas, bg="white")
        self.result_canvas_window = self.result_canvas.create_window((0, 0), window=self.result_frame, anchor="nw")

        self.result_frame.bind("<Configure>", lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        self.result_canvas.bind("<Configure>", lambda e: self.result_canvas.itemconfig(self.result_canvas_window, width=e.width))

        self.result_canvas.configure(yscrollcommand=result_scrollbar.set)
        self.result_canvas.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")

        self.show_welcome_message()

    # ---------------- EVENT HANDLERS ----------------

    def setup_universal_scrolling(self):
        def _on_mousewheel(event):
            widget = self.root.winfo_containing(event.x_root, event.y_root)
            while widget:
                if isinstance(widget, tk.Canvas):
                    if hasattr(event, "delta") and event.delta != 0:
                        widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    elif hasattr(event, "num"):
                        if event.num == 4: widget.yview_scroll(-1, "units")
                        elif event.num == 5: widget.yview_scroll(1, "units")
                    break
                widget = widget.master
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        self.root.bind_all("<Button-4>", _on_mousewheel)
        self.root.bind_all("<Button-5>", _on_mousewheel)

    def show_welcome_message(self):
        self.clear_result_frame()
        box = tk.Frame(self.result_frame, bg="#f8fbff", bd=0, highlightthickness=1, highlightbackground="#e1ebf5")
        box.pack(fill="x", padx=20, pady=20)
        tk.Label(box, text="🩺 Ready for analysis", font=("Segoe UI", 16, "bold"), bg="#f8fbff", fg="#1f2d3d").pack(anchor="w", padx=20, pady=(18, 6))
        tk.Label(
            box, text="Select symptoms from the left panel, then click Analyze to view possible diseases, medications, and home remedies.",
            font=("Segoe UI", 11), bg="#f8fbff", fg="#5f6b7a", wraplength=700, justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 18))

    # ---------------- SYMPTOMS LOGIC ----------------

    def get_all_symptoms(self):
        s = set()
        for d in diseases:
            for sym in d["symptoms"].keys():
                s.add(sym)
        return sorted(s)

    def refresh_symptoms(self):
        for w in self.symptoms_frame.winfo_children():
            w.destroy()

        query = self.search_var.get().strip().lower()

        for sym in self.all_symptoms:
            if query and query not in sym.lower():
                continue
            if sym not in self.symptom_vars:
                self.symptom_vars[sym] = tk.BooleanVar()

            row = tk.Frame(self.symptoms_frame, bg="#f8fbff")
            row.pack(fill="x", padx=10, pady=2)

            cb = tk.Checkbutton(
                row, text="🧬 " + sym.title(), variable=self.symptom_vars[sym],
                bg="#f8fbff", activebackground="#f8fbff", anchor="w",
                font=("Segoe UI", 11), relief="flat", command=self.update_selected_count, cursor="hand2"
            )
            cb.pack(fill="x", padx=6, pady=2)
        self.update_selected_count()

    def update_selected_count(self):
        count = sum(1 for v in self.symptom_vars.values() if v.get())
        self.selected_count_var.set(f"Selected symptoms: {count}")

    # ---------------- ANALYSIS LOGIC ----------------

    def clear_result_frame(self):
        for w in self.result_frame.winfo_children():
            w.destroy()

    def analyze(self):
        self.clear_result_frame()
        self.result_canvas.yview_moveto(0)

        selected = [s for s, v in self.symptom_vars.items() if v.get()]

        if not selected:
            warn = tk.Frame(self.result_frame, bg="#fff4e5", highlightthickness=1, highlightbackground="#ffd59e")
            warn.pack(fill="x", padx=20, pady=20)
            tk.Label(warn, text="⚠ Please select at least one symptom.", font=("Segoe UI", 13, "bold"), bg="#fff4e5", fg="#8a5700").pack(anchor="w", padx=15, pady=15)
            return

        results = diagnose(selected)

        if not results:
            empty = tk.Frame(self.result_frame, bg="#f8fbff", highlightthickness=1, highlightbackground="#dce8f5")
            empty.pack(fill="x", padx=20, pady=20)
            tk.Label(empty, text="No matching diseases found.", font=("Segoe UI", 14, "bold"), bg="#f8fbff", fg="#2c3e50").pack(anchor="w", padx=15, pady=(15, 5))
            tk.Label(empty, text="Try selecting additional or more accurate symptoms.", font=("Segoe UI", 11), bg="#f8fbff", fg="#6c7a89").pack(anchor="w", padx=15, pady=(0, 15))
            return

        summary = tk.Frame(self.result_frame, bg="#eef5ff", highlightthickness=1, highlightbackground="#cfe0ff")
        summary.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(summary, text=f"Found {len(results)} possible condition(s)", font=("Segoe UI", 14, "bold"), bg="#eef5ff", fg="#0b5ed7").pack(anchor="w", padx=15, pady=15)

        for score, disease in results:
            self.create_disease_card(score, disease)

    # ---------------- RESULT CARDS ----------------

    def create_disease_card(self, score, disease):
        card = tk.Frame(self.result_frame, bg="white", bd=0, highlightthickness=1, highlightbackground="#dbe5f0")
        card.pack(fill="x", padx=20, pady=10)

        # Header Frame
        top = tk.Frame(card, bg="#f8fbff")
        top.pack(fill="x")

        # Disease Title & Category
        title_frame = tk.Frame(top, bg="#f8fbff")
        title_frame.pack(side="left", padx=15, pady=12)

        tk.Label(title_frame, text=f"🦠 {disease['name']}", font=("Segoe UI", 15, "bold"), bg="#f8fbff", fg="#1f2d3d").pack(side="left")
        
        # Category Badge
        tk.Label(
            title_frame, text=disease.get('category', 'General').upper(), font=("Segoe UI", 8, "bold"), 
            bg="#d2e3fc", fg="#174ea6", padx=8, pady=2
        ).pack(side="left", padx=(10, 0))

        # Percentage Score
        tk.Label(
            top, text=f"{score:.1f}%", font=("Segoe UI", 12, "bold"), bg="#e8f1ff", fg="#0b5ed7", padx=12, pady=5
        ).pack(side="right", padx=15)

        # Body Frame
        body = tk.Frame(card, bg="white")
        body.pack(fill="x", padx=15, pady=12)

        tk.Label(body, text="Match Strength", font=("Segoe UI", 10, "bold"), bg="white", fg="#4a5568").pack(anchor="w")

        bar = ttk.Progressbar(body, style="Blue.Horizontal.TProgressbar", mode="determinate")
        bar["value"] = score
        bar.pack(fill="x", pady=(6, 14))

        # Medical Fields
        meds_text = "💊 Medications: " + ", ".join(disease.get("medications", []))
        tk.Label(body, text=meds_text, bg="white", fg="#2d3748", wraplength=760, justify="left", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 8))

        home_text = "🏠 Home Remedies: " + ", ".join(disease.get("home_remedies", []))
        tk.Label(body, text=home_text, bg="white", fg="#2d3748", wraplength=760, justify="left", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 5))

        symp_text = "🧾 Related Symptoms: " + ", ".join(disease["symptoms"].keys())
        tk.Label(body, text=symp_text, bg="white", fg="#5f6b7a", wraplength=760, justify="left", font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(6, 10))

        # Doctor Warning Block
        if "doctor_when" in disease:
            warning_frame = tk.Frame(body, bg="#fff3cd", bd=1, relief="solid")
            warning_frame.pack(fill="x", pady=(5, 0))
            
            tk.Label(
                warning_frame, text=f"🚨 When to see a doctor: {disease['doctor_when']}", 
                bg="#fff3cd", fg="#856404", font=("Segoe UI", 10, "bold"), anchor="w", justify="left", wraplength=740
            ).pack(fill="x", padx=10, pady=8)

    # ---------------- RESET LOGIC ----------------

    def reset(self):
        for v in self.symptom_vars.values():
            v.set(False)

        self.search_var.set("")
        self.update_selected_count()
        self.show_welcome_message()


# ==========================================
# EXECUTION
# ==========================================

if __name__ == "__main__":
    # Check if the database loaded properly before launching the GUI
    if len(diseases) == 0:
        print("Warning: Database is empty. The application will launch, but no symptoms or diseases will be available.")
        
    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()
