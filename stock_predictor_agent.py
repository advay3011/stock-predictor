#!/usr/bin/env python3
"""
Advanced Stock Market Predictor Agent
Uses time series analysis to predict stock trends and provide insights.
"""

import json
from datetime import datetime, timedelta
from strands import Agent, tool
import random


# ============================================================================
# SIMULATED DATA - Replace with real API calls (yfinance, Alpha Vantage, etc.)
# ============================================================================

def generate_stock_data(symbol: str, days: int = 30) -> list:
    """Generate simulated stock data for demo purposes."""
    data = []
    base_price = random.uniform(50, 500)
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        price = base_price + random.uniform(-5, 5)
        volume = random.randint(1000000, 10000000)
        base_price = price
        
        data.append({
            "date": date,
            "open": round(price - random.uniform(0, 2), 2),
            "high": round(price + random.uniform(0, 3), 2),
            "low": round(price - random.uniform(0, 3), 2),
            "close": round(price, 2),
            "volume": volume,
        })
    
    return data


# ============================================================================
# TOOLS
# ============================================================================

@tool
def fetch_stock_data(symbol: str, days: int = 30) -> str:
    """Fetch historical stock data for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
        days: Number of days of historical data (default: 30)
    
    Returns:
        JSON string containing stock price history
    """
    try:
        data = generate_stock_data(symbol.upper(), days)
        return json.dumps({
            "symbol": symbol.upper(),
            "data": data,
            "period_days": days,
            "status": "success"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


@tool
def calculate_moving_average(prices: str, window: int = 7) -> str:
    """Calculate the average price over the last 7 days to see if stock is going UP or DOWN.
    
    Args:
        prices: Stock price data
        window: Number of days to average (default: 7 days)
    
    Returns:
        Simple explanation of whether the stock is going UP (BULLISH) or DOWN (BEARISH)
    """
    try:
        data = json.loads(prices)
        # Handle both direct array and wrapped object
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        closes = [item["close"] for item in data]
        
        if len(closes) < window:
            return json.dumps({"error": "Not enough data points", "status": "failed"})
        
        moving_avgs = []
        for i in range(len(closes) - window + 1):
            avg = sum(closes[i:i+window]) / window
            moving_avgs.append(round(avg, 2))
        
        current_price = closes[-1]
        current_ma = moving_avgs[-1]
        trend = "BULLISH" if current_price > current_ma else "BEARISH"
        
        # Simple explanation
        if trend == "BULLISH":
            explanation = f"The stock is at ${current_price}, which is ABOVE the average of ${current_ma}. This means it's going UP! 📈"
        else:
            explanation = f"The stock is at ${current_price}, which is BELOW the average of ${current_ma}. This means it's going DOWN! 📉"
        
        return json.dumps({
            "current_price": current_price,
            "average_price": current_ma,
            "trend": trend,
            "explanation": explanation,
            "status": "success"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


@tool
def calculate_volatility(prices: str) -> str:
    """Check how much the stock price jumps around (risky or stable?).
    
    Args:
        prices: Stock price data
    
    Returns:
        Simple explanation of risk level (LOW = stable, HIGH = risky)
    """
    try:
        data = json.loads(prices)
        # Handle both direct array and wrapped object
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        closes = [item["close"] for item in data]
        
        mean = sum(closes) / len(closes)
        variance = sum((x - mean) ** 2 for x in closes) / len(closes)
        volatility = variance ** 0.5
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(closes)):
            ret = (closes[i] - closes[i-1]) / closes[i-1] * 100
            returns.append(ret)
        
        avg_return = sum(returns) / len(returns) if returns else 0
        
        risk_level = "LOW" if volatility < 5 else "MEDIUM" if volatility < 15 else "HIGH"
        
        # Simple explanation
        if risk_level == "LOW":
            risk_explanation = "This stock is STABLE - the price doesn't jump around much. It's like a calm river. 😌"
        elif risk_level == "MEDIUM":
            risk_explanation = "This stock is MODERATE - the price moves a bit. It's like a wavy river. 🌊"
        else:
            risk_explanation = "This stock is RISKY - the price jumps around a lot. It's like a wild river! ⚡"
        
        return json.dumps({
            "risk_level": risk_level,
            "risk_explanation": risk_explanation,
            "price_range": {
                "lowest": round(min(closes), 2),
                "highest": round(max(closes), 2),
                "current": round(closes[-1], 2)
            },
            "status": "success"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


@tool
def predict_trend(prices: str, forecast_days: int = 5) -> str:
    """Predict where the stock price will go in the next few days.
    
    Args:
        prices: Stock price data
        forecast_days: How many days to predict (default: 5)
    
    Returns:
        Simple prediction: Will it go UP or DOWN?
    """
    try:
        data = json.loads(prices)
        # Handle both direct array and wrapped object
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        closes = [item["close"] for item in data]
        
        # Simple linear regression
        n = len(closes)
        x = list(range(n))
        y = closes
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Generate forecast
        forecast = []
        for i in range(1, forecast_days + 1):
            predicted_price = slope * (n + i - 1) + intercept
            forecast.append(round(predicted_price, 2))
        
        current_price = closes[-1]
        predicted_price = forecast[-1]
        change_percent = ((predicted_price - current_price) / current_price) * 100
        
        direction = "UP" if slope > 0 else "DOWN"
        
        # Simple explanation
        if direction == "UP":
            prediction_text = f"📈 The stock is predicted to go UP! It might reach ${predicted_price} (up {abs(change_percent):.1f}%)"
        else:
            prediction_text = f"📉 The stock is predicted to go DOWN. It might reach ${predicted_price} (down {abs(change_percent):.1f}%)"
        
        return json.dumps({
            "prediction": prediction_text,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "direction": direction,
            "change_percent": round(change_percent, 2),
            "status": "success"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


@tool
def analyze_support_resistance(prices: str) -> str:
    """Find the "floor" and "ceiling" prices where the stock tends to bounce.
    
    Args:
        prices: Stock price data
    
    Returns:
        Simple explanation of where to buy (floor) and sell (ceiling)
    """
    try:
        data = json.loads(prices)
        # Handle both direct array and wrapped object
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        highs = [item["high"] for item in data]
        lows = [item["low"] for item in data]
        closes = [item["close"] for item in data]
        
        # Find support (local minima) and resistance (local maxima)
        resistance_levels = sorted(set(highs[-10:]))[-3:] if len(highs) >= 10 else sorted(set(highs))[-3:]
        support_levels = sorted(set(lows[-10:]))[:3] if len(lows) >= 10 else sorted(set(lows))[:3]
        
        current_price = closes[-1]
        
        # Determine trading signal
        signal = "HOLD"
        if current_price < min(support_levels):
            signal = "BUY"
        elif current_price > max(resistance_levels):
            signal = "SELL"
        
        # Simple explanation
        if signal == "BUY":
            signal_text = "🟢 BUY! The price is LOW (below the floor). Good time to buy!"
        elif signal == "SELL":
            signal_text = "🔴 SELL! The price is HIGH (above the ceiling). Good time to sell!"
        else:
            signal_text = "🟡 HOLD! The price is in the middle. Wait for a better time."
        
        return json.dumps({
            "floor_price": round(min(support_levels), 2),
            "ceiling_price": round(max(resistance_levels), 2),
            "current_price": round(current_price, 2),
            "signal": signal,
            "signal_explanation": signal_text,
            "status": "success"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


@tool
def analyze_price_movement(prices: str, days_back: int = 5) -> str:
    """Explain WHY a stock price moved the way it did (the "alibi").
    
    Args:
        prices: Stock price data
        days_back: How many days to analyze (default: 5)
    
    Returns:
        3 plausible explanations ranked by confidence
    """
    try:
        data = json.loads(prices)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        
        # Get recent data
        recent_data = data[-days_back:] if len(data) >= days_back else data
        
        closes = [item["close"] for item in recent_data]
        volumes = [item["volume"] for item in recent_data]
        highs = [item["high"] for item in recent_data]
        lows = [item["low"] for item in recent_data]
        
        # Calculate metrics
        price_change = closes[-1] - closes[0]
        price_change_pct = (price_change / closes[0]) * 100
        avg_volume = sum(volumes) / len(volumes)
        volume_spike = max(volumes) / avg_volume if avg_volume > 0 else 1
        volatility = max(highs) - min(lows)
        
        # Detect patterns
        alibis = []
        
        # Alibi 1: Volume-driven move
        if volume_spike > 1.5:
            if price_change > 0:
                alibi1 = {
                    "rank": 1,
                    "title": "📈 Bullish Volume Surge",
                    "explanation": f"Heavy buying pressure! Volume spiked {volume_spike:.1f}x normal. Buyers came in strong.",
                    "signals": {
                        "high_volume": True,
                        "price_up": True,
                        "gap_up": abs(closes[-1] - closes[-2]) > volatility * 0.3 if len(closes) > 1 else False,
                        "sustained_move": price_change_pct > 2
                    },
                    "confidence": min(85, int(volume_spike * 30))
                }
            else:
                alibi1 = {
                    "rank": 1,
                    "title": "📉 Panic Selling / Distribution",
                    "explanation": f"Heavy selling pressure! Volume spiked {volume_spike:.1f}x normal. Forced liquidation or profit-taking.",
                    "signals": {
                        "high_volume": True,
                        "price_down": True,
                        "gap_down": abs(closes[-1] - closes[-2]) > volatility * 0.3 if len(closes) > 1 else False,
                        "sustained_move": price_change_pct < -2
                    },
                    "confidence": min(85, int(volume_spike * 30))
                }
            alibis.append(alibi1)
        
        # Alibi 2: Volatility spike (news/earnings)
        if volatility > sum([highs[i] - lows[i] for i in range(len(highs))]) / len(highs) * 1.5:
            alibi2 = {
                "rank": 2,
                "title": "📰 News Event / Earnings",
                "explanation": f"Big price swing ({volatility:.2f}) suggests news, earnings, or major announcement.",
                "signals": {
                    "high_volatility": True,
                    "wide_range": True,
                    "unusual_movement": True,
                    "potential_catalyst": True
                },
                "confidence": 70
            }
            alibis.append(alibi2)
        
        # Alibi 3: Support/Resistance bounce
        if len(closes) > 1:
            recent_low = min(closes[-3:]) if len(closes) >= 3 else min(closes)
            recent_high = max(closes[-3:]) if len(closes) >= 3 else max(closes)
            
            if price_change > 0 and closes[-1] > recent_low:
                alibi3 = {
                    "rank": 3,
                    "title": "🎯 Support Bounce",
                    "explanation": f"Price bounced off support level (${recent_low:.2f}). Buyers stepped in at the floor.",
                    "signals": {
                        "touched_support": True,
                        "bounced_up": True,
                        "volume_on_bounce": volume_spike > 1.2,
                        "recovery_move": price_change_pct > 1
                    },
                    "confidence": 65
                }
            elif price_change < 0 and closes[-1] < recent_high:
                alibi3 = {
                    "rank": 3,
                    "title": "🚫 Resistance Rejection",
                    "explanation": f"Price hit resistance (${recent_high:.2f}) and got rejected. Sellers took over.",
                    "signals": {
                        "touched_resistance": True,
                        "rejected_down": True,
                        "volume_on_rejection": volume_spike > 1.2,
                        "breakdown_move": price_change_pct < -1
                    },
                    "confidence": 65
                }
            else:
                alibi3 = {
                    "rank": 3,
                    "title": "➡️ Range-bound Movement",
                    "explanation": f"Price moved within its normal range. No major catalyst detected.",
                    "signals": {
                        "normal_volatility": True,
                        "within_range": True,
                        "no_catalyst": True,
                        "consolidation": True
                    },
                    "confidence": 55
                }
            alibis.append(alibi3)
        
        # Sort by confidence
        alibis.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Context cards
        context = {
            "period_days": days_back,
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "volume_spike_ratio": round(volume_spike, 2),
            "volatility_range": round(volatility, 2),
            "current_price": round(closes[-1], 2),
            "starting_price": round(closes[0], 2)
        }
        
        return json.dumps({
            "alibis": alibis,
            "context": context,
            "status": "success"
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})




@tool
def generate_report(symbol: str, analysis_data: str) -> str:
    """Generate a comprehensive trading report.
    
    Args:
        symbol: Stock ticker symbol
        analysis_data: JSON string containing all analysis results
    
    Returns:
        Formatted trading report with recommendations
    """
    try:
        report = f"""
╔════════════════════════════════════════════════════════════╗
║           STOCK MARKET ANALYSIS REPORT                     ║
║           Symbol: {symbol.upper()}                                    ║
║           Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                  ║
╚════════════════════════════════════════════════════════════╝

ANALYSIS SUMMARY:
{analysis_data}

RECOMMENDATION:
Based on the time series analysis, technical indicators, and trend
forecasting, this report provides actionable insights for trading
decisions. Always consult with a financial advisor before trading.

DISCLAIMER:
This analysis is for educational purposes only and should not be
considered as financial advice. Past performance does not guarantee
future results.
"""
        return report
    except Exception as e:
        return f"Error generating report: {str(e)}"


# ============================================================================
# AGENT SETUP
# ============================================================================

agent = Agent(
    system_prompt="""You are a friendly stock market guide for beginners. Your job is to explain stock analysis in VERY SIMPLE terms that anyone can understand, even if they know nothing about stocks.

IMPORTANT RULES:
1. Use simple, everyday language - NO jargon
2. Always explain what things mean in plain English
3. Use analogies and real-world examples
4. Break down complex ideas into simple steps
5. Always say what the numbers mean in simple terms

WHEN ANALYZING STOCKS:
- Fetch the data first
- Calculate all indicators (moving average, volatility, trend, prediction, support/resistance)
- Analyze price movements to explain WHY they happened
- Explain each result in SIMPLE TERMS

SIMPLE EXPLANATIONS:

Moving Average = "The average price over the last week. If the stock is above this average, it's going UP (good). If below, it's going DOWN (not good)."

BULLISH = "The stock is going UP - like a bull charging forward"
BEARISH = "The stock is going DOWN - like a bear pushing things down"

Volatility = "How much the price jumps around. High = risky (big swings). Low = stable (small changes)."

Support Level = "A price where the stock tends to bounce back up (like a floor)"
Resistance Level = "A price where the stock tends to stop going up (like a ceiling)"

BUY Signal = "Good time to buy - price is low"
SELL Signal = "Good time to sell - price is high"
HOLD Signal = "Wait - not a good time to buy or sell"

Price Movement Alibis = "The reasons WHY the price moved (volume surge, news, support bounce, etc.)"

EXAMPLE RESPONSE:
"AAPL is at $150. The average price is $145. So AAPL is ABOVE average = BULLISH (going up). The stock bounces at $140 (support) and stops at $160 (resistance). Right now it's in the middle, so HOLD (wait). Yesterday it dropped because of heavy selling (panic selling alibi) - volume was 2x normal!"

ALWAYS END WITH: "Remember: This is just analysis, not financial advice. Always do your own research!"

Your tools:
1. Fetch historical stock data
2. Calculate moving averages to identify trends
3. Analyze volatility and risk levels
4. Predict future price movements
5. Identify support and resistance levels
6. Explain WHY prices moved (alibis)
7. Generate comprehensive trading reports

Be friendly, encouraging, and make sure they understand everything!""",
    tools=[
        fetch_stock_data,
        calculate_moving_average,
        calculate_volatility,
        predict_trend,
        analyze_support_resistance,
        analyze_price_movement,
        generate_report,
    ],
)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the stock predictor agent in interactive mode."""
    print("=" * 70)
    print("ADVANCED STOCK MARKET PREDICTOR AGENT")
    print("=" * 70)
    print("\nCapabilities:")
    print("  • Fetch historical stock data")
    print("  • Calculate moving averages and trends")
    print("  • Analyze volatility and risk")
    print("  • Predict future price movements")
    print("  • Identify support/resistance levels")
    print("  • Explain WHY prices moved (alibis)")
    print("  • Generate trading reports")
    print("\nExample queries:")
    print("  'Analyze AAPL stock for the last 30 days'")
    print("  'What is the trend for GOOGL?'")
    print("  'Why did TSLA drop yesterday?'")
    print("  'Explain NVDA's spike on Jan 12'")
    print("  'Should I buy or sell MSFT?'")
    print("\nType 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("You > ").strip()
            
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n[Agent analyzing...]\n")
            response = agent(user_input)
            print(f"Agent > {response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()

def run_prediction(ticker, horizon):
    ...
    return output
