# Video script — The value of waiting to sell: maize storage in Uasin-Gishu, Kenya

Twelve slides, two paragraphs each (≈ 1,750 spoken words, ≈ 11–12 minutes at a natural pace).
Figures are in `figures/notebook/`. For a ≈ 6–7 minute version: drop slide 6, keep only the
first paragraph of slides 3, 5 and 10, and merge slides 11 and 12.

---

## Slide 1 — The question (title slide)

Maize is Kenya's staple food, and most of it is grown by smallholder farmers. They harvest
between October and December, when prices are at their lowest, and most of them sell
immediately — they need cash, and grain stored at home loses up to a third of its weight to
insects and rodents over a year. In Eldoret, the centre of Kenya's main maize region, the company
agriBORA now runs a certified warehouse, agriGHALA, where farmers can store graded, insured
grain and borrow against it.

So the question of this project is simple: if you are holding maize after the harvest, is it
worth waiting to sell, when should you sell, and does it actually pay once you account for
interest, storage fees and losses? The project was inspired by a Zindi challenge on forecasting
maize prices; I asked the decision question behind the forecast.

## Slide 2 — The variables: one inequality

Everything comes down to one comparison. Selling at the end of month t instead of in December
pays if the expected price ratio, P_t over P_0, times a decay factor e to the minus (i plus c)
times t, is greater than one. P_0 is the December price; i is the interest rate — the cost of
waiting for your money, which in practice is the rate on a loan against the stored grain, about
15% a year in Kenya; and c is the holding cost: storage fees of about 3% a year in a warehouse,
or losses of around 20% a year if the grain sits on the farm.

This is what economists call the cost of carry. The interest rate and the holding cost come from
published sources. The only thing we have to estimate from data is the left-hand side: how much
the price is expected to rise after harvest, and how uncertain that rise is. That is what the
rest of the analysis does.

## Slide 3 — The data (figure 01: price history)

The data are 19 years of monthly wholesale maize prices for Eldoret, from 2006 to mid-2025, from
the World Food Programme's market monitoring, with a few gaps filled from Kenya's government
market system. Prices are in Kenyan shillings per kilogram and are not inflation-adjusted, which
matches the interest rate, which is not inflation-adjusted either.

Two things stand out. Prices drift upward over time, roughly with inflation, and they spike in
drought years — 2011, 2017, and especially 2022–23, when they reached about 90 shillings a
kilogram. But underneath, there is a pattern that repeats every year: low after the harvest, high
a few months later. That repeating pattern is the opportunity.

## Slide 4 — Is there really a seasonal cycle? (figure 02)

Here each line is one season, from December to November. On the left are the actual prices: the
levels differ a lot from year to year. On the right, each season is divided by its own harvest
price, and now a common shape appears: prices climb from January, peak around June, and fall back
as the next harvest arrives. The red line is the average, with a two-standard-error band.

I tested this formally. In 15 of 17 seasons, the price in May to July was higher than at
harvest — a sign test gives p of about 0.001. A permutation test that scrambles the timing within
each year confirms the annual cycle with p of about 0.0002. So the seasonal rise is not noise.

## Slide 5 — The seasonal growth curve (figure 03)

To use the pattern in a model, I need a smooth curve for the expected price change in each
month. The orange points are the raw monthly averages with their error bars; the blue curve is a
Fourier series — a single sine wave over the year — fitted by least squares. I chose one harmonic
by leave-one-year-out cross-validation: it predicted held-out years better than more harmonics or
the raw averages.

I also checked that this curve predicts prices it has not seen. Re-fitting it month by month using
only past data, it beats a "no change" forecast three months ahead — the error falls from about
19% to 15% — and that improvement is statistically significant. The curve implies a typical rise of
about 34% from December to June.

## Slide 6 — The random part, and checking the model (figure 04)

Around that seasonal curve, prices fluctuate randomly. I model this with geometric Brownian
motion: the log price is a random walk with the seasonal drift. The volatility — the standard
deviation of the random part, per square root of a year — is about 0.40. This plot shows it is
not constant: it is highest in years of large price shocks — sharp rises like 2011 and 2022, and
the falls that follow them, like 2010 and 2018 — and in the lean months, May to August.

The shocks also have fat tails and a negative correlation from one year to the next — a shortage
year tends to be followed by a recovery. So the model is an approximation. Still, when I simulate
it, about 89–90% of real three- and six-month price changes fall inside its 90% band, which is
what a well-calibrated model should give.

