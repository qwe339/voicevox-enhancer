"""音声処理モジュール"""

import numpy as np
import librosa
import scipy.signal as signal
import traceback

class AudioProcessor:
    """音声処理の中核エンジン"""
    
    def __init__(self, sample_rate=24000):
        self.sample_rate = sample_rate
    
    def enhance_audio(self, audio_data, settings):
        """音声強化の処理をまとめて実行"""
        if len(audio_data) == 0:
            return audio_data
        
        try:
            # 各種パラメータを取得
            spectrum_enhance = settings.get("spectrum_enhance", 0.5)
            voice_quality = settings.get("voice_quality", 0.5)
            fluctuation = settings.get("fluctuation", 0.02)
            
            # 処理を適用
            enhanced = audio_data.copy()
            
            # 短い音声に対応するためのチェック
            if len(enhanced) >= 256:  # 最小限必要なサンプル数
                # スペクトル強化処理
                enhanced = self.enhance_spectrum(enhanced, spectrum_enhance)
                
                # 声質向上処理
                enhanced = self.enhance_voice_quality(enhanced, self.sample_rate, voice_quality)
                
                # 自然な揺らぎの追加
                enhanced = self.add_natural_fluctuation(enhanced, fluctuation)
            else:
                print(f"警告: 音声が短すぎます ({len(audio_data)} サンプル)。処理をスキップします。")
            
            # 音量の正規化
            enhanced = self.normalize_audio(enhanced)
            
            return enhanced
            
        except Exception as e:
            print(f"音声処理エラー: {e}")
            traceback.print_exc()
            return audio_data
    
    def enhance_spectrum(self, audio_data, enhancement_level=0.5):
        """スペクトル強化処理"""
        # 音声データの長さに基づいてFFTサイズを調整
        n_fft = min(1024, 2**int(np.log2(len(audio_data))))
        hop_length = n_fft // 4
        
        # スペクトル解析
        stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
        magnitude, phase = librosa.magphase(stft)
        
        # 高周波数帯域の強調
        freq_enhance = np.linspace(1.0, 1.0 + enhancement_level, num=magnitude.shape[0])
        enhanced_magnitude = magnitude * freq_enhance[:, np.newaxis]
        
        # スペクトル補正から音声を再構成
        enhanced_stft = enhanced_magnitude * phase
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=hop_length, length=len(audio_data))
        
        return enhanced_audio
    
    def enhance_voice_quality(self, audio_data, sample_rate, enhancement_level=0.5):
        """声質向上処理"""
        # 母音のフォルマント周波数を強調
        formant_freqs = {
            'a': [800, 1200],
            'i': [300, 2500],
            'u': [300, 900],
            'e': [500, 1800],
            'o': [500, 1000]
        }
        
        enhanced_audio = audio_data.copy()
        
        for vowel, freqs in formant_freqs.items():
            for freq in freqs:
                # バンドパスフィルタの作成
                try:
                    freq_min = max(freq - 50, 20)
                    freq_max = min(freq + 50, sample_rate // 2 - 1)
                    
                    b, a = signal.butter(
                        2, 
                        [freq_min / (sample_rate/2), freq_max / (sample_rate/2)],
                        btype='band'
                    )
                    
                    # フィルタ適用
                    filtered = signal.lfilter(b, a, audio_data)
                    enhanced_audio += filtered * (enhancement_level * 0.2)
                except Exception as e:
                    print(f"フィルタ適用エラー: {e}")
        
        return enhanced_audio
    
    def add_natural_fluctuation(self, audio_data, fluctuation_rate=0.02):
        """自然な揺らぎを追加"""
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
        
        return natural_audio
    
    def normalize_audio(self, audio_data, target_level=0.9):
        """音声の正規化"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * target_level
        return audio_data