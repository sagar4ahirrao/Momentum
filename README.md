Momentum Stratergy 15/30 days
```
//@version=5
indicator("Normalized Momentum Score", overlay=false)

// Input parameters for 15 days and 1 month periods
length15d = input.int(15, title="15-Day Period", minval=1)
length1m = input.int(21, title="1-Month Period", minval=1) // Approx. 21 trading days
lookback = input.int(252, title="Lookback Period", minval=1) // Lookback period for mean and std. dev.

calc_return(price, length) =>
    price[length] / price - 1

// Calculate annualized standard deviation
calc_stddev(price, length) =>
    log_return = math.log(price / price[1])
    stddev = ta.stdev(log_return, length) * math.sqrt(252)
    stddev

// Calculate Momentum Ratios
price = close
stddev = calc_stddev(price, length1m) // Using length1m for stddev calculation

momentum_ratio_1m = calc_return(price, length1m) / stddev
momentum_ratio_15d = calc_return(price, length15d) / stddev

// Calculate Z-Scores
mean_mr1m = ta.sma(momentum_ratio_1m, lookback)
std_mr1m = ta.stdev(momentum_ratio_1m, lookback)
mean_mr15d = ta.sma(momentum_ratio_15d, lookback)
std_mr15d = ta.stdev(momentum_ratio_15d, lookback)

z_score_1m = (momentum_ratio_1m - mean_mr1m) / std_mr1m
z_score_15d = (momentum_ratio_15d - mean_mr15d) / std_mr15d

// Calculate Weighted Average Z Score
weighted_z_score = 0.5 * z_score_1m + 0.5 * z_score_15d

// Calculate Normalized Momentum Score
normalized_momentum_score = weighted_z_score >= 0 ? (1 + weighted_z_score) : (1 / (1 - weighted_z_score))

// Plot Normalized Momentum Score
plot(normalized_momentum_score, title="Normalized Momentum Score", color=color.blue, linewidth=2)

// Optional: Show histogram
plot(normalized_momentum_score, style=plot.style_histogram, color=color.blue, linewidth=2, title="Normalized Momentum Score Histogram")

```
