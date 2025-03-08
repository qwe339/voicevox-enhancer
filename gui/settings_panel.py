"""詳細設定パネルモジュール - 音声強化の詳細パラメータを制御する"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSlider, QPushButton, QGroupBox, QTabWidget, 
                           QComboBox, QFileDialog, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import os
import json

class SettingsPanel(QWidget):
    """詳細設定パネル - 音声強化の詳細パラメータを制御するUI"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 設定項目
        self.settings = {
            "spectrum_enhance": 0.5,  # スペクトル強化レベル
            "voice_quality": 0.5,     # 声質向上レベル
            "fluctuation": 0.3,       # 自然揺らぎ
            "breathiness": 0.2,       # 息の音
            "pitch_variation": 0.4,   # ピッチ変動
            "speed_variation": 0.3    # 速度変動
        }
        
        # プリセット関連
        self.preset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "presets")
        if not os.path.exists(self.preset_dir):
            os.makedirs(self.preset_dir)
        
        self.presets = {
            "デフォルト": self.settings.copy(),
            "ナチュラル": {
                "spectrum_enhance": 0.3,
                "voice_quality": 0.4,
                "fluctuation": 0.5,
                "breathiness": 0.3,
                "pitch_variation": 0.6,
                "speed_variation": 0.4
            },
            "クリア": {
                "spectrum_enhance": 0.7,
                "voice_quality": 0.6,
                "fluctuation": 0.2,
                "breathiness": 0.1,
                "pitch_variation": 0.3,
                "speed_variation": 0.2
            },
            "アニメ風": {
                "spectrum_enhance": 0.6,
                "voice_quality": 0.7,
                "fluctuation": 0.4,
                "breathiness": 0.2,
                "pitch_variation": 0.5,
                "speed_variation": 0.5
            }
        }
        
        # UI初期化
        self.init_ui()
        
        # プリセットの読み込み
        self.load_presets_from_disk()
    
    def init_ui(self):
        """UIコンポーネントの初期化"""
        layout = QVBoxLayout(self)
        
        # タブウィジェットの作成
        self.tabs = QTabWidget()
        
        # 音質タブ
        self.sound_quality_tab = QWidget()
        self.create_sound_quality_tab()
        self.tabs.addTab(self.sound_quality_tab, "音質")
        
        # 声質タブ
        self.voice_tab = QWidget()
        self.create_voice_tab()
        self.tabs.addTab(self.voice_tab, "声質")
        
        # 韻律タブ
        self.prosody_tab = QWidget()
        self.create_prosody_tab()
        self.tabs.addTab(self.prosody_tab, "韻律")
        
        # プリセットタブ
        self.preset_tab = QWidget()
        self.create_preset_tab()
        self.tabs.addTab(self.preset_tab, "プリセット")
        
        layout.addWidget(self.tabs)
        
        # 適用ボタン
        self.apply_button = QPushButton("設定を適用")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)
        
        # 初期値を設定
        self.update_ui_from_settings()
    
    def create_sound_quality_tab(self):
        """音質設定タブの作成"""
        layout = QVBoxLayout(self.sound_quality_tab)
        
        # 高周波強調
        spectrum_group = QGroupBox("スペクトル強化")
        spectrum_layout = QVBoxLayout(spectrum_group)
        
        self.spectrum_slider = QSlider(Qt.Horizontal)
        self.spectrum_slider.setRange(0, 100)
        self.spectrum_slider.setValue(int(self.settings["spectrum_enhance"] * 100))
        self.spectrum_label = QLabel(f"{int(self.settings['spectrum_enhance'] * 100)}%")
        self.spectrum_slider.valueChanged.connect(
            lambda v: self.spectrum_label.setText(f"{v}%")
        )
        
        spectrum_layout.addWidget(QLabel("高周波強調レベル:"))
        spectrum_layout.addWidget(self.spectrum_slider)
        spectrum_layout.addWidget(self.spectrum_label)
        
        # 自然揺らぎ
        fluctuation_group = QGroupBox("自然揺らぎ")
        fluctuation_layout = QVBoxLayout(fluctuation_group)
        
        self.fluctuation_slider = QSlider(Qt.Horizontal)
        self.fluctuation_slider.setRange(0, 100)
        self.fluctuation_slider.setValue(int(self.settings["fluctuation"] * 100))
        self.fluctuation_label = QLabel(f"{int(self.settings['fluctuation'] * 100)}%")
        self.fluctuation_slider.valueChanged.connect(
            lambda v: self.fluctuation_label.setText(f"{v}%")
        )
        
        fluctuation_layout.addWidget(QLabel("揺らぎの強さ:"))
        fluctuation_layout.addWidget(self.fluctuation_slider)
        fluctuation_layout.addWidget(self.fluctuation_label)
        
        layout.addWidget(spectrum_group)
        layout.addWidget(fluctuation_group)
        layout.addStretch()
    
    def create_voice_tab(self):
        """声質設定タブの作成"""
        layout = QVBoxLayout(self.voice_tab)
        
        # 声質調整
        voice_group = QGroupBox("声質調整")
        voice_layout = QVBoxLayout(voice_group)
        
        self.voice_quality_slider = QSlider(Qt.Horizontal)
        self.voice_quality_slider.setRange(0, 100)
        self.voice_quality_slider.setValue(int(self.settings["voice_quality"] * 100))
        self.voice_quality_label = QLabel(f"{int(self.settings['voice_quality'] * 100)}%")
        self.voice_quality_slider.valueChanged.connect(
            lambda v: self.voice_quality_label.setText(f"{v}%")
        )
        
        voice_layout.addWidget(QLabel("声質向上レベル:"))
        voice_layout.addWidget(self.voice_quality_slider)
        voice_layout.addWidget(self.voice_quality_label)
        
        # 息の音
        breath_group = QGroupBox("息の音")
        breath_layout = QVBoxLayout(breath_group)
        
        self.breath_slider = QSlider(Qt.Horizontal)
        self.breath_slider.setRange(0, 100)
        self.breath_slider.setValue(int(self.settings["breathiness"] * 100))
        self.breath_label = QLabel(f"{int(self.settings['breathiness'] * 100)}%")
        self.breath_slider.valueChanged.connect(
            lambda v: self.breath_label.setText(f"{v}%")
        )
        
        breath_layout.addWidget(QLabel("息の音の強さ:"))
        breath_layout.addWidget(self.breath_slider)
        breath_layout.addWidget(self.breath_label)
        
        layout.addWidget(voice_group)
        layout.addWidget(breath_group)
        layout.addStretch()
    
    def create_prosody_tab(self):
        """韻律設定タブの作成"""
        layout = QVBoxLayout(self.prosody_tab)
        
        # ピッチ変動
        pitch_group = QGroupBox("ピッチ制御")
        pitch_layout = QVBoxLayout(pitch_group)
        
        self.pitch_variation_slider = QSlider(Qt.Horizontal)
        self.pitch_variation_slider.setRange(0, 100)
        self.pitch_variation_slider.setValue(int(self.settings["pitch_variation"] * 100))
        self.pitch_variation_label = QLabel(f"{int(self.settings['pitch_variation'] * 100)}%")
        self.pitch_variation_slider.valueChanged.connect(
            lambda v: self.pitch_variation_label.setText(f"{v}%")
        )
        
        pitch_layout.addWidget(QLabel("ピッチ変動の自然さ:"))
        pitch_layout.addWidget(self.pitch_variation_slider)
        pitch_layout.addWidget(self.pitch_variation_label)
        
        # 速度変動
        speed_group = QGroupBox("速度制御")
        speed_layout = QVBoxLayout(speed_group)
        
        self.speed_variation_slider = QSlider(Qt.Horizontal)
        self.speed_variation_slider.setRange(0, 100)
        self.speed_variation_slider.setValue(int(self.settings["speed_variation"] * 100))
        self.speed_variation_label = QLabel(f"{int(self.settings['speed_variation'] * 100)}%")
        self.speed_variation_slider.valueChanged.connect(
            lambda v: self.speed_variation_label.setText(f"{v}%")
        )
        
        speed_layout.addWidget(QLabel("速度変動の自然さ:"))
        speed_layout.addWidget(self.speed_variation_slider)
        speed_layout.addWidget(self.speed_variation_label)
        
        layout.addWidget(pitch_group)
        layout.addWidget(speed_group)
        layout.addStretch()
    
    def create_preset_tab(self):
        """プリセットタブの作成"""
        layout = QVBoxLayout(self.preset_tab)
        
        # プリセット選択
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("プリセット:"))
        
        self.preset_combo = QComboBox()
        for preset_name in self.presets.keys():
            self.preset_combo.addItem(preset_name)
        preset_layout.addWidget(self.preset_combo)
        
        layout.addLayout(preset_layout)
        
        # プリセット操作ボタン
        buttons_layout = QHBoxLayout()
        
        self.load_preset_button = QPushButton("読み込み")
        self.load_preset_button.clicked.connect(self.load_preset)
        buttons_layout.addWidget(self.load_preset_button)
        
        self.save_preset_button = QPushButton("保存")
        self.save_preset_button.clicked.connect(self.save_preset)
        buttons_layout.addWidget(self.save_preset_button)
        
        self.new_preset_button = QPushButton("新規作成")
        self.new_preset_button.clicked.connect(self.create_new_preset)
        buttons_layout.addWidget(self.new_preset_button)
        
        layout.addLayout(buttons_layout)
        
        # 説明
        description = QLabel(
            "プリセットは、複数の設定をまとめて保存・適用するための機能です。\n"
            "「読み込み」で選択したプリセットを適用します。\n"
            "「保存」で現在の設定を選択中のプリセットに上書き保存します。\n"
            "「新規作成」で現在の設定から新しいプリセットを作成します。"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        layout.addStretch()
    
    def update_ui_from_settings(self):
        """現在の設定値からUIを更新"""
        # スペクトル強化
        self.spectrum_slider.setValue(int(self.settings["spectrum_enhance"] * 100))
        self.spectrum_label.setText(f"{int(self.settings['spectrum_enhance'] * 100)}%")
        
        # 自然揺らぎ
        self.fluctuation_slider.setValue(int(self.settings["fluctuation"] * 100))
        self.fluctuation_label.setText(f"{int(self.settings['fluctuation'] * 100)}%")
        
        # 声質
        self.voice_quality_slider.setValue(int(self.settings["voice_quality"] * 100))
        self.voice_quality_label.setText(f"{int(self.settings['voice_quality'] * 100)}%")
        
        # 息の音
        self.breath_slider.setValue(int(self.settings["breathiness"] * 100))
        self.breath_label.setText(f"{int(self.settings['breathiness'] * 100)}%")
        
        # ピッチ変動
        self.pitch_variation_slider.setValue(int(self.settings["pitch_variation"] * 100))
        self.pitch_variation_label.setText(f"{int(self.settings['pitch_variation'] * 100)}%")
        
        # 速度変動
        self.speed_variation_slider.setValue(int(self.settings["speed_variation"] * 100))
        self.speed_variation_label.setText(f"{int(self.settings['speed_variation'] * 100)}%")
    
    def apply_settings(self):
        """現在の設定を適用"""
        self.update_settings_from_ui()
        self.settings_changed.emit(self.settings)

    def update_settings_from_ui(self):
        """UIから設定値を更新"""
        self.settings["spectrum_enhance"] = self.spectrum_slider.value() / 100.0
        self.settings["fluctuation"] = self.fluctuation_slider.value() / 100.0
        self.settings["voice_quality"] = self.voice_quality_slider.value() / 100.0
        self.settings["breathiness"] = self.breath_slider.value() / 100.0
        self.settings["pitch_variation"] = self.pitch_variation_slider.value() / 100.0
        self.settings["speed_variation"] = self.speed_variation_slider.value() / 100.0
    
    def get_current_settings(self):
        """現在の設定を取得"""
        self.update_settings_from_ui()
        return self.settings.copy()
    
    def load_preset(self):
        """選択されたプリセットを読み込み"""
        preset_name = self.preset_combo.currentText()
        if preset_name not in self.presets:
            QMessageBox.warning(self, "エラー", f"プリセット '{preset_name}' が見つかりません。")
            return
        
        # プリセットの設定を適用
        self.settings = self.presets[preset_name].copy()
        self.update_ui_from_settings()
        
        # 設定変更イベントを発行
        self.settings_changed.emit(self.settings)
        
        QMessageBox.information(self, "プリセット読み込み", f"プリセット '{preset_name}' を読み込みました。")
    
    def save_preset(self):
        """現在の設定を選択中のプリセットに保存"""
        preset_name = self.preset_combo.currentText()
        
        # 設定を更新
        self.update_settings_from_ui()
        
        # プリセットに保存
        self.presets[preset_name] = self.settings.copy()
        
        # ディスクに保存
        self.save_presets_to_disk()
        
        QMessageBox.information(self, "プリセット保存", f"現在の設定をプリセット '{preset_name}' として保存しました。")
    
    def create_new_preset(self):
        """新規プリセットの作成"""
        # 現在の設定を取得
        self.update_settings_from_ui()
        
        # プリセット名を入力
        preset_name, ok = QInputDialog.getText(self, "新規プリセット", "プリセット名を入力してください:")
        if not ok or not preset_name:
            return
        
        # 既存のプリセット名と重複チェック
        if preset_name in self.presets:
            overwrite = QMessageBox.question(
                self, 
                "上書き確認", 
                f"プリセット '{preset_name}' は既に存在します。上書きしますか？",
                QMessageBox.Yes | QMessageBox.No
            )
            if overwrite != QMessageBox.Yes:
                return
        
        # 新規プリセットとして保存
        self.presets[preset_name] = self.settings.copy()
        
        # コンボボックスに追加（既存の場合は追加しない）
        if self.preset_combo.findText(preset_name) == -1:
            self.preset_combo.addItem(preset_name)
        
        # 現在のプリセットとして選択
        self.preset_combo.setCurrentText(preset_name)
        
        # ディスクに保存
        self.save_presets_to_disk()
        
        QMessageBox.information(self, "プリセット作成", f"新規プリセット '{preset_name}' を作成しました。")
    
    def load_presets_from_disk(self):
        """ディスクからプリセットを読み込み"""
        preset_file = os.path.join(self.preset_dir, "presets.json")
        if not os.path.exists(preset_file):
            return
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                loaded_presets = json.load(f)
            
            # 組み込みプリセットを上書きしないようにする
            for preset_name, preset_data in loaded_presets.items():
                # デフォルトプリセットは上書きしない
                if preset_name == "デフォルト" and preset_name in self.presets:
                    continue
                
                self.presets[preset_name] = preset_data
                
                # コンボボックスに追加（既存の場合は追加しない）
                if self.preset_combo.findText(preset_name) == -1:
                    self.preset_combo.addItem(preset_name)
            
        except Exception as e:
            print(f"プリセット読み込みエラー: {e}")
    
    def save_presets_to_disk(self):
        """ディスクにプリセットを保存"""
        preset_file = os.path.join(self.preset_dir, "presets.json")
        
        try:
            # ディレクトリの存在確認
            if not os.path.exists(self.preset_dir):
                os.makedirs(self.preset_dir)
            
            with open(preset_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            
            print(f"プリセットを保存しました: {preset_file}")
        except Exception as e:
            print(f"プリセット保存エラー: {e}")
            QMessageBox.warning(self, "エラー", f"プリセットの保存に失敗しました: {e}")