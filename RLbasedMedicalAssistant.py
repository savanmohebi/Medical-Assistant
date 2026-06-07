import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


APP_TITLE = "Savan Medical Aid Clinic"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "medical_database.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback_log.json")
HISTORY_FILE = os.path.join(BASE_DIR, "diagnosis_history.json")

DISCLAIMER = (
    "This tool is an educational, rule-based assistant. It does not diagnose, prescribe, "
    "or replace a licensed clinician. Seek urgent medical care for severe symptoms."
)

EMERGENCY_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "severe headache",
    "confusion",
    "fainting",
    "seizure",
    "blood in stool",
    "vomiting blood",
    "severe abdominal pain",
    "high fever",
    "stiff neck",
    "severe allergic reaction",
}

PALETTE = {
    "bg": "#0a1020",
    "bg_alt": "#101a33",
    "panel": "#17233f",
    "panel_soft": "#1d2c4e",
    "glass": "#203257",
    "glass_light": "#2b416d",
    "primary": "#6d7cff",
    "primary_dark": "#9aa6ff",
    "accent": "#47d9ff",
    "text": "#f7f9ff",
    "muted": "#b7c4d9",
    "line": "#40567f",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "danger": "#fb7185",
}

GLASS_BORDER = "#5a6f9b"
SHADOW = "#07101f"


def load_json_file(path, fallback):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return fallback


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_database(filename=DATABASE_FILE):
    if not os.path.exists(filename):
        return []
    data = load_json_file(filename, [])
    normalized = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if "name" not in item or "symptoms" not in item or not isinstance(item["symptoms"], dict):
            continue
        item.setdefault("category", "General")
        item.setdefault("medications", [])
        item.setdefault("home_remedies", [])
        item.setdefault("doctor_when", "Consult a clinician if symptoms persist, worsen, or feel unusual.")
        normalized.append(item)
    return normalized


DISEASES = load_database()


def confidence_label(score):
    if score >= 75:
        return "Strong match", PALETTE["success"]
    if score >= 45:
        return "Moderate match", PALETTE["warning"]
    return "Possible match", PALETTE["muted"]


def diagnose(selected_symptoms, category="All"):
    selected = set(selected_symptoms)
    results = []

    for disease in DISEASES:
        if category != "All" and disease.get("category") != category:
            continue

        disease_symptoms = disease["symptoms"]
        total_weight = sum(disease_symptoms.values()) or 1
        matched = sorted(selected.intersection(disease_symptoms.keys()))
        missing = sorted(set(disease_symptoms.keys()) - selected)
        match_weight = sum(disease_symptoms[symptom] for symptom in matched)

        if match_weight <= 0:
            continue

        score = (match_weight / total_weight) * 100
        coverage = len(matched) / max(1, len(disease_symptoms))
        results.append(
            {
                "score": score,
                "coverage": coverage,
                "disease": disease,
                "matched": matched,
                "missing": missing,
            }
        )

    results.sort(key=lambda result: (result["score"], result["coverage"]), reverse=True)
    return results


def selected_red_flags(selected_symptoms):
    selected = {symptom.lower() for symptom in selected_symptoms}
    return sorted(selected.intersection(EMERGENCY_SYMPTOMS))


