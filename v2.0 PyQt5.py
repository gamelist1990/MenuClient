from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QInputDialog, QColorDialog, QMessageBox,QWidget,QApplication,QVBoxLayout,QPushButton,QMainWindow,QShortcut
from PyQt5.QtGui import QPainter, QPen, QColor,QKeySequence
from PyQt5.QtCore import Qt,QPropertyAnimation,QEasingCurve,QRect
import os
import subprocess
import sys
import psutil
import json
import keyboard
from PyQt5.QtWidgets import QPushButton
import threading
from pynput import keyboard



ver = '2.0'
global alpha
default_settings = {
    'circle': {
        'window': None,
        'visible': False,
        'color': 'white',
        'radius': 50,
        'antialiasing': False,
    },
    'alpha': 0.5,
    'program_path': {'path': ''},
    'menu_color': 'black'
    
}

circle_settings = default_settings['circle']


def ask_for_path():
    path, ok = QInputDialog.getText(None, "パスを入力", "起動したいプログラムのパスを入力してね絶対参照で""は入ってもok",flags=QtCore.Qt.WindowStaysOnTopHint)
    if ok:
        # 既にパスが二重引用符で囲まれている場合、それらを削除します
        path = path.strip('"')
        option2_button.path = path

        # settingsの更新と保存
        default_settings['program_path'] = {'path': path}
        save_settings()


def show_error(title, message):
    msg = QMessageBox()
    msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    msg.setIcon(QMessageBox.Critical)
    msg.setInformativeText(message)
    msg.setWindowTitle(title)
    msg.exec_()

def show_info(title, message):
    msg = QMessageBox()
    msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    msg.setIcon(QMessageBox.Information)  # アイコンをInformationに設定
    msg.setInformativeText(message)
    msg.setWindowTitle(title)
    msg.exec_()



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
        if os.path.isfile(path) and os.path.isfile(python_interpreter_path):
            # venvが存在しない場合は、setup.batを実行するようにアラートを表示
            venv_path = os.path.join(application_path, "venv")
            if not os.path.isdir(venv_path):
                show_error("エラー", "venv は存在しません。付属の setup.bat ファイルを実行してください。ダブルクリックで実行できます\n同フォルダにvenvというフォルダが出来れば成功です\nまたESPのボタンの場所で右クリックをして説明を読んでください")
            if not is_obs_running():
                show_error("エラー", "OBSが起動していません。OBSを起動し、仮想カメラを有効にしてください。\n仮想カメラには検知したいウィンドウをキャプチャーしてください")
            else:
                process = subprocess.Popen([python_interpreter_path,path])
                esp_enabled = True
        else:
                show_error("Error", "パスが存在しないか、ファイルではありません")




class CircleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, QApplication.desktop().width(), QApplication.desktop().height())
        self.showFullScreen()

    def paintEvent(self, event):
     painter = QPainter(self)
     # アンチエイリアシングの設定を反映
     painter.setRenderHint(QPainter.Antialiasing, circle_settings['antialiasing'])  
     pen = QPen()
     pen.setColor(QColor(circle_settings['color']))  # 円の色を設定
     painter.setPen(pen)
     radius = circle_settings['radius']
     painter.drawEllipse(self.width() // 2 - radius, self.height() // 2 - radius, 2 * radius, 2 * radius)


def draw_circle():
    if circle_settings['window'] is not None:
        circle_settings['window'].close()
        circle_settings['window'] = None

    if not circle_settings['visible']:
        circle_settings['window'] = CircleWindow()
        circle_settings['visible'] = True
    else:
        circle_settings['visible'] = False



def toggle_antialiasing():
    items = ("有効", "無効")
    current_state = "有効" if circle_settings['antialiasing'] else "無効"
    item, ok = QInputDialog.getItem(root, "アンチエイリアシング", "現在の状態: " + current_state + "です", items, 0, False, flags=QtCore.Qt.WindowStaysOnTopHint)
    if ok and item:
        # アンチエイリアシングの設定を反転させる
        circle_settings['antialiasing'] = True if item == "有効" else False
        if circle_settings['visible']:
            draw_circle()  # 設定を即時反映
        save_settings()  # 設定を保存
        # 現在の設定状態を表示
        current_state = "有効" if circle_settings['antialiasing'] else "無効"
        QMessageBox.information(root, "アンチエイリアシング", "現在の状態: " + current_state, QMessageBox.Ok)





def change_color():
    color_dialog = QColorDialog()
    color_dialog.setWindowFlags(color_dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    
    # カラーパレットのダイアログが開いたらメニューを非表示
    root.hide()

    color = color_dialog.getColor()

    if color.isValid():
        circle_settings['color'] = color.name()
        if circle_settings['visible']:
            draw_circle()  # 設定を即時反映
        save_settings()  # 設定を保存

    # カラーパレットのダイアログが閉じたらメニューを再表示
    root.show()


def change_size():
    size, ok = QInputDialog.getInt(root, "サイズを入力", "サイズ入力してね0~500", flags=QtCore.Qt.WindowStaysOnTopHint)  # 追加
    if ok:
        circle_settings['radius'] = size
        if circle_settings['visible']:
            draw_circle()  # 設定を即時反映
        save_settings()  # 設定を保存


def save_settings():
    settings = {
        'circle': {
            'color': circle_settings['color'],
            'size': circle_settings['radius'],
            'window': circle_settings['window'],
            'visible': circle_settings['visible'],
            'antialiasing': circle_settings['antialiasing']
        },
        'alpha': alpha,
        'program_path': default_settings['program_path'],
        'menu_color': menu_color
    }
    with open('config.json', 'w') as f:
        json.dump(settings, f)

def load_settings():
    global alpha, menu_color  #グローバル変数
    try:
        with open('config.json', 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = default_settings #configが無ければ

    circle_settings['window'] = settings.get('circle', default_settings['circle']).get('window', default_settings['circle']['window'])
    circle_settings['visible'] = settings.get('circle', default_settings['circle']).get('visible', default_settings['circle']['visible'])
    circle_settings['color'] = settings.get('circle', default_settings['circle']).get('color', default_settings['circle']['color'])
    circle_settings['radius'] = int(settings.get('circle', default_settings['circle']).get('size', default_settings['circle']['radius']))
    circle_settings['antialiasing'] = settings.get('circle', default_settings['circle']).get('antialiasing', default_settings['circle']['antialiasing'])  # アンチエイリアシングの設定を読み込む
    alpha = float(settings.get('alpha', default_settings['alpha']))
    default_settings['program_path'] = settings.get('program_path', default_settings['program_path'])
    menu_color = settings.get('menu_color', default_settings['menu_color'])  # menu_color の設定を読み込む

load_settings()


def show_usage():
    # 使用方法のメッセージ
    usage_message = "このESPを使用するにはOBSの仮想カメラを起動してください\nOBSのカメラから情報を取得しているのでまたFPSがかなり低下します、\n大体10~20fps低下"
    
    # メッセージボックスを表示
    show_info("使用方法", usage_message)

        







def open_alpha_window():
    global alpha_window
    global alpha_scale
    global alpha_label

    alpha_window = QtWidgets.QDialog()
    alpha_window.setWindowFlags(alpha_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 追加
    alpha_window.setWindowTitle("透明度調整")
    alpha_window.setFixedSize(200, 100)

    layout = QtWidgets.QVBoxLayout()

    # スライダー
    alpha_scale = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    alpha_scale.setMinimum(0)
    alpha_scale.setMaximum(100)
    alpha_scale.setValue(int(alpha * 100))  # ここを修正
    alpha_scale.valueChanged.connect(change_alpha)
    layout.addWidget(alpha_scale)

    # 現在の透明度ラベル
    alpha_label = QtWidgets.QLabel(f"現在の透明度: {alpha:.2f}")
    layout.addWidget(alpha_label)

    alpha_window.setLayout(layout)
    alpha_window.show()

def change_alpha(value):
    global alpha
    alpha = max(value / 100, 0.10)  # ここを修正
    root.setWindowOpacity(alpha)
    alpha_label.setText(f"現在の透明度: {alpha:.2f}")
    save_settings()  # 設定を保存


# アプリケーションの開始時に設定を読み込む
load_settings()


def show_overview():
    show_info("説明", f"このアプリケーションの開発者はこう君です\nまたサポートが必要な場合はDiscordのkoukun_にDMを送って下さい\nまたこのソフトウェアはチートクライアントではありません\n各機能ですが円はそのまんま真ん中に円を表示させます\n配信スタートはショートカットなので起動したいパスを右クリックでsubmenuを出しそこでパスを入力してね\nESPは別のpyが必要ですこう君にもらってねまたOBSの仮想カメラを起動しておき画面を検知したいウィンドウにしてください\n透明度はメニューの透明度を変更します\nF9でメニューを閉じたり開いたりできます\nversion:{ver}\nアイコン：BING AI")


class HoverHandler(QtCore.QObject):
    def __init__(self, widget, button_style, hover_style):
        super().__init__(widget)
        self.widget = widget
        self.button_style = button_style
        self.hover_style = hover_style
        self.animation = QPropertyAnimation(self.widget, b"size")
        self.animation.setDuration(100)  # animation duration in milliseconds
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Enter:
            self.widget.setStyleSheet(self.hover_style)
        elif event.type() == QtCore.QEvent.Leave:
            self.widget.setStyleSheet(self.button_style)
        elif event.type() == QtCore.QEvent.MouseButtonPress:
            self.animation.stop()
            self.animation.setEndValue(self.widget.size() * 1.1)  # increase size by 10%
            self.animation.start()
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            self.animation.stop()
            self.animation.setEndValue(self.widget.size() / 1.1)  # restore original size
            self.animation.start()
        return super().eventFilter(watched, event)



    
class DraggableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self._dragPos = QtCore.QPoint()

    def mousePressEvent(self, event):
        self._dragPos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._dragPos)




def show1_sub_menu(button):
    # ボタンの位置と大きさを取得
    button_pos = button.pos()
    button_height = button.height()

    # サブメニューの表示位置を計算（ボタンのすぐ右側）
    menu_pos = button.mapToGlobal(QtCore.QPoint(button.width(), button_height // 2))

    # サブメニューを表示
    sub_menu1.exec_(menu_pos)

def show2_sub_menu(button):
    # ボタンの位置と大きさを取得
    button_pos = button.pos()
    button_height = button.height()

    # サブメニューの表示位置を計算（ボタンのすぐ右側）
    menu_pos = button.mapToGlobal(QtCore.QPoint(button.width(), button_height // 2))

    # サブメニューを表示
    sub_menu2.exec_(menu_pos)

def show3_sub_menu(button):
    # ボタンの位置と大きさを取得
    button_pos = button.pos()
    button_height = button.height()

    # サブメニューの表示位置を計算（ボタンのすぐ右側）
    menu_pos = button.mapToGlobal(QtCore.QPoint(button.width(), button_height // 2))

    # サブメニューを表示
    sub_menu3.exec_(menu_pos)

def show4_sub_menu(button):
    # ボタンの位置と大きさを取得
    button_pos = button.pos()
    button_height = button.height()

    # サブメニューの表示位置を計算（ボタンのすぐ右側）
    menu_pos = button.mapToGlobal(QtCore.QPoint(button.width(), button_height // 2))

    # サブメニューを表示
    sub_menu4.exec_(menu_pos)

def show5_sub_menu(button):
    # ボタンの位置と大きさを取得
    button_pos = button.pos()
    button_height = button.height()

    # サブメニューの表示位置を計算（ボタンのすぐ右側）
    menu_pos = button.mapToGlobal(QtCore.QPoint(button.width(), button_height // 2))

    # サブメニューを表示
    sub_menu5.exec_(menu_pos)

def choose_color_from_palette():
    color_dialog = QColorDialog()
    color_dialog.setWindowFlags(color_dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    
    # カラーパレットのダイアログが開いたらメニューを非表示
    root.hide()

    color = color_dialog.getColor()

    # カラーパレットのダイアログが閉じたらメニューを再表示
    root.show()

    if color.isValid():
        return color.name()  # 選択した色を文字列として返す
    else:
        return default_settings  # 有効な色が選択されなかった場合はNoneを返す


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
    QApplication.quit()

    # アプリケーションを再起動
    os.execl(sys.executable, sys.executable, *sys.argv)

def apply_menu_color():
    # QApplication のインスタンスを取得
    app = QApplication.instance()

    # メニューの色を変更
    app.setStyleSheet(f"QMenu {{ background-color: {menu_color}; }}")

    update_menu()


def gaiyou():
    show_info("バージョン","\nversion2.0\nこのバージョンではTKからPyQt5に移行しました作業時間10時間( ﾉД`)ｼｸｼｸ…\nversion1.0\ntkで最初のチートクライアント風のソフトを作成:バグ修正24時間( ﾉД`)ｼｸｼｸ…")

def toggle_visibility(root):
    if root.windowOpacity() > 0:
        root.setWindowOpacity(0)
    else:
        root.setWindowOpacity(alpha)


def on_press(key):
    try:
        if key == keyboard.Key.f4:
            toggle_visibility(root)
    except AttributeError:
        pass

class HiddenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.Tool)

class DraggableRoot(DraggableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedSize(160, 350) 

# Window creation
app = QtWidgets.QApplication([])
root = DraggableRoot()
root.setWindowOpacity(alpha)  
root.setStyleSheet(f"background-color: {menu_color}; color: white")










# QGroupBoxの作成
group_box = QtWidgets.QGroupBox(root)

menu_frame = QtWidgets.QGridLayout(group_box)


menu_frame.setContentsMargins(6, 71, 0, 0)
text = QtWidgets.QLabel("_______________________________________",group_box)
text.setFixedWidth(root.width() - 3)  # Set text's fixed width to match the root's width
text.move(1, 31)

label = QtWidgets.QLabel("Menu", group_box)
label.setFont(QtGui.QFont("Arial Black", 20))
label.move(40, 15)








style = """
QPushButton {
    background-color: #555555;
    color: #ffffff;
    font-weight: bold;
    border: 2px solid #ffffff;
    border-radius: 5px;
    margin: 0px;
    padding: 0px;
}
"""

button_style = 'background-color: #555555; color: #ffffff; font-weight: bold; border: 2px solid #ffffff; border-radius: 5px;'
hover_style = 'background-color: #888888; color: #ffffff; font-weight: bold; border: 2px solid #ffffff; border-radius: 5px;'


option1_button = QtWidgets.QPushButton("画面に円を設置")
option1_button.clicked.connect(draw_circle)
option1_button.setStyleSheet(button_style)
option1_button.installEventFilter(HoverHandler(option1_button, button_style, hover_style))
menu_frame.setAlignment(option1_button, QtCore.Qt.AlignCenter)

menu_frame.addWidget(option1_button, 1,0)  


# Submenu creation
sub_menu1 = QtWidgets.QMenu(option1_button)
sub_menu1.addAction("色を変える", change_color)
sub_menu1.addAction("サイズ変更", change_size)
sub_menu1.addAction("アンチエイリアス",toggle_antialiasing)

option1_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
option1_button.customContextMenuRequested.connect(lambda: show1_sub_menu(option1_button))

#下部への空白を追加
spacer_bottom = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
menu_frame.addItem(spacer_bottom, 2, 0)

# Option 2 button
option2_button = QtWidgets.QPushButton("配信スタート")
option2_button.clicked.connect(launch_program)
option2_button.setStyleSheet(button_style)
option2_button.installEventFilter(HoverHandler(option2_button, button_style, hover_style))
menu_frame.setAlignment(option2_button, QtCore.Qt.AlignCenter)

menu_frame.addWidget(option2_button, 3, 0)  

sub_menu2 = QtWidgets.QMenu(option2_button)
sub_menu2.addAction("パスを入力",ask_for_path )

option2_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
option2_button.customContextMenuRequested.connect(lambda: show2_sub_menu(option2_button))

#下部への空白を追加
spacer_bottom = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
menu_frame.addItem(spacer_bottom, 4, 0)

# Option 3 button
option3_button = QtWidgets.QPushButton("ESP/[使用して良いか確認]")
option3_button.clicked.connect(launch_ESP_python)
option3_button.setStyleSheet(button_style)
option3_button.installEventFilter(HoverHandler(option3_button, button_style, hover_style))
menu_frame.setAlignment(option3_button, QtCore.Qt.AlignCenter)

menu_frame.addWidget(option3_button, 5, 0)  

sub_menu3 = QtWidgets.QMenu(option3_button)
sub_menu3.addAction("説明",show_usage)

option3_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
option3_button.customContextMenuRequested.connect(lambda: show3_sub_menu(option3_button))

#下部への空白を追加
spacer_bottom = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
menu_frame.addItem(spacer_bottom, 6, 0)

# Option 4 button
option4_button = QtWidgets.QPushButton("透明度調整")
option4_button.clicked.connect(open_alpha_window)
option4_button.setStyleSheet(button_style)
option4_button.installEventFilter(HoverHandler(option4_button, button_style, hover_style))
menu_frame.setAlignment(option4_button, QtCore.Qt.AlignCenter)

menu_frame.addWidget(option4_button, 7, 0)

sub_menu4 = QtWidgets.QMenu(option4_button)
sub_menu4.addAction("メニューの色を変更",choose_and_change_color)

option4_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
option4_button.customContextMenuRequested.connect(lambda: show4_sub_menu(option4_button))




#下部への空白を追加
spacer_bottom = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
menu_frame.addItem(spacer_bottom, 8, 0)

# Option 5 button
option5_button = QtWidgets.QPushButton("概要")
option5_button.clicked.connect(show_overview)
option5_button.setStyleSheet(button_style)
option5_button.installEventFilter(HoverHandler(option5_button, button_style, hover_style))
menu_frame.setAlignment(option5_button, QtCore.Qt.AlignCenter)

menu_frame.addWidget(option5_button, 9, 0)

sub_menu5 = QtWidgets.QMenu(option5_button)
sub_menu5.addAction("バージョン履歴",gaiyou)

option5_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
option5_button.customContextMenuRequested.connect(lambda: show5_sub_menu(option5_button))

#下部への空白を追加
spacer_bottom = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
menu_frame.addItem(spacer_bottom, 10, 0)



option6_button = QtWidgets.QPushButton("アプリを終了")
option6_button.clicked.connect(app.quit)
option6_button.setStyleSheet(style)
option6_button.installEventFilter(HoverHandler(option6_button, style, hover_style))
option6_button.setFixedWidth(80)  # You can adjust this value to your liking
# Add the button to the grid layout
menu_frame.addWidget(option6_button, 11, 0)
# Align the button to the center of its grid cell
menu_frame.setAlignment(option6_button, QtCore.Qt.AlignCenter)

# 下部のスペーサーを作成
spacer_bottom = QtWidgets.QSpacerItem(20, 28, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
menu_frame.addItem(spacer_bottom, 12, 0)


# キーボードリスナーを作成
listener = keyboard.Listener(on_press=on_press)
listener.start()


root.show()
app.exec_()