# Savan Medical Aid Clinic 🏥

**Savan Medical Aid Clinic** is a desktop GUI application built with Python and Tkinter. It serves as a smart, weighted symptom-based medical assistant. By analyzing a patient's symptoms, the application calculates the probability of various medical conditions and provides actionable insights, including potential medications, home remedies, and critical warnings on when to consult a physician.

---

## 📑 Table of Contents
1. [Features](#-features)
2. [Algorithmic Approach](#-algorithmic-approach)
3. [Prerequisites](#-prerequisites)
4. [Installation & Setup](#-installation--setup)
5. [Database Structure](#-database-structure)
6. [Disclaimer](#-disclaimer)

---

## ✨ Features

- **Advanced UI/UX:** Modern, clean Tkinter interface utilizing the `clam` theme, custom progress bars, and custom scrollbars.
- **Dynamic Search:** Real-time search and filtering capability for the symptom checklist.
- **Weighted Diagnosis:** Computes match percentages based on the specific weight/importance of each symptom for a given disease.
- **Universal Scrolling:** Seamless mouse-wheel scrolling implemented across all application canvases.
- **Comprehensive Results:** Displays disease category, match strength (via progress bar), medications, home remedies, related symptoms, and critical medical warnings.

---

## 🧮 Algorithmic Approach

The core diagnosis engine utilizes a weighted matching algorithm. The time complexity of the `diagnose` function is $\mathcal{O}(N \times M)$, where:
- $N$ is the total number of diseases in the database.
- $M$ is the number of symptoms selected by the user.

**Scoring Formula:**
For each disease, the match score is calculated as:
$$ \text{Score} = \left( \frac{\sum \text{Weights of Matched Selected Symptoms}}{\sum \text{Total Symptom Weights for the Disease}} \right) \times 100 $$

This ensures that critical symptoms (higher weights) heavily influence the final percentage, providing a more accurate preliminary diagnosis than a simple unweighted count.

---

## 🛠 Prerequisites

This application relies entirely on standard Python libraries. No external packages (like PyQt or CustomTkinter) are required.

- **Python 3.7 or higher**
- OS: Windows, macOS, or Linux (Tkinter must be installed, which is usually included by default in standard Python distributions).

---

## 🚀 Installation & Setup

1. **Clone or Download the Repository:**
   Ensure the main Python script (e.g., `RLbasedMedicalAssistant.py`) is in your working directory.

2. **Create the Database:**
   The application requires a JSON database named `medical_database.json` to be present in the same directory as the Python script. (See the [Database Structure](#-database-structure) section below).

3. **Run the Application:**
   Execute the script using Python:
```bash
   python RLbasedMedicalAssistant.py
   

