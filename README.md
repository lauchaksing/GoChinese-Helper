# GoChinese Helper

A small Windows app that fills in Lingnan University **GoChinese** exercises for you — pick a chapter and exercise, then let the app do the typing.

**v1.1.1 · Windows 10 / 11 · single .exe · no Python required**

[English](#english) · [繁體中文](#繁體中文)

---

## English

### What it is

GoChinese Helper does two things:

- it fetches the answer data for a course chapter/exercise, and
- it drives your browser **with simulated keystrokes** (Tab / Space / arrow keys / typed text), so the answers land in the right fields on the GoChinese page.

It does **not** read your screen or intercept network traffic. You stay logged in in your own browser; the app only presses keys.

> The answers are a study aid — a reference, not a guaranteed answer key. See [Disclaimer](#disclaimer).

### 1. Download and run

1. Open the [Releases page](https://github.com/lauchaksing/GoChinese-Helper/releases) and download `GoChinese-Helper-v1.1.1.exe`.
2. Put it in any folder (no installer, no Python, no DLLs needed).
3. Double-click it. First launch shows the license agreement → click **I Agree** (declining closes the app).
4. If Windows SmartScreen says *“Windows protected your PC”*: **More info → Run anyway** (the exe is unsigned; that is the only reason for the warning).

An internet connection is needed to load a course: the answer data (`answers/LCC1010.json`) and the version/announcement files are downloaded live from the project's GitHub Pages, so students always get the latest corrections.

### 2. Quick start

1. In your browser, log in to GoChinese and **open the exercise page you want to fill**.
2. In the app: pick **Course** → **Chapter** → **Exercise**. The **Type** field fills itself in.
3. Optional: tick **📌 Pin on Top** if the app keeps getting buried.
4. Click **▶ Start**.
5. If an **Important Note** window appears, read it and press **Got it** (see [section 3](#3-exercises-with-an-important-note-comment)).
6. **Click once on the GoChinese page** (somewhere neutral, not inside a text box), then **keep your hands off keyboard and mouse**. A 5-second countdown runs, then the app types.

### 3. Exercises with an Important Note (comment)

Some exercises have a caveat that must not be missed, so the app opens a **separate always-on-top window**, rings a bell, and blocks the main window until you press **Got it**. Nothing is typed before you acknowledge it.

Currently flagged in **LCC1010**:

| Course | Chapter | Exercise | Type | Why |
| --- | --- | --- | --- | --- |
| LCC1010 | 6 | 謀後作業6.1選擇題 | mc | Contains two identical questions `liúniàn`. Both answers are `留念`, **but the options differ (A and C)** — check each item before submitting. |
| LCC1010 | 10 | 謀後作業10.1選擇題 | answer | Cannot be automated (technical limitation). The app only shows you the reference answers; you must do it manually. |

If a chapter/exercise is added to this list later, the note appears by itself — the app reads it from the data file, no code change needed.

### 4. What each Type does

| Type | What the app does | Before you press Start |
| --- | --- | --- |
| `input` | Tab to each field and types the answer (tone numbers / pinyin — plain ASCII). | Click the page so the browser has focus. |
| `pmc` | Keyboard-selects a pre-known option: Space → Down × (n−1) → Space. | Same. Do **not** open or touch the list yourself. |
| `mc` | Uses the browser console (DevTools) to read the question list, then selects each answer. Full flow below. | Click the page. Do **not** select any option. |
| `mc+input` | 判斷改錯題: selects the option, then Tab and types the corrected pinyin. | Click the page. |
| `answer` | Display only — opens a **Reference Answers** window. Nothing is typed. | Nothing to do. |

#### The `mc` run, step by step

1. A dialog warns you; press **Continue**.
2. In 5 s the app presses **Ctrl+Shift+J** to open DevTools. *(Chrome / Edge only — this shortcut is Chrome-family.)*
3. It types a short JavaScript snippet and presses Enter. The snippet collects the question list from the page and puts it on the clipboard; the console prints `Done! Please continue in GoChinese Helper.`
4. The app closes DevTools again, then asks: *confirm you see `Done!`* → press **Continue**.
5. It compares the clipboard list with the answer data. If any question is missing it stops and shows you the list — **nothing has been typed**, so you can retry safely.
6. 5 s countdown → it answers every question. Don't touch anything.

### 5. Rules while running

- Keep the GoChinese page focused. Clicking another window mid-run sends the keystrokes somewhere else.
- Never touch the mouse or keyboard until the status bar says **✔ Done**.
- There is no pause/stop button. If something goes badly wrong, close the app — but the page may be left half-filled; reload it and start over.
- Answers are plain ASCII by design (tone numbers, numbers, pinyin), because `keyboard` can only reliably type ASCII.

### 6. Troubleshooting

**Nothing is typed.**
Run the app **as administrator** — the `keyboard` module needs a low-level keyboard hook, which Windows blocks for normal processes. Also make sure the browser window has focus.

**Status bar says “New version vX available”.**
That is the update check. Press **Download** to open the Releases page, or **Later**.

**“Questions Not Found”.**
The question list scraped from the page doesn't match the answer data (page redesigned, or questions reordered). Reload the page and try again; if it persists, the data file needs an update.

**“Failed to read clipboard”.**
The snippet didn't run: DevTools wasn't focused, or you clicked away during the 5 s. Retry, and make sure the console is the active panel.

**“Load failed: …”.**
No network / GitHub Pages unreachable. Check your connection and reload the course.

**My antivirus complains.**
Expected for a PyInstaller single-file exe that also hooks the keyboard. Add an exclusion if you trust the source.

**LCC2010 shows “coming soon”.**
Not published yet; the answer file is still a placeholder.

**Reset everything** (license prompt, pin setting, hidden announcements): delete `%USERPROFILE%\.gochinese_helper.json`.

### 7. Privacy

- No account, no analytics, no telemetry, nothing written to the page.
- Settings live in `%USERPROFILE%\.gochinese_helper.json`: `topmost`, `license_accepted`, `ignored_announcements`.
- Network traffic goes only to `lauchaksing.github.io` (answer/version/announcement data) and `github.com` (if you click Download).

### 8. For developers

**Run from source** (Python 3.10+, Windows):

```bat
pip install requests keyboard pyperclip
python python\gui.py
```

**Build the single-file exe** (PyInstaller 6.x):

```bat
pip install pyinstaller requests keyboard pyperclip
pyinstaller --noconfirm --clean --onefile --windowed --optimize 2 ^
  --name GoChinese-Helper --icon python\icon.ico ^
  --add-data "python\icon.ico;." --exclude-module tkinter.test ^
  python\gui.py
```

**Layout**

| Path | Purpose |
| --- | --- |
| `python/gui.py` | The app (Tkinter, ~1.2k lines). Entry point. |
| `python/main.py` | Legacy console version, kept for reference. |
| `python/icon.ico` | App / window icon (9 sizes, 16–256 px). Bundled into the exe. |
| `answers/LCC1010.json` | Answer data, served from GitHub Pages. |
| `answers/LCC2010.json` | Placeholder. |
| `version.json` / `announcement.json` | Update check / startup announcement, served from GitHub Pages. |
| `dist/` | Build output (not tracked). |

**Data schema**

```json
{
  "6": {
    "謀後作業6.1選擇題": {
      "type": "mc",
      "comment": "Optional. Shown in an always-on-top dialog before the run.",
      "answers": { "liúniàn": 1 }
    }
  }
}
```

`type` is one of `input` (`questions` + numeric `answers`), `pmc` (numeric `answers`), `mc` (object mapping question → option index), `mc+input` (`answers` as `[[index, "pinyin"]]`), `answer` (string list, display only). `comment` is optional and works for every type.

### Disclaimer

Provided **for reference and study purposes only**; accuracy is not guaranteed. Open source, **no commercial use, no monetisation** of any kind. Using it in a graded or submitted assessment may violate your course's academic honesty rules — that decision, and its consequences, are yours. Author: **LauChakSing**.

---

## 繁體中文

### 這是什麼

GoChinese Helper 是一個 Windows 小工具，用**模擬鍵盤輸入**的方式，幫你在嶺南大學 GoChinese 的練習頁面上自動填寫答案。

它做兩件事：

- 取得某一課某一練習的答案資料；
- 用 Tab／空格／方向鍵／打字模擬操作你的瀏覽器，把答案填進頁面正確的位置。

它**不會**讀取你的螢幕，也不攔截網絡流量。你照常在瀏覽器登入，程式只負責按鍵。

> 答案僅供學習參考，並非保證正確的標準答案。詳見[免責聲明](#免責聲明)。

### 1. 下載與啟動

1. 到 [Releases 頁面](https://github.com/lauchaksing/GoChinese-Helper/releases) 下載 `GoChinese-Helper-v1.1.1.exe`。
2. 放在任何資料夾都可以（免安裝、不需要 Python、不需要額外 DLL）。
3. 雙擊執行。第一次啟動會顯示授權協議 → 按 **I Agree**（按 Decline 會直接關閉程式）。
4. 若 Windows SmartScreen 提示「Windows 已保護您的電腦」：按 **其他資訊 → 仍要執行**（exe 未做數位簽章，這是唯一原因）。

載入課程需要連網：答案資料（`answers/LCC1010.json`）與版本／公告檔都是即時從專案的 GitHub Pages 下載，確保你拿到最新修正。

### 2. 快速上手

1. 在瀏覽器登入 GoChinese，**打開你要填的那一頁練習**。
2. 在程式裡選 **Course** → **Chapter** → **Exercise**，**Type** 會自動顯示。
3. 若程式常被其他視窗蓋住，勾選 **📌 Pin on Top**（置頂）。
4. 按 **▶ Start**。
5. 若彈出 **Important Note** 視窗，先讀完並按 **Got it**（見[第 3 節](#3-帶-important-notecomment-的題目)）。
6. **用滑鼠在 GoChinese 頁面上點一下**（點空白位置，不要點進輸入框），然後**雙手離開鍵盤和滑鼠**。畫面會倒數 5 秒，之後開始自動輸入。

### 3. 帶 Important Note（comment）的題目

有些題目有不能忽略的注意事項，程式會開一個**獨立的置頂視窗**、響鈴，並鎖住主視窗，直到你按 **Got it** 才繼續——**在你確認之前，一個字都不會輸入**。

目前 **LCC1010** 有以下兩題：

| 課程 | 章 | 練習 | 類型 | 原因 |
| --- | --- | --- | --- | --- |
| LCC1010 | 6 | 謀後作業6.1選擇題 | mc | 內含兩條相同的題目 `liúniàn`，答案同為 `留念`，**但選項不同（A 與 C）**，提交前請逐題核對。 |
| LCC1010 | 10 | 謀後作業10.1選擇題 | answer | 受技術限制無法自動完成，程式只顯示參考答案，需自行手動作答。 |

日後若資料檔新增了 comment，提示窗會自動出現——程式是從資料檔讀取的，不用改代碼。

### 4. 各 Type 的行為

| Type | 程式做什麼 | 按 Start 前你要做什麼 |
| --- | --- | --- |
| `input` | Tab 跳到每個欄位並輸入答案（聲調數字／拼音，純 ASCII）。 | 點一下頁面，讓瀏覽器取得焦點。 |
| `pmc` | 用鍵盤選預先知道的選項：空格 → Down × (n−1) → 空格。 | 同上。**不要**自己打開或碰那個下拉選單。 |
| `mc` | 透過瀏覽器 Console（DevTools）讀取題目清單，然後逐題選答案。流程見下。 | 點一下頁面。**不要**預先選任何選項。 |
| `mc+input` | 判斷改錯題：先選選項，再 Tab 並輸入改正後的拼音。 | 點一下頁面。 |
| `answer` | 只顯示——彈出 **Reference Answers** 視窗，不會輸入任何東西。 | 不用做任何事。 |

#### `mc` 的完整流程

1. 先跳出確認視窗，按 **Continue**。
2. 5 秒後程式按 **Ctrl+Shift+J** 開啟 DevTools（僅支援 Chrome／Edge 系瀏覽器）。
3. 它會自動輸入一段 JavaScript 並按 Enter：該腳本從頁面收集題目清單、複製到剪貼簿，Console 會印出 `Done! Please continue in GoChinese Helper.`
4. 程式關掉 DevTools，然後問你「有看到 `Done!` 嗎」→ 按 **Continue**。
5. 它會拿剪貼簿的題目清單跟答案資料比對。若有題目找不到，會停下來列出清單——此時**尚未輸入任何答案**，可安全重試。
6. 倒數 5 秒後逐題作答。全程不要動鍵鼠。

### 5. 執行中的注意事項

- 保持 GoChinese 頁面在前景。中途點到其他視窗，按鍵會打去別的地方。
- 狀態列顯示 **✔ Done** 之前，不要碰滑鼠和鍵盤。
- 沒有暫停／停止按鈕。真的出事就關掉程式，但頁面可能只填了一半，請重新載入再來一次。
- 答案刻意只用 ASCII（聲調數字、選項序號、拼音），因為 `keyboard` 對非 ASCII 輸入不穩定。

### 6. 疑難排解

**完全沒有輸入。**
以**管理員身分執行**——`keyboard` 模組需要安裝低階鍵盤鉤子，Windows 會擋住一般權限的程序。同時確認瀏覽器視窗有焦點。

**狀態列顯示「New version vX available」。**
那是更新檢查。按 **Download** 會開啟 Releases 頁面，或按 **Later** 稍後再說。

**出現「Questions Not Found」。**
從頁面抓到的題目清單與答案資料不符（頁面改版或題目順序不同）。重新載入頁面再試；若持續發生，代表資料檔需要更新。

**出現「Failed to read clipboard」。**
腳本沒有成功執行：DevTools 沒有取得焦點，或倒數期間你點了別處。重試，並確認 Console 是當前作用中的面板。

**出現「Load failed: …」。**
沒有網絡或 GitHub Pages 連不上。檢查連線後重新選課程。

**防毒軟體報毒。**
PyInstaller 單文件 exe 加上鍵盤鉤子，被誤報很常見。若你信任來源，可加入排除清單。

**LCC2010 顯示 coming soon。**
尚未推出，答案檔仍是空佔位檔。

**完全重置**（授權提示、置頂設定、已隱藏的公告）：刪除 `%USERPROFILE%\.gochinese_helper.json`。

### 7. 私隱

- 不需要帳號、沒有分析、沒有遙測，也不會寫入任何東西到你的頁面。
- 設定存於 `%USERPROFILE%\.gochinese_helper.json`：`topmost`、`license_accepted`、`ignored_announcements`。
- 網絡請求只會連到 `lauchaksing.github.io`（答案／版本／公告）與 `github.com`（按 Download 時）。

### 8. 開發者資訊

**從原始碼執行**（Python 3.10+，Windows）：

```bat
pip install requests keyboard pyperclip
python python\gui.py
```

**打包單文件 exe**（PyInstaller 6.x）：

```bat
pip install pyinstaller requests keyboard pyperclip
pyinstaller --noconfirm --clean --onefile --windowed --optimize 2 ^
  --name GoChinese-Helper --icon python\icon.ico ^
  --add-data "python\icon.ico;." --exclude-module tkinter.test ^
  python\gui.py
```

**專案結構**

| 路徑 | 用途 |
| --- | --- |
| `python/gui.py` | 圖形介面本體（Tkinter，約 1.2k 行），程式入口。 |
| `python/main.py` | 舊版終端機介面，留作參考。 |
| `python/icon.ico` | 程式與視窗圖示（9 種尺寸 16–256 px），會打包進 exe。 |
| `answers/LCC1010.json` | 答案資料，由 GitHub Pages 提供。 |
| `answers/LCC2010.json` | 佔位檔。 |
| `version.json` / `announcement.json` | 更新檢查／啟動公告，由 GitHub Pages 提供。 |
| `dist/` | 打包輸出（不納入版本控制）。 |

**資料格式**

```json
{
  "6": {
    "謀後作業6.1選擇題": {
      "type": "mc",
      "comment": "選填。執行前會以置頂視窗顯示。",
      "answers": { "liúniàn": 1 }
    }
  }
}
```

`type` 可為 `input`（`questions` 加數字 `answers`）、`pmc`（數字 `answers`）、`mc`（題目對選項序號的物件）、`mc+input`（`answers` 為 `[[序號, "拼音"]]`）、`answer`（字串陣列，僅顯示）。`comment` 為選填，所有類型皆適用。

### 免責聲明

本程式所提供的一切內容**僅供參考與學習用途**，不保證準確性。本專案為開源項目，**嚴禁任何形式的商業使用、盈利或變現**。若用於計分作業或提交評分，可能違反課程的學術誠信規定——相關判斷與後果由使用者自負。作者：**LauChakSing**。