class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1320x820")
        self.root.minsize(1120, 720)
        self.root.configure(bg=PALETTE["bg"])
        self.root.option_add("*insertBackground", PALETTE["text"])

        self.symptom_vars = {}
        self.last_results = []
        self.last_selected = []
        self.all_symptoms = self.get_all_symptoms()
        self.categories = ["All"] + sorted({disease.get("category", "General") for disease in DISEASES})

        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="All")
        self.selected_count_var = tk.StringVar(value="Selected: 0")
        self.selected_preview_var = tk.StringVar(value="No symptoms selected yet")
        self.status_var = tk.StringVar(value=f"Loaded {len(DISEASES)} conditions and {len(self.all_symptoms)} symptoms")

        self.setup_styles()
        self.build_header()
        self.build_body()
        self.build_status_bar()
        self.bind_events()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", gripcount=0, background=PALETTE["glass_light"], troughcolor=PALETTE["bg_alt"], bordercolor=PALETTE["bg_alt"], arrowcolor=PALETTE["accent"], darkcolor=PALETTE["glass_light"], lightcolor=PALETTE["glass_light"])
        style.configure("Blue.Horizontal.TProgressbar", troughcolor=PALETTE["bg_alt"], background=PALETTE["accent"], bordercolor=PALETTE["bg_alt"], lightcolor=PALETTE["accent"], darkcolor=PALETTE["primary"], thickness=13)
        style.configure("TCombobox", fieldbackground=PALETTE["glass"], background=PALETTE["glass"], foreground=PALETTE["text"], arrowcolor=PALETTE["accent"], bordercolor=PALETTE["line"], lightcolor=PALETTE["line"], darkcolor=PALETTE["line"])

    def build_header(self):
        header = tk.Frame(self.root, bg=PALETTE["bg_alt"], height=112, highlightthickness=1, highlightbackground=GLASS_BORDER)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_row = tk.Frame(header, bg=PALETTE["bg_alt"])
        title_row.pack(fill="x", padx=24, pady=(16, 4))

        tk.Label(title_row, text="🏥 Savan Medical Aid Clinic", font=("Segoe UI", 25, "bold"), bg=PALETTE["bg_alt"], fg=PALETTE["text"]).pack(side="left")
        tk.Button(title_row, text="📜 History", command=self.show_history, bg=PALETTE["glass_light"], fg=PALETTE["text"], activebackground=PALETTE["primary"], activeforeground="white", relief="flat", padx=14, pady=7, cursor="hand2").pack(side="right")

        tk.Label(header, text=DISCLAIMER, font=("Segoe UI", 10), bg=PALETTE["bg_alt"], fg=PALETTE["muted"], wraplength=1120, justify="left").pack(anchor="w", padx=24)

    def build_body(self):
        main = tk.Frame(self.root, bg=PALETTE["bg"])
        main.pack(fill="both", expand=True, padx=18, pady=18)
        self.build_symptoms_panel(main)
        self.build_results_panel(main)

    def build_symptoms_panel(self, parent):
        left = self.panel(parent)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.configure(width=410)
        left.pack_propagate(False)

        tk.Label(left, text="🤒 Patient Symptoms", font=("Segoe UI", 18, "bold"), bg=PALETTE["panel"], fg=PALETTE["text"]).pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(left, text="Select every symptom that applies. Use search and category filters to narrow suggestions.", font=("Segoe UI", 10), bg=PALETTE["panel"], fg=PALETTE["muted"], wraplength=350, justify="left").pack(anchor="w", padx=18)

        meta = tk.Frame(left, bg=PALETTE["panel"])
        meta.pack(fill="x", padx=18, pady=(12, 8))
        tk.Label(meta, textvariable=self.selected_count_var, font=("Segoe UI", 10, "bold"), bg=PALETTE["glass_light"], fg=PALETTE["primary_dark"], padx=10, pady=6).pack(side="left")
        tk.Button(meta, text="Clear", command=self.reset_symptoms, bg=PALETTE["glass_light"], fg=PALETTE["text"], relief="flat", cursor="hand2", padx=10, pady=5).pack(side="right")

        selected_box = tk.Frame(left, bg=PALETTE["glass"], highlightthickness=1, highlightbackground=GLASS_BORDER)
        selected_box.pack(fill="x", padx=18, pady=(0, 12))
        tk.Label(selected_box, text="Selected Symptoms", font=("Segoe UI", 9, "bold"), bg=PALETTE["glass"], fg=PALETTE["primary_dark"]).pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(selected_box, textvariable=self.selected_preview_var, font=("Segoe UI", 10), bg=PALETTE["glass"], fg=PALETTE["text"], wraplength=335, justify="left").pack(anchor="w", padx=10, pady=(0, 9))

        filters = tk.Frame(left, bg=PALETTE["panel"])
        filters.pack(fill="x", padx=18, pady=(0, 10))
        tk.Label(filters, text="Search", font=("Segoe UI", 9, "bold"), bg=PALETTE["panel"], fg=PALETTE["text"]).pack(anchor="w")
        search_entry = tk.Entry(filters, textvariable=self.search_var, font=("Segoe UI", 11), relief="flat", bd=0, insertbackground=PALETTE["text"], bg=PALETTE["glass"], fg=PALETTE["text"], highlightthickness=1, highlightbackground=GLASS_BORDER, highlightcolor=PALETTE["accent"])
        search_entry.pack(fill="x", ipady=7, pady=(4, 9))
        tk.Label(filters, text="Condition Category", font=("Segoe UI", 9, "bold"), bg=PALETTE["panel"], fg=PALETTE["text"]).pack(anchor="w")
        category_combo = ttk.Combobox(filters, values=self.categories, textvariable=self.category_var, state="readonly")
        category_combo.pack(fill="x", ipady=4, pady=(4, 0))

        list_container = tk.Frame(left, bg=PALETTE["panel_soft"], highlightthickness=1, highlightbackground=GLASS_BORDER)
        list_container.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.symptom_canvas = tk.Canvas(list_container, bg=PALETTE["panel_soft"], highlightthickness=0)
        self.symptoms_frame = tk.Frame(self.symptom_canvas, bg=PALETTE["panel_soft"])
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.symptom_canvas.yview)
        self.symptom_window = self.symptom_canvas.create_window((0, 0), window=self.symptoms_frame, anchor="nw")
        self.symptom_canvas.configure(yscrollcommand=scrollbar.set)
        self.symptoms_frame.bind("<Configure>", lambda event: self.symptom_canvas.configure(scrollregion=self.symptom_canvas.bbox("all")))
        self.symptom_canvas.bind("<Configure>", lambda event: self.symptom_canvas.itemconfig(self.symptom_window, width=event.width))
        self.symptom_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.refresh_symptoms()

    def build_results_panel(self, parent):
        right = tk.Frame(parent, bg=PALETTE["bg"])
        right.pack(side="left", fill="both", expand=True)

        toolbar = tk.Frame(right, bg=PALETTE["bg"])
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="🔬 Clinical Rule-Based Results", font=("Segoe UI", 21, "bold"), bg=PALETTE["bg"], fg=PALETTE["text"]).pack(side="left")
        tk.Button(toolbar, text="🧠 Analyze", command=self.analyze, bg=PALETTE["primary"], fg="white", activebackground=PALETTE["accent"], activeforeground=PALETTE["bg"], relief="flat", padx=18, pady=10, cursor="hand2", font=("Segoe UI", 11, "bold")).pack(side="right", padx=(8, 0))
        tk.Button(toolbar, text="📄 Export", command=self.export_report, bg=PALETTE["glass_light"], fg=PALETTE["text"], activebackground=PALETTE["primary"], activeforeground="white", relief="flat", padx=16, pady=10, cursor="hand2").pack(side="right", padx=(8, 0))
        tk.Button(toolbar, text="📋 Copy", command=self.copy_report, bg=PALETTE["glass_light"], fg=PALETTE["text"], activebackground=PALETTE["primary"], activeforeground="white", relief="flat", padx=16, pady=10, cursor="hand2").pack(side="right")

        tk.Label(right, text="Results show likely matches, matched symptoms, missing symptoms, self-care guidance, and when to see a doctor.", font=("Segoe UI", 10), bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(anchor="w", pady=(4, 12))

        result_container = self.panel(right)
        result_container.pack(fill="both", expand=True)
        self.result_canvas = tk.Canvas(result_container, bg=PALETTE["panel"], highlightthickness=0)
        self.result_frame = tk.Frame(self.result_canvas, bg=PALETTE["panel"])
        scrollbar = ttk.Scrollbar(result_container, orient="vertical", command=self.result_canvas.yview)
        self.result_window = self.result_canvas.create_window((0, 0), window=self.result_frame, anchor="nw")
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        self.result_frame.bind("<Configure>", lambda event: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        self.result_canvas.bind("<Configure>", lambda event: self.result_canvas.itemconfig(self.result_window, width=event.width))
        self.result_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.show_welcome_message()

    def build_status_bar(self):
        status = tk.Label(self.root, textvariable=self.status_var, anchor="w", bg=PALETTE["bg_alt"], fg=PALETTE["muted"], font=("Segoe UI", 9), padx=12, pady=5)
        status.pack(fill="x", side="bottom")

    def bind_events(self):
        self.search_var.trace_add("write", lambda *args: self.refresh_symptoms())
        self.category_var.trace_add("write", lambda *args: self.refresh_symptoms())
        self.root.bind("<Control-Return>", lambda event: self.analyze())
        self.root.bind("<Control-r>", lambda event: self.reset())
        self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind_all("<Button-4>", self.on_mousewheel)
        self.root.bind_all("<Button-5>", self.on_mousewheel)

    def panel(self, parent):
        return tk.Frame(parent, bg=PALETTE["panel"], bd=0, highlightthickness=1, highlightbackground=GLASS_BORDER)

    def on_mousewheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget:
            if isinstance(widget, tk.Canvas):
                if getattr(event, "delta", 0):
                    widget.yview_scroll(int(-event.delta / 120), "units")
                elif getattr(event, "num", None) == 4:
                    widget.yview_scroll(-1, "units")
                elif getattr(event, "num", None) == 5:
                    widget.yview_scroll(1, "units")
                break
            widget = widget.master

    def get_all_symptoms(self):
        symptoms = set()
        for disease in DISEASES:
            symptoms.update(disease["symptoms"].keys())
        return sorted(symptoms)

    def symptoms_for_current_category(self):
        category = self.category_var.get()
        if category == "All":
            return self.all_symptoms
        symptoms = set()
        for disease in DISEASES:
            if disease.get("category") == category:
                symptoms.update(disease["symptoms"].keys())
        return sorted(symptoms)

    def refresh_symptoms(self):
        for widget in self.symptoms_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().strip().lower()
        visible_count = 0
        for symptom in self.symptoms_for_current_category():
            if query and query not in symptom.lower():
                continue
            if symptom not in self.symptom_vars:
                self.symptom_vars[symptom] = tk.BooleanVar()
            row = tk.Frame(self.symptoms_frame, bg=PALETTE["panel_soft"])
            row.pack(fill="x", padx=10, pady=2)
            checkbutton = tk.Checkbutton(
                row,
                text="🧬 " + symptom.title(),
                variable=self.symptom_vars[symptom],
                bg=PALETTE["panel_soft"],
                activebackground=PALETTE["glass"],
                activeforeground=PALETTE["text"],
                fg=PALETTE["text"],
                selectcolor=PALETTE["primary"],
                anchor="w",
                font=("Segoe UI", 10),
                relief="flat",
                command=self.update_selected_count,
                cursor="hand2",
            )
            checkbutton.pack(fill="x", padx=5, pady=2)
            visible_count += 1

        if visible_count == 0:
            tk.Label(self.symptoms_frame, text="No symptoms found.", bg=PALETTE["panel_soft"], fg=PALETTE["muted"], font=("Segoe UI", 11)).pack(pady=24)
        self.update_selected_count()

    def update_selected_count(self):
        selected = [symptom.title() for symptom, variable in self.symptom_vars.items() if variable.get()]
        self.selected_count_var.set(f"Selected: {len(selected)}")
        if selected:
            preview = ", ".join(selected[:8])
            if len(selected) > 8:
                preview += f" + {len(selected) - 8} more"
            self.selected_preview_var.set(preview)
        else:
            self.selected_preview_var.set("No symptoms selected yet")

    def reset_symptoms(self):
        for variable in self.symptom_vars.values():
            variable.set(False)
        self.update_selected_count()

    def reset(self):
        self.reset_symptoms()
        self.search_var.set("")
        self.category_var.set("All")
        self.last_results = []
        self.last_selected = []
        self.show_welcome_message()
        self.status_var.set("Reset complete")

    def clear_result_frame(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def show_welcome_message(self):
        self.clear_result_frame()
        card = tk.Frame(self.result_frame, bg=PALETTE["panel_soft"], highlightthickness=1, highlightbackground=GLASS_BORDER)
        card.pack(fill="x", padx=22, pady=22)
        tk.Label(card, text="🩺 Ready for analysis", font=("Segoe UI", 18, "bold"), bg=PALETTE["panel_soft"], fg=PALETTE["text"]).pack(anchor="w", padx=20, pady=(18, 6))
        tk.Label(card, text="Select symptoms, optionally filter by category, then press Analyze. Use Ctrl+Enter to analyze and Ctrl+R to reset.", font=("Segoe UI", 11), bg=PALETTE["panel_soft"], fg=PALETTE["muted"], wraplength=760, justify="left").pack(anchor="w", padx=20, pady=(0, 12))
        tk.Label(card, text="Safety first: red-flag symptoms trigger urgent-care guidance before showing condition matches.", font=("Segoe UI", 10, "bold"), bg="#3b2f18", fg=PALETTE["warning"], wraplength=760, justify="left", padx=12, pady=8).pack(fill="x", padx=20, pady=(0, 18))

    def analyze(self):
        selected = [symptom for symptom, variable in self.symptom_vars.items() if variable.get()]
        self.last_selected = selected
        self.clear_result_frame()
        self.result_canvas.yview_moveto(0)

        if not selected:
            self.notice("⚠ Please select at least one symptom.", "Choose symptoms from the left panel before analyzing.", "#3b2f18", PALETTE["warning"])
            return

        flags = selected_red_flags(selected)
        if flags:
            self.red_flag_card(flags)

        category = self.category_var.get()
        self.last_results = diagnose(selected, category)
        if not self.last_results:
            self.notice("No matching conditions found.", "Try selecting additional symptoms or changing the category filter.", PALETTE["panel_soft"], PALETTE["text"])
            return

        self.summary_card(selected, category)
        for result in self.last_results[:8]:
            self.create_disease_card(result)
        self.save_history(selected, self.last_results[:5])
        self.status_var.set(f"Analyzed {len(selected)} symptoms · showing top {min(8, len(self.last_results))} of {len(self.last_results)} matches")

    def notice(self, title, text, bg, fg):
        box = tk.Frame(self.result_frame, bg=bg, highlightthickness=1, highlightbackground=GLASS_BORDER)
        box.pack(fill="x", padx=22, pady=22)
        tk.Label(box, text=title, font=("Segoe UI", 14, "bold"), bg=bg, fg=fg).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(box, text=text, font=("Segoe UI", 10), bg=bg, fg=fg, wraplength=760, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

    def red_flag_card(self, flags):
        box = tk.Frame(self.result_frame, bg="#3a1722", highlightthickness=1, highlightbackground=PALETTE["danger"])
        box.pack(fill="x", padx=22, pady=(22, 10))
        tk.Label(box, text="🚨 Urgent-care warning", font=("Segoe UI", 15, "bold"), bg="#3a1722", fg=PALETTE["danger"]).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(box, text="Selected red-flag symptoms: " + ", ".join(flag.title() for flag in flags), font=("Segoe UI", 11, "bold"), bg="#3a1722", fg=PALETTE["danger"], wraplength=800, justify="left").pack(anchor="w", padx=16)
        tk.Label(box, text="If symptoms are severe, sudden, worsening, or life-threatening, seek emergency medical care now.", font=("Segoe UI", 10), bg="#3a1722", fg="#fecdd3", wraplength=800, justify="left").pack(anchor="w", padx=16, pady=(4, 14))

    def summary_card(self, selected, category):
        box = tk.Frame(self.result_frame, bg=PALETTE["glass"], highlightthickness=1, highlightbackground=GLASS_BORDER)
        box.pack(fill="x", padx=22, pady=(10, 10))
        tk.Label(box, text=f"Found {len(self.last_results)} possible match(es)", font=("Segoe UI", 15, "bold"), bg=PALETTE["glass"], fg=PALETTE["primary_dark"]).pack(anchor="w", padx=16, pady=(14, 4))
        detail = f"Category: {category} · Symptoms: " + ", ".join(symptom.title() for symptom in selected)
        tk.Label(box, text=detail, font=("Segoe UI", 10), bg=PALETTE["glass"], fg=PALETTE["muted"], wraplength=860, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

    def create_disease_card(self, result):
        score = result["score"]
        disease = result["disease"]
        label, label_color = confidence_label(score)

        card = tk.Frame(self.result_frame, bg=PALETTE["panel"], highlightthickness=1, highlightbackground=GLASS_BORDER)
        card.pack(fill="x", padx=22, pady=10)

        top = tk.Frame(card, bg=PALETTE["panel_soft"])
        top.pack(fill="x")
        title_area = tk.Frame(top, bg=PALETTE["panel_soft"])
        title_area.pack(side="left", fill="x", expand=True, padx=16, pady=12)
        tk.Label(title_area, text=f"🦠 {disease['name']}", font=("Segoe UI", 15, "bold"), bg=PALETTE["panel_soft"], fg=PALETTE["text"]).pack(side="left")
        tk.Label(title_area, text=disease.get("category", "General").upper(), font=("Segoe UI", 8, "bold"), bg=PALETTE["glass_light"], fg=PALETTE["primary_dark"], padx=8, pady=3).pack(side="left", padx=(10, 0))
        tk.Label(top, text=f"{score:.1f}% · {label}", font=("Segoe UI", 10, "bold"), bg="#173725" if score >= 75 else "#3b2f18", fg=label_color, padx=12, pady=6).pack(side="right", padx=16)

        body = tk.Frame(card, bg=PALETTE["panel"])
        body.pack(fill="x", padx=16, pady=14)
        tk.Label(body, text="Match Strength", font=("Segoe UI", 10, "bold"), bg=PALETTE["panel"], fg=PALETTE["text"]).pack(anchor="w")
        progress = ttk.Progressbar(body, style="Blue.Horizontal.TProgressbar", mode="determinate", maximum=100)
        progress["value"] = score
        progress.pack(fill="x", pady=(6, 12))

        self.info_line(body, "✅ Matched", ", ".join(symptom.title() for symptom in result["matched"]))
        self.info_line(body, "🔎 Also associated", ", ".join(symptom.title() for symptom in result["missing"][:10]) or "None")
        self.info_line(body, "💊 Medication ideas", ", ".join(disease.get("medications", [])) or "Not listed")
        self.info_line(body, "🏠 Home care", ", ".join(disease.get("home_remedies", [])) or "Not listed")

        warning = tk.Frame(body, bg="#3b2f18", highlightthickness=1, highlightbackground=PALETTE["warning"])
        warning.pack(fill="x", pady=(8, 0))
        tk.Label(warning, text="🚨 When to see a doctor: " + disease.get("doctor_when", "Consult a clinician if symptoms persist."), bg="#3b2f18", fg="#fde68a", font=("Segoe UI", 10, "bold"), wraplength=820, justify="left").pack(anchor="w", padx=10, pady=8)

    def info_line(self, parent, label, value):
        tk.Label(parent, text=f"{label}: {value}", bg=PALETTE["panel"], fg=PALETTE["text"], wraplength=860, justify="left", font=("Segoe UI", 10)).pack(anchor="w", pady=3)

    def build_report_text(self):
        if not self.last_results:
            return "No diagnosis report available yet. Run Analyze first."
        lines = [APP_TITLE, datetime.now().strftime("Generated: %Y-%m-%d %H:%M"), "", DISCLAIMER, "", "Selected symptoms:", ", ".join(self.last_selected), "", "Top matches:"]
        for index, result in enumerate(self.last_results[:8], start=1):
            disease = result["disease"]
            lines.extend(
                [
                    "",
                    f"{index}. {disease['name']} ({disease.get('category', 'General')}) - {result['score']:.1f}%",
                    "Matched: " + ", ".join(result["matched"]),
                    "Medication ideas: " + ", ".join(disease.get("medications", [])),
                    "Home care: " + ", ".join(disease.get("home_remedies", [])),
                    "Doctor visit: " + disease.get("doctor_when", "Consult a clinician if symptoms persist."),
                ]
            )
        return "\n".join(lines)

    def copy_report(self):
        report = self.build_report_text()
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        self.status_var.set("Report copied to clipboard")

    def export_report(self):
        if not self.last_results:
            messagebox.showinfo("Export", "Run Analyze first, then export the report.")
            return
        default_name = "medical_assistant_report.txt"
        path = filedialog.asksaveasfilename(initialdir=BASE_DIR, initialfile=default_name, defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as file:
            file.write(self.build_report_text())
        self.status_var.set(f"Report exported: {path}")

    def save_history(self, selected, results):
        history = load_json_file(HISTORY_FILE, [])
        history.insert(
            0,
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "category": self.category_var.get(),
                "symptoms": selected,
                "results": [
                    {"name": item["disease"]["name"], "category": item["disease"].get("category"), "score": round(item["score"], 1)}
                    for item in results
                ],
            },
        )
        save_json_file(HISTORY_FILE, history[:50])

    def show_history(self):
        history = load_json_file(HISTORY_FILE, [])
        window = tk.Toplevel(self.root)
        window.title("Diagnosis History")
        window.geometry("760x520")
        window.configure(bg=PALETTE["bg"])
        tk.Label(window, text="📜 Recent Diagnosis History", font=("Segoe UI", 17, "bold"), bg=PALETTE["bg"], fg=PALETTE["text"]).pack(anchor="w", padx=16, pady=(14, 8))
        text = tk.Text(window, wrap="word", font=("Segoe UI", 10), bg=PALETTE["glass_light"], fg=PALETTE["text"], insertbackground=PALETTE["text"], selectbackground=PALETTE["primary"], relief="flat")
        text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        if not history:
            text.insert("end", "No history yet. Run an analysis first.")
        for item in history:
            text.insert("end", f"{item.get('time')} · {item.get('category', 'All')}\n")
            text.insert("end", "Symptoms: " + ", ".join(item.get("symptoms", [])) + "\n")
            for result in item.get("results", []):
                text.insert("end", f"  - {result.get('name')} ({result.get('score')}%)\n")
            text.insert("end", "\n")
        text.configure(state="disabled")

    def log_feedback(self, helpful):
        if not self.last_results:
            messagebox.showinfo("Feedback", "Run an analysis first.")
            return
        feedback = load_json_file(FEEDBACK_FILE, [])
        feedback.insert(
            0,
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "helpful": helpful,
                "symptoms": self.last_selected,
                "top_result": self.last_results[0]["disease"]["name"] if self.last_results else None,
            },
        )
        save_json_file(FEEDBACK_FILE, feedback[:100])
        self.status_var.set("Feedback saved. Thank you.")


if __name__ == "__main__":
    root = tk.Tk()
    if not DISEASES:
        messagebox.showwarning("Database Warning", f"No valid diseases loaded from:\n{DATABASE_FILE}")
    app = MedicalApp(root)
    feedback_frame = tk.Frame(root, bg=PALETTE["bg"])
    feedback_frame.place(relx=1, rely=1, x=-16, y=-28, anchor="se")
    tk.Button(feedback_frame, text="👍 Helpful", command=lambda: app.log_feedback(True), bg=PALETTE["glass"], fg=PALETTE["success"], relief="flat", padx=10, cursor="hand2").pack(side="left", padx=4)
    tk.Button(feedback_frame, text="👎 Not helpful", command=lambda: app.log_feedback(False), bg=PALETTE["glass"], fg=PALETTE["danger"], relief="flat", padx=10, cursor="hand2").pack(side="left")
    root.mainloop()
