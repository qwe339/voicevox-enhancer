# core/voice_naturalizer.py

import numpy as np
import scipy.signal as signal

class VoiceNaturalizer:
    def __init__(self):
        self.formant_freqs = {
            'a': [800, 1200],
            'i': [300, 2500],
            'u': [300, 900],
            'e': [500, 1800],
            'o': [500, 1000]
        }
    
    def enhance_formants(self, audio_data, sample_rate, vowel_emphasis=1.2):
        """フォルマントを強調して声質を自然化"""
        # 各母音のフォルマント周波数を強調するフィルタを適用
        enhanced_audio = np.copy(audio_data)
        
        for vowel, freqs in self.formant_freqs.items():
            for freq in freqs:
                # バンドパスフィルタの作成
                b, a = signal.butter(
                    2, 
                    [max(freq - 50, 20), min(freq + 50, sample_rate//2-1)],
                    btype='band',
                    fs=sample_rate
                )
                
                # フィルタ適用
                filtered = signal.lfilter(b, a, audio_data)
                enhanced_audio += filtered * (vowel_emphasis - 1.0) * 0.2
        
        # 正規化
        enhanced_audio = enhanced_audio / np.max(np.abs(enhanced_audio))
        
        return enhanced_audio
    
    def add_vocal_texture(self, audio_data, texture_amount=0.1):
        """声帯振動の質感を追加"""
        # 微小なハーモニックノイズを生成
        noise = np.random.normal(0, 0.01, size=len(audio_data))
        envelope = np.abs(audio_data)
        
        # エンベロープに基づいてノイズを変調
        textured_noise = noise * envelope
        textured_audio = audio_data + textured_noise * texture_amount
        
        return textured_audio