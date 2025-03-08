# core/audio_processor.py

import numpy as np
import librosa
import soundfile as sf

class AudioProcessor:
    def __init__(self, sample_rate=24000):
        self.sample_rate = sample_rate
        
    def process(self, audio_data, enhancement_level=0.5):
        """音声データに基本的な処理を適用"""
        # スペクトル分析のためのSTFT
        stft = librosa.stft(audio_data)
        magnitude, phase = librosa.magphase(stft)
        
        # 基本的なスペクトル補正（高周波数帯域の強調）
        freq_enhance = np.linspace(1.0, 1.0 + enhancement_level, num=magnitude.shape[0])
        enhanced_magnitude = magnitude * freq_enhance[:, np.newaxis]
        
        # 補正したスペクトルから音声を再構成
        enhanced_stft = enhanced_magnitude * phase
        enhanced_audio = librosa.istft(enhanced_stft)
        
        return enhanced_audio
    
    def add_natural_fluctuation(self, audio_data, fluctuation_rate=0.02):
        """自然な揺らぎを追加"""
        # 微小なランダム変動を生成
        fluctuation = np.random.normal(1.0, fluctuation_rate, size=len(audio_data))
        smoothed_fluctuation = np.convolve(fluctuation, np.ones(128)/128, mode='same')
        
        # 揺らぎを適用
        natural_audio = audio_data * smoothed_fluctuation
        
        return natural_audio
    
    def save_audio(self, audio_data, file_path):
        """処理した音声を保存"""
        sf.write(file_path, audio_data, self.sample_rate)