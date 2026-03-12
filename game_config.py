# game_config.py
"""游戏配置文件"""
import json
import datetime

class GameConfig:
    """游戏配置类"""
    
    # 是否启用无血量中控模式
    # True: 无血量中控模式（不维护血量，只判断捕食成功/失败）
    # False: 标准模式（维护血量）
    NO_BLOOD_MODE = False
    
    @classmethod
    def set_mode(cls, no_blood: bool):
        """设置游戏模式"""
        cls.NO_BLOOD_MODE = no_blood
        print(f"游戏模式已设置为: {'无血量中控模式' if no_blood else '标准模式'}")


class GameSaveData:
    """游戏存档数据类"""
    
    @staticmethod
    def save_game(game_state: dict, filename: str = None):
        """保存游戏状态到文件"""
        if filename is None:
            filename = f"save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, ensure_ascii=False, indent=2)
            print(f"游戏已保存到 {filename}")
            return filename
        except Exception as e:
            print(f"保存失败: {e}")
            return None
    
    @staticmethod
    def load_game(filename: str):
        """从文件加载游戏状态"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            print(f"成功从 {filename} 加载游戏")
            return game_state
        except FileNotFoundError:
            print(f"文件 {filename} 不存在！")
            return None
        except json.JSONDecodeError:
            print(f"文件 {filename} 格式错误！")
            return None
        except Exception as e:
            print(f"加载失败: {e}")
            return None
    
    @staticmethod
    def list_save_files():
        """列出所有存档文件"""
        import glob
        save_files = glob.glob("save_*.json")
        return sorted(save_files, reverse=True)
