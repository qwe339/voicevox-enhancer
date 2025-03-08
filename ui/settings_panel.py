"""詳細設定パネルモジュール"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class AdvancedSettingsPanel(QWidget):
    """詳細設定パネル"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UIコンポーネントの初期化"""
        layout = QVBoxLayout(self)
        
        # 音質設定
        layout.addWidget(QLabel("<b>音質設定</b>"))
        
        # 高周波強調
        layout.addWidget(QLabel("高周波強調:"))
        self.high_freq_slider = QSlider(Qt.Horizontal)
        self.high_freq_slider.setRange(0, 100)
        self.high_freq_slider.setValue(50)
        self.high_freq_label = QLabel("50%")
        self.high_freq_slider.valueChanged.connect(
            lambda v: self.high_freq_label.setText(f"{v}%")
        )
        layout.addWidget(self.high_freq_slider)
        layout.addWidget(self.high_freq_label)
        
        # 声質調整
        layout.addWidget(QLabel("声質調整:"))
        self.voice_quality_slider = QSlider(Qt.Horizontal)
        self.voice_quality_slider.setRange(0, 100)
        self.voice_quality_slider.setValue(50)
        self.voice_quality_label = QLabel("50%")
        self.voice_quality_slider.valueChanged.connect(
            lambda v: self.voice_quality_label.setText(f"{v}%")
        )
        layout.addWidget(self.voice_quality_slider)
        layout.addWidget(self.voice_quality_label)
        
        # 自然揺らぎ
        layout.addWidget(QLabel("自然揺らぎ:"))
        self.fluctuation_slider = QSlider(Qt.Horizontal)
        self.fluctuation_slider.setRange(0, 100)
        self.fluctuation_slider.setValue(30)
        self.fluctuation_label = QLabel("30%")
        self.fluctuation_slider.valueChanged.connect(
            lambda v: self.fluctuation_label.setText(f"{v}%")
        )
        layout.addWidget(self.fluctuation_slider)
        layout.addWidget(self.fluctuation_label)
        
        # 適用ボタン
        self.apply_button = QPushButton("設定を適用")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)
        
        # スペーサー
        layout.addStretch()
    
    def apply_settings(self):
        """現在の設定を適用"""
        settings = self.get_current_settings()
        self.settings_changed.emit(settings)
    
    def get_current_settings(self):
        """現在の設定を取得"""
        return {
            "spectrum_enhance": self.high_freq_slider.value() / 100.0,
            "voice_quality": self.voice_quality_slider.value() / 100.0,
            "fluctuation": self.fluctuation_slider.value() / 100.0
        }