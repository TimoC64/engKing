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

## 🚀 執行方式

```bash
pipenv install
pipenv run python main.py

📚 字彙資料
CSV 檔案路徑：app/data/words_grade_full.csv
格式為：word,meaning,example,translation

