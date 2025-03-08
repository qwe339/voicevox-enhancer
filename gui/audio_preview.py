# gui/audio_preview.py

import os
import tempfile
import threading
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSlider, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import pygame
import soundfile as sf
import numpy as np

class AudioPreviewPanel(QWidget):
    """音声プレビューパネル - PyGameを使用した実装"""
    
    playbackFinished = pyqtSignal()
    positionChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # PyGameの初期化
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
        # 内部状態
        self.is_playing = False
        self.audio_length = 0  # 秒単位
        self.current_position = 0  # 秒単位
        self.temp_dir = tempfile.mkdtemp()
        self.original_file = os.path.join(self.temp_dir, "original.wav")
        self.enhanced_file = os.path.join(self.temp_dir, "enhanced.wav")
        self.current_file = None
        
        # UI初期化
        self.initUI()
        
        # 更新タイマー
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_playback_status)
        self.update_timer.start(100)  # 100msごとに更新
    
    def initUI(self):
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
        
        self.time_label = QLabel("00:00 / 00:00")
        control_layout.addWidget(self.time_label)
        
        layout.addLayout(control_layout)
        
        # 再生位置スライダー
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.setValue(0)
        self.position_slider.sliderReleased.connect(self.seek_position)
        self.position_slider.setEnabled(False)
        layout.addWidget(self.position_slider)
        
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
        try:
            # 一時ファイルに書き出し
            sf.write(self.original_file, original_data, sample_rate)
            sf.write(self.enhanced_file, enhanced_data, sample_rate)
            
            # 音声の長さを計算
            self.audio_length = len(original_data) / sample_rate
            
            # UIを有効化
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.position_slider.setEnabled(True)
            self.original_button.setEnabled(True)
            self.enhanced_button.setEnabled(True)
            
            # デフォルトで強化音声を選択
            self.current_file = self.enhanced_file
            
            # スライダーの最大値を設定
            self.position_slider.setRange(0, int(self.audio_length * 10))
            
            # 時間表示を更新
            mins = int(self.audio_length) // 60
            secs = int(self.audio_length) % 60
            self.time_label.setText(f"00:00 / {mins:02d}:{secs:02d}")
            
            self.status_label.setText("音声データを読み込みました")
            
        except Exception as e:
            self.status_label.setText(f"エラー: {str(e)}")
    
    def toggle_playback(self):
        """再生/一時停止の切り替え"""
        if not self.current_file:
            return
        
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_button.setText("再生")
            self.is_playing = False
        else:
            # 途中から再開する場合
            if pygame.mixer.music.get_busy() and pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
            else:
                # 新規再生
                try:
                    pygame.mixer.music.load(self.current_file)
                    pygame.mixer.music.play()
                except Exception as e:
                    self.status_label.setText(f"再生エラー: {str(e)}")
                    return
            
            self.play_button.setText("一時停止")
            self.is_playing = True
    
    def stop_playback(self):
        """再生の停止"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        self.play_button.setText("再生")
        self.is_playing = False
        self.current_position = 0
        self.position_slider.setValue(0)
        self.update_time_display()
    
    def play_original(self):
        """元の音声を再生"""
        self.stop_playback()
        self.current_file = self.original_file
        self.status_label.setText("元の音声を選択しました")
        self.toggle_playback()
    
    def play_enhanced(self):
        """強化された音声を再生"""
        self.stop_playback()
        self.current_file = self.enhanced_file
        self.status_label.setText("強化された音声を選択しました")
        self.toggle_playback()
    
    def seek_position(self):
        """スライダーから再生位置を設定"""
        if not self.current_file or not pygame.mixer.music.get_busy():
            return
        
        # スライダー値から再生位置を計算（秒）
        position_percent = self.position_slider.value() / self.position_slider.maximum()
        target_pos = position_percent * self.audio_length
        
        # 一度停止して新しい位置から再生
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.current_file)
        pygame.mixer.music.play(start=target_pos)
        
        self.is_playing = True
        self.play_button.setText("一時停止")
    
    def update_playback_status(self):
        """再生状態の更新（タイマーで定期的に呼び出される）"""
        if self.is_playing and pygame.mixer.music.get_busy():
            # 再生位置を更新（ミリ秒から秒に変換）
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms > 0:
                self.current_position = pos_ms / 1000.0
                
                # スライダー位置を更新
                slider_value = int((self.current_position / self.audio_length) * self.position_slider.maximum())
                self.position_slider.setValue(slider_value)
                
                # 時間表示の更新
                self.update_time_display()
        elif self.is_playing and not pygame.mixer.music.get_busy():
            # 再生が終了した場合
            self.is_playing = False
            self.play_button.setText("再生")
            self.current_position = 0
            self.position_slider.setValue(0)
            self.update_time_display()
            self.playbackFinished.emit()
    
    def update_time_display(self):
        """時間表示の更新"""
        current_mins = int(self.current_position) // 60
        current_secs = int(self.current_position) % 60
        
        total_mins = int(self.audio_length) // 60
        total_secs = int(self.audio_length) % 60
        
        self.time_label.setText(f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            pygame.mixer.quit()
            
            # 一時ファイルの削除
            if os.path.exists(self.original_file):
                os.remove(self.original_file)
            if os.path.exists(self.enhanced_file):
                os.remove(self.enhanced_file)
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def closeEvent(self, event):
        """ウィジェットが閉じられるときの処理"""
        self.cleanup()
        super().closeEvent(event)