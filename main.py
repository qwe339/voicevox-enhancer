"""
VOICEVOX Enhancer - 音声合成の品質向上ツール
メインアプリケーションモジュール

このプログラムは、VOICEVOXが生成した音声を処理し、
より自然でリアルな音質に変換するためのツールです。
"""

import sys
import os
import traceback
import platform
import tempfile
import numpy as np
from datetime import datetime

# PyQt5インポート
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel, 
                            QTextEdit, QFileDialog, QTabWidget, QMessageBox, 
                            QProgressDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

# 音声処理関連のインポート
try:
   import soundfile as sf
   import librosa
   import scipy.signal as signal
   import pygame
except ImportError as e:
   print(f"必要なライブラリが見つかりません: {e}")
   print("以下のコマンドを実行してください:")
   print("pip install soundfile librosa scipy pygame")
   sys.exit(1)


class VOICEVOXConnector:
   """VOICEVOX音声合成エンジンとの連携クラス"""
   
   def __init__(self, host="127.0.0.1", port=50021):
       """
       VOICEVOX APIへの接続を初期化します
       
       Parameters:
           host (str): VOICEVOXエンジンのホスト
           port (int): VOICEVOXエンジンのポート
       """
       self.base_url = f"http://{host}:{port}"
       
       # requestsライブラリのインポート
       try:
           import requests
           import json
           self.requests = requests
           self.json = json
       except ImportError:
           print("requestsライブラリがインストールされていません")
           print("pip install requests を実行してください")
           sys.exit(1)
   
   def get_speakers(self):
       """利用可能な話者の一覧を取得"""
       try:
           response = self.requests.get(f"{self.base_url}/speakers")
           if response.status_code == 200:
               return response.json()
           else:
               print(f"話者一覧の取得に失敗しました: {response.status_code}")
               return []
       except Exception as e:
           print(f"VOICEVOX接続エラー: {e}")
           return []
   
   def text_to_speech(self, text, speaker_id=1):
       """
       テキストから音声を合成
       
       Parameters:
           text (str): 合成するテキスト
           speaker_id (int): 話者ID
           
       Returns:
           tuple: (音声データ, サンプルレート)
       """
       try:
           # 音声合成用のクエリを作成
           params = {"text": text, "speaker": speaker_id}
           response = self.requests.post(
               f"{self.base_url}/audio_query",
               params=params
           )
           
           if response.status_code != 200:
               raise Exception(f"音声クエリの作成に失敗しました: {response.status_code}")
           
           query = response.json()
           
           # 音声を合成
           params = {"speaker": speaker_id}
           response = self.requests.post(
               f"{self.base_url}/synthesis",
               headers={"Content-Type": "application/json"},
               params=params,
               data=self.json.dumps(query)
           )
           
           if response.status_code != 200:
               raise Exception(f"音声合成に失敗しました: {response.status_code}")
           
           # バイナリデータをnumpy配列に変換
           audio_data, sample_rate = sf.read(response.content)
           
           return audio_data, sample_rate
           
       except Exception as e:
           print(f"音声合成エラー: {e}")
           # デモ用の空の音声データを返す
           return np.zeros(1000), 24000


