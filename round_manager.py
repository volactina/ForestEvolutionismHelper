# round_manager.py
"""轮次管理模块 - 独立处理游戏轮次和进化卡逻辑"""

import time
import random
import datetime
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from game_config import GameConfig

class EvolutionCard:
    """进化卡类"""
    
    # 轮次1进化卡
    ROUND1_CARDS = {
        "1-1": "鹰眼",
        "1-2": "尖刺",
        "1-3": "百毒不侵",
        "1-4": "基因突变",
        "1-5": "嗜血",
        "1-6": "剧毒"
    }
    
    # 轮次2进化卡
    ROUND2_CARDS = {
        "2-1": "两栖",
        "2-2": "寄生",
        "2-3": "大胃王",
        "2-4": "闪避",
        "2-5": "物种消亡",
        "2-6": "断尾",
        "2-7": "森林权杖"
    }
    
    # 轮次3进化卡
    ROUND3_CARDS = {
        "3-1": "巨大化",
        "3-2": "食腐",
        "3-3": "三头犬",
        "3-4": "狼王号召",
        "3-5": "替罪羊",
        "3-6": "冬眠",
        "3-7": "天敌血统"
    }
    
    # 所有轮次进化卡
    ALL_CARDS = {
        **ROUND1_CARDS,
        **ROUND2_CARDS,
        **ROUND3_CARDS
    }
    
    def __init__(self, card_id: str, name: str):
        self.card_id = card_id  # 卡牌编号，如 "1-1"
        self.name = name        # 卡牌名称
        self.owner = None       # 拥有者玩家编号
        self.round_obtained = None  # 获得的轮次
        
    def __str__(self) -> str:
        owner_info = f"玩家{self.owner}" if self.owner else "未拍出"
        return f"{self.card_id} {self.name} [{owner_info}]"


