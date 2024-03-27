import cv2
from ultralytics import YOLO
import wx
from PIL import Image
import logging
import numpy as np
import os
import ctypes
from pynput import keyboard
import win32api
import win32con
from mss import mss


move_mouse = False
mouse_speed = 5
MOUSEEVENTF_MOVE = 0x0001

logging.basicConfig(level=logging.INFO)

model = YOLO(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apex_8s.pt'))

sct = mss()


app = wx.App()
# フレームを作成
frame = wx.Frame(None, -1, 'win.py', style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.STAY_ON_TOP | wx.TRANSPARENT_WINDOW | wx.FRAME_SHAPED)  # フレームスタイルを変更
frame.SetTransparent(0)  # フレームの透明度を最初に0に設定

# ディスプレイの解像度を取得
display_size = wx.DisplaySize()
frame.SetSize(display_size)  # ディスプレイの解像度に合わせてサイズを変更
frame.Show()  # 追加
frame.SetTransparent(50)  # フレームが表示された後に透明度を50に設定

# パネルを作成
panel = wx.Panel(frame, -1, size=display_size)  # パネルのサイズもディスプレイの解像度に合わせる

# 画像を保存するための変数
photo = None

# ALT+M が押されたときの動作を定義
def toggle_mouse_movement(e):
    global move_mouse
    move_mouse = not move_mouse

with keyboard.GlobalHotKeys({
    '<alt>+n': toggle_mouse_movement
}) as h:
    h.join()
def update_frame(event=None):  # event引数をオプションに
    global photo  # グローバル変数として扱う

    # スクリーンショットを取得
    screenshot = sct.grab(sct.monitors[1])
    frame = np.array(screenshot)

    #BGRからRGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    

    # YOLOv8で推論
    results = model(frame)

    frame_height, frame_width = frame.shape[:2]

    bounding_boxes = results[0].boxes.xyxy
    class_ids = results[0].boxes.cls
    class_names_dict = results[0].names

    overlay = np.zeros_like(frame)

    relative_x = relative_y = 0 



    for box, class_id in zip(bounding_boxes, class_ids):
        # Get the class name
        class_name = class_names_dict[int(class_id)]

        x1, y1, x2, y2 = box

        frame_aspect_ratio = frame_width / frame_height
        display_aspect_ratio = display_size[0] / display_size[1]
        
        if display_aspect_ratio > frame_aspect_ratio:
            scale = display_size[1] / frame_height
        else:
            scale = display_size[0] / frame_width
        
        x1 = x1 * scale
        y1 = y1 * scale
        x2 = x2 * scale
        y2 = y2 * scale


        cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)


        class_name = class_names_dict[int(class_id)]

        cv2.putText(overlay, class_name, (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        
        current_mouse_x, current_mouse_y = win32api.GetCursorPos()
        
        relative_x = center_x - current_mouse_x
        relative_y = center_y - current_mouse_y
        
        
        right_click_state = win32api.GetKeyState(win32con.VK_RBUTTON)
        if right_click_state == -127 or right_click_state == -128:  
            right_click_pressed = True
        else:  
            right_click_pressed = False
        
        if move_mouse and right_click_pressed:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, relative_x * mouse_speed, relative_y * mouse_speed, 0, 0)
        

    image = Image.fromarray(overlay)
    image = image.resize(display_size, Image.LANCZOS)

    photo = wx.Bitmap.FromBufferRGBA(image.width, image.height, np.array(image.convert("RGBA")))

    panel.Refresh()  

    wx.CallLater(1, update_frame)

update_frame()

def on_paint(event):
    if photo is not None:
        dc = wx.BufferedPaintDC(panel)  
        dc.DrawBitmap(photo, 0, 0, True)  

# パネルに描画イベントハンドラをバインド
panel.Bind(wx.EVT_PAINT, on_paint)
panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)  

# メインループ
app.MainLoop()
