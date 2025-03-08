"""
VOICEVOX Enhancer - 音声合成の品質向上ツール
メインアプリケーションモジュール
"""

import sys
import traceback
import os

# Pythonクラッシュ時のスタックトレース表示
sys.excepthook = traceback.print_exception

# 必要なライブラリのインポート
try:
    from PyQt5.QtWidgets import QApplication
    import pygame
except ImportError as e:
    print(f"必要なライブラリが見つかりません: {e}")
    print("以下のコマンドを実行してください:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# 自作モジュールのインポート
from voicevox.connector import VoicevoxConnector
from audio.processor import AudioProcessor
from gui.main_window import MainWindow

def main():
    """メイン関数"""
    # 必要なディレクトリの作成
    os.makedirs("output", exist_ok=True)
    
    # PyGameの初期化（音声再生用）
    pygame.init()
    
    # アプリケーションの初期化
    app = QApplication(sys.argv)
    
    # アプリケーションスタイルの設定
    app.setStyle("Fusion")
    
    # 依存オブジェクトの作成
    voicevox = VoicevoxConnector()
    processor = AudioProcessor()
    
    # メインウィンドウの表示
    window = MainWindow(voicevox, processor)
    window.show()
    
    # イベントループの開始
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()