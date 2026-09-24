import cv2
import collections
import argparse

def main():

    CAM_WIDTH = 640
    CAM_HEIGHT = 480

    # 引数解析
    parser = argparse.ArgumentParser(description='Delay Camera')

    parser.add_argument('-d', '--dispsize', type=float, default=1.0, help="Display size ratio. default = (1.0 * 640, 1.0 * 480)")

    args = parser.parse_args()

    # カメラの初期化（デバイスID: 0）
    cap = cv2.VideoCapture(0)
    
    # 指定の解像度に設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    
    # カメラの実際のFPSを取得（取得不可のデバイスの場合は30と仮定）
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
        
    # 遅延設定（初期値は5秒に設定）
    delay_sec = 5
    max_delay_sec = 30
    min_delay_sec = 1

    # いろいろな設定
    flip_en = True # 左右反転
    disp_width = int(CAM_WIDTH * args.dispsize)    # 表示サイズ
    disp_height = int(CAM_HEIGHT * args.dispsize)  # 表示サイズ
    
    
    # 30秒分のフレームを保持できるキューを作成
    max_frames = int(max_delay_sec * fps)
    frame_buffer = collections.deque(maxlen=max_frames)
    
    # 小窓（Picture in Picture）の縮小率
    pip_scale = 0.25

    window_name = "Delay Camera System"
#    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO) # ドラッグでリサイズ可能, 縦横比は固定
    
    print(f"システム稼働開始。カメラFPS: {fps}")
    

    while True:
        ret, frame = cap.read()
        if not ret:
            print("エラー：カメラからフレームを取得できない。")
            break
            
        # 最新のフレームをバッファに追加（最大数を超えると古いものから破棄される）
        frame_buffer.append(frame)
        
        # 現在設定されている遅延秒数に必要なフレーム数
        target_delay_frames = int(delay_sec * fps)
        
        # バッファが指定の遅延時間に満たない場合は、一番古いフレームを表示
        if len(frame_buffer) < target_delay_frames:
            display_frame = frame_buffer[0].copy()
        else:
            # 指定フレーム数前の映像を取得
            display_frame = frame_buffer[-target_delay_frames].copy()

        # 必要なら左右反転
        if(flip_en): 
            display_frame = cv2.flip(display_frame, 1)
        
            
        # 小窓（現在のリアルタイム映像）の生成
        h, w = frame.shape[:2]
        pip_w = int(w * pip_scale)
        pip_h = int(h * pip_scale)
        pip_frame = cv2.resize(frame, (pip_w, pip_h))
        pip_frame = cv2.flip(pip_frame, 1) # 左右反転(鏡写し)
        
        # 小窓を画面右下に配置
        display_frame[h - pip_h:h, w - pip_w:w] = pip_frame

        # 表示サイズの変更
        display_frame = cv2.resize(display_frame, (disp_width, disp_height))
        
        # UI情報の描画
        ui_text_delay = f"Delay: {delay_sec} sec"
        ui_text_keys = "Keys: 'w'=+1s, 's'=-1s, 'f'=flip, 'q'=quit"
        
        # テキストの背景に黒い帯を入れると視認性が上がるが、今回はシンプルに描画
        cv2.putText(display_frame, ui_text_delay, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_frame, ui_text_keys, (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow(window_name, display_frame)
        
        # キー入力処理 (1ミリ秒待機)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('w'):
            delay_sec = min(delay_sec + 1, max_delay_sec)
        elif key == ord('s'):
            delay_sec = max(delay_sec - 1, min_delay_sec)
        elif key == ord('f'):
            flip_en = not flip_en
            
    # リソースの解放
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()