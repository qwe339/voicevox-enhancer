# gui/advanced_controls.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QPushButton, QComboBox, QGroupBox, 
                            QTabWidget, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

class AdvancedParameterPanel(QWidget):
    """詳細パラメータ調整パネル"""
    
    parametersChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout(self)
        
        # タブウィジェットの作成
        self.tabs = QTabWidget()
        
        # 音質タブ
        self.sound_quality_tab = QWidget()
        self.createSoundQualityTab()
        self.tabs.addTab(self.sound_quality_tab, "音質")
        
        # 韻律タブ
        self.prosody_tab = QWidget()
        self.createProsodyTab()
        self.tabs.addTab(self.prosody_tab, "韻律")
        
        # 声質タブ
        self.voice_tab = QWidget()
        self.createVoiceTab()
        self.tabs.addTab(self.voice_tab, "声質")
        
        # プリセットタブ
        self.preset_tab = QWidget()
        self.createPresetTab()
        self.tabs.addTab(self.preset_tab, "プリセット")
        
        self.layout.addWidget(self.tabs)
        
        # 適用ボタン
        self.apply_button = QPushButton("パラメータを適用")
        self.apply_button.clicked.connect(self.applyParameters)
        self.layout.addWidget(self.apply_button)
    
    def createSoundQualityTab(self):
        layout = QVBoxLayout(self.sound_quality_tab)
        
        # スペクトル強化
        spectrum_group = QGroupBox("スペクトル強化")
        spectrum_layout = QVBoxLayout(spectrum_group)
        
        self.spectrum_slider = QSlider(Qt.Horizontal)
        self.spectrum_slider.setRange(0, 100)
        self.spectrum_slider.setValue(50)
        self.spectrum_label = QLabel("50%")
        self.spectrum_slider.valueChanged.connect(lambda v: self.spectrum_label.setText(f"{v}%"))
        
        spectrum_layout.addWidget(QLabel("高周波強調レベル:"))
        spectrum_layout.addWidget(self.spectrum_slider)
        spectrum_layout.addWidget(self.spectrum_label)
        
        # ノイズ除去
        noise_group = QGroupBox("ノイズ処理")
        noise_layout = QVBoxLayout(noise_group)
        
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setRange(0, 100)
        self.noise_slider.setValue(30)
        self.noise_label = QLabel("30%")
        self.noise_slider.valueChanged.connect(lambda v: self.noise_label.setText(f"{v}%"))
        
        noise_layout.addWidget(QLabel("ノイズ除去レベル:"))
        noise_layout.addWidget(self.noise_slider)
        noise_layout.addWidget(self.noise_label)
        
        layout.addWidget(spectrum_group)
        layout.addWidget(noise_group)
        layout.addStretch()
    
    def createProsodyTab(self):
        layout = QVBoxLayout(self.prosody_tab)
        
        # ピッチ変動
        pitch_group = QGroupBox("ピッチ制御")
        pitch_layout = QVBoxLayout(pitch_group)
        
        self.pitch_variation_slider = QSlider(Qt.Horizontal)
        self.pitch_variation_slider.setRange(0, 100)
        self.pitch_variation_slider.setValue(40)
        self.pitch_variation_label = QLabel("40%")
        self.pitch_variation_slider.valueChanged.connect(lambda v: self.pitch_variation_label.setText(f"{v}%"))
        
        pitch_layout.addWidget(QLabel("ピッチ変動の自然さ:"))
        pitch_layout.addWidget(self.pitch_variation_slider)
        pitch_layout.addWidget(self.pitch_variation_label)
        
        # 話速変動
        speed_group = QGroupBox("話速制御")
        speed_layout = QVBoxLayout(speed_group)
        
        self.speed_variation_slider = QSlider(Qt.Horizontal)
        self.speed_variation_slider.setRange(0, 100)
        self.speed_variation_slider.setValue(50)
        self.speed_variation_label = QLabel("50%")
        self.speed_variation_slider.valueChanged.connect(lambda v: self.speed_variation_label.setText(f"{v}%"))
        
        speed_layout.addWidget(QLabel("話速変動の自然さ:"))
        speed_layout.addWidget(self.speed_variation_slider)
        speed_layout.addWidget(self.speed_variation_label)
        
        layout.addWidget(pitch_group)
        layout.addWidget(speed_group)
        layout.addStretch()
    
    def createVoiceTab(self):
        layout = QVBoxLayout(self.voice_tab)
        
        # 声質テクスチャ
        texture_group = QGroupBox("声質テクスチャ")
        texture_layout = QVBoxLayout(texture_group)
        
        self.texture_slider = QSlider(Qt.Horizontal)
        self.texture_slider.setRange(0, 100)
        self.texture_slider.setValue(20)
        self.texture_label = QLabel("20%")
        self.texture_slider.valueChanged.connect(lambda v: self.texture_label.setText(f"{v}%"))
        
        texture_layout.addWidget(QLabel("声帯振動テクスチャ:"))
        texture_layout.addWidget(self.texture_slider)
        texture_layout.addWidget(self.texture_label)
        
        # 息の音
        breath_group = QGroupBox("息の音")
        breath_layout = QVBoxLayout(breath_group)
        
        self.breath_slider = QSlider(Qt.Horizontal)
        self.breath_slider.setRange(0, 100)
        self.breath_slider.setValue(30)
        self.breath_label = QLabel("30%")
        self.breath_slider.valueChanged.connect(lambda v: self.breath_label.setText(f"{v}%"))
        
        breath_layout.addWidget(QLabel("息の音の強さ:"))
        breath_layout.addWidget(self.breath_slider)
        breath_layout.addWidget(self.breath_label)
        
        layout.addWidget(texture_group)
        layout.addWidget(breath_group)
        layout.addStretch()
    
    def createPresetTab(self):
        layout = QVBoxLayout(self.preset_tab)
        
        # プリセット選択
        preset_selection = QHBoxLayout()
        preset_selection.addWidget(QLabel("プリセット:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["デフォルト", "ナチュラル", "アニメ風", "大人っぽい", "かわいい"])
        preset_selection.addWidget(self.preset_combo)
        
        # プリセット操作ボタン
        preset_buttons = QHBoxLayout()
        
        self.load_preset_button = QPushButton("読み込み")
        self.load_preset_button.clicked.connect(self.loadPreset)
        preset_buttons.addWidget(self.load_preset_button)
        
        self.save_preset_button = QPushButton("保存")
        self.save_preset_button.clicked.connect(self.savePreset)
        preset_buttons.addWidget(self.save_preset_button)
        
        self.new_preset_button = QPushButton("新規作成")
        self.new_preset_button.clicked.connect(self.createNewPreset)
        preset_buttons.addWidget(self.new_preset_button)
        
        layout.addLayout(preset_selection)
        layout.addLayout(preset_buttons)
        layout.addStretch()
    
    def applyParameters(self):
        """現在のパラメータ設定を収集して送信"""
        parameters = {
            # 音質パラメータ
            "spectrum_enhance": self.spectrum_slider.value() / 100.0,
            "noise_reduction": self.noise_slider.value() / 100.0,
            
            # 韻律パラメータ
            "pitch_variation": self.pitch_variation_slider.value() / 100.0,
            "speed_variation": self.speed_variation_slider.value() / 100.0,
            
            # 声質パラメータ
            "vocal_texture": self.texture_slider.value() / 100.0,
            "breathiness": self.breath_slider.value() / 100.0
        }
        
        self.parametersChanged.emit(parameters)
    
    def loadPreset(self):
        """プリセットを読み込み"""
        preset_name = self.preset_combo.currentText()
        # ここで実際のプリセット読み込み処理
        QMessageBox.information(self, "プリセット読み込み", f"プリセット '{preset_name}' を読み込みました")
    
    def savePreset(self):
        """現在の設定をプリセットとして保存"""
        preset_name = self.preset_combo.currentText()
        # ここで実際のプリセット保存処理
        QMessageBox.information(self, "プリセット保存", f"現在の設定をプリセット '{preset_name}' として保存しました")
    
    def createNewPreset(self):
        """新規プリセットの作成"""
        # 新規プリセット作成ダイアログなどの処理
        preset_name, ok = QInputDialog.getText(self, "新規プリセット", "プリセット名を入力してください:")
        if ok and preset_name:
            self.preset_combo.addItem(preset_name)
            self.preset_combo.setCurrentText(preset_name)