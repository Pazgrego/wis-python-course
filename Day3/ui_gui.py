import tkinter as tk
from tkinter import messagebox
from logic import calculate_dilution


def on_calculate():
    try:
        c1 = float(entry_c1.get())
        c2 = float(entry_c2.get())
        v2 = float(entry_v2.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter numeric values for all fields.")
        return

    stock_vol, diluent_vol = calculate_dilution(c1, c2, v2)
    result_text = (
        f"Stock to take:  {stock_vol:.2f} ul\n"
        f"Diluent to add: {diluent_vol:.2f} ul\n"
        f"Total volume:   {stock_vol + diluent_vol:.2f} ul"
    )
    label_result.config(text=result_text)


root = tk.Tk()
root.title("Dilution Calculator")
root.resizable(False, False)

padding = {"padx": 10, "pady": 6}

tk.Label(root, text="Stock concentration (C1):").grid(row=0, column=0, sticky="e", **padding)
entry_c1 = tk.Entry(root, width=12)
entry_c1.grid(row=0, column=1, **padding)

tk.Label(root, text="Desired concentration (C2):").grid(row=1, column=0, sticky="e", **padding)
entry_c2 = tk.Entry(root, width=12)
entry_c2.grid(row=1, column=1, **padding)

tk.Label(root, text="Final volume V2 (ul):").grid(row=2, column=0, sticky="e", **padding)
entry_v2 = tk.Entry(root, width=12)
entry_v2.grid(row=2, column=1, **padding)

tk.Button(root, text="Calculate", command=on_calculate).grid(row=3, column=0, columnspan=2, pady=10)

label_result = tk.Label(root, text="", justify="left", font=("Courier", 11))
label_result.grid(row=4, column=0, columnspan=2, **padding)

root.mainloop()
