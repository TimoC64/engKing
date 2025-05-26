# engKing

🎯 **engKing** 是一套互動式英文拼字練習應用，專為國小至國中程度設計，透過填空題形式幫助孩子增強字彙記憶力。

## 📁 專案結構
├── app
│   ├── core
│   ├── data
│   │   └── words_grade_full.csv
│   ├── db
│   ├── reports
│   └── ui
│       ├── fill_in_input.py
│       └── main_gui.py
├── main.py
├── Pipfile
├── Pipfile.lock
└── README.md


---

## 🚀 快速啟動教學

### 1. 環境需求

- Python 3.11（建議使用 [conda](https://docs.conda.io/zh/latest/) 或 [pyenv](https://github.com/pyenv/pyenv) 來管理）
- 建議用 conda 虛擬環境，安裝依賴最穩定

### 2. 安裝依賴套件

```bash
conda activate engking
cd ./engKing
pip install pandas playsound requests
python main.py
```

### 3. 📚 單字資料格式
檔案路徑：app/data/words_grade_full.csv

基本格式：
word,meaning,example,translation
其他學習進度與記錄欄位會由系統自動新增：
interval,repetitions,next_due,total_attempts,error_count,total_correct,total_wrong,last_correct_date

### 4. 🧩 主要功能介紹
拼字填空練習：每題需完全拼對才能過關，答錯會隨機給出提示字母（最多一半）。
SRS 間隔重複記憶：根據記憶熟悉度自動調整單字出現頻率，確保複習效率。
語音朗讀：例句會用 Google TTS 線上朗讀（需要網路）。
家長專區：密碼保護，可以查詢所有曾正確答過的單字，支援單字或全部重置。
每日學習成果統計：關閉程式時會自動彈出今日新學會單字數。
學習進度追蹤：每個單字都會記錄作答次數、正確/錯誤次數、最後答對日期等，存於 CSV。
🔒 家長模式：點選畫面上的「家長專用」按鈕。輸入家長密碼（預設：1234）即可檢視、重設學習進度。


### 5. 🌐 執行需求
Python 3.11（建議 conda/pyenv 虛擬環境）
必需套件：pandas, playsound, requests
需要網路連線（Google TTS 發音）