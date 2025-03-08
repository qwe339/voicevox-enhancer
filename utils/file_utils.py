"""ファイル操作ユーティリティ"""

import os
import json
import tempfile
import shutil
import soundfile as sf
import numpy as np

def ensure_dir(directory):
    """ディレクトリが存在することを確認し、必要なら作成する"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def sanitize_filename(filename):
    """ファイル名を安全な形式に変換"""
    # 使用できない文字を置換
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 長すぎる場合は切り詰める
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100] + ext
    
    return filename

def save_audio(audio_data, sample_rate, file_path):
    """音声データをファイルに保存"""
    # ディレクトリの存在確認
    directory = os.path.dirname(file_path)
    ensure_dir(directory)
    
    # 保存
    sf.write(file_path, audio_data, sample_rate)
    
    return os.path.exists(file_path)

def save_settings(settings, file_path):
    """設定をJSONファイルに保存"""
    # ディレクトリの存在確認
    directory = os.path.dirname(file_path)
    ensure_dir(directory)
    
    # 一時ファイルに書き込んでから移動（書き込みエラー防止）
    with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
        json.dump(settings, temp_file, indent=2, ensure_ascii=False)
        temp_path = temp_file.name
    
    # 完成したファイルを目的の場所に移動
    shutil.move(temp_path, file_path)
    
    return os.path.exists(file_path)

def load_settings(file_path):
    """設定をJSONファイルから読み込み"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_presets_list(preset_dir):
    """プリセットファイルの一覧を取得"""
    ensure_dir(preset_dir)
    
    presets = []
    for filename in os.listdir(preset_dir):
        if filename.endswith('.json'):
            preset_path = os.path.join(preset_dir, filename)
            try:
                preset_data = load_settings(preset_path)
                if preset_data and 'name' in preset_data:
                    presets.append({
                        'name': preset_data['name'],
                        'path': preset_path
                    })
            except:
                pass
    
    return presets