"""プレビューパネルモジュール - メモリ内音声再生の実装"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QSlider, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QByteArray, QBuffer, QIODevice, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import numpy as np
import io
import tempfile
import os
import soundfile as sf
import wave

class AudioPreviewPanel(QWidget):
    """音声プレビューパネル - QMediaPlayerを使用した実装"""
    
    playbackFinished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 内部状態の初期化
        self.is_playing = False
        self.audio_length = 0  # 秒単位
        self.current_position = 0  # ミリ秒単位
        
        # 音声データ
        self.original_audio = None
        self.enhanced_audio = None
        self.sample_rate = 24000
        
        # メディアプレーヤーの初期化
        self.player = QMediaPlayer()
        self.player.positionChanged.connect(self.update_position)
        self.player.stateChanged.connect(self.handle_state_change)
        self.player.mediaStatusChanged.connect(self.handle_media_status_change)
        
        # 現在再生中のタイプ
        self.current_type = "enhanced"  # "original" または "enhanced"
        
        # UI初期化
        self.initUI()
    
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
        
        # 音声比較コントロール
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
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
    
    def set_audio_data(self, original_data, enhanced_data, sample_rate):
        """音声データの設定"""
        try:
            # 既存の再生を停止
            self.stop_playback()
            
            # データを格納
            self.original_audio = original_data
            self.enhanced_audio = enhanced_data
            self.sample_rate = sample_rate
            
            # 音声の長さを計算
            self.audio_length = len(original_data) / sample_rate * 1000  # ミリ秒単位
            
            # UIを有効化
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.position_slider.setEnabled(True)
            self.original_button.setEnabled(True)
            self.enhanced_button.setEnabled(True)
            
            # デフォルトで強化音声を選択
            self.current_type = "enhanced"
            
            # 時間表示を更新
            mins = int(self.audio_length / 1000) // 60
            secs = int(self.audio_length / 1000) % 60
            self.time_label.setText(f"00:00 / {mins:02d}:{secs:02d}")
            
            self.status_label.setText("音声データを読み込みました")
            
        except Exception as e:
            self.status_label.setText(f"エラー: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def prepare_media(self):
        """現在選択されている音声データをメディアに変換"""
        try:
            # 使用するデータを選択
            audio_data = None
            if self.current_type == "original" and self.original_audio is not None:
                audio_data = self.original_audio
            elif self.current_type == "enhanced" and self.enhanced_audio is not None:
                audio_data = self.enhanced_audio
            else:
                return False
            
            # 一時ファイルを作成
            temp_path = self._create_temp_wav(audio_data, self.sample_rate)
            if not temp_path:
                return False
            
            # メディアコンテンツを設定
            media_content = QMediaContent(QUrl.fromLocalFile(temp_path))
            self.player.setMedia(media_content)
            
            return True
        except Exception as e:
            self.status_label.setText(f"メディア準備エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_temp_wav(self, audio_data, sample_rate):
        """一時WAVファイルを作成"""
        try:
            # カレントディレクトリ内のtempディレクトリ
            temp_dir = "./temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # 既存のファイルをすべて削除
            for file_name in os.listdir(temp_dir):
                if file_name.endswith(".wav"):
                    try:
                        os.remove(os.path.join(temp_dir, file_name))
                    except:
                        pass
            
            # 新しいファイル名
            temp_path = os.path.join(temp_dir, f"audio_{self.current_type}.wav")
            
            # WAVファイルとして保存
            sf.write(temp_path, audio_data, sample_rate)
            
            return temp_path
        except Exception as e:
            self.status_label.setText(f"一時ファイル作成エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def toggle_playback(self):
        """再生/一時停止の切り替え"""
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_button.setText("再生")
            self.is_playing = False
            self.status_label.setText("一時停止中")
        else:
            if self.player.mediaStatus() == QMediaPlayer.NoMedia:
                # メディアが設定されていない場合は準備
                if not self.prepare_media():
                    return
            
            self.player.play()
            self.play_button.setText("一時停止")
            self.is_playing = True
            
            if self.current_type == "original":
                self.status_label.setText("元の音声を再生中")
            else:
                self.status_label.setText("強化された音声を再生中")
    
    def stop_playback(self):
        """再生の停止"""
        self.player.stop()
        self.play_button.setText("再生")
        self.is_playing = False
        self.current_position = 0
        self.position_slider.setValue(0)
        self.progress_bar.setValue(0)
        self.update_time_display()
        self.status_label.setText("停止しました")
    
    def play_original(self):
        """元の音声を再生"""
        if self.original_audio is None:
            return
        
        self.stop_playback()
        self.current_type = "original"
        self.status_label.setText("元の音声を選択しました")
        
        # メディアを準備して再生
        if self.prepare_media():
            self.toggle_playback()
    
    def play_enhanced(self):
        """強化された音声を再生"""
        if self.enhanced_audio is None:
            return
        
        self.stop_playback()
        self.current_type = "enhanced"
        self.status_label.setText("強化された音声を選択しました")
        
        # メディアを準備して再生
        if self.prepare_media():
            self.toggle_playback()
    
    def seek_position(self):
        """スライダーから再生位置を設定"""
        if not self.player.isSeekable():
            return
        
        # スライダー値から再生位置を計算（ミリ秒）
        position_percent = self.position_slider.value() / self.position_slider.maximum()
        target_pos = int(position_percent * self.audio_length)
        
        # 再生位置を設定
        self.player.setPosition(target_pos)
    
    def update_position(self, position):
        """再生位置の更新（ミリ秒単位）"""
        self.current_position = position
        
        # スライダー位置を更新
        if self.audio_length > 0:
            slider_value = int((position / self.audio_length) * self.position_slider.maximum())
            self.position_slider.setValue(slider_value)
            
            # プログレスバーを更新
            progress_value = int((position / self.audio_length) * 100)
            self.progress_bar.setValue(progress_value)
        
        # 時間表示の更新
        self.update_time_display()
    
    def handle_state_change(self, state):
        """プレーヤーの状態変更処理"""
        if state == QMediaPlayer.StoppedState:
            self.play_button.setText("再生")
            self.is_playing = False
            self.current_position = 0
            self.position_slider.setValue(0)
            self.progress_bar.setValue(0)
            self.update_time_display()
    
    def handle_media_status_change(self, status):
        """メディアのステータス変更処理"""
        if status == QMediaPlayer.EndOfMedia:
            self.playbackFinished.emit()
            self.status_label.setText("再生完了")
    
    def update_time_display(self):
        """時間表示の更新"""
        current_mins = int(self.current_position / 1000) // 60
        current_secs = int(self.current_position / 1000) % 60
        
        total_mins = int(self.audio_length / 1000) // 60
        total_secs = int(self.audio_length / 1000) % 60
        
        self.time_label.setText(f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            # プレーヤーを停止して解放
            self.player.stop()
            self.player.setMedia(QMediaContent())
            
            # 一時ファイルを削除
            temp_dir = "./temp"
            if os.path.exists(temp_dir):
                for file_name in os.listdir(temp_dir):
                    if file_name.endswith(".wav"):
                        try:
                            os.remove(os.path.join(temp_dir, file_name))
                        except:
                            pass
        except Exception as e:
            print(f"クリーンアップエラー: {e}")
    
    def closeEvent(self, event):
        """ウィジェットが閉じられるときの処理"""
        self.cleanup()
        super().closeEvent(event)