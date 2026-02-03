import random
import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple

class CardRank(Enum):
    """卡牌点数"""
    K = "K"
    Q = "Q"
    J = "J"
    JOKER = "Joker"

class CardSuit(Enum):
    """卡牌花色"""
    SPADE = "黑桃"
    HEART = "红桃"
    CLUB = "梅花"
    DIAMOND = "方片"
    JOKER = "Joker"

class Player:
    """玩家类"""
    def __init__(self, no: int):
        self.no = no  # 玩家编号
        self.blood = 20  # 当前血量
        self.trade = 0  # 交易血量
        self.rank: Optional[CardRank] = None  # 身份牌点数
        self.suit: Optional[CardSuit] = None  # 身份牌花色
        self.is_alive = True
        
    def __str__(self) -> str:
        if self.suit == CardSuit.JOKER or self.rank == CardRank.JOKER:
            return f"玩家{self.no}: Joker"
        return f"玩家{self.no}: {self.suit.value}{self.rank.value}"
    
    def get_info(self) -> str:
        """获取玩家完整信息"""
        return f"{str(self)} | 血量: {self.blood} | 交易血量: {self.trade} | 状态: {'存活' if self.is_alive else '死亡'}"

class Game:
    """游戏主类"""
    def __init__(self):
        self.players: List[Player] = []
        self.records: List[str] = []
        self.player_count = 0
        self.joker_count = 0
        
    def setup_game(self):
        """初始化游戏"""
        print("=== 游戏初始化 ===")
        
        # 1. 设置游玩人数
        while True:
            try:
                self.player_count = int(input("请输入游玩人数(6-13人): "))
                if 6 <= self.player_count <= 13:
                    break
                print("人数必须在6-13人之间！")
            except ValueError:
                print("请输入有效的数字！")
        
        # 创建玩家
        self.players = [Player(i+1) for i in range(self.player_count)]
        
        # 2. 分配身份
        self._assign_identities()
        
        # 打印所有玩家身份
        print("\n=== 玩家身份分配 ===")
        for player in self.players:
            print(str(player))
        
        # 3. 初始化血量
        for player in self.players:
            player.blood = 20
            player.trade = 0
            player.is_alive = True
            
        # 添加初始化记录
        self.records.append(f"游戏初始化 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.records.append(f"玩家数量: {self.player_count}")
        for player in self.players:
            self.records.append(f"玩家{player.no}: {str(player)} 初始血量20")
            
        print("\n游戏初始化完成！")
        
    def _assign_identities(self):
        """根据人数分配身份"""
        all_cards = []
        
        if self.player_count == 13:
            # 4种花色的kqj + joker
            suits = [CardSuit.SPADE, CardSuit.HEART, CardSuit.CLUB, CardSuit.DIAMOND]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            self.joker_count = 1
            
        elif self.player_count == 12:
            # 4种花色的kqj
            suits = [CardSuit.SPADE, CardSuit.HEART, CardSuit.CLUB, CardSuit.DIAMOND]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            self.joker_count = 0
            
        elif self.player_count == 11:
            # 黑桃、红桃、梅花的kqj + 2个joker
            suits = [CardSuit.SPADE, CardSuit.HEART, CardSuit.CLUB]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            self.joker_count = 2
            
        elif self.player_count == 10:
            # 黑桃、红桃、梅花的kqj + 1个joker
            suits = [CardSuit.SPADE, CardSuit.HEART, CardSuit.CLUB]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            self.joker_count = 1
            
        elif self.player_count == 9:
            # 黑桃、红桃、梅花的kqj
            suits = [CardSuit.SPADE, CardSuit.HEART, CardSuit.CLUB]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            self.joker_count = 0
            
        elif self.player_count == 8:
            # 黑桃、红桃的kqj + 2个joker
            suits = [CardSuit.SPADE, CardSuit.HEART]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            self.joker_count = 2
            
        elif self.player_count == 7:
            # 黑桃、红桃的kqj + 1个joker
            suits = [CardSuit.SPADE, CardSuit.HEART]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            all_cards.append((CardSuit.JOKER, CardRank.JOKER))
            self.joker_count = 1
            
        elif self.player_count == 6:
            # 黑桃、红桃的kqj
            suits = [CardSuit.SPADE, CardSuit.HEART]
            ranks = [CardRank.K, CardRank.Q, CardRank.J]
            for suit in suits:
                for rank in ranks:
                    all_cards.append((suit, rank))
            self.joker_count = 0
            
        # 洗牌并分配
        random.shuffle(all_cards)
        for i, player in enumerate(self.players):
            suit, rank = all_cards[i]
            player.suit = suit
            player.rank = rank
    
    def _check_restraint(self, player1: Player, player2: Player) -> int:
        """
        检查克制关系
        返回: 1表示player1克制player2, -1表示player2克制player1, 0表示平局
        """
        # 处理Joker的特殊情况
        if player1.rank == CardRank.JOKER and player2.rank == CardRank.JOKER:
            if self.player_count in [11, 8]:  # 11人局和8人局有多个joker
                return 0  # joker之间打平
            return 1  # joker > 任意牌
        
        if player1.rank == CardRank.JOKER:
            return 1  # joker > 任意牌
        if player2.rank == CardRank.JOKER:
            return 1  # 任意牌 > joker
            
        # 检查点数克制
        rank_order = {CardRank.K: 3, CardRank.Q: 2, CardRank.J: 1}
        rank1 = rank_order[player1.rank]
        rank2 = rank_order[player2.rank]
        
        # K>Q>J>K的循环克制
        if (rank1 == 3 and rank2 == 2) or (rank1 == 2 and rank2 == 1) or (rank1 == 1 and rank2 == 3):
            return 1
        elif (rank2 == 3 and rank1 == 2) or (rank2 == 2 and rank1 == 1) or (rank2 == 1 and rank1 == 3):
            return -1
        
        # 点数相同，检查花色克制
        if self.player_count in [13, 12]:
            # 13/12人局：黑桃>红桃>梅花>方片>黑桃
            suit_order = {
                CardSuit.SPADE: 4,
                CardSuit.HEART: 3,
                CardSuit.CLUB: 2,
                CardSuit.DIAMOND: 1
            }
            suit1 = suit_order[player1.suit]
            suit2 = suit_order[player2.suit]
            
            # 检查是否打平
            if (player1.suit == CardSuit.SPADE and player2.suit == CardSuit.CLUB) or \
               (player1.suit == CardSuit.CLUB and player2.suit == CardSuit.SPADE) or \
               (player1.suit == CardSuit.HEART and player2.suit == CardSuit.DIAMOND) or \
               (player1.suit == CardSuit.DIAMOND and player2.suit == CardSuit.HEART):
                return 0
            
            # 循环克制
            if (suit1 == 4 and suit2 == 3) or (suit1 == 3 and suit2 == 2) or \
               (suit1 == 2 and suit2 == 1) or (suit1 == 1 and suit2 == 4):
                return 1
            elif (suit2 == 4 and suit1 == 3) or (suit2 == 3 and suit1 == 2) or \
                 (suit2 == 2 and suit1 == 1) or (suit2 == 1 and suit1 == 4):
                return -1
                
        elif self.player_count in [11, 10, 9]:
            # 11/10/9人局：黑桃>红桃>梅花>黑桃
            suit_order = {
                CardSuit.SPADE: 3,
                CardSuit.HEART: 2,
                CardSuit.CLUB: 1
            }
            suit1 = suit_order[player1.suit]
            suit2 = suit_order[player2.suit]
            
            # 循环克制
            if (suit1 == 3 and suit2 == 2) or (suit1 == 2 and suit2 == 1) or (suit1 == 1 and suit2 == 3):
                return 1
            elif (suit2 == 3 and suit1 == 2) or (suit2 == 2 and suit1 == 1) or (suit2 == 1 and suit1 == 3):
                return -1
                
        elif self.player_count in [8, 7, 6]:
            # 8/7/6人局：黑桃>红桃>黑桃
            if player1.suit == CardSuit.SPADE and player2.suit == CardSuit.HEART:
                return 1
            elif player1.suit == CardSuit.HEART and player2.suit == CardSuit.SPADE:
                return -1
        
        return 0  # 默认平局
    
    def trade(self, player1_no: int, player2_no: int, k: int):
        """交易功能"""
        try:
            p1 = self.players[player1_no-1]
            p2 = self.players[player2_no-1]
            
            if not p1.is_alive or not p2.is_alive:
                print("交易失败：有玩家已死亡！")
                return
                
            # 检查交易血量是否超过10
            if p2.trade + k > 10:
                print("交易失败：玩家{}的交易血量将超过10！".format(player2_no))
                return
                
            # 检查玩家1是否有足够血量
            if p1.blood < k:
                print("交易失败：玩家{}血量不足！".format(player1_no))
                return
                
            # 执行交易
            p1.blood -= k
            p2.blood += k
            p1.trade -= k
            p2.trade += k
            
            record = f"交易 - 玩家{player1_no} -> 玩家{player2_no}: {k}点血"
            self.records.append(record)
            print(f"交易成功！{record}")
            print(f"玩家{player1_no}血量: {p1.blood}, 交易血量: {p1.trade}")
            print(f"玩家{player2_no}血量: {p2.blood}, 交易血量: {p2.trade}")
            
            # 自动执行导出
            self.export_data()
            
        except IndexError:
            print("玩家编号不存在！")
            
    def hunt(self, player1_no: int, player2_no: int, k: int):
        """捕食功能"""
        try:
            p1 = self.players[player1_no-1]
            p2 = self.players[player2_no-1]
            
            if not p1.is_alive or not p2.is_alive:
                print("捕食失败：有玩家已死亡！")
                return
                
            # 检查克制关系
            result = self._check_restraint(p1, p2)
            
            if result == 1:  # player1克制player2
                print(f"捕食成功！玩家{player1_no}克制玩家{player2_no}")
                
                if p2.blood <= k:  # player2死亡
                    reward = p2.blood + 3
                    p1.blood += reward
                    p2.blood = 0
                    p2.is_alive = False
                    
                    record = f"捕食 - 玩家{player1_no}捕食玩家{player2_no}成功，玩家{player2_no}死亡，玩家{player1_no}获得{reward}点血"
                    self.records.append(record)
                    print(f"玩家{player2_no}死亡！玩家{player1_no}获得{reward}点血奖励")
                    
                else:  # player2存活
                    p1.blood += k
                    p2.blood -= k
                    record = f"捕食 - 玩家{player1_no}捕食玩家{player2_no}成功: {k}点血"
                    self.records.append(record)
                    print(f"玩家{player1_no}获得{k}点血，玩家{player2_no}损失{k}点血")
                    
            elif result == -1:  # player2克制player1
                print(f"捕食失败！玩家{player2_no}克制玩家{player1_no}")
                
                if p1.blood <= k:  # player1死亡
                    reward = p1.blood + 3
                    p2.blood += reward
                    p1.blood = 0
                    p1.is_alive = False
                    
                    record = f"捕食 - 玩家{player1_no}捕食玩家{player2_no}失败，玩家{player1_no}死亡，玩家{player2_no}获得{reward}点血"
                    self.records.append(record)
                    print(f"玩家{player1_no}死亡！玩家{player2_no}获得{reward}点血奖励")
                    
                else:  # player1存活
                    p2.blood += k
                    p1.blood -= k
                    record = f"捕食 - 玩家{player1_no}捕食玩家{player2_no}失败: 玩家{player2_no}获得{k}点血"
                    self.records.append(record)
                    print(f"玩家{player2_no}获得{k}点血，玩家{player1_no}损失{k}点血")
                    
            else:  # 平局
                print("捕食无效：双方身份打平！")
                record = f"捕食 - 玩家{player1_no}与玩家{player2_no}打平"
                self.records.append(record)
                
            # 打印当前血量
            print(f"玩家{player1_no}当前血量: {p1.blood}")
            print(f"玩家{player2_no}当前血量: {p2.blood}")
            
            # 自动执行f.导出功能
            self.export_full_report()
            
        except IndexError:
            print("玩家编号不存在！")
            
    def modify_blood(self, player_no: int, k: int, note: str = ""):
        """修改血量"""
        try:
            player = self.players[player_no-1]
            
            if not player.is_alive:
                print("操作失败：该玩家已死亡！")
                return
                
            player.blood += k
            
            if player.blood <= 0:
                player.blood = 0
                player.is_alive = False
                print(f"玩家{player_no}死亡！")
                
            record = f"修改血量 - 玩家{player_no} {'增加' if k > 0 else '减少'}{abs(k)}点血"
            if note:
                record += f" ({note})"
            self.records.append(record)
            
            print(f"操作成功！玩家{player_no}当前血量: {player.blood}")
            
            # 自动执行导出
            self.export_data()
            
        except IndexError:
            print("玩家编号不存在！")
            
    def view_blood(self):
        """查看血量"""
        print("\n=== 玩家状态 ===")
        for player in self.players:
            print(player.get_info())
            
    def export_data(self):
        """导出数据到txt文件"""
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"游戏数据导出 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"玩家人数: {self.player_count}\n")
                f.write("=" * 50 + "\n")
                
                f.write("\n=== 操作记录 ===\n")
                for record in self.records:
                    f.write(record + "\n")
                    
                f.write("\n=== 当前玩家状态 ===\n")
                for player in self.players:
                    f.write(player.get_info() + "\n")
                    
            print(f"数据已导出到 {filename}")
        except Exception as e:
            print(f"导出失败: {e}")
            
    def export_full_report(self):
        """导出完整报告"""
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}_full.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"游戏完整报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"玩家人数: {self.player_count}\n")
                f.write("=" * 60 + "\n")
                
                f.write("\n=== 身份分配 ===\n")
                for player in self.players:
                    f.write(str(player) + "\n")
                    
                f.write("\n=== 详细操作记录 ===\n")
                for i, record in enumerate(self.records, 1):
                    f.write(f"{i:3d}. {record}\n")
                    
                f.write("\n=== 最终玩家状态 ===\n")
                for player in self.players:
                    f.write(player.get_info() + "\n")
                    
            print(f"完整报告已导出到 {filename}")
        except Exception as e:
            print(f"导出失败: {e}")
            
    def end_game(self):
        """结束游戏"""
        print("\n=== 游戏结束 ===")
        self.view_blood()
        self.export_full_report()
        print("游戏已结束，感谢游玩！")
        
    def run(self):
        """运行游戏"""
        self.setup_game()
        
        while True:
            print("\n=== 主菜单 ===")
            print("a. 交易")
            print("b. 捕食")
            print("c. 修改血量")
            print("d. 查看血量")
            print("e. 导出数据")
            print("f. 结束游戏")
            
            choice = input("请输入选项: ").strip().lower()
            
            if choice == 'a':
                try:
                    cmd = input("请输入交易命令(格式: 编号1 编号2 数值): ").split()
                    if len(cmd) == 3:
                        self.trade(int(cmd[0]), int(cmd[1]), int(cmd[2]))
                    else:
                        print("命令格式错误！")
                except ValueError:
                    print("请输入有效的数字！")
                    
            elif choice == 'b':
                try:
                    cmd = input("请输入捕食命令(格式: 编号1 编号2 数值): ").split()
                    if len(cmd) == 3:
                        self.hunt(int(cmd[0]), int(cmd[1]), int(cmd[2]))
                    else:
                        print("命令格式错误！")
                except ValueError:
                    print("请输入有效的数字！")
                    
            elif choice == 'c':
                try:
                    cmd = input("请输入修改血量命令(格式: 编号 数值 备注): ").split()
                    if len(cmd) >= 2:
                        note = " ".join(cmd[2:]) if len(cmd) > 2 else ""
                        self.modify_blood(int(cmd[0]), int(cmd[1]), note)
                    else:
                        print("命令格式错误！")
                except ValueError:
                    print("请输入有效的数字！")
                    
            elif choice == 'd':
                self.view_blood()
                
            elif choice == 'e':
                self.export_data()
                
            elif choice == 'f':
                self.end_game()
                break
                
            else:
                print("无效选项，请重新选择！")

if __name__ == "__main__":
    game = Game()
    game.run()
