# models/model_utils.py

import os
import torch
import numpy as np
import json

def save_model(model, path):
    """モデルを保存"""
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")

def load_model(model, path):
    """モデルをロード"""
    if os.path.exists(path):
        model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
        print(f"Model loaded from {path}")
        return True
    else:
        print(f"No model found at {path}")
        return False

class CharacterPreset:
    """キャラクターごとの最適化プリセット"""
    def __init__(self, character_id, name):
        self.character_id = character_id
        self.name = name
        self.parameters = {
            "spectrum_enhance": 0.5,
            "pitch_variation": 0.3,
            "vocal_texture": 0.2,
            "formant_clarity": 0.4,
            "breathiness": 0.3
        }
    
    def save(self, directory="presets"):
        """プリセットをJSONとして保存"""
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_path = os.path.join(directory, f"preset_{self.character_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "character_id": self.character_id,
                "name": self.name,
                "parameters": self.parameters
            }, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    @classmethod
    def load(cls, character_id, directory="presets"):
        """プリセットをロード"""
        file_path = os.path.join(directory, f"preset_{character_id}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        preset = cls(data["character_id"], data["name"])
        preset.parameters = data["parameters"]
        return preset