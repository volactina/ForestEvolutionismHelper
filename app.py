# app.py
"""森林进化论游戏Web界面 - Flask后端"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
import sys
import traceback
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入游戏核心类
from forest import Game, Player, CardRank, CardSuit
from game_config import GameConfig, GameSaveData
from round_manager import RoundManager, EvolutionCard, run_with_round_manager

app = Flask(__name__)
app.secret_key = 'forest_evolution_game_secret_key'

# 全局游戏实例
game_instance = None
round_manager_instance = None

class WebGameWrapper:
    """Web游戏包装器，用于管理游戏状态"""
    
    def __init__(self):
        self.game = None
        self.round_manager = None
        self.initialized = False
        self.current_round = 0
        self.free_phase_start_time = None
        self.free_phase_duration = 15 * 60  # 默认15分钟，单位秒
        
    def init_game(self, player_count, no_blood_mode=False):
        """初始化游戏"""
        try:
            # 创建游戏实例
            self.game = Game()
            self.game.player_count = player_count
            
            # 设置游戏模式
            GameConfig.set_mode(no_blood_mode)
            
            # 创建玩家
            self.game.players = [Player(i+1) for i in range(player_count)]
            
            # 分配身份
            self.game._assign_identities()
            
            # 初始化血量
            if not no_blood_mode:
                for player in self.game.players:
                    player.blood = 20
                    player.trade = 0
                    player.is_alive = True
            
            # 添加初始化记录
            self.game.records.append(f"游戏初始化 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.game.records.append(f"玩家数量: {player_count}")
            self.game.records.append(f"游戏模式: {'无血量中控模式' if no_blood_mode else '标准模式'}")
            
            self.initialized = True
            return True, "游戏初始化成功"
        except Exception as e:
            return False, f"游戏初始化失败: {str(e)}"
    
    def init_round_manager(self, round1_cards, round2_cards, round3_cards, free_phase_minutes=15):
        """初始化轮次管理器"""
        try:
            self.round_manager = RoundManager(self.game)
            
            # 手动设置进化卡
            self.round_manager.round_cards = {1: [], 2: [], 3: []}
            self.round_manager.evolution_cards = []
            
            # 添加第1轮进化卡
            for card_id in round1_cards:
                if card_id in EvolutionCard.ROUND1_CARDS:
                    name = EvolutionCard.ROUND1_CARDS[card_id]
                    card = EvolutionCard(card_id, name)
                    self.round_manager.evolution_cards.append(card)
                    self.round_manager.round_cards[1].append(card)
            
            # 添加第2轮进化卡
            for card_id in round2_cards:
                if card_id in EvolutionCard.ROUND2_CARDS:
                    name = EvolutionCard.ROUND2_CARDS[card_id]
                    card = EvolutionCard(card_id, name)
                    self.round_manager.evolution_cards.append(card)
                    self.round_manager.round_cards[2].append(card)
            
            # 添加第3轮进化卡
            for card_id in round3_cards:
                if card_id in EvolutionCard.ROUND3_CARDS:
                    name = EvolutionCard.ROUND3_CARDS[card_id]
                    card = EvolutionCard(card_id, name)
                    self.round_manager.evolution_cards.append(card)
                    self.round_manager.round_cards[3].append(card)
            
            # 设置自由阶段时间
            self.round_manager.free_phase_minutes = free_phase_minutes
            
            # 设置当前轮次为1
            self.current_round = 1
            self.round_manager.current_round = 1
            
            return True, "轮次管理器初始化成功"
        except Exception as e:
            return False, f"轮次管理器初始化失败: {str(e)}"
    
    def start_round(self, round_num):
        """开始新轮次"""
        if not self.round_manager:
            return False, "轮次管理器未初始化"
        
        self.round_manager.start_round(round_num)
        self.current_round = round_num
        return True, f"第{round_num}大轮开始"
    
    def get_players_status(self):
        """获取所有玩家状态"""
        if not self.game:
            return []
        
        players_data = []
        for player in self.game.players:
            players_data.append({
                'no': player.no,
                'blood': player.blood,
                'trade': player.trade,
                'rank': str(player.rank.value) if player.rank else '',
                'suit': player.suit.value if player.suit else '',
                'is_alive': player.is_alive,
                'skills': player.skills.copy(),
                'display': str(player)
            })
        return players_data
    
    def modify_blood(self, player_no, amount, note=""):
        """修改血量"""
        if not self.game:
            return False, "游戏未初始化"
        
        try:
            self.game.modify_blood(player_no, amount, note)
            return True, f"玩家{player_no}血量修改成功"
        except Exception as e:
            return False, str(e)
    
    def trade(self, player1, player2, amount):
        """交易"""
        if not self.game:
            return False, "游戏未初始化"
        
        try:
            self.game.trade(player1, player2, amount)
            return True, f"交易成功"
        except Exception as e:
            return False, str(e)
    
    def hunt(self, hunter, prey, amount=None):
        """捕食"""
        if not self.game:
            return False, "游戏未初始化"
        
        try:
            if GameConfig.NO_BLOOD_MODE:
                self.game.hunt(hunter, prey)
            else:
                self.game.hunt(hunter, prey, amount)
            return True, f"捕食执行成功"
        except Exception as e:
            return False, str(e)
    
    def get_evolution_cards(self):
        """获取进化卡信息"""
        if not self.round_manager:
            return {}
        
        result = {}
        for round_num in [1, 2, 3]:
            cards = self.round_manager.round_cards.get(round_num, [])
            result[round_num] = [
                {
                    'card_id': c.card_id,
                    'name': c.name,
                    'owner': c.owner,
                    'round_obtained': c.round_obtained
                }
                for c in cards
            ]
        return result
    
    def auction_card(self, card_id, player_no, blood_cost):
        """拍卖进化卡"""
        if not self.round_manager:
            return False, "轮次管理器未初始化"
        
        # 查找对应的卡
        target_card = None
        for card in self.round_manager.round_cards.get(self.current_round, []):
            if card.card_id == card_id and card.owner is None:
                target_card = card
                break
        
        if not target_card:
            return False, "找不到可拍卖的进化卡"
        
        # 检查玩家是否存在
        if player_no < 1 or player_no > len(self.game.players):
            return False, "无效的玩家编号"
        
        player = self.game.players[player_no-1]
        if not player.is_alive:
            return False, "玩家已死亡"
        
        if player.blood <= blood_cost:
            return False, f"玩家血量不足 (当前: {player.blood}, 需要: {blood_cost})"
        
        # 执行拍卖
        player.blood -= blood_cost
        target_card.owner = player_no
        target_card.round_obtained = self.current_round
        player.add_skill(target_card.name)
        
        self.round_manager.auction_records.append({
            'card': target_card.card_id,
            'winner': player_no,
            'blood': blood_cost,
            'round': self.current_round
        })
        
        self.game.records.append(f"第{self.current_round}大轮 玩家{player_no} 拍得 {target_card} 消耗{blood_cost}血")
        
        return True, f"玩家{player_no} 拍得 {target_card.name}"


# 全局游戏包装器
game_wrapper = WebGameWrapper()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/init_game', methods=['POST'])
def api_init_game():
    """初始化游戏"""
    data = request.json
    player_count = data.get('player_count', 6)
    no_blood_mode = data.get('no_blood_mode', False)
    
    success, message = game_wrapper.init_game(player_count, no_blood_mode)
    
    return jsonify({
        'success': success,
        'message': message,
        'players': game_wrapper.get_players_status() if success else []
    })


@app.route('/api/init_round_manager', methods=['POST'])
def api_init_round_manager():
    """初始化轮次管理器"""
    data = request.json
    round1_cards = data.get('round1_cards', [])
    round2_cards = data.get('round2_cards', [])
    round3_cards = data.get('round3_cards', [])
    free_phase_minutes = data.get('free_phase_minutes', 15)
    
    success, message = game_wrapper.init_round_manager(
        round1_cards, round2_cards, round3_cards, free_phase_minutes
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'cards': game_wrapper.get_evolution_cards() if success else {}
    })


@app.route('/api/start_round', methods=['POST'])
def api_start_round():
    """开始轮次"""
    data = request.json
    round_num = data.get('round_num', 1)
    
    success, message = game_wrapper.start_round(round_num)
    
    return jsonify({
        'success': success,
        'message': message,
        'current_round': game_wrapper.current_round
    })


@app.route('/api/get_players', methods=['GET'])
def api_get_players():
    """获取玩家状态"""
    return jsonify({
        'success': True,
        'players': game_wrapper.get_players_status()
    })


@app.route('/api/modify_blood', methods=['POST'])
def api_modify_blood():
    """修改血量"""
    data = request.json
    player_no = data.get('player_no')
    amount = data.get('amount')
    note = data.get('note', '')
    
    success, message = game_wrapper.modify_blood(player_no, amount, note)
    
    return jsonify({
        'success': success,
        'message': message,
        'players': game_wrapper.get_players_status() if success else []
    })


@app.route('/api/trade', methods=['POST'])
def api_trade():
    """交易"""
    data = request.json
    player1 = data.get('player1')
    player2 = data.get('player2')
    amount = data.get('amount')
    
    success, message = game_wrapper.trade(player1, player2, amount)
    
    return jsonify({
        'success': success,
        'message': message,
        'players': game_wrapper.get_players_status() if success else []
    })


@app.route('/api/hunt', methods=['POST'])
def api_hunt():
    """捕食"""
    data = request.json
    hunter = data.get('hunter')
    prey = data.get('prey')
    amount = data.get('amount')
    
    success, message = game_wrapper.hunt(hunter, prey, amount)
    
    return jsonify({
        'success': success,
        'message': message,
        'players': game_wrapper.get_players_status() if success else []
    })


@app.route('/api/get_evolution_cards', methods=['GET'])
def api_get_evolution_cards():
    """获取进化卡信息"""
    return jsonify({
        'success': True,
        'cards': game_wrapper.get_evolution_cards()
    })


@app.route('/api/auction_card', methods=['POST'])
def api_auction_card():
    """拍卖进化卡"""
    data = request.json
    card_id = data.get('card_id')
    player_no = data.get('player_no')
    blood_cost = data.get('blood_cost')
    
    success, message = game_wrapper.auction_card(card_id, player_no, blood_cost)
    
    return jsonify({
        'success': success,
        'message': message,
        'players': game_wrapper.get_players_status() if success else [],
        'cards': game_wrapper.get_evolution_cards() if success else {}
    })


@app.route('/api/save_game', methods=['POST'])
def api_save_game():
    """保存游戏"""
    if game_wrapper.game:
        game_wrapper.game.save_game()
        return jsonify({'success': True, 'message': '游戏保存成功'})
    return jsonify({'success': False, 'message': '游戏未初始化'})


@app.route('/api/get_free_phase_status', methods=['GET'])
def api_get_free_phase_status():
    """获取自由阶段状态"""
    if not game_wrapper.round_manager:
        return jsonify({'success': False, 'message': '轮次管理器未初始化'})
    
    return jsonify({
        'success': True,
        'current_round': game_wrapper.current_round,
        'free_phase_minutes': game_wrapper.round_manager.free_phase_minutes
    })


if __name__ == '__main__':
    print("=" * 50)
    print("森林进化论游戏Web界面")
    print("=" * 50)
    print("尝试启动服务器...")
    print("如果端口5000被占用，将自动使用端口5001")
    print("您也可以手动指定端口: python app.py --port=8080")
    print("-" * 50)
    
    # 尝试多个端口
    ports_to_try = [5000, 5001, 5002, 5003, 8080, 8081]
    
    for port in ports_to_try:
        try:
            print(f"尝试启动在端口 {port}...")
            app.run(debug=True, host='0.0.0.0', port=5001)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"  端口 {port} 已被占用，尝试下一个...")
                continue
            else:
                print(f"  启动失败: {e}")
                break
