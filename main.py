import tkinter as tk
from tkinter import messagebox,Scale, HORIZONTAL,Tk
from tkinter import simpledialog, colorchooser
from tkinter.simpledialog import askstring
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk


import os
import subprocess
import json
import sys
import psutil
from pynput import keyboard






ver = '3.0'

global alpha



default_settings = {
    'circle': {
        'window_exists': False,
        'visible': False,
        'color': 'white',
        'radius': 50,
        'antialiasing': False,
    },
    'alpha': 0.5,
    'program_path': {'path': ''},
    'menu_color': 'black',
    'window_position': {
        'x': 100,
        'y': 100
    }
}

circle_settings = default_settings['circle']

def ask_for_path(event=None):
    path = askstring("パスを入力", "起動したいプログラムのパスを入力してね絶対参照で""は入ってもok", parent=root)
    if path is not None:
        # 既にパスが二重引用符で囲まれている場合、それらを削除します
        path = path.strip('"')
        option2_button.path = path

        # settingsの更新と保存
        default_settings['program_path'] = {'path': path}
        save_settings()


def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)



def launch_program():
    load_settings()
    path = default_settings.get('program_path', {}).get('path', '')

    if os.path.isfile(path):
        try:
            subprocess.Popen(path)
        except Exception as e:
            show_error("エラー", f"プログラムでエラーが起きました: {str(e)}")
    else:
        show_error("エラー", "パスが存在しないか実行できるファイルではありません\n実行におすすめなのは,bat,ショートカット,exeです")




def is_obs_running():
    # OBSが実行中かどうかを確認
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'obs64.exe':
            return True
    return False

def launch_ESP_python():
    # Pythonのインタープリタのパスを指定
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    python_interpreter_path = os.path.join(application_path, "venv/Scripts/python.exe")

    # このファイルを起動したフォルダと同じ場所にあるnew.pyを起動するように自動でosで検知
    path = os.path.join(application_path, "new.py")

    # ESPの状態とプロセスを保持するフラグ
    global esp_enabled, process
    if 'esp_enabled' not in globals():
        esp_enabled = False
        process = None

    # ESPの状態に応じてプログラムを起動または終了
    if esp_enabled:
        # ESPが有効な場合は無効にする
        if process is not None:
            process.terminate()  # terminate()からkill()に変更
            process = None
        esp_enabled = False
    else:
        # ESPが無効な場合は有効にする
        if not os.path.isfile(path):
            show_error("エラー", "new.pyが存在しません")
        elif not os.path.isfile(python_interpreter_path):
            show_error("エラー", "Pythonのインタープリタが存在しません 付属のsetup.batを実行してください！！")
        else:
            # venvが存在しない場合は、setup.batを実行するようにアラートを表示
            venv_path = os.path.join(application_path, "venv")
            if not os.path.isdir(venv_path):
                show_error("エラー", "venv は存在しません。付属の setup.bat ファイルを実行してください。ダブルクリックで実行できます\n同フォルダにvenvというフォルダが出来れば成功です\nまたESPのボタンの場所で右クリックをして説明を読んでください")
            elif not is_obs_running():
                show_error("エラー", "OBSが起動していません。OBSを起動し、仮想カメラを有効にしてください。\n仮想カメラには検知したいウィンドウをキャプチャーしてください")
            else:
                process = subprocess.Popen([python_interpreter_path,path])
                esp_enabled = True




def toggle_menu(event=None):
    if menu_frame.winfo_viewable():
        menu_frame.grid_remove()
    else:
        menu_frame.grid()

def draw_circle():
    # 既存の円ウィンドウがあれば閉じる
    if circle_settings['window_exists']:
        circle_settings['window'].destroy()
        circle_settings['window'] = None
        circle_settings['window_exists'] = False

    # 円が非表示の場合は表示する
    if not circle_settings['visible']:
        create_circle_window()
    else:
        circle_settings['visible'] = False



