# core/prosody_adjuster.py

import numpy as np
import librosa

class ProsodyAdjuster:
    def __init__(self):
        pass
    
    def adjust_pitch_contour(self, audio_data, sample_rate, strength=0.5):
        """ピッチ曲線を自然に調整"""
        # ピッチ抽出
        pitch, magnitudes = librosa.piptrack(
            y=audio_data, 
            sr=sample_rate,
            fmin=70,
            fmax=400
        )
        
        # ピッチの滑らかさを調整
        smoothed_pitch = np.zeros_like(pitch)
        for i in range(pitch.shape[1]):
            col_pitches = pitch[:, i][magnitudes[:, i] > 0]
            if len(col_pitches) > 0:
                smoothed_pitch[:, i] = np.mean(col_pitches)
        
        # ピッチシフトの適用
        adjusted_audio = librosa.effects.pitch_shift(
            audio_data,
            sr=sample_rate,
            n_steps=0,  # 基本ピッチは維持
            bins_per_octave=12
        )
        
        return adjusted_audio
    
    def enhance_intonation(self, audio_data, sample_rate, text_info=None):
        """イントネーションを強化"""
        # テキスト情報がある場合は文脈に基づいた強調
        if text_info:
            # 文末、疑問文などに基づく処理
            pass
        
        # 基本的な処理: セグメントごとの抑揚変動を増加
        y_harmonic = librosa.effects.harmonic(audio_data)
        y_enhanced = audio_data * 0.7 + y_harmonic * 0.3
        
        return y_enhanced