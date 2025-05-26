from app.ui.main_gui import run_app

from app.ui.fill_in_input import run_fill_in_input


if __name__ == "__main__":
    import tkinter as tk
    run_fill_in_input()

    root = tk.Tk()
    root.title("engKing 主選單")

    root.mainloop()
