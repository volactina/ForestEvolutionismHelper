import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import io

# 添加父目录到路径，以便导入forest模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from forest import Game, Player, CardRank, CardSuit
except ImportError:
    # 如果导入失败，可能是命名问题，尝试其他导入方式
    import importlib.util
    spec = importlib.util.spec_from_file_location("forest", "forest.py")
    forest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(forest)
    Game = forest.Game
    Player = forest.Player
    CardRank = forest.CardRank
    CardSuit = forest.CardSuit


class TestForestGame(unittest.TestCase):
    """森林进化论游戏测试类"""
    
    def setUp(self):
        """每个测试前的准备工作"""
        self.game = Game()
        # 手动设置游戏参数，避免需要输入
        self.game.player_count = 12
        self.game.joker_count = 0
        
    def test_player_initialization(self):
        """测试玩家初始化"""
        player = Player(1)
        self.assertEqual(player.no, 1)
        self.assertEqual(player.blood, 20)
        self.assertEqual(player.trade, 0)
        self.assertIsNone(player.rank)
        self.assertIsNone(player.suit)
        self.assertTrue(player.is_alive)
    
    def test_assign_identities_12_players(self):
        """测试12人局身份分配"""
        self.game.player_count = 12
        self.game.players = [Player(i+1) for i in range(12)]
        self.game._assign_identities()
        
        # 检查是否有12个玩家获得身份
        self.assertEqual(len(self.game.players), 12)
        
        # 统计各种身份的数量
        ranks = {'K': 0, 'Q': 0, 'J': 0}
        suits = {'黑桃': 0, '红桃': 0, '梅花': 0, '方片': 0}
        
        for player in self.game.players:
            self.assertIsNotNone(player.rank)
            self.assertIsNotNone(player.suit)
            
            if player.rank == CardRank.JOKER:
                self.fail("12人局不应有Joker")
            else:
                ranks[player.rank.value] += 1
                suits[player.suit.value] += 1
        
        # 检查每种点数都有4个
        self.assertEqual(ranks['K'], 4)
        self.assertEqual(ranks['Q'], 4)
        self.assertEqual(ranks['J'], 4)
        
        # 检查每种花色都有3个
        self.assertEqual(suits['黑桃'], 3)
        self.assertEqual(suits['红桃'], 3)
        self.assertEqual(suits['梅花'], 3)
        self.assertEqual(suits['方片'], 3)
    
    def test_trade_success(self):
        """测试交易成功"""
        # 创建两个测试玩家
        player1 = Player(1)
        player2 = Player(2)
        player1.blood = 30
        player2.trade = 5
        
        self.game.players = [player1, player2]
        
        # 模拟交易
        with patch('sys.stdout', new=io.StringIO()):
            self.game.trade(1, 2, 5)
        
        # 验证交易结果
        self.assertEqual(player1.blood, 25)  # 30-5
        self.assertEqual(player2.blood, 25)  # 20+5
        self.assertEqual(player1.trade, -5)
        self.assertEqual(player2.trade, 10)  # 5+5
    
    def test_trade_fail_exceeds_limit(self):
        """测试交易失败：超过交易血量限制"""
        player1 = Player(1)
        player2 = Player(2)
        player2.trade = 8  # 交易血量已接近上限
        
        self.game.players = [player1, player2]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.game.trade(1, 2, 5)  # 8+5=13 > 10，应该失败
            
            output = fake_out.getvalue()
            self.assertIn("交易失败", output)
            self.assertIn("交易血量将超过10", output)
    
    def test_trade_fail_insufficient_blood(self):
        """测试交易失败：血量不足"""
        player1 = Player(1)
        player2 = Player(2)
        player1.blood = 3  # 血量不足
        
        self.game.players = [player1, player2]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.game.trade(1, 2, 5)
            
            output = fake_out.getvalue()
            self.assertIn("交易失败", output)
            self.assertIn("血量不足", output)
    
    def test_check_restraint_12_players(self):
        """测试12人局克制关系"""
        self.game.player_count = 12
        
        # 测试K>Q
        player_k = Player(1)
        player_q = Player(2)
        player_k.rank = CardRank.K
        player_k.suit = CardSuit.SPADE
        player_q.rank = CardRank.Q
        player_q.suit = CardSuit.SPADE
        
        result = self.game._check_restraint(player_k, player_q)
        self.assertEqual(result, 1, "K应该克制Q")
        
        # 测试Q>J
        player_j = Player(3)
        player_j.rank = CardRank.J
        player_j.suit = CardSuit.SPADE
        
        result = self.game._check_restraint(player_q, player_j)
        self.assertEqual(result, 1, "Q应该克制J")
        
        # 测试J>K
        result = self.game._check_restraint(player_j, player_k)
        self.assertEqual(result, 1, "J应该克制K")
    
    def test_suit_restraint_12_players(self):
        """测试12人局花色克制关系"""
        self.game.player_count = 12
        
        # 创建相同点数不同花色的玩家
        player_spade = Player(1)
        player_heart = Player(2)
        player_club = Player(3)
        player_diamond = Player(4)
        
        for p in [player_spade, player_heart, player_club, player_diamond]:
            p.rank = CardRank.K
        
        player_spade.suit = CardSuit.SPADE
        player_heart.suit = CardSuit.HEART
        player_club.suit = CardSuit.CLUB
        player_diamond.suit = CardSuit.DIAMOND
        
        # 测试黑桃>红桃
        result = self.game._check_restraint(player_spade, player_heart)
        self.assertEqual(result, 1, "黑桃应该克制红桃")
        
        # 测试红桃>梅花
        result = self.game._check_restraint(player_heart, player_club)
        self.assertEqual(result, 1, "红桃应该克制梅花")
        
        # 测试梅花>方片
        result = self.game._check_restraint(player_club, player_diamond)
        self.assertEqual(result, 1, "梅花应该克制方片")
        
        # 测试方片>黑桃
        result = self.game._check_restraint(player_diamond, player_spade)
        self.assertEqual(result, 1, "方片应该克制黑桃")
    
    def test_tie_conditions_12_players(self):
        """测试12人局平局情况"""
        self.game.player_count = 12
        
        # 测试黑桃与梅花打平
        player_spade = Player(1)
        player_club = Player(2)
        player_spade.rank = CardRank.K
        player_spade.suit = CardSuit.SPADE
        player_club.rank = CardRank.K
        player_club.suit = CardSuit.CLUB
        
        result = self.game._check_restraint(player_spade, player_club)
        self.assertEqual(result, 0, "黑桃与梅花应该打平")
        
        # 测试红桃与方片打平
        player_heart = Player(3)
        player_diamond = Player(4)
        player_heart.rank = CardRank.Q
        player_heart.suit = CardSuit.HEART
        player_diamond.rank = CardRank.Q
        player_diamond.suit = CardSuit.DIAMOND
        
        result = self.game._check_restraint(player_heart, player_diamond)
        self.assertEqual(result, 0, "红桃与方片应该打平")
    
    def test_heart_k_vs_spade_q_should_fail(self):
        """测试：红桃K捕食黑桃Q应该失败（根据规则应该是成功的）"""
        # 注意：根据规则，K>Q 且 红桃>黑桃？我们需要验证实际规则
        
        self.game.player_count = 12
        
        # 创建玩家
        player1 = Player(1)  # 红桃K
        player2 = Player(2)  # 黑桃Q
        
        player1.rank = CardRank.K
        player1.suit = CardSuit.HEART
        player2.rank = CardRank.Q
        player2.suit = CardSuit.SPADE
        
        # 根据规则：
        # 1. 先看点克制：K>Q，所以player1克制player2 ✓
        # 2. 如果点数相同才看花色克制
        
        result = self.game._check_restraint(player1, player2)
        print(f"红桃K vs 黑桃Q 克制结果: {result}")
        
        # 根据描述："优先检查k>q>j>k，其次检查黑桃>红桃>梅花>方片>黑桃"
        # 所以先看点克制，K>Q，因此应该是成功的
        self.assertEqual(result, 1, "红桃K应该克制黑桃Q（因为K>Q）")
    
    def test_hunt_success(self):
        """测试捕食成功"""
        self.game.player_count = 12
        
        # 创建玩家：黑桃K捕食红桃Q（K>Q）
        player1 = Player(1)
        player2 = Player(2)
        player1.rank = CardRank.K
        player1.suit = CardSuit.SPADE
        player1.blood = 20
        player2.rank = CardRank.Q
        player2.suit = CardSuit.HEART
        player2.blood = 20
        
        self.game.players = [player1, player2]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.game.hunt(1, 2, 10)
            
            output = fake_out.getvalue()
            self.assertIn("捕食成功", output)
            self.assertIn("玩家1获得10点血", output)
            self.assertIn("玩家2损失10点血", output)
        
        self.assertEqual(player1.blood, 30)  # 20+10
        self.assertEqual(player2.blood, 10)  # 20-10
    
    def test_hunt_fail_reverse(self):
        """测试捕食失败（被反克制）"""
        self.game.player_count = 12
        
        # 创建玩家：红桃K捕食黑桃J（K被J克制）
        player1 = Player(1)
        player2 = Player(2)
        player1.rank = CardRank.K
        player1.suit = CardSuit.HEART
        player1.blood = 20
        player2.rank = CardRank.J
        player2.suit = CardSuit.SPADE
        player2.blood = 20
        
        self.game.players = [player1, player2]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.game.hunt(1, 2, 10)
            
            output = fake_out.getvalue()
            self.assertIn("捕食失败", output)
            self.assertIn("玩家2克制玩家1", output)
            self.assertIn("玩家2获得10点血", output)
            self.assertIn("玩家1损失10点血", output)
        
        self.assertEqual(player1.blood, 10)  # 20-10
        self.assertEqual(player2.blood, 30)  # 20+10
    
    def test_hunt_player_death(self):
        """测试捕食导致玩家死亡"""
        self.game.player_count = 12
        
        player1 = Player(1)
        player2 = Player(2)
        player1.rank = CardRank.K
        player1.suit = CardSuit.SPADE
        player1.blood = 20
        player2.rank = CardRank.Q
        player2.suit = CardSuit.HEART
        player2.blood = 5  # 血量很低
        
        self.game.players = [player1, player2]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.game.hunt(1, 2, 10)  # 捕食10点，但对方只有5点
            
            output = fake_out.getvalue()
            self.assertIn("死亡", output)
            # bugfix 击杀玩家获得全部捕食血量，而不是只获得剩余血量
            self.assertIn("获得13点血奖励", output)  # 10+3
        
        self.assertFalse(player2.is_alive)
        self.assertEqual(player2.blood, 0)
        self.assertEqual(player1.blood, 33)  # 20+10+3
    
    def test_modify_blood(self):
        """测试修改血量"""
        player = Player(1)
        player.blood = 20
        
        self.game.players = [player]
        
        with patch('sys.stdout', new=io.StringIO()):
            self.game.modify_blood(1, 10, "测试增加血量")
        
        self.assertEqual(player.blood, 30)
        
        with patch('sys.stdout', new=io.StringIO()):
            self.game.modify_blood(1, -15, "测试减少血量")
        
        self.assertEqual(player.blood, 15)
    
    def test_modify_blood_to_death(self):
        """测试修改血量导致死亡"""
        player = Player(1)
        player.blood = 5
        
        self.game.players = [player]
        
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            self.game.modify_blood(1, -10, "测试致死")
            
            output = fake_out.getvalue()
            self.assertIn("死亡", output)
        
        self.assertFalse(player.is_alive)
        self.assertEqual(player.blood, 0)
    
    def test_joker_special_rules(self):
        """测试Joker特殊规则"""
        self.game.player_count = 13  # 有Joker的局
        
        # 创建Joker玩家和普通玩家
        player_joker = Player(1)
        player_normal = Player(2)
        
        player_joker.rank = CardRank.JOKER
        player_joker.suit = CardSuit.JOKER
        player_normal.rank = CardRank.K
        player_normal.suit = CardSuit.SPADE
        
        # 测试Joker > 任意牌
        result = self.game._check_restraint(player_joker, player_normal)
        self.assertEqual(result, 1, "Joker应该克制任意牌")
        
        # 测试任意牌 > Joker
        result = self.game._check_restraint(player_normal, player_joker)
        self.assertEqual(result, 1, "任意牌应该克制Joker")
    
    def test_different_player_counts(self):
        """测试不同人数局的规则差异"""
        test_cases = [
            (13, ["黑桃", "红桃", "梅花", "方片"], 1),
            (12, ["黑桃", "红桃", "梅花", "方片"], 0),
            (11, ["黑桃", "红桃", "梅花"], 2),
            (10, ["黑桃", "红桃", "梅花"], 1),
            (9, ["黑桃", "红桃", "梅花"], 0),
            (8, ["黑桃", "红桃"], 2),
            (7, ["黑桃", "红桃"], 1),
            (6, ["黑桃", "红桃"], 0),
        ]
        
        for player_count, expected_suits, expected_jokers in test_cases:
            with self.subTest(player_count=player_count):
                game = Game()
                game.player_count = player_count
                game.players = [Player(i+1) for i in range(player_count)]
                game._assign_identities()
                
                # 验证joker数量
                joker_count = sum(1 for p in game.players if p.rank == CardRank.JOKER)
                self.assertEqual(joker_count, expected_jokers,
                                 f"{player_count}人局应有{expected_jokers}个Joker")
                
                # 验证花色
                suits_found = set()
                for player in game.players:
                    if player.suit != CardSuit.JOKER:
                        suits_found.add(player.suit.value)
                
                for suit in expected_suits:
                    self.assertIn(suit, suits_found,
                                  f"{player_count}人局应有{suit}花色")


