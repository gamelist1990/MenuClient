import cv2
from ultralytics import YOLO
import wx
from PIL import Image
import logging
import numpy as np
import os
import ctypes
import keyboard
import win32api
import win32con
import dxcam


#エイムボットの検知範囲
aimbot_range = 150
#エイムボットの有効か？
move_mouse = False
#敵にエイムが吸い付く精度1~5がおすすめ
mouse_speed = 1
# 適切な値武器によって変わる 99は30 まぁ基本30で良いただ精度がmouse_speed = X と同期しているので2とかにしないと効果わからないかも
anti_recoil_value = 30




MOUSEEVENTF_MOVE = 0x0001

logging.basicConfig(level=logging.INFO)

model = YOLO(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apex_8s.pt'))

camera = dxcam.create()
app = wx.App()
frame = wx.Frame(None, -1, 'win.py', style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.STAY_ON_TOP | wx.TRANSPARENT_WINDOW | wx.FRAME_SHAPED)
frame.SetTransparent(0)

display_size = wx.DisplaySize()
frame.SetSize(display_size)
frame.Show()
frame.SetTransparent(50)

panel = wx.Panel(frame, -1, size=display_size)

photo = None

def toggle_mouse_movement(e):
    global move_mouse
    move_mouse = not move_mouse

keyboard.on_press_key('.', toggle_mouse_movement, suppress=True)


def update_frame(event=None):
    global photo
    frame = camera.grab()
    if frame is None:
        update_frame()

    frame = np.array(frame)

    if frame.dtype != np.uint8:
        update_frame()

    if frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        print("Frame is None, cannot convert color space")

    results = model(frame)

    frame_height, frame_width = frame.shape[:2]

    bounding_boxes = results[0].boxes.xyxy
    class_ids = results[0].boxes.cls
    class_names_dict = results[0].names
    scores = results[0].boxes.conf

    overlay = np.zeros_like(frame)

    relative_x = relative_y = 0

    min_distance = float('inf')
    closest_box_center = None

    distance = float('inf')

    for box, class_id, score in zip(bounding_boxes, class_ids, scores):
        if score <= 0.5:
            continue
    
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
    
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
    
        current_mouse_x, current_mouse_y = win32api.GetCursorPos()
    
        distance = np.sqrt((center_x - current_mouse_x)**2 + (center_y - current_mouse_y)**2)
    
        if distance <= aimbot_range:
            color = (0, 255, 0)  # Green for boxes within the aimbot range
        else:
            color = (255,0,0)  # Red for boxes outside the aimbot range
    
        cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    
        cv2.putText(overlay, class_name, (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
        if distance < min_distance and color == (0, 255, 0):  # Only consider boxes within the aimbot range
            min_distance = distance
            closest_box_center = (center_x, center_y)


    
    if closest_box_center is not None:
        relative_x = closest_box_center[0] - current_mouse_x
        relative_y = closest_box_center[1] - current_mouse_y


    # マウスの左クリックと右クリックのキーコード
    VK_LBUTTON = win32con.VK_LBUTTON
    VK_RBUTTON = win32con.VK_RBUTTON

    left_click_state = win32api.GetKeyState(VK_LBUTTON)
    right_click_state = win32api.GetKeyState(VK_RBUTTON)


    if left_click_state == -127 or left_click_state == -128:
        left_click_state = True
    else:
        left_click_state = False
    
    if right_click_state == -127 or right_click_state == -128:
        right_click_pressed = True
    else:
        right_click_pressed = False

    


    if move_mouse and right_click_pressed:
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_MOVE, relative_x * mouse_speed, relative_y * mouse_speed, 0, 0)
    if move_mouse and right_click_pressed and left_click_state:
        # アンチリコイルの調整値を追加
        relative_y += anti_recoil_value
        ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_MOVE, relative_x * mouse_speed, relative_y * mouse_speed, 0, 0)



    image = Image.fromarray(overlay)
    image = image.resize(display_size, Image.LANCZOS)

    photo = wx.Bitmap.FromBufferRGBA(image.width, image.height, np.array(image.convert("RGBA")))

    panel.Refresh()

    wx.CallLater(0, update_frame)

update_frame()


def on_paint(event):
    if photo is not None:
        dc = wx.BufferedPaintDC(panel)
        dc.DrawBitmap(photo, 0, 0, True)

panel.Bind(wx.EVT_PAINT, on_paint)
panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)

app.MainLoop()
