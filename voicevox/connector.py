"""VOICEVOXとの連携モジュール - VOICEVOXエンジンAPIとの通信を担当"""

import requests
import json
import os
import tempfile
import soundfile as sf
import numpy as np
import traceback

class VoicevoxConnector:
    """VOICEVOX音声合成エンジンとの連携クラス"""
    
    def __init__(self, host="127.0.0.1", port=50021):
        """初期化"""
        self.base_url = f"http://{host}:{port}"
        self.speakers = {}
        self.initialized = False
    
    def test_connection(self):
        """VOICEVOXサーバーへの接続テスト"""
        try:
            response = requests.get(f"{self.base_url}/version", timeout=3)
            if response.status_code == 200:
                print(f"VOICEVOX接続成功: バージョン {response.json()}")
                self.initialized = True
                return True
            else:
                print(f"VOICEVOX接続失敗: ステータスコード {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("VOICEVOX接続エラー: サーバーに接続できません")
            return False
        except Exception as e:
            print(f"VOICEVOX接続エラー: {e}")
            traceback.print_exc()
            return False
    
    def get_speakers(self):
        """利用可能な話者の一覧を取得"""
        if not self.initialized:
            if not self.test_connection():
                return False
        
        try:
            response = requests.get(f"{self.base_url}/speakers")
            if response.status_code == 200:
                speakers_data = response.json()
                self.speakers = {}
                
                for speaker in speakers_data:
                    for style in speaker["styles"]:
                        self.speakers[style["id"]] = f"{speaker['name']}（{style['name']}）"
                
                print(f"話者情報取得成功: {len(self.speakers)}件の話者スタイルを取得")
                return True
            else:
                print(f"話者一覧の取得に失敗しました: {response.status_code}")
                return False
        except Exception as e:
            print(f"話者一覧取得エラー: {e}")
            traceback.print_exc()
            return False
    
    def text_to_speech(self, text, speaker_id=1):
        """テキストから音声を合成"""
        if not text:
            raise ValueError("テキストが空です")
        
        if not self.initialized:
            if not self.test_connection():
                raise ConnectionError("VOICEVOXエンジンに接続できません")
        
        try:
            # 音声合成用のクエリを作成
            params = {"text": text, "speaker": speaker_id}
            print(f"音声クエリ作成開始: テキスト={text[:20]}..., 話者ID={speaker_id}")
            
            response = requests.post(
                f"{self.base_url}/audio_query",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"音声クエリの作成に失敗しました: {response.status_code}")
            
            query = response.json()
            print("音声クエリ作成成功")
            
            # 音声を合成
            params = {"speaker": speaker_id}
            print(f"音声合成開始: 話者ID={speaker_id}")
            
            response = requests.post(
                f"{self.base_url}/synthesis",
                headers={"Content-Type": "application/json"},
                params=params,
                data=json.dumps(query)
            )
            
            if response.status_code != 200:
                raise Exception(f"音声合成に失敗しました: {response.status_code}")
            
            print("音声合成成功")
            
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(response.content)
            
            print(f"一時ファイル作成: {temp_path}")
            
            # 音声データを読み込み
            audio_data, sample_rate = sf.read(temp_path)
            
            # 一時ファイル削除
            try:
                os.remove(temp_path)
                print("一時ファイル削除完了")
            except Exception as e:
                print(f"一時ファイル削除エラー: {e}")
            
            return audio_data, sample_rate
            
        except Exception as e:
            print(f"音声合成エラー: {e}")
            traceback.print_exc()
            raise