class TestComprehensiveScenarios(unittest.TestCase):
    """综合场景测试"""
    
    def test_full_game_flow(self):
        """测试完整游戏流程"""
        game = Game()
        game.player_count = 8
        game.players = [Player(i+1) for i in range(8)]
        game._assign_identities()
        
        # 初始血量检查
        for player in game.players:
            self.assertEqual(player.blood, 20)
            self.assertEqual(player.trade, 0)
            self.assertTrue(player.is_alive)
        
        # 进行一些交易
        game.players[0].blood = 30
        game.trade(1, 2, 5)
        
        self.assertEqual(game.players[0].blood, 25)
        self.assertEqual(game.players[1].blood, 25)
        self.assertEqual(game.players[0].trade, -5)
        self.assertEqual(game.players[1].trade, 5)
        
        # 进行捕食
        # 设置特定身份以便测试
        game.players[2].rank = CardRank.K
        game.players[2].suit = CardSuit.SPADE
        game.players[3].rank = CardRank.Q
        game.players[3].suit = CardSuit.HEART
        
        with patch('sys.stdout', new=io.StringIO()):
            game.hunt(3, 4, 8)  # 玩家3捕食玩家4
        
        # 检查操作记录
        self.assertGreater(len(game.records), 0)
        self.assertTrue(any("交易" in record for record in game.records))
        self.assertTrue(any("捕食" in record for record in game.records))


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)