def create_circle_window():
    circle_window = tk.Toplevel(root)
    circle_window.attributes('-fullscreen', True) 
    circle_window.attributes('-alpha', 1.0)  
    circle_window.attributes('-topmost', True) 
    circle_window.title("Circle Window") 
    circle_window.overrideredirect(True) 
    circle_window.attributes('-transparentcolor', 'black')  

    # PILを使用してアンチエイリアシングを適用した円を描画
    screen_width = circle_window.winfo_screenwidth()
    screen_height = circle_window.winfo_screenheight()
    image = Image.new('RGBA', (screen_width, screen_height), (0, 0, 0, 0))  # 透明な背景
    draw = ImageDraw.Draw(image)
    if circle_settings['antialiasing']:
        draw.ellipse([(screen_width//2 - circle_settings['radius'], screen_height//2 - circle_settings['radius']), (screen_width//2 + circle_settings['radius'], screen_height//2 + circle_settings['radius'])], outline=circle_settings['color'], width=3)
    else:
        draw.ellipse([(screen_width//2 - circle_settings['radius'], screen_height//2 - circle_settings['radius']), (screen_width//2 + circle_settings['radius'], screen_height//2 + circle_settings['radius'])], outline=circle_settings['color'])

    # PILのImageをTkinterのPhotoImageに変換
    circle_settings['photo'] = ImageTk.PhotoImage(image)

    # PhotoImageをCanvasに表示
    canvas = tk.Canvas(circle_window, bg='black', highlightthickness=0)
    canvas.create_image(0, 0, image=circle_settings['photo'], anchor='nw')
    canvas.pack(fill='both', expand=True)

    # 円ウィンドウを保存
    circle_settings['window'] = circle_window
    circle_settings['window_exists'] = True
    circle_settings['visible'] = True




def save_settings():
    settings = {
        'circle': {
            'window_exists': circle_settings['window_exists'],  # ウィンドウが存在するかどうかを保存
            'visible': circle_settings['visible'],
            'color': circle_settings['color'],
            'size': circle_settings['radius'],
            'antialiasing': circle_settings['antialiasing']
        },
         'alpha': alpha,
        'program_path': default_settings['program_path'],
         'menu_color': menu_color,
         'window_position': {  # ウィンドウの位置を保存
            'x': root.winfo_x(),
            'y': root.winfo_y()
        }
    }
    with open('config.json', 'w') as f:
        json.dump(settings, f, indent=4)




var = circle_settings['antialiasing']



def toggle_antialiasing():
    # アンチエイリアシングの設定を反転させる
    circle_settings['antialiasing'] = not circle_settings['antialiasing']
    if circle_settings['visible']:
        draw_circle()  # 設定を即時反映
    save_settings()  # 設定を保存
    # 現在の設定状態を表示
    current_state = "有効" if circle_settings['antialiasing'] else "無効"
    messagebox.showinfo("アンチエイリアシング", "現在の状態: " + current_state)



def change_color():
    color_code = colorchooser.askcolor(title ="色を選択してね！")
    if color_code[1] is not None:
        circle_settings['color'] = color_code[1]
        if circle_settings['visible']:
            draw_circle()  # 設定を即時反映
        save_settings()  # 設定を保存

def change_size():
    root = Tk()
    root.withdraw()  # Hide the main window
    size = simpledialog.askinteger("サイズを入力", "サイズ入力してね0~500", minvalue=0, maxvalue=500)
    if size is not None:
        circle_settings['radius'] = size
        if circle_settings['visible']:
            draw_circle()  # 設定を即時反映
        save_settings()  # 設定を保存
    else:
        messagebox.showinfo("情報", "操作がキャンセルされました")




def show_usage(event):
    # 使用方法のメッセージ
    usage_message = "このESPを使用するにはOBSの仮想カメラを起動してください\nOBSのカメラから情報を取得しているのでまたFPSがかなり低下します、\n大体10~20fps低下"
    
    # メッセージボックスを表示
    messagebox.showinfo("使用方法", usage_message)

# ドラッグでウィンドウを移動するための関数
def start_move(event):
    root.x = event.x_root - root.winfo_x()
    root.y = event.y_root - root.winfo_y()
    

def do_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")
    save_settings()



def show_sub_menu(event, menu):
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()





def open_alpha_window():
 global alpha_window
 global alpha_scale
 global alpha_label

 alpha_window = tk.Toplevel(root)
 alpha_window.geometry('200x100')
 alpha_window.title("透明度調整")
 alpha_window.configure(bg='black')
 alpha_window.option_add('*Background', 'black')
 alpha_window.option_add('*Foreground', 'white')
 alpha_window.attributes('-topmost', True)  # 追加

 # スライダー
 alpha_scale = tk.Scale(alpha_window, from_=0.0, to=1.0, resolution=0.01, command=change_alpha, orient='horizontal')
 alpha_scale.pack(padx=10, pady=10)

 # 現在の透明度ラベル
 alpha_label = tk.Label(alpha_window, text=f"現在の透明度: {alpha:.2f}", bg='black', fg='white')
 alpha_label.pack()

 # ウィンドウにフチとタイトルバーを追加
 alpha_window.option_add('*relief', 'raised')  # reliefを'solid'から'raised'に変更
 alpha_window.option_add('*borderwidth', 5)  # borderwidthを2から5に変更


def change_alpha(value):
    global alpha
    value = float(value)  # valueをfloatに変換
    alpha = max(value, 0.10)  # ここを修正
    root.attributes('-alpha', alpha)  # メインウィンドウの透明度を変更
    alpha_label.config(text=f"現在の透明度: {alpha:.2f}")  # Use config method to update the text
    save_settings()




# 新しいオプション5のボタン (概要表示)
def show_overview():
    messagebox.showinfo("説明", f"このアプリケーションの開発者はこう君です\nまたサポートが必要な場合はDiscordのkoukun_にDMを送って下さい\nまたこのソフトウェアはチートクライアントではありません\n各機能ですが円はそのまんま真ん中に円を表示させます\n配信スタートはショートカットなので起動したいパスを右クリックでsubmenuを出しそこでパスを入力してね\nESPは別のpyが必要ですこう君にもらってねまたOBSの仮想カメラを起動しておき画面を検知したいウィンドウにしてください\n透明度はメニューの透明度を変更します\nF9でメニューを閉じたり開いたりできます\nversion:{ver}\nアイコン：BING AI")




def on_enter(e):
    e.widget['background'] = 'darkgray'

def on_leave(e):
    e.widget['background'] = 'gray'




def choose_color_from_palette():
    # カラーダイアログを開く
    color_code = colorchooser.askcolor(title ="Choose color")
    if color_code[1] is None:
        return default_settings  # 有効な色が選択されなかった場合はNoneを返す
    else:
        return color_code[1]  # 選択した色を文字列として返す

def change_menu_color(new_color):
    global menu_color  # menu_color を global 変数として追加
    menu_color = new_color
    save_settings()
    apply_menu_color()  # 新しい色をメニューに適用

def choose_and_change_color():
    # カラーパレットから色を選択
    new_color = choose_color_from_palette()

    # 新しい色が有効な場合、メニューの色を変更
    if new_color != default_settings:
        # メニューの色を変更
        change_successful = change_menu_color(new_color)
        
        # メニューの色が変更できた場合、メニューを更新
        if change_successful:
            update_menu()

def update_menu():
    # 現在のアプリケーションを終了
    root.quit()

    # アプリケーションを再起動
    os.execl(sys.executable, sys.executable, *sys.argv)

def apply_menu_color():
    # メニューの色を変更
    root.config(bg=menu_color)
    root.option_add('*Background', menu_color)
    root.option_add('*Foreground', 'white') # テキストの色を変更は実施しない

    update_menu()
# Window creation
root = tk.Tk()



def load_settings():
    global alpha, menu_color #グローバル変数を定義
    try:
        with open('config.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = default_settings

    circle_settings['window_exists'] = settings.get('circle', default_settings['circle']).get('window_exists', default_settings['circle']['window_exists'])  # ウィンドウが存在するかどうかをconfigから取得
    circle_settings['visible'] = settings.get('circle', default_settings['circle']).get('visible', default_settings['circle']['visible'])
    circle_settings['color'] = settings.get('circle', default_settings['circle']).get('color', default_settings['circle']['color'])
    circle_settings['radius'] = int(settings.get('circle', default_settings['circle']).get('size', default_settings['circle']['radius']))
    circle_settings['antialiasing'] = settings.get('circle', default_settings['circle']).get('antialiasing', default_settings['circle']['antialiasing'])  # アンチエイリアシングの設定を読み込む
    alpha = float(settings.get('alpha', default_settings['alpha']))
    default_settings['program_path'] = settings.get('program_path', default_settings['program_path'])
    menu_color = settings.get('menu_color', default_settings['menu_color'])  # menu_color の設定を読み込む
    # ウィンドウの位置を読み込む
    window_position = settings.get('window_position', default_settings['window_position']) #Configから取得
    root.geometry('+%d+%d' % (window_position.get('x', 0), window_position.get('y', 0)))  # ウィンドウの位置をconfigから取得



load_settings()


def gaiyou():
    show_info("バージョン","version3.0\n結局PyQt5からtkに戻しました(´;ω;｀)無駄な10時間..\nversion2.0\nこのバージョンではTKからPyQt5に移行しました作業時間10時間( ﾉД`)ｼｸｼｸ…\nversion1.0\ntkで最初のチートクライアント風のソフトを作成:バグ修正24時間( ﾉД`)ｼｸｼｸ…")







root.geometry('160x350')  # Set window size to 160x350
root.attributes('-alpha', 0.5)  # Semi-transparent window
root.attributes('-topmost', True)  # Always display window in the foreground
root.title("Menu Window")  # Set window title
root.overrideredirect(True)  # Remove window border
root.bind("<ButtonPress-1>", start_move)
root.bind("<B1-Motion>", do_move)

# Dark mode settings
root.configure(bg=menu_color)
root.option_add('*Background', menu_color)
root.option_add('*Foreground', 'white')



menu_frame = tk.Frame(root, bg=menu_color)
menu_frame.grid(row=0, column=0)


tk.Label(menu_frame, text="_______________________________", bg=menu_color, fg='white').grid(row=1,pady=(35, 0))  # Adjust the pady value here
label = tk.Label(root, text="Menu", anchor='center', justify='center', font=("Arial Black", 20))
label.place(x=40, y=7.4)
# Option 1 button
option1_button = tk.Button(menu_frame, text="画面に円を設置", command=draw_circle, bg='gray', fg='white', anchor='center', justify='center')
option1_button.grid(row=2, column=0, padx=10, pady=10, sticky=tk.NSEW)  # Add sticky parameter
option1_button.bind("<Enter>", on_enter)
option1_button.bind("<Leave>", on_leave)
# Submenu creation
sub_menu1 = tk.Menu(root, tearoff=0)
sub_menu1.add_command(label="色を変える", command=change_color)
sub_menu1.add_command(label="サイズ変更", command=change_size)
sub_menu1.add_command(label="アンチエイリアシング", command=toggle_antialiasing)

option1_button.bind("<Button-3>", lambda event: show_sub_menu(event, sub_menu1))

# Option 2 button
option2_button = tk.Button(menu_frame, text="配信スタート", command=launch_program, bg='gray', fg='white', anchor='center', justify='center')
option2_button.grid(row=3, column=0, padx=10, pady=10, sticky=tk.NSEW)  # Add sticky parameter
option2_button.bind("<Button-3>", ask_for_path)
option2_button.bind("<Enter>", on_enter)
option2_button.bind("<Leave>", on_leave)

# Option 3 button
option3_button = tk.Button(menu_frame, text="ESP/[使用して良いか確認]", command=launch_ESP_python, bg='gray', fg='white', anchor='center', justify='center')
option3_button.grid(row=4, column=0, padx=10, pady=10, sticky=tk.NSEW)  # Add sticky parameter
option3_button.bind("<Button-3>", show_usage)
option3_button.bind("<Enter>", on_enter)
option3_button.bind("<Leave>", on_leave)

# Option 4 button
option4_button = tk.Button(menu_frame, text="透明度調整", command=open_alpha_window, bg='gray', fg='white', anchor='center', justify='center')
option4_button.grid(row=5, column=0, padx=10, pady=10, sticky=tk.NSEW)
option4_button.bind("<Enter>", on_enter)
option4_button.bind("<Leave>", on_leave)
sub_menu = tk.Menu(root, tearoff=0)
sub_menu.add_command(label="背景色", command=choose_and_change_color)

option4_button.bind("<Button-3>", lambda event: show_sub_menu(event, sub_menu))



# Option 5 button
option5_button = tk.Button(menu_frame, text="概要", command=show_overview, bg='gray', fg='white', anchor='center', justify='center')
option5_button.grid(row=6, column=0, padx=10, pady=10, sticky=tk.NSEW)
option5_button.bind("<Enter>", on_enter)
option5_button.bind("<Leave>", on_leave)

submenu2 = tk.Menu(root,tearoff=0)
submenu2.add_command(label="説明",command=gaiyou)

option5_button.bind("<Button-3>", lambda event: show_sub_menu(event, submenu2))


option6_button = tk.Button(menu_frame, text="アプリを終了", command=root.quit, bg='gray', fg='white', anchor='center', justify='center')
option6_button.grid(row=7, column=0, padx=30, pady=15, sticky=tk.NSEW)
option6_button.bind("<Enter>", on_enter)
option6_button.bind("<Leave>", on_leave)




# F9キーでメニューの表示/非表示を切り替える

def toggle_visibility(root):
    if root.winfo_viewable():
        root.withdraw()
    else:
        root.deiconify()


hotkey = keyboard.GlobalHotKeys({
    '<alt>+m': lambda: toggle_visibility(root)
})
hotkey.start()

root.mainloop()