class AudioProcessor:
   """音声処理の中核エンジン"""
   
   def __init__(self, sample_rate=24000):
       """
       音声処理エンジンを初期化
       
       Parameters:
           sample_rate (int): デフォルトのサンプルレート
       """
       self.sample_rate = sample_rate
   
   def process(self, audio_data, enhancement_level=0.5):
       """
       音声データの基本的な処理
       
       Parameters:
           audio_data (numpy.ndarray): 入力音声データ
           enhancement_level (float): 強化レベル (0.0～1.0)
           
       Returns:
           numpy.ndarray: 処理された音声データ
       """
       # 音声データが空の場合は何もしない
       if len(audio_data) == 0:
           return audio_data
       
       try:
           # スペクトル解析
           stft = librosa.stft(audio_data)
           magnitude, phase = librosa.magphase(stft)
           
           # 高周波数帯域の強調（声の透明感を増加）
           freq_enhance = np.linspace(1.0, 1.0 + enhancement_level, num=magnitude.shape[0])
           enhanced_magnitude = magnitude * freq_enhance[:, np.newaxis]
           
           # スペクトル補正から音声を再構成
           enhanced_stft = enhanced_magnitude * phase
           enhanced_audio = librosa.istft(enhanced_stft, length=len(audio_data))
           
           # 音量の正規化
           if np.max(np.abs(enhanced_audio)) > 0:
               enhanced_audio = enhanced_audio / np.max(np.abs(enhanced_audio)) * 0.9
           
           return enhanced_audio
       
       except Exception as e:
           print(f"音声処理エラー: {e}")
           return audio_data
   
   def add_natural_fluctuation(self, audio_data, fluctuation_rate=0.02):
       """
       自然な揺らぎを音声に追加
       
       Parameters:
           audio_data (numpy.ndarray): 入力音声データ
           fluctuation_rate (float): 揺らぎの強さ
           
       Returns:
           numpy.ndarray: 処理された音声データ
       """
       try:
           # 微小なランダム変動を生成
           fluctuation = np.random.normal(1.0, fluctuation_rate, size=len(audio_data))
           
           # 急激な変化を防ぐためのスムージング
           window_size = min(128, len(audio_data) // 10)
           if window_size < 2:
               window_size = 2
               
           smoothed_fluctuation = np.convolve(
               fluctuation, 
               np.ones(window_size) / window_size, 
               mode='same'
           )
           
           # 揺らぎを適用
           natural_audio = audio_data * smoothed_fluctuation
           
           # 音量の正規化
           if np.max(np.abs(natural_audio)) > 0:
               natural_audio = natural_audio / np.max(np.abs(natural_audio)) * 0.9
           
           return natural_audio
           
       except Exception as e:
           print(f"自然揺らぎ処理エラー: {e}")
           return audio_data
   
   def enhance_voice_quality(self, audio_data, sample_rate, voice_enhancement=0.5):
       """
       声質向上処理
       
       Parameters:
           audio_data (numpy.ndarray): 入力音声データ
           sample_rate (int): サンプルレート
           voice_enhancement (float): 声質向上レベル (0.0～1.0)
           
       Returns:
           numpy.ndarray: 処理された音声データ
       """
       try:
           # 母音のフォルマント周波数を強調
           formant_freqs = {
               'a': [800, 1200],
               'i': [300, 2500],
               'u': [300, 900],
               'e': [500, 1800],
               'o': [500, 1000]
           }
           
           enhanced_audio = np.copy(audio_data)
           
           for vowel, freqs in formant_freqs.items():
               for freq in freqs:
                   # バンドパスフィルタの作成
                   freq_min = max(freq - 50, 20)
                   freq_max = min(freq + 50, sample_rate // 2 - 1)
                   
                   b, a = signal.butter(
                       2, 
                       [freq_min, freq_max],
                       btype='band',
                       fs=sample_rate
                   )
                   
                   # フィルタ適用
                   filtered = signal.lfilter(b, a, audio_data)
                   enhanced_audio += filtered * (voice_enhancement * 0.2)
           
           # 音量の正規化
           if np.max(np.abs(enhanced_audio)) > 0:
               enhanced_audio = enhanced_audio / np.max(np.abs(enhanced_audio)) * 0.9
           
           return enhanced_audio
           
       except Exception as e:
           print(f"声質向上処理エラー: {e}")
           return audio_data
   
   def save_audio(self, audio_data, file_path, sample_rate=None):
       """
       音声ファイルの保存
       
       Parameters:
           audio_data (numpy.ndarray): 音声データ
           file_path (str): 保存先ファイルパス
           sample_rate (int, optional): サンプルレート（指定なしの場合はデフォルト値）
       """
       if sample_rate is None:
           sample_rate = self.sample_rate
           
       try:
           # 保存先ディレクトリがなければ作成
           directory = os.path.dirname(file_path)
           if directory and not os.path.exists(directory):
               os.makedirs(directory)
               
           # 音声ファイルの保存
           sf.write(file_path, audio_data, sample_rate)
           print(f"音声を保存しました: {file_path}")
           
       except Exception as e:
           print(f"音声保存エラー: {e}")
           raise


class AudioPreviewPanel(QWidget):
   """音声プレビューパネル - PyGameを使用した実装"""
   
   playbackFinished = pyqtSignal()
   positionChanged = pyqtSignal(int)
   
   def __init__(self, parent=None):
       super().__init__(parent)
       
       # PyGameの初期化
       try:
           pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
       except Exception as e:
           print(f"PyGame初期化エラー: {e}")
       
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


class AdvancedSettingsPanel(QWidget):
   """詳細設定パネル"""
   
   settingsChanged = pyqtSignal(dict)
   
   def __init__(self, parent=None):
       super().__init__(parent)
       self.initUI()
   
   def initUI(self):
       """UIコンポーネントの初期化"""
       layout = QVBoxLayout(self)
       
       # 音質設定
       sound_quality_group = QVBoxLayout()
       layout.addWidget(QLabel("<b>音質設定</b>"))
       
       # 高周波強調
       layout.addWidget(QLabel("高周波強調:"))
       self.high_freq_slider = QSlider(Qt.Horizontal)
       self.high_freq_slider.setRange(0, 100)
       self.high_freq_slider.setValue(50)
       layout.addWidget(self.high_freq_slider)
       
       # 声質調整
       layout.addWidget(QLabel("声質調整:"))
       self.voice_quality_slider = QSlider(Qt.Horizontal)
       self.voice_quality_slider.setRange(0, 100)
       self.voice_quality_slider.setValue(50)
       layout.addWidget(self.voice_quality_slider)
       
       # 自然揺らぎ
       layout.addWidget(QLabel("自然揺らぎ:"))
       self.fluctuation_slider = QSlider(Qt.Horizontal)
       self.fluctuation_slider.setRange(0, 100)
       self.fluctuation_slider.setValue(30)
       layout.addWidget(self.fluctuation_slider)
       
       # 適用ボタン
       self.apply_button = QPushButton("設定を適用")
       self.apply_button.clicked.connect(self.apply_settings)
       layout.addWidget(self.apply_button)
       
       # スペーサー
       layout.addStretch()
   
   def apply_settings(self):
       """現在の設定を適用"""
       settings = {
           "high_freq": self.high_freq_slider.value() / 100.0,
           "voice_quality": self.voice_quality_slider.value() / 100.0,
           "fluctuation": self.fluctuation_slider.value() / 100.0
       }
       
       self.settingsChanged.emit(settings)


class MainWindow(QMainWindow):
   """メインウィンドウ"""
   
   def __init__(self):
       super().__init__()
       
       # ウィンドウ設定
       self.setWindowTitle("VOICEVOX Enhancer")
       self.setGeometry(100, 100, 800, 600)
       
       # 内部状態
       self.original_audio = None
       self.enhanced_audio = None
       self.sample_rate = 24000
       self.current_settings = {}
       
       # UI初期化
       self.initUI()
       
       # コンポーネント初期化
       self.voicevox = VOICEVOXConnector()
       self.processor = AudioProcessor()
       
       # 利用可能な話者の取得
       self.loadSpeakers()
   
   def initUI(self):
       """UIコンポーネントの初期化"""
       # 中央ウィジェット
       central_widget = QWidget()
       self.setCentralWidget(central_widget)
       
       # メインレイアウト（左右分割）
       main_layout = QHBoxLayout(central_widget)
       
       # 左側：入力と基本コントロール
       left_panel = QWidget()
       left_layout = QVBoxLayout(left_panel)
       
       # テキスト入力
       left_layout.addWidget(QLabel("入力テキスト:"))
       self.text_input = QTextEdit()
       self.text_input.setPlaceholderText("ここにテキストを入力してください")
       left_layout.addWidget(self.text_input)
       
       # 話者選択
       left_layout.addWidget(QLabel("VOICEVOX話者ID:"))
       speaker_layout = QHBoxLayout()
       
       self.speaker_slider = QSlider(Qt.Horizontal)
       self.speaker_slider.setRange(1, 10)
       self.speaker_slider.setValue(1)
       self.speaker_slider.valueChanged.connect(self.update_speaker_label)
       speaker_layout.addWidget(self.speaker_slider)
       
       self.speaker_label = QLabel("1: ずんだもん（ノーマル）")
       speaker_layout.addWidget(self.speaker_label)
       
       left_layout.addLayout(speaker_layout)
       
       # 音声リアル化レベル
       left_layout.addWidget(QLabel("音声リアル化レベル:"))
       enhance_layout = QHBoxLayout()
       
       self.enhance_slider = QSlider(Qt.Horizontal)
       self.enhance_slider.setRange(0, 100)
       self.enhance_slider.setValue(50)
       enhance_layout.addWidget(self.enhance_slider)
       
       self.enhance_label = QLabel("50%")
       self.enhance_slider.valueChanged.connect(
           lambda v: self.enhance_label.setText(f"{v}%")
       )
       enhance_layout.addWidget(self.enhance_label)
       
       left_layout.addLayout(enhance_layout)
       
       # 処理ボタン
       self.process_button = QPushButton("音声合成と強化")
       self.process_button.clicked.connect(self.process_audio)
       left_layout.addWidget(self.process_button)
       
       # 保存ボタン
       self.save_button = QPushButton("音声を保存")
       self.save_button.clicked.connect(self.save_audio)
       self.save_button.setEnabled(False)
       left_layout.addWidget(self.save_button)
       
       # バッチ処理ボタン
       self.batch_button = QPushButton("バッチ処理")
       self.batch_button.clicked.connect(self.batch_process)
       left_layout.addWidget(self.batch_button)
       
       # ステータス
       self.status_label = QLabel("準備完了")
       left_layout.addWidget(self.status_label)
       
       # 右側：タブ付きコントロール
       right_panel = QTabWidget()
       
       # プレビュータブ
       self.preview_panel = AudioPreviewPanel()
       right_panel.addTab(self.preview_panel, "プレビュー")
       
       # 詳細設定タブ
       self.settings_panel = AdvancedSettingsPanel()
       self.settings_panel.settingsChanged.connect(self.update_settings)
       right_panel.addTab(self.settings_panel, "詳細設定")
       
       # レイアウトに追加
       main_layout.addWidget(left_panel, 1)
       main_layout.addWidget(right_panel, 1)
   
   def loadSpeakers(self):
       """VOICEVOXの話者一覧を取得"""
       try:
           speakers = self.voicevox.get_speakers()
           if speakers:
               # 話者の最大数に基づいてスライダーの範囲を設定
               max_id = 0
               self.speaker_names = {}
               
               for speaker in speakers:
                   for style in speaker["styles"]:
                       self.speaker_names[style["id"]] = f"{speaker['name']}（{style['name']}）"
                       max_id = max(max_id, style["id"])
               
               self.speaker_slider.setRange(1, max_id)
               self.update_speaker_label()
           
       except Exception as e:
           print(f"話者一覧の読み込みエラー: {e}")
   
   def update_speaker_label(self):
       """話者ラベルの更新"""
       speaker_id = self.speaker_slider.value()
       if hasattr(self, "speaker_names") and speaker_id in self.speaker_names:
           self.speaker_label.setText(f"{speaker_id}: {self.speaker_names[speaker_id]}")
       else:
           self.speaker_label.setText(f"{speaker_id}")
   
   def update_settings(self, settings):
       """詳細設定の更新"""
       self.current_settings = settings
       self.status_label.setText("詳細設定が更新されました")
   
   def process_audio(self):
       """音声合成と処理の実行"""
       # 入力テキストの取得
       text = self.text_input.toPlainText()
       if not text:
           self.status_label.setText("テキストを入力してください")
           return
       
       self.status_label.setText("処理中...")
       
       try:
           # VOICEVOX話者ID
           speaker_id = self.speaker_slider.value()
           
           # 音声合成
           self.original_audio, self.sample_rate = self.voicevox.text_to_speech(text, speaker_id)
           
           # 基本パラメータ
           enhancement_level = self.enhance_slider.value() / 100.0
           
           # 詳細設定（設定されていれば使用）
           high_freq = self.current_settings.get("high_freq", enhancement_level)
           voice_quality = self.current_settings.get("voice_quality", enhancement_level)
           fluctuation = self.current_settings.get("fluctuation", enhancement_level * 0.6)
           
           # 音声処理
           enhanced_audio = self.processor.process(self.original_audio, high_freq)
           enhanced_audio = self.processor.enhance_voice_quality(
               enhanced_audio, self.sample_rate, voice_quality
           )
           enhanced_audio = self.processor.add_natural_fluctuation(
               enhanced_audio, fluctuation * 0.05
           )
           
           self.enhanced_audio = enhanced_audio
           
           # プレビューパネルに設定
           self.preview_panel.set_audio_data(
               self.original_audio, self.enhanced_audio, self.sample_rate
           )
           
           # 保存ボタンを有効化
           self.save_button.setEnabled(True)
           
           self.status_label.setText("処理完了")
           
       except Exception as e:
           self.status_label.setText(f"処理エラー: {str(e)}")
           traceback.print_exc()
   
   def save_audio(self):
       """処理した音声の保存"""
       if self.enhanced_audio is None:
           self.status_label.setText("音声を処理してください")
           return
       
       try:
           # 保存先の選択
           file_path, _ = QFileDialog.getSaveFileName(
               self,
               "音声を保存",
               os.path.join(os.getcwd(), "output", "enhanced.wav"),
               "WAVファイル (*.wav)"
           )
           
           if not file_path:
               return
           
           # 音声の保存
           self.processor.save_audio(self.enhanced_audio, file_path, self.sample_rate)
           
           self.status_label.setText(f"保存完了: {file_path}")
           
       except Exception as e:
           self.status_label.setText(f"保存エラー: {str(e)}")
           traceback.print_exc()
   
   def batch_process(self):
       """バッチ処理の実行"""
       try:
           # テキストファイルの選択
           file_path, _ = QFileDialog.getOpenFileName(
               self,
               "テキストファイルを選択",
               os.getcwd(),
               "テキストファイル (*.txt)"
           )
           
           if not file_path:
               return
           
           # 出力ディレクトリの選択
           output_dir = QFileDialog.getExistingDirectory(
               self,
               "出力ディレクトリを選択",
               os.path.join(os.getcwd(), "output")
           )
           
           if not output_dir:
               return
           
           # テキストファイルの読み込み
           with open(file_path, 'r', encoding='utf-8') as f:
               lines = [line.strip() for line in f.readlines() if line.strip()]
           
           if not lines:
               self.status_label.setText("処理するテキストがありません")
               return
           
           # パラメータの取得
           speaker_id = self.speaker_slider.value()
           enhancement_level = self.enhance_slider.value() / 100.0
           
           # 詳細設定の適用
           high_freq = self.current_settings.get("high_freq", enhancement_level)
           voice_quality = self.current_settings.get("voice_quality", enhancement_level)
           fluctuation = self.current_settings.get("fluctuation", enhancement_level * 0.6)
           
           # 進捗ダイアログ
           progress = QProgressDialog(
               "バッチ処理中...", "キャンセル", 0, len(lines), self
           )
           progress.setWindowTitle("バッチ処理")
           progress.setWindowModality(Qt.WindowModal)
           
           # 各行を処理
           processed_count = 0
           for i, text in enumerate(lines):
               if progress.wasCanceled():
                   break
               
               progress.setValue(i)
               progress.setLabelText(f"処理中: {text[:30]}...")
               
               try:
                   # ファイル名の生成
                   file_name = f"{i+1:03d}_{text[:20]}.wav"
                   file_name = "".join(c for c in file_name if c.isalnum() or c in "._- ")
                   output_path = os.path.join(output_dir, file_name)
                   
                   # 音声合成
                   audio_data, sample_rate = self.voicevox.text_to_speech(text, speaker_id)
                   
                   # 音声処理
                   enhanced_audio = self.processor.process(audio_data, high_freq)
                   enhanced_audio = self.processor.enhance_voice_quality(
                       enhanced_audio, sample_rate, voice_quality
                   )
                   enhanced_audio = self.processor.add_natural_fluctuation(
                       enhanced_audio, fluctuation * 0.05
                   )
                   
                   # 保存
                   self.processor.save_audio(enhanced_audio, output_path, sample_rate)
                   
                   processed_count += 1
                   
               except Exception as e:
                   print(f"行 {i+1} の処理エラー: {e}")
           
           progress.setValue(len(lines))
           
           # 処理完了メッセージ
           QMessageBox.information(
               self,
               "バッチ処理完了",
               f"{processed_count}件のテキストを処理しました。\n"
               f"出力先: {output_dir}"
           )
           
           self.status_label.setText(f"バッチ処理完了: {processed_count}/{len(lines)}件")
           
       except Exception as e:
           self.status_label.setText(f"バッチ処理エラー: {str(e)}")
           traceback.print_exc()


def main():
   """メイン関数"""
   # 必要なディレクトリの作成
   os.makedirs("output", exist_ok=True)
   
   app = QApplication(sys.argv)
   
   # アプリケーションスタイルの設定
   app.setStyle("Fusion")
   
   window = MainWindow()
   window.show()
   
   sys.exit(app.exec_())


if __name__ == "__main__":
   main()