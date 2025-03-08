"""音声エフェクトモジュール"""

import numpy as np
import librosa
import scipy.signal as signal

def add_breathing(audio_data, sample_rate, breath_amount=0.1):
    """息の音を追加するエフェクト"""
    # 息の音のシミュレーション（ホワイトノイズをフィルタリング）
    noise = np.random.normal(0, 0.01, size=len(audio_data))
    
    # 低域通過フィルタで息の音らしく
    b, a = signal.butter(2, 2000 / (sample_rate/2), btype='low')
    breath = signal.lfilter(b, a, noise)
    
    # 音声の振幅に合わせて息の音の強さを調整
    envelope = np.abs(audio_data)
    envelope = np.convolve(envelope, np.ones(1000)/1000, mode='same')
    
    # 音声に息の音を混ぜる
    result = audio_data + breath * envelope * breath_amount
    
    return result

def adjust_pitch_variation(audio_data, sample_rate, variation_amount=0.3):
    """ピッチ変動の自然さを調整"""
    if variation_amount <= 0:
        return audio_data
    
    # 短いセグメントに分割して処理
    segment_length = int(0.05 * sample_rate)  # 50ms
    hop_length = segment_length // 2
    
    # 結果を格納する配列
    result = np.zeros_like(audio_data)
    
    # 重みを格納する配列（オーバーラップ部分の処理用）
    weights = np.zeros_like(audio_data)
    
    # ウィンドウ関数
    window = np.hanning(segment_length)
    
    for i in range(0, len(audio_data) - segment_length, hop_length):
        # セグメントを取得
        segment = audio_data[i:i+segment_length].copy()
        
        # ランダムなピッチシフト量
        shift_amount = np.random.normal(0, variation_amount * 0.5)
        
        # ピッチシフト（非常に小さい変動）
        if abs(shift_amount) > 0.01:
            try:
                shifted_segment = librosa.effects.pitch_shift(
                    segment, 
                    sr=sample_rate,
                    n_steps=shift_amount,
                    bins_per_octave=12
                )
            except:
                shifted_segment = segment
        else:
            shifted_segment = segment
        
        # ウィンドウ関数を適用
        shifted_segment = shifted_segment * window
        
        # 結果に追加
        result[i:i+segment_length] += shifted_segment
        weights[i:i+segment_length] += window
    
    # 重みで正規化（オーバーラップしている部分の処理）
    weights[weights < 0.001] = 1.0  # ゼロ除算防止
    result = result / weights
    
    return result

def adjust_speed_variation(audio_data, sample_rate, variation_amount=0.3):
    """話速変動の自然さを調整"""
    if variation_amount <= 0:
        return audio_data
    
    # 短いセグメントに分割して処理
    segment_length = int(0.2 * sample_rate)  # 200ms
    hop_length = int(segment_length * 0.75)  # 75%のオーバーラップ
    
    # 結果を格納する配列（長さは変わる可能性がある）
    result = np.zeros(len(audio_data) + int(len(audio_data) * variation_amount * 0.5))
    
    # 重みを格納する配列
    weights = np.zeros_like(result)
    
    # ウィンドウ関数
    window = np.hanning(segment_length)
    
    # 出力位置のトラッキング
    output_pos = 0
    
    for i in range(0, len(audio_data) - segment_length, hop_length):
        # セグメントを取得
        segment = audio_data[i:i+segment_length].copy()
        
        # ランダムな速度変化（わずかな伸縮）
        speed_factor = 1.0 + np.random.normal(0, variation_amount * 0.1)
        if speed_factor <= 0.8:
            speed_factor = 0.8
        elif speed_factor >= 1.2:
            speed_factor = 1.2
        
        # 速度変化をシミュレート（単純な方法）
        if speed_factor != 1.0:
            try:
                # 時間軸の長さを変えずに内容を伸縮
                segment = segment * window
            except:
                pass
        
        # 出力位置が配列の範囲内かチェック
        if output_pos + segment_length <= len(result):
            # ウィンドウ関数を適用したセグメントを結果に追加
            result[output_pos:output_pos+segment_length] += segment * window
            weights[output_pos:output_pos+segment_length] += window
        
        # 出力位置を更新（速度変化に応じて）
        output_pos += int(hop_length * speed_factor)
    
    # 有効な部分のみを取得
    valid_length = np.max(np.nonzero(weights)[0]) + 1
    result = result[:valid_length]
    weights = weights[:valid_length]
    
    # 重みで正規化
    weights[weights < 0.001] = 1.0  # ゼロ除算防止
    result = result / weights
    
    # 元の長さにリサンプリング
    if len(result) != len(audio_data):
        result = librosa.resample(
            result, 
            orig_sr=len(result),
            target_sr=len(audio_data)
        )
    
    return result