class RoundManager:
    """轮次管理器"""
    
    def __init__(self, game):
        self.game = game  # 关联主游戏实例
        self.current_round = 0  # 当前大轮 (1-4)
        self.round_phase = ""   # 当前阶段
        self.evolution_cards: List[EvolutionCard] = []  # 所有进化卡
        self.round_auction_cards: List[EvolutionCard] = []  # 当前轮次拍卖的进化卡
        self.auction_records: List[Dict] = []  # 拍卖记录
        self.round_cards = {1: [], 2: [], 3: []}  # 每轮对应的进化卡
        self.free_phase_minutes = 15  # 默认自由阶段时间
        
        # 自然保护区 - 存储每轮进入保护区的玩家
        self.nature_reserve_round1 = set()  # 第1轮自然保护区
        self.nature_reserve_round2 = set()  # 第2轮自然保护区
        
        # 当前捕食的状态
        self.current_hunt_index = 0  # 当前是第几次捕食 (0或1)
        self.hunt_first_round_pass = set()  # 当前捕食的第一圈pass的玩家
        self.hunt_second_round_pass = set()  # 当前捕食的第二圈pass的玩家
        self.hunt_victims = set()  # 当前捕食的被捕食玩家
        self.hunt_attackers = set()  # 当前捕食的主动捕食玩家
        
        # 整个大轮的记录
        self.round_all_victims = set()  # 整个大轮被捕食过的玩家
        self.round_all_pass_players = set()  # 整个大轮所有圈都pass的玩家
        
    def setup_evolution_cards(self):
        """初始化进化卡"""
        print("\n=== 初始化进化卡 ===")
        
        # 第1轮进化卡
        print("\n第1轮可选进化卡:")
        for card_id, name in EvolutionCard.ROUND1_CARDS.items():
            print(f"  {card_id}: {name}")
        round1_selected = self._select_cards("第1轮", list(EvolutionCard.ROUND1_CARDS.keys()))
        
        # 第2轮进化卡
        print("\n第2轮可选进化卡:")
        for card_id, name in EvolutionCard.ROUND2_CARDS.items():
            print(f"  {card_id}: {name}")
        round2_selected = self._select_cards("第2轮", list(EvolutionCard.ROUND2_CARDS.keys()))
        
        # 第3轮进化卡
        print("\n第3轮可选进化卡:")
        for card_id, name in EvolutionCard.ROUND3_CARDS.items():
            print(f"  {card_id}: {name}")
        round3_selected = self._select_cards("第3轮", list(EvolutionCard.ROUND3_CARDS.keys()))
        
        # 创建进化卡对象并按轮次分类
        self.round_cards[1] = []
        self.round_cards[2] = []
        self.round_cards[3] = []
        
        for card_id in round1_selected:
            name = EvolutionCard.ROUND1_CARDS[card_id]
            card = EvolutionCard(card_id, name)
            self.evolution_cards.append(card)
            self.round_cards[1].append(card)
        
        for card_id in round2_selected:
            name = EvolutionCard.ROUND2_CARDS[card_id]
            card = EvolutionCard(card_id, name)
            self.evolution_cards.append(card)
            self.round_cards[2].append(card)
        
        for card_id in round3_selected:
            name = EvolutionCard.ROUND3_CARDS[card_id]
            card = EvolutionCard(card_id, name)
            self.evolution_cards.append(card)
            self.round_cards[3].append(card)
        
        total_cards = len(self.evolution_cards)
        print(f"\n已选择 {total_cards} 张进化卡")
        
        # 显示每轮进化卡数量
        print(f"\n=== 进化卡分配 ===")
        print(f"第1轮: {len(self.round_cards[1])} 张")
        for card in self.round_cards[1]:
            print(f"  {card}")
        print(f"第2轮: {len(self.round_cards[2])} 张")
        for card in self.round_cards[2]:
            print(f"  {card}")
        print(f"第3轮: {len(self.round_cards[3])} 张")
        for card in self.round_cards[3]:
            print(f"  {card}")
        
        # 设置自由阶段时间
        self._setup_free_phase_time()
    
    def _select_cards(self, round_name: str, available_cards: List[str]) -> List[str]:
        """选择指定轮次的进化卡"""
        selected = []
        while True:
            try:
                choice = input(f"请选择{round_name}要使用的进化卡编号(多个用空格分隔，直接回车跳过): ").strip()
                if not choice:
                    break
                
                cards = choice.split()
                valid = True
                for card in cards:
                    if card not in available_cards:
                        print(f"无效卡牌编号: {card}")
                        valid = False
                        break
                
                if valid:
                    selected = cards
                    break
                else:
                    print("请重新选择")
            except Exception as e:
                print(f"输入错误: {e}")
        
        return selected
    
    def _setup_free_phase_time(self):
        """设置自由阶段时间"""
        print("\n=== 自由阶段时间设置 ===")
        print("默认自由阶段时间为15分钟")
        print("可以输入自定义时间（分钟），直接回车使用默认值")
        
        while True:
            try:
                time_input = input("请输入自由阶段时间(分钟) [15]: ").strip()
                if not time_input:
                    self.free_phase_minutes = 15
                    break
                
                minutes = int(time_input)
                if minutes > 0:
                    self.free_phase_minutes = minutes
                    break
                else:
                    print("时间必须大于0！")
            except ValueError:
                print("请输入有效的数字！")
        
        print(f"自由阶段时间设置为: {self.free_phase_minutes} 分钟")
    
    def start_round(self, round_num: int):
        """开始新大轮"""
        self.current_round = round_num
        print(f"\n{'='*50}")
        print(f"第 {round_num} 大轮开始")
        print(f"{'='*50}")
        
        # 重置自然保护区（每轮独立）
        if round_num == 1:
            self.nature_reserve_round1.clear()
        elif round_num == 2:
            self.nature_reserve_round2.clear()
        
        # 重置大轮记录
        self.round_all_victims = set()
        self.round_all_pass_players = set()
        
        # 记录
        self.game.records.append(f"第{round_num}大轮开始")
    
    def free_phase(self):
        """自由阶段"""
        self.round_phase = "自由阶段"
        
        print(f"\n--- 第{self.current_round}大轮 自由阶段 ({self.free_phase_minutes}分钟) ---")
        print("输入 'next' 提前结束自由阶段")
        print("可用命令:")
        print("  trade 1 2 5  - 交易血量")
        print("  mod 1 5      - 修改血量 (正数增加，负数减少)")
        print("  blood        - 查看血量/技能")
        print("  save         - 保存游戏")
        
        start_time = time.time()
        end_time = start_time + self.free_phase_minutes * 60
        
        while True:
            remaining = int(end_time - time.time())
            if remaining <= 0:
                print("\n自由阶段时间到！")
                break
            
            cmd = input(f"\n剩余 {remaining//60}:{remaining%60:02d} 分钟，输入命令: ").strip().lower()
            
            if cmd == 'next':
                print("自由阶段提前结束")
                break
            elif cmd.startswith('trade'):
                # 复用原有交易命令
                parts = cmd.split()
                if len(parts) == 4:
                    self.game.trade(int(parts[1]), int(parts[2]), int(parts[3]))
                else:
                    print("交易格式: trade 编号1 编号2 数值")
            elif cmd.startswith('mod'):
                # 修改血量命令
                parts = cmd.split()
                if len(parts) >= 3:
                    try:
                        player_no = int(parts[1])
                        blood_change = int(parts[2])
                        note = " ".join(parts[3:]) if len(parts) > 3 else ""
                        self.game.modify_blood(player_no, blood_change, note)
                    except ValueError:
                        print("请输入有效的数字")
                else:
                    print("修改血量格式: mod 编号 数值 [备注]")
            elif cmd == 'blood':
                self.game.view_blood()
            elif cmd == 'save':
                self.game.save_game()
            else:
                print("未知命令，可用命令: next, trade 1 2 5, mod 1 5, blood, save")
        
        self.game.records.append(f"第{self.current_round}大轮自由阶段结束")
    
    def get_predation_blood(self, round_num: int, hunt_index: int) -> int:
        """获取当前大轮、当前捕食次数的血量
        hunt_index: 0表示第1次捕食，1表示第2次捕食
        """
        blood_map = {
            1: [2],                    # 第1大轮: 只有1次捕食，血量2
            2: [3],                    # 第2大轮: 只有1次捕食，血量3
            3: [4, 5],                 # 第3大轮: 2次捕食，血量4和5
            4: [6, 7]                  # 第4大轮: 2次捕食，血量6和7
        }
        return blood_map[round_num][hunt_index]
    
    def predation_phase(self):
        """捕食阶段"""
        self.round_phase = "捕食阶段"
        
        # 确定本轮捕食次数
        hunt_times = 2 if self.current_round >= 3 else 1
        print(f"\n--- 第{self.current_round}大轮 捕食阶段 (共{hunt_times}次捕食) ---")
        
        # 确定先手玩家（每次捕食可能不同，但这里简化，假设整轮相同）
        first_player = self._get_first_player()
        print(f"先手玩家: 玩家{first_player}")
        
        # 进行多次捕食
        for hunt_index in range(hunt_times):
            blood_amount = self.get_predation_blood(self.current_round, hunt_index)
            self.current_hunt_index = hunt_index
            
            print(f"\n>>> 第{self.current_round}大轮 第{hunt_index+1}次捕食 (血量: {blood_amount}) <<<")
            
            # 重置本次捕食的状态
            self.hunt_first_round_pass = set()
            self.hunt_second_round_pass = set()
            self.hunt_victims = set()
            self.hunt_attackers = set()
            
            # 第一圈：所有存活玩家按顺序询问
            print("\n--- 第一圈 (所有存活玩家，可pass) ---")
            self._run_hunt_first_round(first_player, blood_amount)
            
            # 显示第一圈pass的玩家
            if self.hunt_first_round_pass:
                pass_players = sorted(list(self.hunt_first_round_pass))
                print(f"\n第一圈选择pass的玩家: {', '.join([str(p) for p in pass_players])}")
                
                # 第二圈：只询问第一圈pass的玩家
                print("\n--- 第二圈 (只询问第一圈pass的玩家，可pass) ---")
                self._run_hunt_second_round(first_player, blood_amount)
                
                # 显示第二圈pass的玩家
                if self.hunt_second_round_pass:
                    second_pass_players = sorted(list(self.hunt_second_round_pass))
                    print(f"\n第二圈选择pass的玩家: {', '.join([str(p) for p in second_pass_players])}")
            else:
                print("\n没有玩家在第一圈选择pass，第二圈跳过")
            
            # 更新整个大轮的记录
            self.round_all_victims.update(self.hunt_victims)
        
        # 所有捕食结束后，检查饥饿惩罚
        self._check_starvation_penalty()
        
        self.game.records.append(f"第{self.current_round}大轮捕食阶段结束")
    
    def _get_first_player(self) -> int:
        """获取先手玩家"""
        while True:
            try:
                first = int(input("请输入先手玩家编号: "))
                if 1 <= first <= len(self.game.players) and self.game.players[first-1].is_alive:
                    return first
                print("无效的玩家编号或玩家已死亡")
            except ValueError:
                print("请输入数字")
    
    def _run_hunt_first_round(self, first_player: int, blood_amount: int):
        """执行一次捕食的第一圈（所有存活玩家）"""
        player_count = len(self.game.players)
        start_idx = first_player - 1
        
        for i in range(player_count):
            current_idx = (start_idx + i) % player_count
            current_player = self.game.players[current_idx]
            player_no = current_player.no
            
            if not current_player.is_alive:
                continue
            
            # 检查是否在自然保护区
            in_reserve = self._in_nature_reserve(player_no)
            if in_reserve:
                print(f"玩家{player_no}在自然保护区中（只能主动捕食，不能被选为对象）")
            
            # 处理第一圈回合
            self._handle_hunt_first_round_turn(player_no, blood_amount, in_reserve)
    
    def _run_hunt_second_round(self, first_player: int, blood_amount: int):
        """执行一次捕食的第二圈（只询问第一圈pass的玩家）"""
        player_count = len(self.game.players)
        start_idx = first_player - 1
        
        # 初始化第二圈pass记录
        self.hunt_second_round_pass = set()
        
        # 按顺序收集第一圈pass的玩家
        pass_players_in_order = []
        for i in range(player_count):
            current_idx = (start_idx + i) % player_count
            player_no = current_idx + 1
            if player_no in self.hunt_first_round_pass and self.game.players[current_idx].is_alive:
                pass_players_in_order.append(player_no)
        
        if not pass_players_in_order:
            return
        
        print(f"第二圈按顺序询问玩家: {', '.join([str(p) for p in pass_players_in_order])}")
        
        for player_no in pass_players_in_order:
            current_player = self.game.players[player_no-1]
            
            # 检查玩家是否还存活
            if not current_player.is_alive:
                continue
            
            # 检查是否在自然保护区
            in_reserve = self._in_nature_reserve(player_no)
            if in_reserve:
                print(f"玩家{player_no}在自然保护区中（只能主动捕食，不能被选为对象）")
            
            # 处理第二圈回合
            self._handle_hunt_second_round_turn(player_no, blood_amount, in_reserve)
    
    def _handle_hunt_first_round_turn(self, player_no: int, blood_amount: int, in_reserve: bool):
        """处理一次捕食的第一圈回合"""
        # 构建提示信息
        prompt = f"玩家{player_no} 第一圈 请选择捕食对象"
        if in_reserve:
            prompt += " [在自然保护区中]"
        prompt += " (输入p跳过): "
        
        while True:
            choice = input(prompt).strip().lower()
            
            if choice == 'p':
                print(f"玩家{player_no} 第一圈选择pass")
                self.hunt_first_round_pass.add(player_no)
                self.game.records.append(f"第{self.current_round}大轮第{self.current_hunt_index+1}次捕食第一圈 玩家{player_no} pass")
                break
            
            try:
                target = int(choice)
                if target == player_no:
                    print("不能捕食自己")
                    continue
                
                if target < 1 or target > len(self.game.players):
                    print("无效的玩家编号")
                    continue
                
                target_player = self.game.players[target-1]
                if not target_player.is_alive:
                    print("目标玩家已死亡")
                    continue
                
                # 检查目标是否在自然保护区（前2轮）
                if self._in_nature_reserve(target):
                    print(f"目标玩家{target}在自然保护区中，无法被选中")
                    continue
                
                # 执行捕食
                self._execute_hunt(player_no, target, blood_amount)
                break
                
            except ValueError:
                print("请输入有效数字或p")
    
    def _handle_hunt_second_round_turn(self, player_no: int, blood_amount: int, in_reserve: bool):
        """处理一次捕食的第二圈回合"""
        # 构建提示信息
        prompt = f"玩家{player_no} 第二圈 请选择捕食对象 [第一圈pass]"
        if in_reserve:
            prompt += " [在自然保护区中]"
        prompt += " (输入p跳过): "
        
        while True:
            choice = input(prompt).strip().lower()
            
            if choice == 'p':
                print(f"玩家{player_no} 第二圈选择pass")
                self.hunt_second_round_pass.add(player_no)
                self.game.records.append(f"第{self.current_round}大轮第{self.current_hunt_index+1}次捕食第二圈 玩家{player_no} pass")
                break
            
            try:
                target = int(choice)
                if target == player_no:
                    print("不能捕食自己")
                    continue
                
                if target < 1 or target > len(self.game.players):
                    print("无效的玩家编号")
                    continue
                
                target_player = self.game.players[target-1]
                if not target_player.is_alive:
                    print("目标玩家已死亡")
                    continue
                
                # 检查目标是否在自然保护区（前2轮）
                if self._in_nature_reserve(target):
                    print(f"目标玩家{target}在自然保护区中，无法被选中")
                    continue
                
                # 执行捕食
                self._execute_hunt(player_no, target, blood_amount)
                break
                
            except ValueError:
                print("请输入有效数字")
    
    def _execute_hunt(self, attacker: int, target: int, blood_amount: int):
        """执行捕食并处理自然保护区"""
        # 记录捕食前的克制关系
        p1 = self.game.players[attacker-1]
        p2 = self.game.players[target-1]
        result = self.game._check_restraint(p1, p2)
        
        # 记录攻击者
        self.hunt_attackers.add(attacker)
        
        # 执行捕食
        self.game.hunt(attacker, target, blood_amount)
        
        # 记录被捕食（用于饥饿惩罚判断）
        self.hunt_victims.add(target)
        
        # 自然保护区规则（仅前2轮）
        if self.current_round <= 2:
            if result == -1:
                # 捕食方失败，捕食方进自然保护区
                self._add_to_nature_reserve(attacker)
                print(f"玩家{attacker} 捕食失败，进入自然保护区")
            elif result == 1:
                # 捕食方成功，被捕食方失败，被捕食方进自然保护区
                self._add_to_nature_reserve(target)
                print(f"玩家{target} 被捕食失败，进入自然保护区")
            # 平局：双方都不进自然保护区
    
    def _check_starvation_penalty(self):
        """检查饥饿惩罚"""
        if self.current_round == 1:
            blood_amount = 2
        elif self.current_round == 2:
            blood_amount = 3
        elif self.current_round == 3:
            blood_amount = 4
        else:  # 第4轮
            blood_amount = 6
        
        print(f"\n--- 检查饥饿惩罚 (血量: {blood_amount}) ---")
        
        # 收集所有存活玩家
        starved_players = []
        
        # 对于第1-2大轮（只有1次捕食）
        if self.current_round <= 2:
            # 获取第一圈和第二圈都pass的玩家
            both_rounds_pass = self.hunt_first_round_pass.intersection(self.hunt_second_round_pass)
            
            for player_no in both_rounds_pass:
                # 检查是否被捕食过
                if player_no not in self.hunt_victims:
                    starved_players.append(player_no)
        
        # 对于第3-4大轮（有2次捕食）
        else:
            # 这里需要更复杂的逻辑，记录两次捕食的pass情况
            # 由于状态管理复杂，暂时简化处理
            # 实际应该记录两次捕食中每圈的情况
            pass
        
        # 执行饥饿惩罚
        for player_no in starved_players:
            player = self.game.players[player_no-1]
            player.blood -= blood_amount
            print(f"玩家{player_no} 两圈都选择pass且未被捕食，饥饿惩罚，损失{blood_amount}点血")
            self.game.records.append(f"第{self.current_round}大轮 玩家{player_no} 饥饿惩罚 -{blood_amount}")
            
            if player.blood <= 0:
                player.blood = 0
                player.is_alive = False
                print(f"玩家{player_no} 因饥饿死亡！")
        
        if not starved_players:
            print("没有玩家受到饥饿惩罚")
        else:
            print(f"受惩罚玩家: {', '.join([str(p) for p in sorted(starved_players)])}")
    
    def _in_nature_reserve(self, player_no: int) -> bool:
        """检查玩家是否在当前轮次的自然保护区"""
        if self.current_round == 1:
            return player_no in self.nature_reserve_round1
        elif self.current_round == 2:
            return player_no in self.nature_reserve_round2
        return False
    
    def _add_to_nature_reserve(self, player_no: int):
        """将玩家加入自然保护区"""
        if self.current_round == 1:
            self.nature_reserve_round1.add(player_no)
            self.game.records.append(f"第1大轮 玩家{player_no} 进入自然保护区")
        elif self.current_round == 2:
            self.nature_reserve_round2.add(player_no)
            self.game.records.append(f"第2大轮 玩家{player_no} 进入自然保护区")
    
    def evolution_phase(self):
        """进化阶段"""
        self.round_phase = "进化阶段"
        print(f"\n--- 第{self.current_round}大轮 进化阶段 ---")
        
        # 显示当前所有玩家的血量
        print("\n【当前玩家血量】")
        self.game.view_blood()
        
        if self.current_round > 3:
            print("第4轮没有进化阶段")
            return
        
        # 获取本轮对应的进化卡
        round_cards = self.round_cards.get(self.current_round, [])
        if not round_cards:
            print(f"第{self.current_round}轮没有进化卡")
            return
        
        # 过滤掉已经拍出的卡
        available_cards = [c for c in round_cards if c.owner is None]
        
        if not available_cards:
            print(f"第{self.current_round}轮的所有进化卡都已拍出")
            return
        
        print(f"\n本轮有 {len(available_cards)} 张进化卡可供拍卖:")
        for i, card in enumerate(available_cards, 1):
            print(f"  {i}. {card}")
        
        # 逐一拍卖
        self.round_auction_cards = available_cards
        for card in self.round_auction_cards:
            self._auction_card(card)
        
        self.game.records.append(f"第{self.current_round}大轮进化阶段结束")
    
    def _auction_card(self, card: EvolutionCard):
        """拍卖单张进化卡"""
        print(f"\n拍卖: {card}")
        
        while True:
            try:
                bid_input = input("请输入拍下玩家编号和消耗血量(格式: 编号 血量，输入0跳过): ").strip()
                if bid_input == '0':
                    print(f"{card} 流拍")
                    self.auction_records.append({
                        'card': card.card_id,
                        'winner': None,
                        'blood': 0,
                        'round': self.current_round
                    })
                    break
                
                parts = bid_input.split()
                if len(parts) != 2:
                    print("格式错误，应为: 编号 血量")
                    continue
                
                player_no = int(parts[0])
                blood_cost = int(parts[1])
                
                if player_no < 1 or player_no > len(self.game.players):
                    print("无效的玩家编号")
                    continue
                
                player = self.game.players[player_no-1]
                if not player.is_alive:
                    print("玩家已死亡")
                    continue
                
                if player.blood <= blood_cost:
                    print(f"玩家血量不足 (当前: {player.blood}, 需要: {blood_cost})")
                    continue
                
                # 扣血并分配卡牌
                player.blood -= blood_cost
                card.owner = player_no
                card.round_obtained = self.current_round
                
                # 给玩家添加技能
                player.add_skill(card.name)
                
                print(f"玩家{player_no} 拍得 {card}，消耗 {blood_cost} 点血")
                print(f"玩家{player_no} 剩余血量: {player.blood}")
                print(f"玩家{player_no} 获得技能: {card.name}")
                
                self.auction_records.append({
                    'card': card.card_id,
                    'winner': player_no,
                    'blood': blood_cost,
                    'round': self.current_round
                })
                
                self.game.records.append(f"第{self.current_round}大轮 玩家{player_no} 拍得 {card} 消耗{blood_cost}血")
                break
                
            except ValueError:
                print("请输入数字")
    
    def end_round(self):
        """结束当前大轮"""
        print(f"\n第{self.current_round}大轮结束")
        self.game.view_blood()
        self.game.records.append(f"第{self.current_round}大轮结束")
        
        # 自动保存
        self.game.save_game()
    
    def show_summary(self):
        """显示游戏总结"""
        print("\n" + "="*50)
        print("游戏总结")
        print("="*50)
        
        # 显示进化卡获得情况
        print("\n进化卡获得情况:")
        owned_cards = [c for c in self.evolution_cards if c.owner]
        for card in owned_cards:
            # 查找拥有该技能的玩家
            owner_player = self.game.players[card.owner-1] if card.owner else None
            if owner_player:
                print(f"  玩家{card.owner}: {card} (血量: {owner_player.blood})")
            else:
                print(f"  玩家{card.owner}: {card}")
        
        # 显示未拍出的卡
        unowned_cards = [c for c in self.evolution_cards if c.owner is None]
        if unowned_cards:
            print("\n未拍出的进化卡:")
            for card in unowned_cards:
                print(f"  {card}")
        
        # 显示拍卖记录
        print("\n拍卖记录:")
        for record in self.auction_records:
            if record['winner']:
                print(f"  第{record['round']}大轮: {record['card']} -> 玩家{record['winner']} ({record['blood']}血)")
            else:
                print(f"  第{record['round']}大轮: {record['card']} 流拍")


def run_with_round_manager(game):
    """使用轮次管理器运行游戏"""
    print("\n=== 轮次管理助手 ===")
    print("是否启动轮次管理助手？")
    print("1. 是 - 使用轮次管理进行游戏")
    print("2. 否 - 使用原有模式")
    
    while True:
        choice = input("请选择(1或2): ").strip()
        if choice == '1':
            return True
        elif choice == '2':
            return False
        else:
            print("请输入1或2！")
