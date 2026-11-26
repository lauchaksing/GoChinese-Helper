# -*- coding: utf-8 -*-
"""
GoChinese Helper — GUI Edition
Compact · Modern · Always-on-top · Auto-update · Announcements · License Gate

Author: LauChakSing (GUI refactor)
"""

from __future__ import annotations

import json
import os
import sys
import threading
import webbrowser
from time import sleep

import tkinter as tk
from tkinter import ttk

try:
    import requests
except Exception:                       # pragma: no cover
    requests = None

try:
    import pyperclip
    import keyboard as _keyboard
except Exception:                       # pragma: no cover
    pyperclip = None
    _keyboard = None


# ============================================================
#  Constants / Config
# ============================================================
APP_NAME      = "GoChinese Helper"
VERSION       = "1.1.1"
BASE_URL      = "https://lauchaksing.github.io/GoChinese-Helper"
COURSES       = ["LCC1010", "LCC2010"]
ICON_FILE     = "icon.ico"
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".gochinese_helper.json")

# ---------- Palette (Catppuccin Mocha inspired) ----------
BG         = "#1e1e2e"
SURFACE    = "#313244"
SURFACE2   = "#45475a"
FG         = "#cdd6f4"
MUTED      = "#a6adc8"
ACCENT     = "#89b4fa"
ACCENT_HV  = "#b4befe"
OK_COLOR   = "#a6e3a1"
ERR_COLOR  = "#f38ba8"
WARN_COLOR = "#f9e2af"

# ---------- Fonts ----------
if sys.platform == "win32":
    UI_FONT = "Segoe UI"
elif sys.platform == "darwin":
    UI_FONT = "SF Pro Display"
else:
    UI_FONT = "Noto Sans"

# ---------- Injected console snippet ----------
JS_SNIPPET = (
    'const questions=[];'
    'document.querySelectorAll(\'table[width="666"]\').forEach(e=>{'
    'let o=e.querySelector("td.goChineseUserInputFontFamily");'
    'if(!o)return;'
    'let t=o.innerText.trim().split("\\n").map(e=>e.trim()).filter(e=>e);'
    'if(t.length>=2){t[0].replace(".","").trim();let e=t[1];questions.push(e)}'
    '});'
    'const result=JSON.stringify(questions);'
    'copy(result);'
    'console.log("Done! Please continue in GoChinese Helper.");'
)

# ---------- License text (bilingual) ----------
LICENSE_TEXT = """GoChinese Helper — License Agreement
使用者授權協議

═══════════════════════════════════════════════════════════════

1.  REFERENCE ONLY / 僅供參考
    All answers and materials provided by this application are
    for REFERENCE PURPOSES ONLY. The author does not guarantee
    the accuracy or completeness of any information presented.

    本程式所提供的一切答案與內容僅供參考，作者不保證其準確性
    及完整性。

2.  OPEN SOURCE / 開源項目
    This project is an open-source project.

    本項目為開源項目。

3.  EDUCATIONAL USE ONLY / 僅供學習用途
    This application is intended SOLELY for learning and
    educational purposes.

    本程式僅用於學習與教育用途。

4.  NO COMMERCIAL USE / 禁止商業用途
    Commercial use, profit-making, or any form of monetization
    is strictly prohibited.

    嚴禁任何形式的商業使用、盈利或變現行為。

5.  AUTHOR / 作者
    LauChakSing

6.  ACCEPTANCE / 接受條款
    By clicking "I Agree", you confirm that you have read and
    understood the terms above, and agree to use this application
    in full compliance with them.

    點擊「同意」即表示您已閱讀並理解上述條款，並同意完全遵守
    這些條款使用本程式。

If you do not agree, the application will exit.
如果您不同意，程式將退出。

═══════════════════════════════════════════════════════════════
"""


# ============================================================
#  Helpers
# ============================================================
def resource_path(filename: str) -> str:
    """取得隨程式打包的資源檔路徑。

    直接執行 .py 時取本檔案所在資料夾；PyInstaller 單文件 exe 執行時，
    資源會被解壓到 sys._MEIPASS 指向的暫存資料夾。
    """
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def parse_version(v) -> tuple:
    parts = []
    for p in str(v).strip().lstrip("vV").split("."):
        num = ""
        for ch in p:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def letter(n) -> str:
    return {1: "A", 2: "B", 3: "C", 4: "D"}.get(n, str(n))


