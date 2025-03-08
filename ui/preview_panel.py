"""プレビューパネルモジュール"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import pygame

class AudioPreviewPanel(QWidget):
    """音声プレビューパネル"""
    
    playback_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 内部状態
        self.original_audio = None
        self.enhanced_audio = None
        self.sample_rate = 24000
        self.is_playing = False
        self.current_audio = None  # 'original' or 'enhanced'
        
        # オーディオプレーヤー初期化
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=4096)
        except Exception as e:
            print(f"PyGame初期化エラー: {e}")
        
        # UI初期化
        self.init_ui()
        
        # 更新タイマー
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_playback_status)
        self.update_timer.start(100)  # 100msごとに更新
    
    def init_ui(self):
        """UIコンポーネントの初期化"""
        layout = QVBoxLayout(self)
        
        # 再生コントロール
        control_layout = QHBoxLayout()
        
        self.play_button = QPushButton("再生")
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setEnabled(False)
        control_layout.addWidget(self.play_button)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_playback)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        layout.addLayout(control_layout)
        
        # 比較コントロール
        compare_layout = QHBoxLayout()
        
        self.original_button = QPushButton("元の音声")
        self.original_button.clicked.connect(self.play_original)
        self.original_button.setEnabled(False)
        compare_layout.addWidget(self.original_button)
        
        self.enhanced_button = QPushButton("強化された音声")
        self.enhanced_button.clicked.connect(self.play_enhanced)
        self.enhanced_button.setEnabled(False)
        compare_layout.addWidget(self.enhanced_button)
        
        layout.addLayout(compare_layout)
        
        # ステータス表示
        self.status_label = QLabel("準備完了")
        layout.addWidget(self.status_label)
    
    def set_audio_data(self, original_data, enhanced_data, sample_rate):
        """音声データの設定"""
        self.original_audio = original_data
        self.enhanced_audio = enhanced_data
        self.sample_rate = sample_rate
        
        # UIを有効化
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.original_button.setEnabled(True)
        self.enhanced_button.setEnabled(True)
        
        # デフォルトで強化音声を選択
        self.current_audio = 'enhanced'
        
        self.status_label.setText("音声データを読み込みました")
    
    def toggle_playback(self):
        """再生/一時停止の切り替え"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_button.setText("再生")
            self.is_playing = False
            self.status_label.setText("一時停止")
        else:
            self.play_current_audio()
    
    def play_current_audio(self):
        """現在選択されている音声を再生"""
        import soundfile as sf
        import tempfile
        import os
        
        try:
            # 再生する音声データを選択
            audio_data = None
            if self.current_audio == 'original' and self.original_audio is not None:
                audio_data = self.original_audio
                status_text = "元の音声を再生中"
            elif self.current_audio == 'enhanced' and self.enhanced_audio is not None:
                audio_data = self.enhanced_audio
                status_text = "強化された音声を再生中"
            else:
                return
            
            # 一時ファイルに保存して再生
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            sf.write(temp_path, audio_data, self.sample_rate)
            
            # 再生
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            self.play_button.setText("一時停止")
            self.is_playing = True
            self.status_label.setText(status_text)
            
        except Exception as e:
            self.status_label.setText(f"再生エラー: {str(e)}")
    
    def stop_playback(self):
        """再生の停止"""
        pygame.mixer.music.stop()
        self.play_button.setText("再生")
        self.is_playing = False
        self.status_label.setText("停止")
    
    def play_original(self):
        """元の音声を再生"""
        self.stop_playback()
        self.current_audio = 'original'
        self.status_label.setText("元の音声を選択しました")
        self.play_current_audio()
    
    def play_enhanced(self):
        """強化された音声を再生"""
        self.stop_playback()
        self.current_audio = 'enhanced'
        self.status_label.setText("強化された音声を選択しました")
        self.play_current_audio()
    
    def update_playback_status(self):
        """再生状態の更新（タイマーで定期的に呼び出される）"""
        if self.is_playing and not pygame.mixer.music.get_busy():
            # 再生が終了した場合
            self.is_playing = False
            self.play_button.setText("再生")
            self.status_label.setText("再生完了")
            self.playback_finished.emit()