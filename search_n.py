import random
import itertools
from collections import Counter
import matplotlib.pyplot as plt

def rank_value(rank):
    if rank.isdigit():
        return int(rank)
    elif rank == 'T':
        return 10
    elif rank == 'J':
        return 11
    elif rank == 'Q':
        return 12
    elif rank == 'K':
        return 13
    elif rank == 'A':
        return 14

def get_rank_and_suit(card):
    return card[:-1], card[-1]

def evaluate_hand(hand):
    ranks = [rank_value(get_rank_and_suit(card)[0]) for card in hand]
    suits = [get_rank_and_suit(card)[1] for card in hand]
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    is_flush = max(suit_counts.values()) == 5
    sorted_ranks = sorted(ranks, reverse=True)
    unique_sorted_ranks = sorted(set(ranks), reverse=True)

    is_straight = (len(unique_sorted_ranks) == 5 and unique_sorted_ranks[0] - unique_sorted_ranks[-1] == 4) or set(unique_sorted_ranks) == {14, 2, 3, 4, 5}

    if is_straight and is_flush:
        if unique_sorted_ranks == [14, 13, 12, 11, 10]:
            return (10, sorted_ranks)  # ロイヤルフラッシュ
        else:
            return (9, sorted_ranks)  # ストレートフラッシュ
    if 4 in rank_counts.values():
        four_of_a_kind = rank_counts.most_common(1)[0][0]
        kicker = [rank for rank in sorted_ranks if rank != four_of_a_kind]
        return (8, [four_of_a_kind] * 4 + kicker)  # フォーカード
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        three_of_a_kind = rank_counts.most_common(1)[0][0]
        pair = rank_counts.most_common(2)[1][0]
        return (7, [three_of_a_kind] * 3 + [pair] * 2)  # フルハウス
    if is_flush:
        return (6, sorted_ranks)  # フラッシュ
    if is_straight:
        return (5, sorted_ranks if unique_sorted_ranks != [14, 5, 4, 3, 2] else [5, 4, 3, 2, 1])  # ストレート
    if 3 in rank_counts.values():
        three_of_a_kind = rank_counts.most_common(1)[0][0]
        kickers = [rank for rank in sorted_ranks if rank != three_of_a_kind]
        return (4, [three_of_a_kind] * 3 + kickers)  # スリーカード
    if list(rank_counts.values()).count(2) == 2:
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        kicker = [rank for rank in sorted_ranks if rank_counts[rank] == 1]
        return (3, pairs * 2 + kicker)  # ツーペア
    if 2 in rank_counts.values():
        pair = rank_counts.most_common(1)[0][0]
        kickers = [rank for rank in sorted_ranks if rank != pair]
        return (2, [pair] * 2 + kickers)  # ワンペア
    return (1, sorted_ranks)  # ハイカード

def simulate_hands(player_hands, community_cards, num_simulations):
    deck = [r+s for r in '23456789TJQKA' for s in 'CDHS']
    known_cards = set(itertools.chain(*player_hands, community_cards))
    deck = [card for card in deck if card not in known_cards]
    
    win_counts = [0] * len(player_hands)

    win_rates_ave = [0]
    for _ in range(10):
        for _ in range(num_simulations):
            random.shuffle(deck)
            remaining_deck = deck[:]
            
            if len(community_cards) < 5:
                num_cards_to_draw = 5 - len(community_cards)
                drawn_cards = random.sample(remaining_deck, num_cards_to_draw)
                board = community_cards + drawn_cards
            else:
                board = community_cards
            
            player_evaluations = [evaluate_hand(player_hand + board) for player_hand in player_hands]
            max_eval = max(player_evaluations)
            
            winners = [i for i, eval in enumerate(player_evaluations) if eval == max_eval]
            
            for winner in winners:
                win_counts[winner] += 1 / len(winners)
        win_rates = [count / num_simulations for count in win_counts]
        win_rates_ave[0] += win_rates[0]
    win_rates_ave[0] = win_rates_ave[0]/10
    return win_rates_ave

def evaluate_simulation_accuracy(player_hands, community_cards, max_simulations, step):
    simulations = list(range(step, max_simulations + step, step))
    accuracy_data = {i: [] for i in range(len(player_hands))}
    
    for num_simulations in simulations:
        win_rates = simulate_hands(player_hands, community_cards, num_simulations)
        print(win_rates)
        for i, rate in enumerate(win_rates):
            accuracy_data[i].append(rate)
    
    return simulations, accuracy_data

# グラフを描く
def plot_accuracy(simulations, accuracy_data):
    for player, rates in accuracy_data.items():
        plt.plot(simulations, rates, label=f'Player {player+1}')
    
    plt.xlabel('Number of Simulations')
    plt.ylabel('Win Rate')
    plt.legend()
    plt.title('Win Rate Convergence')
    plt.show()

# プレイヤーの手札とコミュニティカードの設定
player_hands = [['AS', 'KS']]
community_cards = ['AD', 'KD', 'QS']

# シミュレーションの評価
max_simulations = 10000
step = 500
simulations, accuracy_data = evaluate_simulation_accuracy(player_hands, community_cards, max_simulations, step)

# グラフのプロット
plot_accuracy(simulations, accuracy_data[0])
