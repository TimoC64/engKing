from app.ui.main_gui import run_app
from app.ui.fill_in_input import run_fill_in_input
import pyttsx3

if __name__ == "__main__":
    import tkinter as tk

    def launch_gui(mode):
        if mode == "learn":
            run_app()
        elif mode == "quiz":
            run_quiz()
        elif mode == "fill":
            run_fill_in_quiz()
        elif mode == "fill_input":
            run_fill_in_input()

    root = tk.Tk()
    root.title("engKing 主選單")

    tk.Label(root, text="請選擇功能", font=("Arial", 18)).pack(pady=10)
    tk.Button(root, text="📘 單字學習模式", command=lambda: launch_gui("learn"), width=30).pack(pady=5)
    tk.Button(root, text="🧠 小測驗（中翻英）", command=lambda: launch_gui("quiz"), width=30).pack(pady=5)
    tk.Button(root, text="✍️ 句子填空測驗", command=lambda: launch_gui("fill"), width=30).pack(pady=5)
    tk.Button(root, text="🎯 拼字填空練習", command=lambda: launch_gui("fill_input"), width=30).pack(pady=5)

    root.mainloop()