## Slide 7 — Solving "when to sell" (figure 08: the tree)

Choosing when to sell is an optimal stopping problem — in finance, an American-style option. I
solve it on a binomial tree: at each step the price can go up or down, with the up-probability
set by the seasonal curve. Working backwards from November, each node compares selling now with
the discounted expected value of waiting one more step — the Bellman equation.

The result is striking. Blue nodes mean "wait", red means "sell". Every node is blue until June,
and in June every node is red — whatever the price. The optimal rule does not depend on the price
at all; it depends only on the calendar. I checked the tree against a standard textbook option,
and against 200,000 simulated price paths, which agree within one standard error.

## Slide 8 — How much is waiting worth? (figure 05)

This plot shows the expected gain from committing in December to sell in a given month. In a
certified warehouse, selling at the end of June gains about 27% over selling at harvest — roughly
950 shillings on a 90-kilogram bag. On the farm, with 20% annual losses, the gain is about 18%. So
most of the difference between warehouse and farm storage is the losses.

Why is the rule a fixed date? The payoff is the price itself, and every cost is proportional to
the price. Then the value is simply the price times a function of time, so the comparison "sell
now or wait" is the same at every price. The tree is just the cost-of-carry inequality, checked
month by month: keep holding while next month's expected rise beats the roughly 1.5% monthly cost
of waiting.

## Slide 9 — Does it work on real seasons? (figure 06)

The model is only an approximation, so the real test is history. For each of 17 seasons, I
re-estimated the model using only data available before that season, picked the sale month, and
computed what a farmer would actually have earned, after interest, fees and losses. Each bar is
one season; the year is the December the season starts in.

Warehouse storage beat selling at harvest in 13 of 17 seasons, with an average gain of 28% and a
95% confidence interval of 7 to 52%. Even without the 2022–23 spike the average is 25%. But the bad
seasons are real: the seasons starting in December 2009 and 2017 lost 28 to 57%. I also tested a
price-dependent rule — sell early if the price runs ahead of its usual path — and it never helped.

## Slide 10 — How high can costs go? (figure 07)

Finally, how sensitive is this to the costs? On the left I vary the on-farm loss rate; on the
right, the interest rate in the warehouse. Blue is the model, orange is the historical average.
The point where each line crosses zero is the break-even.

Warehouse storage keeps paying up to an interest rate of about 53 to 68% a year — far above
Kenyan lending rates of about 15%. On-farm storage breaks even at losses of about 45 to 60% a year,
so typical losses of 20 to 36% still pay, but with a much thinner margin. For agriBORA, the message
is that the value of certified storage is mainly in removing losses.

## Slide 11 — How does this compare to stocks and options?

As an investment, storing maize in a warehouse from December to June returned on average 28% per
season — after paying 15% interest — with a season-to-season standard deviation of about 47%.
That is a mean-to-volatility ratio of about 0.6 per year, comparable to or better than a broad
stock index, which historically sits around 0.3 to 0.5 — but from only 17 observations and a very
lopsided distribution. Month to month, maize is about as volatile as a single risky stock, roughly
twice a broad index. The key difference is predictability: a stock price has no reliable
calendar pattern, because any predictable rise would be traded away. The maize rise survives
because exploiting it requires physical storage, financing and absorbing losses — exactly the
barriers a warehouse with receipt-backed loans lowers.

Compared with options, the result is almost the opposite of what one might expect. For a normal
option, volatility adds value, and an American put has an early-exercise boundary that depends
on the price. Here the payoff is linear and the costs are proportional, so volatility does not
create any option value and the "option to wait" collapses to a calendar rule — much like the
textbook result that an American call on a stock without dividends is never exercised early. And
where maize futures exist, a farmer could lock in the June price today and the decision would be
riskless; Kenyan farmers cannot, which is why the bad seasons matter.

## Slide 12 — Limitations and what I learned

The main limitations: one wholesale market, not farm-gate prices; only 17 seasons; costs from
recent sources applied to two decades of prices; a farmer who cares only about the average, not
the risk of a bad year; and no model of government interventions such as import-duty waivers,
which can dominate a single season.

What I learned: textbook option pricing assumes you can hedge, and when you cannot, you have to
estimate the real expected price path and validate it. A sophisticated model can turn out to be
equivalent to a simple principle — here, cost of carry — and recognising that is a result, not a
failure. And the most convincing evidence came from the simplest test: replaying the decision on
real seasons.
