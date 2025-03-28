import random
import json
from datetime import datetime
from data_loader import load_data
from backtester import apply_indicators, simulate_trades

# Define strategy rule set
def generate_random_rule():
    return random.choice([
        "macd_rsi_buy", "macd_rsi_sell", "ema_cross_buy", "ema_cross_sell",
        "rsi_reversal_buy", "rsi_reversal_sell", "atr_breakout_buy", "atr_breakout_sell",
        "stoch_rsi_long", "stoch_rsi_short", "adx_momentum_buy", "adx_momentum_sell",
        "bollinger_band_long", "bollinger_band_short", "williams_reversal_buy", "williams_reversal_sell",
        "cci_breakout_buy", "cci_breakout_sell"
    ])

def evolve_strategies(generations=10, population=10):
    df = load_data()
    df = apply_indicators(df)

    best_strategy = None
    best_fitness = float('-inf')
    top_strategies = []

    for gen in range(generations):
        print(f"\n=== Generation {gen+1} ===")
        population_results = []

        for _ in range(population):
            rule = generate_random_rule()
            result = simulate_trades(df.copy(), rule)
            result['fitness'] = result['return'] + (result['win_rate'] * 2) + (result['winning_trades'] * 0.1)
            population_results.append(result)

        population_results.sort(key=lambda x: x['fitness'], reverse=True)
        top_3 = population_results[:3]

        for rank, res in enumerate(top_3):
            print(f"#{rank+1}: {res['strategy']} | Return: {res['return']:.2f} | Win Rate: {res['win_rate']}% | Wins: {res['winning_trades']} | Fitness: {res['fitness']:.2f}")

        top_strategies.extend(top_3)

        if population_results[0]['fitness'] > best_fitness:
            best_fitness = population_results[0]['fitness']
            best_strategy = population_results[0]

    with open("best_strategies.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "best_overall": best_strategy,
            "top_strategies": top_strategies
        }, f, indent=2)

    print("\n=== Best Strategy Found ===")
    print(f"Strategy: {best_strategy['strategy']}")
    print(f"Return: {best_strategy['return']:.2f}")
    print(f"Win Rate: {best_strategy['win_rate']}%")
    print(f"Wins: {best_strategy['winning_trades']}")
    print(f"Fitness Score: {best_strategy['fitness']:.2f}")

if __name__ == '__main__':
    evolve_strategies(generations=5, population=10)
    