"""メインウィンドウモジュール"""

import os
import traceback
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QSlider, QLabel, QTextEdit, 
                            QFileDialog, QMessageBox, QTabWidget, QProgressDialog)
from PyQt5.QtCore import Qt, QTimer
import soundfile as sf

from ui.preview_panel import AudioPreviewPanel
from ui.settings_panel import AdvancedSettingsPanel

class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self, voicevox_connector, audio_processor):
        super().__init__()
        
        # 依存オブジェクト
        self.voicevox = voicevox_connector
        self.processor = audio_processor
        
        # ウィンドウ設定
        self.setWindowTitle("VOICEVOX Enhancer")
        self.setGeometry(100, 100, 900, 600)
        
        # 内部状態
        self.original_audio = None
        self.enhanced_audio = None
        self.sample_rate = 24000
        self.current_settings = {}
        
        # UI初期化
        self.init_ui()
        
        # VOICEVOXの接続確認と話者読み込み
        QTimer.singleShot(100, self.check_voicevox_connection)
    
    def init_ui(self):
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
        
        self.speaker_label = QLabel("1: 話者情報取得中...")
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
        self.settings_panel.settings_changed.connect(self.update_settings)
        right_panel.addTab(self.settings_panel, "詳細設定")
        
        # レイアウトに追加
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
    
    def check_voicevox_connection(self):
        """VOICEVOXとの接続を確認"""
        self.status_label.setText("VOICEVOXとの接続を確認中...")
        
        if self.voicevox.test_connection():
            self.status_label.setText("VOICEVOX接続成功")
            # 話者情報を取得
            if self.voicevox.get_speakers():
                # 話者の最大数に基づいてスライダーの範囲を設定
                max_id = max(self.voicevox.speakers.keys()) if self.voicevox.speakers else 1
                self.speaker_slider.setRange(1, max_id)
                self.update_speaker_label()
                self.status_label.setText("話者情報を取得しました")
            else:
                self.status_label.setText("話者情報の取得に失敗しました")
        else:
            self.status_label.setText("VOICEVOXとの接続に失敗しました")
            QMessageBox.warning(
                self,
                "接続エラー",
                "VOICEVOXエンジンとの接続に失敗しました。\n"
                "VOICEVOXが起動しているか確認してください。"
            )
    
    def update_speaker_label(self):
        """話者ラベルの更新"""
        speaker_id = self.speaker_slider.value()
        if speaker_id in self.voicevox.speakers:
            self.speaker_label.setText(f"{speaker_id}: {self.voicevox.speakers[speaker_id]}")
        else:
            self.speaker_label.setText(f"{speaker_id}")
    
    def update_settings(self, settings):
        """詳細設定の更新"""
        self.current_settings = settings
        self.status_label.setText("詳細設定が更新されました")
        
        # 既に音声がある場合は再処理
        if self.original_audio is not None:
            self.process_audio(reprocess=True)
    
    def process_audio(self, reprocess=False):
        """音声合成と処理の実行"""
        if not reprocess:
            # 入力テキストの取得
            text = self.text_input.toPlainText()
            if not text:
                self.status_label.setText("テキストを入力してください")
                return
            
            self.status_label.setText("音声合成中...")
            
            try:
                # VOICEVOX話者ID
                speaker_id = self.speaker_slider.value()
                
                # 音声合成
                self.original_audio, self.sample_rate = self.voicevox.text_to_speech(text, speaker_id)
            except Exception as e:
                self.status_label.setText(f"音声合成エラー: {str(e)}")
                return
        
        # 音声処理
        self.status_label.setText("音声処理中...")
        
        try:
            # 基本パラメータ
            enhancement_level = self.enhance_slider.value() / 100.0

# 詳細設定（設定されていれば使用）
           if not self.current_settings:
               self.current_settings = self.settings_panel.get_current_settings()
           
           # 基本強化レベルを反映
           self.current_settings["spectrum_enhance"] = enhancement_level
           
           # 音声処理
           self.enhanced_audio = self.processor.enhance_audio(
               self.original_audio, 
               self.current_settings
           )
           
           # プレビューパネルに設定
           self.preview_panel.set_audio_data(
               self.original_audio, 
               self.enhanced_audio, 
               self.sample_rate
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
               os.path.join(os.getcwd(), "enhanced.wav"),
               "WAVファイル (*.wav)"
           )
           
           if not file_path:
               return
           
           # 音声の保存
           sf.write(file_path, self.enhanced_audio, self.sample_rate)
           
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
               os.getcwd()
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
           settings = self.settings_panel.get_current_settings()
           settings["spectrum_enhance"] = self.enhance_slider.value() / 100.0
           
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
                   enhanced_audio = self.processor.enhance_audio(audio_data, settings)
                   
                   # 保存
                   sf.write(output_path, enhanced_audio, sample_rate)
                   
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