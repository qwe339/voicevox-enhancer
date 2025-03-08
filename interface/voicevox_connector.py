# interface/voicevox_connector.py

import requests
import json
import numpy as np
import soundfile as sf
from io import BytesIO

class VoicevoxConnector:
    def __init__(self, host="127.0.0.1", port=50021):
        self.base_url = f"http://{host}:{port}"
    
    def get_audio_query(self, text, speaker_id=1):
        """テキストから音声合成用のクエリを作成"""
        params = {"text": text, "speaker": speaker_id}
        response = requests.post(
            f"{self.base_url}/audio_query",
            params=params
        )
        return response.json()
    
    def synthesize(self, query, speaker_id=1):
        """クエリから音声を合成"""
        params = {"speaker": speaker_id}
        response = requests.post(
            f"{self.base_url}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(query)
        )
        
        # 音声データをnumpy配列に変換
        audio_data, sample_rate = sf.read(BytesIO(response.content))
        return audio_data, sample_rate
    
    def text_to_speech(self, text, speaker_id=1):
        """テキストから直接音声を合成"""
        query = self.get_audio_query(text, speaker_id)
        return self.synthesize(query, speaker_id)