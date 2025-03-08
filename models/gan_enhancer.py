# models/gan_enhancer.py

import torch
import torch.nn as nn
import numpy as np
import librosa

class VoiceEnhancementGAN(nn.Module):
    def __init__(self, input_size=1024, hidden_size=512):
        super(VoiceEnhancementGAN, self).__init__()
        
        # ジェネレーターネットワーク
        self.generator = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(16),
            nn.LeakyReLU(0.2),
            nn.Conv1d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(32),
            nn.LeakyReLU(0.2),
            nn.Conv1d(32, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(16),
            nn.LeakyReLU(0.2),
            nn.Conv1d(16, 1, kernel_size=3, stride=1, padding=1),
            nn.Tanh()
        )
        
    def forward(self, x):
        """音声波形を入力し、強化された波形を出力"""
        # 入力形状の変換 (batch_size, sequence_length) -> (batch_size, 1, sequence_length)
        x = x.unsqueeze(1)
        # 生成器を通過
        enhanced = self.generator(x)
        # 出力形状を元に戻す
        return enhanced.squeeze(1)

class GANEnhancer:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = VoiceEnhancementGAN().to(self.device)
        
        # 事前学習済みモデルのロード
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
    def enhance(self, audio_data, sample_rate=24000, segment_size=16384, overlap=0.25):
        """音声データをGANモデルで強化"""
        # オーディオデータをモデル入力用に準備
        audio_tensor = torch.FloatTensor(audio_data).to(self.device)
        
        # 長い音声を処理するためのセグメント分割処理
        enhanced_segments = []
        segment_samples = segment_size
        hop_size = int(segment_samples * (1 - overlap))
        
        for start_idx in range(0, len(audio_data), hop_size):
            end_idx = min(start_idx + segment_samples, len(audio_data))
            segment = audio_tensor[start_idx:end_idx]
            
            # セグメントが短すぎる場合は0埋め
            if len(segment) < segment_samples:
                segment = torch.nn.functional.pad(
                    segment, (0, segment_samples - len(segment)), "constant", 0
                )
            
            # モデルによる強化
            with torch.no_grad():
                enhanced_segment = self.model(segment)
            
            # 強化されたセグメントを保存
            enhanced_segments.append(enhanced_segment.cpu().numpy())
        
        # オーバーラップを考慮したセグメントの結合
        enhanced_audio = np.zeros(len(audio_data))
        normalization = np.zeros(len(audio_data))
        
        # 三角窓関数で重み付け
        window = np.hanning(segment_samples)
        
        idx = 0
        for start_idx in range(0, len(audio_data), hop_size):
            end_idx = min(start_idx + segment_samples, len(audio_data))
            actual_segment_len = end_idx - start_idx
            
            # 強化されたセグメントを出力音声に追加
            segment_data = enhanced_segments[idx][:actual_segment_len]
            enhanced_audio[start_idx:end_idx] += segment_data * window[:actual_segment_len]
            normalization[start_idx:end_idx] += window[:actual_segment_len]
            
            idx += 1
        
        # 正規化（オーバーラップによる重複を調整）
        normalization[normalization < 1e-10] = 1.0  # ゼロ除算防止
        enhanced_audio /= normalization
        
        return enhanced_audio