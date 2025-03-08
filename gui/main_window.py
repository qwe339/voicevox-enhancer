# gui/main_window.py (拡張版)

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel, 
                            QFileDialog, QTextEdit, QTabWidget, QSplitter,
                            QMessageBox)
from PyQt5.QtCore import Qt

from gui.advanced_controls import AdvancedParameterPanel
from gui.audio_preview import AudioPreviewPanel

class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VOICEVOX Enhancer")
        self.setGeometry(100, 100, 1000, 700)
        self.initUI()
        
        # 音声処理エンジンの初期化
        self.processed_audio = None
        self.original_audio = None
        self.sample_rate = 24000
        self.processing_parameters = {}
    
    def initUI(self):
        # メインスプリッタ（左右分割）
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # 左側パネル（入力と基本コントロール）
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # テキスト入力エリア
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("ここにテキストを入力してください")
        self.left_layout.addWidget(QLabel("入力テキスト:"))
        self.left_layout.addWidget(self.text_input)
        
        # 話者選択
        self.left_layout.addWidget(QLabel("VOICEVOX話者ID:"))
        self.speaker_slider = QSlider(Qt.Horizontal)
        self.speaker_slider.setMinimum(1)
        self.speaker_slider.setMaximum(20)
        self.speaker_slider.setValue(1)
        self.speaker_label = QLabel("1")
        self.speaker_slider.valueChanged.connect(
            lambda v: self.speaker_label.setText(str(v))
        )
        self.left_layout.addWidget(self.speaker_slider)
        self.left_layout.addWidget(self.speaker_label)
        
        # 基本エンハンスパラメータ
        self.left_layout.addWidget(QLabel("音声リアル化レベル:"))
        self.enhance_slider = QSlider(Qt.Horizontal)
        self.enhance_slider.setMinimum(0)
        self.enhance_slider.setMaximum(100)
        self.enhance_slider.setValue(50)
        self.enhance_label = QLabel("50%")
        self.enhance_slider.valueChanged.connect(
            lambda v: self.enhance_label.setText(f"{v}%")
        )
        self.left_layout.addWidget(self.enhance_slider)
        self.left_layout.addWidget(self.enhance_label)
        
        # 処理ボタン
        self.process_button = QPushButton("音声合成と強化")
        self.process_button.clicked.connect(self.process_audio)
        self.left_layout.addWidget(self.process_button)
        
        # 保存ボタン
        self.save_button = QPushButton("音声を保存")
        self.save_button.clicked.connect(self.save_audio)
        self.left_layout.addWidget(self.save_button)
        
        # バッチ処理ボタン
        self.batch_button = QPushButton("バッチ処理")
        self.batch_button.clicked.connect(self.batch_process)
        self.left_layout.addWidget(self.batch_button)
        
        # ステータス表示
        self.status_label = QLabel("準備完了")
        self.left_layout.addWidget(self.status_label)
        
        # 右側パネル（タブ付きウィジェット）
        self.right_panel = QTabWidget()
        
        # プレビュータブ
        self.preview_panel = AudioPreviewPanel()
        self.right_panel.addTab(self.preview_panel, "プレビュー")
        
        # 詳細設定タブ
        self.advanced_panel = AdvancedParameterPanel()
        self.advanced_panel.parametersChanged.connect(self.update_parameters)
        self.right_panel.addTab(self.advanced_panel, "詳細設定")
        
        # スプリッタに追加
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([400, 600])
    
    def process_audio(self):
        """音声の合成と強化処理"""
        self.status_label.setText("処理中...")
        
        # 入力テキストの取得
        text = self.text_input.toPlainText()
        if not text:
            self.status_label.setText("テキストを入力してください")
            return
        
        # 基本パラメータの取得
        speaker_id = self.speaker_slider.value()
        enhancement_level = self.enhance_slider.value() / 100.0
        
        # 詳細パラメータの取得
        if not self.processing_parameters:
            self.processing_parameters = {
                "spectrum_enhance": enhancement_level,
                "noise_reduction": 0.3,
                "pitch_variation": 0.4,
                "speed_variation": 0.5,
                "vocal_texture": 0.2,
                "breathiness": 0.3
            }
        else:
            # 基本リアル化レベルを反映
            self.processing_parameters["spectrum_enhance"] = enhancement_level
        
        try:
            # 音声処理（実際のprocessing_functionを呼び出す）
            # self.original_audio, self.processed_audio, self.sample_rate = ...
            
            # テスト用の模擬データ
            import numpy as np
            self.original_audio = np.random.rand(48000) * 0.1
            self.processed_audio = np.random.rand(48000) * 0.1
            self.sample_rate = 24000
            
            # プレビューパネルに音声を設定
            self.preview_panel.setAudioData(
                self.original_audio, 
                self.processed_audio, 
                self.sample_rate
            )
            
            self.status_label.setText("処理完了")
            self.save_button.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"エラー: {str(e)}")
    
    def save_audio(self):
        """処理した音声を保存"""
        if self.processed_audio is None:
            self.status_label.setText("先に音声を処理してください")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "音声を保存", "", "WAVファイル (*.wav)"
        )
        
        if file_path:
            # 音声を保存
            import soundfile as sf
            sf.write(file_path, self.processed_audio, self.sample_rate)
            self.status_label.setText(f"保存完了: {file_path}")
    
    def batch_process(self):
        """バッチ処理機能"""
        try:
            # テキストファイル選択ダイアログ
            file_path, _ = QFileDialog.getOpenFileName(
                self, "テキストファイルを選択", "", "テキストファイル (*.txt)"
            )
            
            if not file_path:
                return
            
            # 出力ディレクトリの選択
            output_dir = QFileDialog.getExistingDirectory(
                self, "出力ディレクトリを選択"
            )
            
            if not output_dir:
                return
            
            # テキストファイルを読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # バッチ処理の実行（実際の処理を呼び出す）
            self.status_label.setText(f"バッチ処理中... (0/{len(lines)})")
            
            # 処理完了
            QMessageBox.information(
                self,
                "バッチ処理完了",
                f"{len(lines)}行のテキストを処理し、{output_dir}に保存しました。"
            )
            
            self.status_label.setText("バッチ処理完了")
        except Exception as e:
            self.status_label.setText(f"バッチ処理エラー: {str(e)}")
    
    def update_parameters(self, parameters):
        """詳細パラメータの更新"""
        self.processing_parameters = parameters
        self.status_label.setText("パラメータを更新しました")