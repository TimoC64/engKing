import tkinter as tk
import pandas as pd
import random
import os
import re
import pyttsx3
import time
import requests
import tempfile
from playsound import playsound

def play_google_tts(text, lang='en'):
    tts_url = f'https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={lang}&client=tw-ob'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(tts_url, headers=headers)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        playsound(tmp_path)
        os.remove(tmp_path)
    else:
        print("Failed to get TTS audio")



def run_fill_in_input():
    start_time = time.time()

    # 載入單字資料
    csv_path = os.path.join(os.path.dirname(__file__), "../data/words_grade_full.csv")
    df = pd.read_csv(csv_path)
    words = df.to_dict(orient="records")
    random.shuffle(words)

    engine = pyttsx3.init()

    root = tk.Tk()
    root.title("engKing 拼字填空練習")
    root.geometry("800x600")

    question_text = tk.Text(root, font=("Arial", 18), wrap="word", height=3, width=70)
    question_text.pack(pady=10)
    question_text.config(state="disabled")

    entry = tk.Entry(root, font=("Arial", 16), justify="center")
    entry.pack(pady=5)

    result_label = tk.Label(root, text="", font=("Arial", 14))
    result_label.pack(pady=5)

    next_button = tk.Button(root, text="➡️ 下一題", state="disabled")
    next_button.pack(pady=10)

    hint_label = tk.Label(root, text="", font=("Arial", 14), fg="gray", wraplength=700, justify="left")
    hint_label.pack(pady=5)

    timer_label = tk.Label(root, text="", font=("Arial", 12), fg="gray")
    timer_label.pack(pady=2)

    def update_timer():
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        timer_label.config(text=f"⏱️ 已執行時間：{mins:02d}:{secs:02d}")
        root.after(1000, update_timer)

    current_word = {"answer": "", "example": "", "meaning": "", "full_translation": ""}

    def speak_example():
        # engine.say(current_word["example"])
        # engine.runAndWait()
        play_google_tts(current_word["example"], lang='en')
        

    def show_translation():
        full = current_word["full_translation"]
        hint_label.config(text=f"📘 中文提示：{full}")

    def delayed_speak():
        root.after_idle(speak_example)

    def display_highlighted_example(example, keyword):
        question_text.config(state="normal")
        question_text.delete("1.0", tk.END)
        start = 0
        while True:
            match = re.search(re.escape(keyword), example[start:], re.IGNORECASE)
            if not match:
                question_text.insert(tk.END, example[start:])
                break
            match_start = start + match.start()
            match_end = start + match.end()
            question_text.insert(tk.END, example[start:match_start])
            question_text.insert(tk.END, example[match_start:match_end], "highlight")
            start = match_end
        question_text.tag_config("highlight", foreground="blue")
        question_text.config(state="disabled")

    def make_question():
        result_label.config(text="", fg="black")
        hint_label.config(text="")
        entry.delete(0, tk.END)
        next_button.config(state="disabled")
        question_text.config(state="normal")
        question_text.delete("1.0", tk.END)
        question_text.config(state="disabled")

        word_data = random.choice(words)
        correct = word_data["word"]
        example = word_data["example"]
        meaning = word_data["meaning"]
        translation = word_data.get("translation", meaning)

        pattern = re.compile(re.escape(correct), re.IGNORECASE)
        blanked = pattern.sub("_____", example)

        current_word["answer"] = correct
        current_word["example"] = example
        current_word["meaning"] = meaning
        current_word["full_translation"] = translation

        question_text.config(state="normal")
        question_text.insert(tk.END, blanked)
        question_text.config(state="disabled")
        delayed_speak()

    def check_answer():
        user_input = entry.get().strip().lower()
        correct = current_word["answer"].lower()
        if user_input == correct:
            display_highlighted_example(current_word["example"], current_word["answer"])
            result_label.config(text="✅ 正確！", fg="green")
            next_button.config(state="normal")
        else:
            result_label.config(text="❌ 錯了，再試一次", fg="red")
            next_button.config(state="disabled")

    next_button.config(command=make_question)
    tk.Button(root, text="✅ 送出", command=check_answer).pack(pady=5)
    tk.Button(root, text="🔊 再唸一次句子", command=speak_example).pack(pady=5)
    tk.Button(root, text="💡 顯示中文意思", command=show_translation).pack(pady=5)

    update_timer()
    make_question()
    root.mainloop()