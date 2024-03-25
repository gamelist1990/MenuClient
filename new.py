import cv2
from ultralytics import YOLO
import wx
from PIL import Image
import logging
import numpy as np
import os

# ロギングの設定
logging.basicConfig(level=logging.INFO)

# YOLOv8モデルのロード
model = YOLO(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'yolov8s.pt'))

# OBS仮想カメラからのストリームを開始
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    logging.error("Could not open video stream")

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

def update_frame(event=None):  # event引数をオプションに
    global photo  # グローバル変数として扱う

    # フレームを読み込む
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to read frame")
        return

    # YOLOv8で推論
    results = model(frame)

    # Get the bounding boxes and labels
    bounding_boxes = results[0].boxes.xyxy
    class_ids = results[0].boxes.cls
    class_names_dict = results[0].names

    # Create a transparent overlay for drawing bounding boxes
    overlay = np.zeros_like(frame)

    # Loop through each bounding box
    for box, class_id in zip(bounding_boxes, class_ids):
        # Get the class name
        class_name = class_names_dict[int(class_id)]

        # If the class name is not 'person', skip this box
        if class_name != 'person':
            continue

        # Extract the coordinates
        x1, y1, x2, y2 = box

        # Draw a green rectangle around the detected object
        cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        # Get the class name
        class_name = class_names_dict[int(class_id)]

        # Put the class name on the bounding box
        cv2.putText(overlay, class_name, (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 画像をリスケール
    image = Image.fromarray(overlay)
    image = image.resize(display_size, Image.LANCZOS)

    photo = wx.Bitmap.FromBufferRGBA(image.width, image.height, np.array(image.convert("RGBA")))

    panel.Refresh()  # パネルを更新

    # 'q'キーが押されたらループを抜ける
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        frame.Close(True)
        return

    # 30ms後に再度update_frameを呼び出す
    wx.CallLater(1, update_frame)

# update_frameを初回呼び出し
update_frame()

def on_paint(event):
    if photo is not None:
        dc = wx.BufferedPaintDC(panel)  # BufferedPaintDCを使用
        dc.DrawBitmap(photo, 0, 0, True)  # ビットマップの描画位置もディスプレイの解像度に合わせる

# パネルに描画イベントハンドラをバインド
panel.Bind(wx.EVT_PAINT, on_paint)
panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)  # ちかちか問題は再描写オフで解決


# メインループ
app.MainLoop()
