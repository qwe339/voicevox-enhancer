"""音声処理モジュール - 音声強化機能の中核エンジン"""

import numpy as np
import librosa
import scipy.signal as signal
import traceback

class AudioProcessor:
    """音声処理の中核エンジン - 様々な処理を適用して音声を強化する"""
    
    def __init__(self, sample_rate=24000):
        """初期化"""
        self.sample_rate = sample_rate
    
    def enhance_audio(self, audio_data, settings):
        """音声強化の処理をまとめて実行"""
        if len(audio_data) == 0:
            return audio_data
        
        try:
            # 各種パラメータを取得
            spectrum_enhance = settings.get("spectrum_enhance", 0.5)
            voice_quality = settings.get("voice_quality", 0.5)
            fluctuation = settings.get("fluctuation", 0.3)
            breathiness = settings.get("breathiness", 0.2)
            pitch_variation = settings.get("pitch_variation", 0.4)
            speed_variation = settings.get("speed_variation", 0.3)
            
            # 処理を適用
            enhanced = audio_data.copy()
            
            # 短い音声に対応するためのチェック
            if len(enhanced) >= 256:  # 最小限必要なサンプル数
                # スペクトル強化処理
                enhanced = self.enhance_spectrum(enhanced, spectrum_enhance)
                
                # 声質向上処理
                enhanced = self.enhance_voice_quality(enhanced, voice_quality)
                
                # 息の音追加（息っぽさ）
                if breathiness > 0.05:  # 閾値以上の場合のみ適用
                    enhanced = self.add_breathiness(enhanced, breathiness)
                
                # 自然な揺らぎの追加
                enhanced = self.add_natural_fluctuation(enhanced, fluctuation)
                
                # ピッチ変動（韻律）
                if pitch_variation > 0.05:  # 閾値以上の場合のみ適用
                    enhanced = self.enhance_pitch_variation(enhanced, pitch_variation)
                
                # 速度変動（韻律）
                if speed_variation > 0.05:  # 閾値以上の場合のみ適用
                    enhanced = self.enhance_speed_variation(enhanced, speed_variation)
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
        """スペクトル強化処理 - 高周波数帯域を強調して明瞭さを向上させる"""
        # 音声データの長さに基づいてFFTサイズを調整
        n_fft = min(2048, 2**int(np.log2(len(audio_data))))
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
    
    def enhance_voice_quality(self, audio_data, enhancement_level=0.5):
        """声質向上処理 - 母音のフォルマント周波数を強調"""
        # 母音のフォルマント周波数を強調
        formant_freqs = {
            'a': [800, 1200],   # 'あ'の音
            'i': [300, 2500],   # 'い'の音
            'u': [300, 900],    # 'う'の音
            'e': [500, 1800],   # 'え'の音
            'o': [500, 1000]    # 'お'の音
        }
        
        enhanced_audio = audio_data.copy()
        
        for vowel, freqs in formant_freqs.items():
            for freq in freqs:
                # バンドパスフィルタの作成
                try:
                    freq_min = max(freq - 50, 20)
                    freq_max = min(freq + 50, self.sample_rate // 2 - 1)
                    
                    b, a = signal.butter(
                        2, 
                        [freq_min / (self.sample_rate/2), freq_max / (self.sample_rate/2)],
                        btype='band'
                    )
                    
                    # フィルタ適用
                    filtered = signal.lfilter(b, a, audio_data)
                    enhanced_audio += filtered * (enhancement_level * 0.2)
                except Exception as e:
                    print(f"フィルタ適用エラー: {e}")
        
        return enhanced_audio
    
    def add_breathiness(self, audio_data, breath_amount=0.2):
        """息の音を追加 - 声にリアルな息っぽさを加える"""
        # ホワイトノイズを生成
        noise = np.random.normal(0, 0.01, size=len(audio_data))
        
        # 息らしく整形するためのフィルタ
        b, a = signal.butter(2, 2000 / (self.sample_rate/2), btype='low')
        breath_noise = signal.lfilter(b, a, noise)
        
        # 音声の振幅に合わせて息の音を調整
        envelope = np.abs(audio_data)
        # 包絡線をスムージング
        window_size = min(1000, len(envelope) // 10)
        if window_size < 2:
            window_size = 2
        smoothed_env = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
        
        # 息の音を振幅に合わせて音声に加える
        breathy_audio = audio_data + breath_noise * smoothed_env * breath_amount
        
        return breathy_audio
    
    def add_natural_fluctuation(self, audio_data, fluctuation_rate=0.3):
        """自然な揺らぎを追加 - 機械的な安定さを軽減し自然さを向上"""
        # 微小なランダム変動を生成
        fluctuation = np.random.normal(1.0, fluctuation_rate * 0.05, size=len(audio_data))
        
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
    
    def enhance_pitch_variation(self, audio_data, variation_amount=0.4):
        """ピッチ変動の強化 - より自然な抑揚を追加"""
        # 音声を短いセグメントに分割
        segment_length = min(2048, len(audio_data) // 4)
        if segment_length < 256:
            return audio_data  # 音声が短すぎる場合は処理をスキップ
        
        hop_length = segment_length // 2
        
        # 結果を格納する配列
        result = np.zeros_like(audio_data)
        
        # 重みを格納する配列（オーバーラップ部分の処理用）
        weights = np.zeros_like(audio_data)
        
        # ウィンドウ関数
        window = np.hanning(segment_length)
        
        # 各セグメントを処理
        for i in range(0, len(audio_data) - segment_length, hop_length):
            # セグメントを取得
            segment = audio_data[i:i+segment_length].copy()
            
            # ごく小さなピッチシフト量（自然な変動）
            shift_amount = np.random.normal(0, variation_amount * 0.1)
            
            # 変動が小さすぎる場合はスキップ
            if abs(shift_amount) < 0.01:
                shifted_segment = segment
            else:
                try:
                    # ピッチシフト処理
                    shifted_segment = librosa.effects.pitch_shift(
                        segment, 
                        sr=self.sample_rate,
                        n_steps=shift_amount
                    )
                except Exception as e:
                    print(f"ピッチシフトエラー: {e}")
                    shifted_segment = segment
            
            # ウィンドウ関数を適用
            windowed_segment = shifted_segment * window
            
            # 結果に追加
            result[i:i+segment_length] += windowed_segment
            weights[i:i+segment_length] += window
        
        # 重みで正規化（オーバーラップしている部分の処理）
        weights[weights < 0.001] = 1.0  # ゼロ除算防止
        normalized_result = result / weights
        
        return normalized_result
    
    def enhance_speed_variation(self, audio_data, variation_amount=0.3):
        """速度変動の強化 - より自然な話速変化を追加"""
        # 基本的な実装 - 完全な話速変化は計算コストが高いため簡易実装
        # 実際のアプリケーションでは、より高度なタイムストレッチアルゴリズムを検討
        
        # 音声長が短い場合は処理をスキップ
        if len(audio_data) < 1000:
            return audio_data
        
        # 小さなランダム変動を加えるだけの簡易実装
        # これは本当の速度変化ではなく、単なる振幅変調
        modulation = 1.0 + np.sin(np.linspace(0, 10 * np.pi, len(audio_data))) * (variation_amount * 0.05)
        modulated_audio = audio_data * modulation
        
        return modulated_audio
    
    def normalize_audio(self, audio_data, target_level=0.9):
        """音声の正規化 - 音量を適切なレベルに調整"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * target_level
        return audio_data