def fetch_update_info():
    """Fetch version metadata from the repository. Returns None on failure."""
    if requests is None:
        return None
    for name in ("version.json", "update.json", "latest.json"):
        try:
            r = requests.get(f"{BASE_URL}/{name}", timeout=6)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and ("version" in data or "latest" in data):
                    return data
        except Exception:
            continue
    try:
        r = requests.get(f"{BASE_URL}/version.txt", timeout=6)
        if r.status_code == 200 and r.text.strip():
            return {"version": r.text.strip()}
    except Exception:
        pass
    return None


def fetch_announcement():
    """Fetch announcement from the repository. Returns None on failure."""
    if requests is None:
        return None
    for name in ("announcement.json", "notice.json"):
        try:
            r = requests.get(f"{BASE_URL}/{name}", timeout=6)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and data.get("id"):
                    return data
        except Exception:
            continue
    return None


# ============================================================
#  Main Application
# ============================================================
class GoChineseHelper:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = load_settings()
        self.answers: dict | None = None
        self.running = False
        self._license_result = False
        self._license_denied = False
        # 同一時間只允許一個模態對話框（更新提示／公告／錯誤），避免互相搶 grab
        self._modal_lock = threading.Lock()

        # 先隱藏主視窗，避免授權視窗彈出前主視窗先閃現
        self.root.withdraw()

        self._setup_window()
        self._setup_style()

        # ---- License gate ----
        if not self.settings.get("license_accepted"):
            if not self._show_license_dialog():
                self._license_denied = True
                return
            self.settings["license_accepted"] = True
            save_settings(self.settings)
        # ----------------------

        self.root.deiconify()
        self._build_ui()

        # Kick off background startup tasks
        self.root.after(400, self._post_start)

    # --------------------------------------------------------
    #  Window & style
    # --------------------------------------------------------
    def _setup_window(self):
        self.root.title(APP_NAME)
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._apply_icon()

        w, h = 360, 470
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        try:
            self.root.attributes("-topmost", bool(self.settings.get("topmost", False)))
        except Exception:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_icon(self):
        """套用視窗與工作列圖示；找不到 .ico 時靜默略過，不影響啟動。"""
        self._apply_icon_to(self.root)

    def _apply_icon_to(self, window) -> None:
        """把同一個 .ico 套到指定視窗。

        實測 Tk 8.6 的 `iconbitmap(default=...)` 在 Windows 上不會傳給之後建立的
        Toplevel，所以每個對話框都要自己再套一次，否則會變成 Tk 預設圖示。
        """
        try:
            icon = resource_path(ICON_FILE)
            if os.path.exists(icon):
                window.iconbitmap(icon)
        except Exception:
            pass

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.style = style

        # Combobox dropdown appearance
        self.root.option_add("*TCombobox*Listbox.background", SURFACE)
        self.root.option_add("*TCombobox*Listbox.foreground", FG)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", BG)
        self.root.option_add("*TCombobox*Listbox.font", (UI_FONT, 10))

        style.configure(".", background=BG, foreground=FG, font=(UI_FONT, 10))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=(UI_FONT, 9))
        style.configure("TSeparator", background=SURFACE2)

        style.configure(
            "TButton",
            background=SURFACE, foreground=FG,
            borderwidth=0, focusthickness=0, focuscolor=SURFACE,
            padding=(14, 9), font=(UI_FONT, 10),
        )
        style.map(
            "TButton",
            background=[("active", SURFACE2), ("pressed", SURFACE2)],
            foreground=[("disabled", MUTED)],
        )

        style.configure(
            "Accent.TButton",
            background=ACCENT, foreground="#11111b",
            borderwidth=0, focusthickness=0, focuscolor=ACCENT,
            padding=(14, 9), font=(UI_FONT, 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_HV), ("disabled", SURFACE2)],
            foreground=[("disabled", MUTED)],
        )

        style.configure(
            "TCombobox",
            fieldbackground=SURFACE, background=SURFACE,
            foreground=FG, arrowcolor=FG,
            borderwidth=0, padding=6, font=(UI_FONT, 10),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", SURFACE), ("disabled", BG)],
            foreground=[("readonly", FG)],
            selectbackground=[("readonly", SURFACE)],
            selectforeground=[("readonly", FG)],
        )

    # --------------------------------------------------------
    #  UI construction
    # --------------------------------------------------------
    def _build_ui(self):
        # ============ Header ============
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(18, 6))

        left = tk.Frame(header, bg=BG)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(
            left, text="GoChinese Helper", bg=BG, fg=FG,
            font=(UI_FONT, 16, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            left, text=f"LauChakSing  ·  v{VERSION}", bg=BG, fg=MUTED,
            font=(UI_FONT, 9), anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        self.pin_var = tk.BooleanVar(value=bool(self.settings.get("topmost", False)))
        pin = tk.Checkbutton(
            header, text="📌 Pin on Top", variable=self.pin_var,
            command=self._toggle_topmost,
            bg=BG, fg=MUTED, activebackground=BG, activeforeground=FG,
            selectcolor=SURFACE, bd=0, highlightthickness=0,
            font=(UI_FONT, 9), cursor="hand2",
        )
        pin.pack(side="right", anchor="n")

        ttk.Separator(self.root, orient="horizontal").pack(
            fill="x", padx=20, pady=(10, 4))

        # ============ Form ============
        form = tk.Frame(self.root, bg=BG)
        form.pack(fill="x", padx=20, pady=(10, 4))
        form.columnconfigure(1, weight=1)

        def make_label(row, text):
            tk.Label(
                form, text=text, bg=BG, fg=MUTED,
                font=(UI_FONT, 10), anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 14))

        # Course
        make_label(0, "Course")
        self.course_var = tk.StringVar()
        self.course_cb = ttk.Combobox(
            form, textvariable=self.course_var, state="readonly",
            values=COURSES, font=(UI_FONT, 10),
        )
        self.course_cb.grid(row=0, column=1, sticky="ew", pady=6)
        self.course_cb.bind("<<ComboboxSelected>>", self._on_course)

        # Chapter
        make_label(1, "Chapter")
        self.chapter_var = tk.StringVar()
        self.chapter_cb = ttk.Combobox(
            form, textvariable=self.chapter_var, state="readonly",
            values=[], font=(UI_FONT, 10),
        )
        self.chapter_cb.grid(row=1, column=1, sticky="ew", pady=6)
        self.chapter_cb.bind("<<ComboboxSelected>>", self._on_chapter)

        # Exercise
        make_label(2, "Exercise")
        self.exercise_var = tk.StringVar()
        self.exercise_cb = ttk.Combobox(
            form, textvariable=self.exercise_var, state="readonly",
            values=[], font=(UI_FONT, 10),
        )
        self.exercise_cb.grid(row=2, column=1, sticky="ew", pady=6)
        self.exercise_cb.bind("<<ComboboxSelected>>", self._on_exercise)

        # Type
        make_label(3, "Type")
        self.type_var = tk.StringVar(value="—")
        tk.Label(
            form, textvariable=self.type_var, bg=BG, fg=ACCENT,
            font=(UI_FONT, 10, "bold"), anchor="w",
        ).grid(row=3, column=1, sticky="w", pady=6)

        # ============ Buttons ============
        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(18, 10))

        self.run_btn = ttk.Button(
            btn_row, text="▶   Start", style="Accent.TButton",
            command=self._on_run,
        )
        self.run_btn.pack(side="left", fill="x", expand=True)

        self.update_btn = ttk.Button(
            btn_row, text="Check for Updates",
            command=lambda: self._check_update(manual=True),
        )
        self.update_btn.pack(side="left", padx=(10, 0))

        # ============ Status bar ============
        status_bar = tk.Frame(self.root, bg=SURFACE, height=38)
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready · Select a course")
        self.status_label = tk.Label(
            status_bar, textvariable=self.status_var,
            bg=SURFACE, fg=MUTED, anchor="w",
            font=(UI_FONT, 9), padx=20,
        )
        self.status_label.pack(fill="both", expand=True)

    # --------------------------------------------------------
    #  Status & generic dialogs
    # --------------------------------------------------------
    def _set_status(self, text: str, color: str | None = None):
        def update():
            try:
                self.status_var.set(text)
                self.status_label.config(fg=color or MUTED)
            except Exception:
                pass
        try:
            self.root.after(0, update)
        except Exception:
            pass

    def _toggle_topmost(self):
        self.root.attributes("-topmost", self.pin_var.get())
        self.settings["topmost"] = self.pin_var.get()
        save_settings(self.settings)

    # ---------- Thread-safe modal dialogs ----------
    def _run_on_ui(self, func):
        """
        Run `func` on the Tk main thread and return its result.

        IMPORTANT: if we are ALREADY on the UI thread, calling
        `root.after(0, ...)` + `ev.wait()` would deadlock the
        mainloop (the event loop is blocked waiting for an event
        that only it can dispatch). This was the root cause of the
        "select LCC2010 → crash" bug. Fix: detect the UI thread and
        call `func` directly.
        """
        if threading.current_thread() is threading.main_thread():
            try:
                return func()
            except Exception:
                return None

        ev = threading.Event()
        box = {}

        def wrapper():
            try:
                box["v"] = func()
            except Exception:
                box["v"] = None
            finally:
                ev.set()

        try:
            self.root.after(0, wrapper)
        except Exception:
            # 主視窗已被銷毀（例如使用者直接關閉程式），不要讓背景執行緒卡死
            return None
        ev.wait()
        return box.get("v")

    def _dialog(self, title: str, message: str,
                ok_text: str = "OK", cancel_text: str | None = None,
                topmost: bool = False, bell: bool = False) -> bool:
        top = tk.Toplevel(self.root)
        top.title(title)
        top.configure(bg=BG)
        top.resizable(False, False)
        top.transient(self.root)
        self._apply_icon_to(top)
        if topmost:
            # 重要提示用獨立置頂視窗，避免只出現在狀態列被忽略
            try:
                top.attributes("-topmost", True)
            except Exception:
                pass
        if bell:
            try:
                top.bell()
            except Exception:
                pass
        top.grab_set()

        frame = tk.Frame(top, bg=BG, padx=24, pady=20)
        frame.pack()

        tk.Label(
            frame, text=message, bg=BG, fg=FG,
            font=(UI_FONT, 10), justify="left", anchor="w",
            wraplength=390,
        ).pack(fill="x")

        btns = tk.Frame(frame, bg=BG)
        btns.pack(fill="x", pady=(18, 0))

        result = {"v": False}

        def on_ok():
            result["v"] = True
            top.destroy()

        ttk.Button(
            btns, text=ok_text, style="Accent.TButton", command=on_ok,
        ).pack(side="right")

        if cancel_text:
            ttk.Button(
                btns, text=cancel_text, command=top.destroy,
            ).pack(side="right", padx=(0, 10))
        else:
            top.bind("<Return>", lambda e: on_ok())
            top.bind("<Escape>", lambda e: top.destroy())

        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        self.root.wait_window(top)
        return result["v"]

    def _show_info(self, title: str, message: str, ok_text: str = "OK",
                   topmost: bool = False, bell: bool = False):
        with self._modal_lock:
            self._run_on_ui(lambda: self._dialog(
                title, message, ok_text=ok_text,
                topmost=topmost, bell=bell,
            ))

    def _notify_comment(self, data: dict) -> None:
        """該題組若帶 comment，用獨立置頂視窗顯示，不再只靠狀態列（容易被忽略）。"""
        if not isinstance(data, dict):
            return
        comment = str(data.get("comment") or "").strip()
        if not comment:
            return
        self._show_info(
            "⚠️  Important Note",
            comment,
            ok_text="Got it",
            topmost=True,
            bell=True,
        )

    def _confirm(self, title: str, message: str,
                 ok_text: str = "Continue", cancel_text: str = "Cancel") -> bool:
        with self._modal_lock:
            return bool(self._run_on_ui(
                lambda: self._dialog(title, message, ok_text, cancel_text)
            ))

    # --------------------------------------------------------
    #  License dialog
    # --------------------------------------------------------
    def _show_license_dialog(self) -> bool:
        """Show the license agreement. Returns True if accepted."""
        top = tk.Toplevel(self.root)
        top.title("License Agreement")
        top.configure(bg=BG)
        top.resizable(False, False)
        self._apply_icon_to(top)
        top.protocol("WM_DELETE_WINDOW", lambda: self._close_license(top, False))

        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        # 螢幕較小時自動縮小，否則固定 580x640 會超出畫面
        w = min(580, max(sw - 80, 420))
        h = min(640, max(sh - 80, 360))
        x, y = max((sw - w) // 2, 0), max((sh - h) // 2, 0)
        top.geometry(f"{w}x{h}+{x}+{y}")

        try:
            top.attributes("-topmost", True)
        except Exception:
            pass

        # ---- Header ----
        header = tk.Frame(top, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 6))
        tk.Label(
            header, text="📜  License Agreement", bg=BG, fg=FG,
            font=(UI_FONT, 15, "bold"), anchor="w",
        ).pack(anchor="w")
        tk.Label(
            header, text="Please read carefully and accept to continue",
            bg=BG, fg=MUTED, font=(UI_FONT, 9), anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(top, orient="horizontal").pack(
            fill="x", padx=28, pady=(10, 0))

        # ---- Buttons ----
        # 注意：按鈕必須「先」pack 並固定在底部。若先 pack 會擴張的文字區，
        # 文字區會獨佔整個視窗高度，把按鈕擠到視窗外（只剩 1px，看起來像沒有按鈕）。
        btns = tk.Frame(top, bg=BG)
        btns.pack(side="bottom", fill="x", padx=28, pady=(16, 24))

        ttk.Button(
            btns, text="Decline",
            command=lambda: self._close_license(top, False),
        ).pack(side="left")
        ttk.Button(
            btns, text="I Agree", style="Accent.TButton",
            command=lambda: self._close_license(top, True),
        ).pack(side="right")

        # ---- Scrollable text ----
        text_wrap = tk.Frame(top, bg=SURFACE)
        text_wrap.pack(fill="both", expand=True, padx=28, pady=(16, 0))

        scrollbar = ttk.Scrollbar(text_wrap, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            text_wrap, bg=SURFACE, fg=FG, font=(UI_FONT, 10),
            wrap="word", padx=16, pady=14, bd=0, highlightthickness=0,
            yscrollcommand=scrollbar.set, cursor="arrow",
            spacing1=2, spacing3=6, width=48, height=12,
        )
        text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text.yview)

        text.insert("1.0", LICENSE_TEXT)
        text.config(state="disabled")

        top.lift()
        top.focus_force()
        top.grab_set()

        self.root.wait_window(top)
        return self._license_result

    def _close_license(self, top: tk.Toplevel, accepted: bool):
        self._license_result = accepted
        top.destroy()

    # --------------------------------------------------------
    #  Post-start tasks: update check / announcement
    # --------------------------------------------------------
    def _post_start(self):
        if requests is None:
            self._show_info(
                "Missing Dependencies",
                "The `requests` module is unavailable, so update checks,\n"
                "announcements and answer downloads are disabled.\n\n"
                "Install it in your terminal:\n\npip install requests",
            )
            return
        self._check_update(manual=False)
        self._show_announcement()

    # ---------- Update check ----------
    def _check_update(self, manual: bool = False):
        if requests is None:
            if manual:
                self._show_info(
                    "Check for Updates",
                    "The `requests` module is unavailable.\n\n"
                    "Install it in your terminal:\n\npip install requests",
                )
            return

        def work():
            info = fetch_update_info()
            self._handle_update(info, manual)
        threading.Thread(target=work, daemon=True).start()

    def _handle_update(self, info, manual: bool):
        if info is None:
            if manual:
                self._set_status("Update check failed (network error)", ERR_COLOR)
                self._show_info(
                    "Check for Updates",
                    "Unable to reach the update server.\n"
                    "Please check your network and try again."
                )
            return

        latest = str(info.get("version") or info.get("latest") or "").strip()
        if not latest:
            if manual:
                self._show_info("Check for Updates",
                                "The server did not return version info.")
            return

        if parse_version(latest) > parse_version(VERSION):
            notes = info.get("notes") or info.get("changelog") or ""
            msg = (
                f"New version available!\n\n"
                f"Current : v{VERSION}\n"
                f"Latest  : v{latest}"
            )
            if notes:
                msg += f"\n\nWhat's new:\n{notes}"

            go = self._confirm("Check for Updates", msg,
                               ok_text="Download", cancel_text="Later")
            if go:
                webbrowser.open(info.get("url") or BASE_URL)
            self._set_status(f"New version v{latest} available", WARN_COLOR)
        else:
            if manual:
                self._show_info("Check for Updates",
                                f"You're on the latest version (v{VERSION}).")
            self._set_status(f"Up to date (v{VERSION})", OK_COLOR)

    # ---------- Announcements ----------
    def _show_announcement(self):
        def work():
            data = fetch_announcement()
            if not data:
                return
            aid = str(data.get("id", ""))
            ignored = set(self.settings.get("ignored_announcements", []))
            if aid and aid in ignored:
                return
            # 走 _run_on_ui 並加模態鎖，避免與更新提示對話框同時彈出而互相搶 grab
            with self._modal_lock:
                self._run_on_ui(lambda: self._announcement_dialog(data, aid))
        threading.Thread(target=work, daemon=True).start()

    def _announcement_dialog(self, data: dict, aid: str):
        top = tk.Toplevel(self.root)
        top.title("📢 Announcement")
        top.configure(bg=BG)
        top.resizable(False, False)
        top.transient(self.root)
        self._apply_icon_to(top)
        top.grab_set()

        frame = tk.Frame(top, bg=BG, padx=24, pady=20)
        frame.pack()

        tk.Label(
            frame, text=data.get("title", "Announcement"), bg=BG, fg=ACCENT,
            font=(UI_FONT, 13, "bold"), anchor="w", justify="left",
            wraplength=390,
        ).pack(fill="x")

        body = data.get("body") or data.get("content") or ""
        tk.Label(
            frame, text=body, bg=BG, fg=FG, font=(UI_FONT, 10),
            wraplength=390, justify="left", anchor="w",
        ).pack(fill="x", pady=(10, 0))

        date = data.get("date")
        if date:
            tk.Label(
                frame, text=str(date), bg=BG, fg=MUTED,
                font=(UI_FONT, 8), anchor="w",
            ).pack(fill="x", pady=(8, 0))

        var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame, text="Don't show this announcement again", variable=var,
            bg=BG, fg=MUTED, activebackground=BG, activeforeground=FG,
            selectcolor=SURFACE, bd=0, highlightthickness=0,
            font=(UI_FONT, 9), cursor="hand2",
        ).pack(anchor="w", pady=(14, 0))

        def close():
            if var.get() and aid:
                ignored = self.settings.setdefault("ignored_announcements", [])
                if aid not in ignored:
                    ignored.append(aid)
                save_settings(self.settings)
            top.destroy()

        ttk.Button(
            frame, text="Got it", style="Accent.TButton", command=close,
        ).pack(fill="x", pady=(14, 0))

        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - top.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # --------------------------------------------------------
    #  Course / Chapter / Exercise
    # --------------------------------------------------------
    def _on_course(self, event=None):
        course = self.course_var.get()
        self.answers = None
        self.chapter_cb["values"] = []
        self.exercise_cb["values"] = []
        self.chapter_var.set("")
        self.exercise_var.set("")
        self.type_var.set("—")

        if not course:
            return

        if course == "LCC2010":
            self._set_status("LCC2010 coming soon…", WARN_COLOR)
            self._show_info("Notice", "LCC2010 is in preparation. Stay tuned!")
            return

        self._set_status(f"Loading {course} …")
        threading.Thread(target=self._load_course, args=(course,), daemon=True).start()

    def _load_course(self, course: str):
        if requests is None:
            self._set_status("Load failed: `requests` is not installed", ERR_COLOR)
            return
        try:
            r = requests.get(f"{BASE_URL}/answers/{course}.json", timeout=15)
            r.raise_for_status()
            data = r.json()
            self.root.after(0, lambda: self._on_course_loaded(data))
        except Exception as e:
            # 注意：except 區塊結束後 e 會被刪除，lambda 直接引用的話會 NameError，
            # 所以先把訊息算好、再用預設參數綁進 lambda
            msg = f"Load failed: {e}"
            self.root.after(0, lambda m=msg: self._set_status(m, ERR_COLOR))

    def _on_course_loaded(self, data: dict):
        self.answers = data
        chapters = list(data.keys())
        self.chapter_cb["values"] = chapters
        if chapters:
            self.chapter_var.set(chapters[0])
            self._on_chapter()
        self._set_status(f"Loaded {len(chapters)} chapter(s)", OK_COLOR)

    def _on_chapter(self, event=None):
        chapter = self.chapter_var.get()
        self.exercise_cb["values"] = []
        self.exercise_var.set("")
        self.type_var.set("—")

        if not chapter or not self.answers or chapter not in self.answers:
            return

        exercises = list(self.answers[chapter].keys())
        self.exercise_cb["values"] = exercises
        if exercises:
            self.exercise_var.set(exercises[0])
            self._on_exercise()

    def _on_exercise(self, event=None):
        chapter = self.chapter_var.get()
        exercise = self.exercise_var.get()
        if not chapter or not exercise or not self.answers:
            return
        try:
            self.type_var.set(self.answers[chapter][exercise].get("type", "—"))
        except Exception:
            self.type_var.set("—")

    # --------------------------------------------------------
    #  Run
    # --------------------------------------------------------
    def _on_run(self):
        if self.running:
            return

        if _keyboard is None:
            self._show_info(
                "Missing Dependencies",
                "The `keyboard` module is unavailable, so answers cannot be\n"
                "typed automatically.\n\n"
                "Install it in your terminal:\n\npip install keyboard\n\n"
                "Note: on Windows, `keyboard` normally needs administrator\n"
                "privileges to hook keys.",
            )
            return

        chapter = self.chapter_var.get()
        exercise = self.exercise_var.get()

        if not self.answers or not chapter or not exercise:
            self._set_status("Please select a chapter and exercise first", WARN_COLOR)
            return

        data = self.answers.get(chapter, {}).get(exercise)
        if not data:
            self._set_status("No data found for this exercise", ERR_COLOR)
            return

        self.running = True
        self.run_btn.state(["disabled"])
        threading.Thread(target=self._run_exercise, args=(data,), daemon=True).start()

    def _finish(self):
        self.running = False
        try:
            self.root.after(0, lambda: self.run_btn.state(["!disabled"]))
        except Exception:
            pass

    def _run_exercise(self, data: dict):
        try:
            typ = data.get("type")
            # 先彈出獨立提示窗（帶響鈴、置頂），使用者按「Got it」後才開始輸入
            self._notify_comment(data)
            if typ == "input":
                self._run_input(data)
            elif typ == "pmc":
                self._run_pmc(data)
            elif typ == "mc":
                self._run_mc(data)
            elif typ == "mc+input":
                self._run_mc_input(data)
            elif typ == "answer":
                self._run_answer(data)
            else:
                self._set_status(f"Unknown exercise type: {typ}", ERR_COLOR)
        except Exception as e:
            self._set_status(f"Run error: {e}", ERR_COLOR)
        finally:
            self._finish()

    # ---------- input ----------
    def _run_input(self, data: dict):
        questions = data.get("questions", [])
        answers = data.get("answers", [])
        total = min(len(questions), len(answers))
        self._set_status("Typing starts in 5s — click the answer page now…", WARN_COLOR)
        sleep(5)
        for i in range(total):
            q = questions[i]
            _keyboard.press_and_release("tab")
            _keyboard.write(str(answers[i]))
            self._set_status(f"[{q}] {answers[i]}")
        _keyboard.press_and_release("tab")
        _keyboard.press_and_release("tab")
        if total < len(questions):
            self._set_status(
                f"✔ Done (only {total}/{len(questions)} answered — data incomplete)",
                WARN_COLOR,
            )
        else:
            self._set_status("✔ Done", OK_COLOR)

    # ---------- pmc ----------
    def _run_pmc(self, data: dict):
        questions = data.get("questions", [])
        answers = data.get("answers", [])
        total = min(len(questions), len(answers))
        self._set_status("Answering starts in 5s — click the answer page now…", WARN_COLOR)
        sleep(5)
        for i in range(total):
            q = questions[i]
            _keyboard.press_and_release("tab")
            _keyboard.press_and_release("space")
            for _ in range(answers[i] - 1):
                _keyboard.press_and_release("down")
            _keyboard.press_and_release("space")
            self._set_status(f"[{q}] {letter(answers[i])}")
        _keyboard.press_and_release("tab")
        _keyboard.press_and_release("tab")
        if total < len(questions):
            self._set_status(
                f"✔ Done (only {total}/{len(questions)} answered — data incomplete)",
                WARN_COLOR,
            )
        else:
            self._set_status("✔ Done", OK_COLOR)

    # ---------- mc (requires browser DevTools) ----------
    def _run_mc(self, data: dict):
        answers = data.get("answers", {})

        if pyperclip is None:
            self._show_info(
                "Missing Dependencies",
                "The `pyperclip` module is required to read the question list\n"
                "from your clipboard.\n\n"
                "Install it in your terminal:\n\npip install pyperclip",
            )
            self._set_status("Cancelled — pyperclip is not installed", ERR_COLOR)
            return

        if not self._confirm(
            "Multiple Choice Assistant",
            "The app will now:\n\n"
            "① Open the browser DevTools (Ctrl+Shift+J) in 5s\n"
            "② Paste and run a JavaScript snippet\n"
            "③ Copy the question list to your clipboard\n\n"
            "Please click the answer page first, and DO NOT select any option!",
        ):
            self._set_status("Cancelled", WARN_COLOR)
            return

        self._set_status("Opening DevTools…", WARN_COLOR)
        sleep(5)
        _keyboard.press_and_release("ctrl+shift+j")
        sleep(3)
        _keyboard.write(JS_SNIPPET)
        _keyboard.press_and_release("enter")
        sleep(5)
        _keyboard.press_and_release("ctrl+shift+j")

        self._confirm(
            "Multiple Choice Assistant",
            "The script has finished running.\n\n"
            "Confirm you see \"Done!\" in the console, then click Continue.",
        )

        try:
            questions = json.loads(pyperclip.paste())
        except Exception:
            self._set_status("Failed to read clipboard — please try again", ERR_COLOR)
            return

        if not isinstance(questions, list) or not questions:
            self._set_status("No questions were found in the clipboard", ERR_COLOR)
            return

        # 先核對題目是否都在答案資料內，避免輸入到一半才 KeyError 造成答錯
        missing = [q for q in questions if q not in answers]
        if missing:
            preview = "\n".join(f"• {m}" for m in missing[:6])
            if len(missing) > 6:
                preview += f"\n… and {len(missing) - 6} more"
            self._show_info(
                "Questions Not Found",
                "These questions are not in the answer data, so the run was\n"
                "cancelled before typing anything:\n\n" + preview,
            )
            self._set_status("Cancelled — question list does not match the data", ERR_COLOR)
            return

        self._set_status("Answering starts in 5s — click the answer page now…", WARN_COLOR)
        sleep(5)
        for q in questions:
            _keyboard.press_and_release("tab")
            _keyboard.press_and_release("space")
            for _ in range(answers[q] - 1):
                _keyboard.press_and_release("down")
            _keyboard.press_and_release("space")
            self._set_status(f"[{q}] {letter(answers[q])}")
        _keyboard.press_and_release("tab")
        _keyboard.press_and_release("tab")

        comment = data.get("comment")
        if comment:
            self._set_status("✔ Done · Note was shown before the run", WARN_COLOR)
        else:
            self._set_status("✔ Done", OK_COLOR)

    # ---------- mc+input ----------
    def _run_mc_input(self, data: dict):
        questions = data.get("questions", [])
        answers = data.get("answers", [])
        total = min(len(questions), len(answers))
        self._set_status("Answering starts in 5s — click the answer page now…", WARN_COLOR)
        sleep(5)
        for i in range(total):
            q = questions[i]
            choice, text = answers[i][0], answers[i][1]
            _keyboard.press_and_release("tab")
            _keyboard.press_and_release("space")
            for _ in range(choice - 1):
                _keyboard.press_and_release("down")
            _keyboard.press_and_release("space")

            _keyboard.press_and_release("tab")
            _keyboard.write(str(text))
            self._set_status(f"[{q}] {letter(choice)} · {text}")
        _keyboard.press_and_release("tab")
        _keyboard.press_and_release("tab")
        if total < len(questions):
            self._set_status(
                f"✔ Done (only {total}/{len(questions)} answered — data incomplete)",
                WARN_COLOR,
            )
        else:
            self._set_status("✔ Done", OK_COLOR)

    # ---------- answer (display only) ----------
    def _run_answer(self, data: dict):
        body = "\n".join(f"• {a}" for a in data.get("answers", []))
        self._show_info("Reference Answers", body or "(none)")
        self._set_status("✔ Reference answers shown", OK_COLOR)

    # --------------------------------------------------------
    #  Close
    # --------------------------------------------------------
    def _on_close(self):
        # 若授權未通過就關閉，pin_var 可能還未建立
        if hasattr(self, "pin_var"):
            self.settings["topmost"] = self.pin_var.get()
        save_settings(self.settings)
        try:
            self.root.destroy()
        except Exception:
            pass


# ============================================================
#  Entry point
# ============================================================
def _enable_dpi_awareness() -> None:
    """在 Windows 上開啟高 DPI 感知，讓介面不模糊、不縮放錯位。

    必須在 tk.Tk() 之前呼叫，否則對已建立的視窗不會生效。
    """
    if sys.platform != "win32":
        return
    try:
        from ctypes import windll
    except Exception:
        return
    try:
        windll.shcore.SetProcessDpiAwareness(1)   # per-monitor aware
        return
    except Exception:
        pass
    try:
        windll.user32.SetProcessDPIAware()        # 舊版 Windows 的備用方案
    except Exception:
        pass


def main():
    # DPI 感知必須在建立任何視窗之前設定，否則在 tk.Tk() 之後才呼叫會完全無效
    _enable_dpi_awareness()

    root = tk.Tk()
    app = GoChineseHelper(root)

    if app._license_denied:        # User declined → exit immediately
        root.destroy()
        return

    root.mainloop()


if __name__ == "__main__":
    main()