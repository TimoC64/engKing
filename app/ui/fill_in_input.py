import tkinter as tk
import pandas as pd
import random
import os
import re
import time
from datetime import datetime, timedelta
import requests
import tempfile
from tkinter import messagebox, simpledialog

csv_path = os.path.join(os.path.dirname(__file__), "../data/words_grade_full.csv")

def play_google_tts(text, lang='en'):
    tts_url = f'https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={lang}&client=tw-ob'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(tts_url, headers=headers)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        try:
            from playsound import playsound
            playsound(tmp_path)
        except Exception as e:
            print("播放音訊失敗：", e)
        os.remove(tmp_path)
    else:
        print("TTS audio 取得失敗")

def run_fill_in_input():
    now = datetime.now()
    print("csv_path:", csv_path)
    df = pd.read_csv(csv_path)

    # SRS 與統計欄位自動補全
    if "interval" not in df.columns:
        df["interval"] = 1
    if "repetitions" not in df.columns:
        df["repetitions"] = 0
    if "next_due" not in df.columns:
        df["next_due"] = now.strftime("%Y-%m-%d %H:%M:%S")
    if "total_attempts" not in df.columns:
        df["total_attempts"] = 0
    if "error_count" not in df.columns:
        df["error_count"] = 0
    if "total_correct" not in df.columns:
        df["total_correct"] = 0
    if "total_wrong" not in df.columns:
        df["total_wrong"] = 0
    if "last_correct_date" not in df.columns:
        df["last_correct_date"] = ""

    df["next_due"] = pd.to_datetime(df["next_due"])
    due_words = df[df["next_due"] <= now].copy()
    if due_words.empty:
        messagebox.showinfo("完成！", "🎉 今天沒題目要複習！")
        return

    words = due_words.sample(frac=1).to_dict(orient="records")

    # 字體大小
    FONT_MAIN = ("Arial", 22)
    FONT_LABEL = ("Arial", 18)
    FONT_HINT = ("Arial", 18)
    FONT_BTN = ("Arial", 18)
    FONT_PARENT = ("Arial", 16)

    current_idx = [0]
    hint_indices = []
    error_count = [0]
    start_time = [time.time()]
    total_correct = [0]
    total_wrong = [0]
    give_up = [False]

    root = tk.Tk()
    root.title("engKing SRS 互動拼字練習")
    root.geometry("900x700")
    question_text = tk.Text(root, font=FONT_MAIN, wrap="word", height=4, width=75)
    question_text.pack(pady=12)
    question_text.config(state="disabled")
    entry = tk.Entry(root, font=FONT_MAIN, justify="center")
    entry.pack(pady=7)
    result_label = tk.Label(root, text="", font=FONT_LABEL)
    result_label.pack(pady=6)
    next_button = tk.Button(root, text="➡️ 下一題", state="disabled", font=FONT_BTN)
    next_button.pack(pady=10)
    hint_label = tk.Label(root, text="", font=FONT_HINT, fg="gray", wraplength=800, justify="left")
    hint_label.pack(pady=6)
    translation_label = tk.Label(root, text="", font=FONT_LABEL, fg="black", wraplength=800, justify="left")
    translation_label.pack(pady=6)
    timer_label = tk.Label(root, text="", font=FONT_PARENT, fg="gray")
    timer_label.pack(pady=2)
    stats_label = tk.Label(root, text="", font=FONT_PARENT, fg="darkgreen")
    stats_label.pack(pady=3)

    reveal_btn = None

    def update_timer():
        elapsed = int(time.time() - start_time[0])
        mins, secs = divmod(elapsed, 60)
        timer_label.config(text=f"⏱️ 這題已用時：{mins:02d}:{secs:02d}")
        root.after(1000, update_timer)

    def display_highlighted_example(example, keyword, meaning):
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
        question_text.insert(tk.END, f"\n\n【解釋】{meaning}")
        question_text.tag_config("highlight", foreground="blue")
        question_text.config(state="disabled")

    def show_translation():
        idx = current_idx[0]
        if idx < len(words):
            translation_label.config(text=f"📘 中文翻譯：{words[idx]['translation']}")

    def speak_example():
        idx = current_idx[0]
        if idx < len(words):
            play_google_tts(words[idx]['example'])

    def update_stats():
        attempted = total_correct[0] + total_wrong[0]
        if attempted == 0:
            stats = "本日統計：尚未作答"
        else:
            rate = int(total_correct[0] * 100 / attempted)
            stats = f"本日統計：{attempted} 題，正確 {total_correct[0]}，錯誤 {total_wrong[0]}，正確率 {rate}%"
        stats_label.config(text=stats)

    def make_question():
        entry.config(state="normal")
        entry.delete(0, tk.END)
        result_label.config(text="")
        translation_label.config(text="")
        hint_label.config(text="")
        next_button.config(state="disabled")
        if reveal_btn:
            reveal_btn.config(state="normal")
        error_count[0] = 0
        start_time[0] = time.time()
        give_up[0] = False
        idx = current_idx[0]
        update_stats()

        if idx >= len(words):
            question_text.config(state="normal")
            question_text.delete("1.0", tk.END)
            question_text.insert(tk.END, "🎉 今日題目全部完成！")
            question_text.config(state="disabled")
            entry.config(state="disabled")
            stats_label.config(text="學習結束！")
            return

        word = words[idx]
        answer = word["word"]
        example = word["example"]
        blanked = re.sub(re.escape(answer), '_'*len(answer), example, flags=re.IGNORECASE)
        question_text.config(state="normal")
        question_text.delete("1.0", tk.END)
        question_text.insert(tk.END, blanked + f"\n\n【解釋】{word['meaning']}")
        question_text.config(state="disabled")

        hint_indices.clear()
        root.after(800, speak_example)
        update_timer()

    def check_answer():
        if give_up[0]:
            return
        idx = current_idx[0]
        word = words[idx]
        answer = word["word"].lower()
        user_input = entry.get().strip().lower()
        max_hint = len(answer) // 2
        if user_input == answer:
            display_highlighted_example(word["example"], word["word"], word["meaning"])
            translation_label.config(text=f"📘 中文翻譯：{word['translation']}")
            result_label.config(text="✅ 正確！", fg="green")
            next_button.config(state="normal")
            total_correct[0] += 1
            srs_update(word["word"], error_count[0])
            entry.config(state="disabled")
            if reveal_btn:
                reveal_btn.config(state="disabled")
        else:
            result_label.config(text="❌ 錯了，再試一次", fg="red")
            error_count[0] += 1
            if len(hint_indices) < max_hint:
                unrevealed = [i for i in range(len(answer)) if i not in hint_indices]
                if unrevealed:
                    hint_indices.append(random.choice(unrevealed))
            hint_text = "".join(
                answer[i] if i in hint_indices else "_" for i in range(len(answer))
            )
            hint_label.config(text=f"提示：{hint_text}")
            next_button.config(state="disabled")
        update_stats()

    def reveal_answer():
        idx = current_idx[0]
        word = words[idx]
        display_highlighted_example(word["example"], word["word"], word["meaning"])
        translation_label.config(text=f"📘 中文翻譯：{word['translation']}")
        result_label.config(text="😅 放棄，本題答案：" + word["word"], fg="red")
        entry.config(state="disabled")
        next_button.config(state="normal")
        if reveal_btn:
            reveal_btn.config(state="disabled")
        give_up[0] = True
        total_wrong[0] += 1
        srs_update(word["word"], 99)
        update_stats()

    def srs_update(word, error_cnt):
        idxs = df[df['word'] == word].index
        if len(idxs) == 0:
            print("沒找到這個單字", word)
            return
        idx = idxs[0]
        interval = float(df.at[idx, "interval"])
        if error_cnt == 0:
            new_interval = interval * 2
            new_repetitions = df.at[idx, "repetitions"] + 1
            df.at[idx, "last_correct_date"] = datetime.now().strftime('%Y-%m-%d')
        elif error_cnt == 1:
            new_interval = interval * 1.2
            new_repetitions = df.at[idx, "repetitions"] + 1
            df.at[idx, "last_correct_date"] = datetime.now().strftime('%Y-%m-%d')
        else:
            new_interval = 0.2
            new_repetitions = 0

        df.at[idx, "interval"] = max(1, float(new_interval))
        df.at[idx, "repetitions"] = new_repetitions
        df.at[idx, "next_due"] = (datetime.now() + timedelta(days=float(df.at[idx, "interval"])))
        df.at[idx, "total_attempts"] += 1
        df.at[idx, "total_correct"] += 1 if error_cnt <= 1 else 0
        df.at[idx, "total_wrong"] += error_cnt if error_cnt < 99 else 1
        df.at[idx, "error_count"] = 0
        df.to_csv(csv_path, index=False)
        print(f"[srs_update] 已寫入 {csv_path} {word=} {idx=} {error_cnt=} repetitions={df.at[idx, 'repetitions']}")

    def next_question():
        current_idx[0] += 1
        make_question()

    PARENT_PASSWORD = "1234"

    def parent_mode():
        pwd = simpledialog.askstring("家長專用", "請輸入家長密碼：", show="*")
        if pwd != PARENT_PASSWORD:
            messagebox.showerror("密碼錯誤", "密碼錯誤，無法進入家長模式。")
            return

        top = tk.Toplevel(root)
        top.title("家長專用：有作答過單字／重置單字")
        text = tk.Text(top, width=60, height=25, font=FONT_PARENT)
        text.pack()

        mastered = df[df['total_correct'] > 0].copy()
        if mastered.empty:
            text.insert(tk.END, "尚未有作答過的單字！")
        else:
            text.insert(tk.END, "以下是有作答紀錄的單字（可點選 reset）：\n\n")
            for idx, row in mastered.iterrows():
                text.insert(tk.END, f"{row['word']}: {row['meaning']} | {row['translation']}\n", f"row_{idx}")
            text.insert(tk.END, f"\n總共：{len(mastered)} 個單字\n")
            text.insert(tk.END, "\n【說明】點選上方單字，可以重置該字的熟練度與複習狀態\n")

        def reset_all():
            pwd2 = simpledialog.askstring("再次驗證", "請再次輸入家長密碼：", show="*")
            if pwd2 != PARENT_PASSWORD:
                messagebox.showerror("密碼錯誤", "密碼錯誤，無法執行全重置。")
                return
            for idx in df.index:
                df.at[idx, "repetitions"] = 0
                df.at[idx, "interval"] = 1
                df.at[idx, "next_due"] = datetime.now()
                df.at[idx, "total_attempts"] = 0
                df.at[idx, "total_wrong"] = 0
                df.at[idx, "total_correct"] = 0
                df.at[idx, "error_count"] = 0
                df.at[idx, "last_correct_date"] = ""
            df.to_csv(csv_path, index=False)
            messagebox.showinfo("重置完成", "已將所有單字全部重置！")
            top.destroy()
            parent_mode()

        tk.Button(top, text="全部重置（需要再輸入密碼）", command=reset_all, font=FONT_PARENT).pack(pady=8)

        def reset_word(event):
            line = text.index("@%s,%s linestart" % (event.x, event.y))
            content = text.get(line, f"{line} lineend").strip()
            if not content or ":" not in content:
                return
            word_ = content.split(":")[0]
            if messagebox.askyesno("重置確認", f"確定要重置「{word_}」嗎？"):
                idxs = df[df['word'] == word_].index
                if len(idxs) > 0:
                    idx = idxs[0]
                    df.at[idx, "repetitions"] = 0
                    df.at[idx, "interval"] = 1
                    df.at[idx, "next_due"] = datetime.now()
                    df.at[idx, "total_attempts"] = 0
                    df.at[idx, "total_wrong"] = 0
                    df.at[idx, "total_correct"] = 0
                    df.at[idx, "error_count"] = 0
                    df.at[idx, "last_correct_date"] = ""
                    df.to_csv(csv_path, index=False)
                    messagebox.showinfo("重置完成", f"已重置「{word_}」，下次會重新進入複習。")
                    top.destroy()
                    parent_mode()
        text.bind("<Button-1>", reset_word)

    next_button.config(command=next_question)
    tk.Button(root, text="✅ 送出", command=check_answer, font=FONT_BTN).pack(pady=5)
    tk.Button(root, text="🔊 再唸一次句子", command=speak_example, font=FONT_BTN).pack(pady=5)
    tk.Button(root, text="💡 顯示中文意思", command=show_translation, font=FONT_BTN).pack(pady=5)
    reveal_btn = tk.Button(root, text="😅 看答案/放棄", command=reveal_answer, font=FONT_BTN)
    reveal_btn.pack(pady=5)
    tk.Button(root, text="👨‍👩‍👧‍👦 家長專用", command=parent_mode, font=FONT_BTN).pack(pady=5)

    # === 關閉時顯示今日學會單字數 ===
    def on_closing():
        _df = pd.read_csv(csv_path)
        today = datetime.now().strftime('%Y-%m-%d')
        learned_today = (_df["last_correct_date"] == today).sum()
        messagebox.showinfo("今日成果", f"今天你已經學會了 {learned_today} 個新單字！")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    make_question()
    root.mainloop()

if __name__ == "__main__":
    run_fill_in_input()
