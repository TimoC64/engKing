import tkinter as tk
import pandas as pd
import pyttsx3
import random
import os
from app.ui.fill_in_input import run_fill_in_input


def run_app():
    # 載入單字資料
    csv_path = os.path.join(os.path.dirname(__file__), "../data/words_grade_1.csv")
    df = pd.read_csv(csv_path)
    words = df.to_dict(orient="records")
    random.shuffle(words)

    engine = pyttsx3.init()

    # GUI 建立
    root = tk.Tk()
    root.title("engKing 單字卡片")

    word_var = tk.StringVar()
    meaning_var = tk.StringVar()
    example_var = tk.StringVar()

    def show_word(index):
        word_data = words[index]
        word_var.set(word_data["word"])
        meaning_var.set(f"{word_data['part_of_speech']}：{word_data['meaning']}")
        example_var.set(word_data["example"])

    current_index = [0]

    def next_word():
        current_index[0] += 1
        if current_index[0] >= len(words):
            current_index[0] = 0
            random.shuffle(words)
        show_word(current_index[0])

    def speak_word():
        engine.say(word_var.get())
        engine.runAndWait()

    tk.Label(root, textvariable=word_var, font=("Arial", 24)).pack(pady=10)
    tk.Label(root, textvariable=meaning_var, font=("Arial", 16)).pack()
    tk.Label(root, textvariable=example_var, wraplength=400, justify="center", font=("Arial", 12)).pack(pady=10)

    tk.Button(root, text="🔊 播放發音", command=speak_word).pack(pady=5)
    tk.Button(root, text="➡️ 下一個單字", command=next_word).pack(pady=5)

    show_word(0)
    root.mainloop()
