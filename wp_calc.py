import random
import itertools
from collections import Counter

# ランクを評価するための数値に変換
def rank_value(rank):
    values = '23456789TJQKA'
    return values.index(rank)

# ポーカーの手役を評価する関数
def evaluate_hand(hand):
    
    # カードをランクと柄に分けてソート
    ranks = sorted([rank_value(card[0]) for card in hand], reverse=True)
    suits = [card[1] for card in hand]
    # ランクと柄の重複数をカウント
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    # フラッシュとストレートが存在するかを確認
    is_flush = max(suit_counts.values()) == 5
    is_straight = (len(rank_counts) == 5) and ((ranks[0] - ranks[-1] == 4) or (ranks == [12, 3, 2, 1, 0]))

    if is_straight and is_flush:
        if ranks[0] == 12:
            return (10, ranks)  # ロイヤルフラッシュ
        else:
            return (9, ranks)  # ストレートフラッシュ
    if 4 in rank_counts.values():
        four_of_a_kind = rank_counts.most_common(1)[0][0]
        kicker = [rank for rank in ranks if rank != four_of_a_kind]
        return (8, [four_of_a_kind] * 4 + kicker)  # フォーカード
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        three_of_a_kind = rank_counts.most_common(1)[0][0]
        pair = rank_counts.most_common(2)[1][0]
        return (7, [three_of_a_kind] * 3 + [pair] * 2)  # フルハウス
    if is_flush:
        return (6, ranks)  # フラッシュ
    if is_straight:
        return (5, ranks)  # ストレート
    if 3 in rank_counts.values():
        three_of_a_kind = rank_counts.most_common(1)[0][0]
        kickers = [rank for rank in ranks if rank != three_of_a_kind]
        return (4, [three_of_a_kind] * 3 + kickers)  # スリーカード
    if list(rank_counts.values()).count(2) == 2:
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        kicker = [rank for rank in ranks if rank_counts[rank] == 1]
        return (3, pairs * 2 + kicker)  # ツーペア
    if 2 in rank_counts.values():
        pair = rank_counts.most_common(1)[0][0]
        kickers = [rank for rank in ranks if rank != pair]
        return (2, [pair] * 2 + kickers)  # ワンペア
    return (1, ranks)  # ハイカード

# シミュレーション関数
def simulate_game(player_hands, community_cards, num_simulations=10000):

    # 残りの山札にあるカードをdeckに格納
    deck = [r+s for r in '23456789TJQKA' for s in 'CDHS']
    known_cards = set(itertools.chain(*player_hands, community_cards))
    deck = [card for card in deck if card not in known_cards]
    # 各プレイヤーの勝利回数を保存する配列を初期化
    wins = [0] * len(player_hands)

    # モンテカルロシミュレーションの開始
    for _ in range(num_simulations):
        # 残りの山札をシャッフル（結果の一貫性を確保するため毎回初期化してからシャッフルする）
        remaining_deck = deck.copy()
        random.shuffle(remaining_deck)
        #リバーまでカードをめくる
        if len(community_cards) < 5:
            needed_cards = 5 - len(community_cards)
            community_draw = community_cards + remaining_deck[:needed_cards]
        else:
            community_draw = community_cards
        # ハンドの強さと勝者を初期化
        best_hand_strength = (-1, [])
        winning_players = []

        # 各プレイヤーのハンドを判定
        for i, hand in enumerate(player_hands):
            # 最も強い役を作れるカード５枚を抽出
            full_hand = hand + community_draw
            best_five_hand = max(itertools.combinations(full_hand, 5), key=evaluate_hand)
            hand_strength = evaluate_hand(best_five_hand)
            # 最も強い役かどうかを判定
            if hand_strength > best_hand_strength:
                best_hand_strength = hand_strength
                winning_players = [i]
            elif hand_strength == best_hand_strength:
                winning_players.append(i)
        # 各プレイヤーの勝利回数を保存（引き分けの場合は勝利数を分割）
        for winner in winning_players:
            wins[winner] += 1 / len(winning_players)
            
    # 各プレイヤーの勝率を算出
    win_rates = [win / num_simulations for win in wins]
    return win_rates

# プレイヤーの手札と場のカードを設定
player_hands = [['AS', 'KS'], ['QH', 'QD'], ['7C', '7D']]
community_cards = ['2H', '5S', '9D', '4C']  # 例えば、場に4枚のカードが出ている場合

# 勝率を計算
win_rates = simulate_game(player_hands, community_cards)
print("各プレイヤーの勝率: ", win_rates)
