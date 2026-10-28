"""
quantkit — cleaned-up, tested versions of the core functions from the
Erdős Institute *Quantitative Methods in Finance* notebooks
(TheErdosInstitute/quant-finance, Summer 2025 – Fall 2026).

Every function here exists, in some form, in the course notebooks. The
notebooks redefine the same functions dozens of times with different argument
orders and a few bugs; this module keeps ONE version of each, with one
convention, and is checked by ``test_quantkit.py``.

Conventions (used everywhere below)
-----------------------------------
* Argument order follows the course: ``(S, K, sigma, t, r, q=0)``.
* ``t`` is time to expiration in **years**; ``sigma``, ``r``, ``q`` are
  **annualized**, continuously compounded.
* ``q`` is a continuous yield paid out by the asset (dividend yield, foreign
  interest rate, or — for commodities — a cost/convenience yield). ``q=0``
  recovers the plain course formulas.
* Theta is reported the course's way: ``theta = -dV/dt`` per **year**
  (divide by 365 or 52 for a per-day or per-week figure).
* All pricing functions accept NumPy arrays and broadcast.
* Random functions take an optional ``rng`` (``np.random.Generator``) so
  results can be reproduced: ``rng = np.random.default_rng(42)``.

Bugs fixed relative to the notebooks (see test_quantkit.py)
----------------------------------------------------------
* ``bs_put_delta`` returned +Phi(-d1) instead of -Phi(-d1)
  (Fall 2026 L9, "Completed American and Dividends", both the q=0 and q
  versions).
* ``bs_vega`` had an extra factor of sigma, S*sigma*sqrt(t)*phi(d1)
  (Spring 2026 L9 and L10 Complete notebooks).
* ``bs_gamma`` was missing sigma in the denominator (Spring 2026 L11 Blank).
* ``bs_call_delta`` returned the call *price* (Summer 2026 L12 Blank).

Sections
--------
1. Returns and volatility            (course Lecture 3a; F26 L8)
2. Testing GBM assumptions           (Lecture 8; F26 L8, Su26 L7)
3. Monte Carlo                       (Lecture 2)
4. Path simulation                   (Lectures 4, 11b; F26 L8, Su26 L8)
5. Black–Scholes prices and Greeks   (Lectures 5–6, 9)
6. Implied volatility                (Lecture 10; Su26 L10–12)
7. Binomial trees / early exercise   (Lecture 9; F26 L9) + one extension
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm
from scipy.stats import chi2, norm, normaltest, shapiro

__all__ = [
    # 1
    "log_returns", "annualized_vol", "rolling_vol",
    # 2
    "test_normality", "ljung_box",
    # 3
    "mc_estimate",
    # 4
    "gbm_paths", "markov_vol_states", "correlated_normals",
    # 5
    "bs_d1_d2", "bs_call", "bs_put", "bs_call_delta", "bs_put_delta",
    "bs_gamma", "bs_vega", "bs_call_theta", "bs_put_theta",
    "bs_call_rho", "bs_put_rho", "bs_vanna", "bs_volga",
    # 6
    "bs_implied_vol",
    # 7
    "crr_parameters", "american_call", "american_put",
    "binomial_optimal_stopping",
]


# ---------------------------------------------------------------------------
# 1. Returns and volatility
# ---------------------------------------------------------------------------

def log_returns(prices):
    """Log returns ln(S_i / S_{i-1}) of a price series.

    Parameters
    ----------
    prices : array-like or pandas Series/DataFrame
        Prices in time order. A DataFrame is handled column by column.

    Returns
    -------
    Same type as the input (NumPy array, Series or DataFrame), one row
    shorter. For pandas input the first (NaN) row is dropped.
    """
    if hasattr(prices, "shift"):                      # pandas object
        return np.log(prices / prices.shift(1)).dropna(how="all")
    p = np.asarray(prices, dtype=float)
    return np.log(p[1:] / p[:-1])


def annualized_vol(returns, periods_per_year=252):
    """Annualized volatility: std of log returns times sqrt(periods per year).

    The course uses 252 for daily data. Use 52 for weekly data (e.g. the
    agriBORA maize prices) and 12 for monthly data.

    Uses the sample standard deviation (ddof=1), matching pandas ``.std()``.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    return np.std(r, ddof=1) * np.sqrt(periods_per_year)


def rolling_vol(returns, window, periods_per_year=252):
    """Rolling annualized volatility of a pandas Series/DataFrame of returns.

    Mirrors ``returns.rolling(window).std() * sqrt(periods_per_year)`` from
    the Fall 2026 Lecture 8 notebook. NaN rows from the warm-up are dropped.
    """
    return (returns.rolling(window).std() * np.sqrt(periods_per_year)).dropna(how="all")


# ---------------------------------------------------------------------------
# 2. Testing the GBM / Black–Scholes assumptions (Lecture 8)
# ---------------------------------------------------------------------------

def test_normality(returns, alpha=0.05):
    """Test whether log returns look normally distributed.

    Runs the two tests used in the course: D'Agostino–Pearson
    (``scipy.stats.normaltest``) and Shapiro–Wilk (``scipy.stats.shapiro``).

    Returns
    -------
    dict with p-values, sample skewness / excess kurtosis, and
    ``reject_normal`` = True if either p-value is below ``alpha``.

    Notes
    -----
    A small p-value is evidence AGAINST normality. A large p-value is not
    proof of normality — short samples (e.g. ~100 weekly prices) have little
    power to reject.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    _, p_dagostino = normaltest(r)
    _, p_shapiro = shapiro(r)
    z = (r - r.mean()) / r.std(ddof=1)
    return {
        "n": r.size,
        "p_dagostino": float(p_dagostino),
        "p_shapiro": float(p_shapiro),
        "skewness": float(np.mean(z**3)),
        "excess_kurtosis": float(np.mean(z**4) - 3.0),
        "reject_normal": bool(min(p_dagostino, p_shapiro) < alpha),
    }


def ljung_box(x, lags=10):
    """Ljung–Box test for autocorrelation, lags 1..``lags``.

    Same statistic as ``statsmodels.stats.diagnostic.acorr_ljungbox`` used in
    the course (implemented here so statsmodels is not required):

        Q(h) = n (n + 2) * sum_{k=1}^{h} rho_k^2 / (n - k),   Q(h) ~ chi2(h)

    Course usage:
      * ``ljung_box(r)``        — are signed returns autocorrelated?
      * ``ljung_box(abs(r))``   — volatility clustering?
      * ``ljung_box(r**2)``     — same idea with squared returns.

    Returns
    -------
    dict with arrays ``lags``, ``lb_stat``, ``lb_pvalue`` (one entry per lag).
    Small p-values = evidence of autocorrelation up to that lag.
    """
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if lags >= n:
        raise ValueError(f"lags ({lags}) must be smaller than the sample size ({n}).")
    xc = x - x.mean()
    denom = np.sum(xc**2)
    acf = np.array([np.sum(xc[k:] * xc[:-k]) / denom for k in range(1, lags + 1)])
    ks = np.arange(1, lags + 1)
    stat = n * (n + 2) * np.cumsum(acf**2 / (n - ks))
    return {"lags": ks, "lb_stat": stat, "lb_pvalue": chi2.sf(stat, ks), "acf": acf}


# ---------------------------------------------------------------------------
# 3. Monte Carlo (Lecture 2)
# ---------------------------------------------------------------------------

def mc_estimate(samples):
    """Monte Carlo estimate of E[X] with its standard error.

    Returns ``(mean, standard_error)``. A rough 95% confidence interval is
    ``mean ± 2 * standard_error`` (the course's 68–95–99.7 rule).

    Example
    -------
    >>> payoff = np.exp(-r*t) * np.maximum(S_T - K, 0)
    >>> price, se = mc_estimate(payoff)
    """
    x = np.asarray(samples, dtype=float).ravel()
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(x.size))


# ---------------------------------------------------------------------------
# 4. Path simulation (Lectures 4, 11b)
# ---------------------------------------------------------------------------

def gbm_paths(S0, sigma, t, r, n_steps, n_sims, mu=0.0, q=0.0, rng=None,
              return_times=False):
    """Simulate geometric Brownian motion paths (course ``gbm_paths``).

    Each step multiplies the price by

        exp((mu + r - q - sigma^2 / 2) dt + sigma sqrt(dt) Z),  Z ~ N(0, 1)

    so E[S_t] = S0 * exp((mu + r - q) t). ``mu`` is the course's *excess*
    log-drift: ``mu=0`` is the risk-neutral model.

    Parameters
    ----------
    S0 : float            starting price
    sigma : float or array
        Annualized volatility. An array of shape ``(n_sims, n_steps)`` gives
        a different sigma per step — use it with ``markov_vol_states`` for
        regime-switching paths (Summer 2026 Lecture 8).
    t : float             horizon in years
    r : float             risk-free rate
    n_steps, n_sims : int
    mu : float or array of length n_steps
        Excess drift; an array allows a time-varying (e.g. seasonal) drift.
    q : float             yield paid by the asset (dividends, carry)
    rng : np.random.Generator, optional
    return_times : bool   also return the time grid (length n_steps + 1)

    Returns
    -------
    paths : ndarray, shape (n_sims, n_steps + 1); column 0 equals S0.
    """
    rng = np.random.default_rng() if rng is None else rng
    dt = t / n_steps
    sigma = np.broadcast_to(np.asarray(sigma, dtype=float), (n_sims, n_steps))
    mu = np.broadcast_to(np.asarray(mu, dtype=float), (n_steps,))
    z = rng.standard_normal((n_sims, n_steps))
    steps = (mu + r - q - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    log_paths = np.concatenate([np.zeros((n_sims, 1)), np.cumsum(steps, axis=1)], axis=1)
    paths = S0 * np.exp(log_paths)
    if return_times:
        return paths, np.linspace(0.0, t, n_steps + 1)
    return paths


def markov_vol_states(n_sims, n_steps, P=None, alpha=None, beta=None, dt=None,
                      start_state=0, rng=None):
    """Simulate a two-state (0 = low vol, 1 = high vol) Markov chain.

    Give EITHER a one-step transition matrix ``P`` (discrete chain), OR the
    continuous switching rates ``alpha`` (low→high) and ``beta`` (high→low)
    together with the step size ``dt``; then P = expm(Q dt) with
    Q = [[-alpha, alpha], [beta, -beta]] (Summer 2026 Lecture 8).

    ``start_state`` may be 0, 1, or ``"stationary"`` (draw from the long-run
    distribution, P(high) = alpha / (alpha + beta)).

    Returns
    -------
    states : int ndarray, shape (n_sims, n_steps)

    Example (regime-switching GBM)
    -------
    >>> s = markov_vol_states(1000, 52, alpha=3, beta=4, dt=1/52)
    >>> sig = np.where(s == 0, 0.20, 0.60)
    >>> paths = gbm_paths(100, sig, 1.0, 0.05, 52, 1000)
    """
    rng = np.random.default_rng() if rng is None else rng
    if P is None:
        if alpha is None or beta is None or dt is None:
            raise ValueError("Give P, or all of alpha, beta and dt.")
        P = expm(np.array([[-alpha, alpha], [beta, -beta]], dtype=float) * dt)
    P = np.asarray(P, dtype=float)
    if start_state == "stationary":
        p_high = (1 - P[0, 0]) / ((1 - P[0, 0]) + (1 - P[1, 1]))
        first = (rng.uniform(size=n_sims) < p_high).astype(int)
    else:
        first = np.full(n_sims, int(start_state))
    states = np.empty((n_sims, n_steps), dtype=int)
    states[:, 0] = first
    u = rng.uniform(size=(n_sims, n_steps))
    for i in range(1, n_steps):
        prev = states[:, i - 1]
        stay = np.where(prev == 0, P[0, 0], P[1, 1])
        states[:, i] = np.where(u[:, i] < stay, prev, 1 - prev)
    return states


def correlated_normals(corr, size, rng=None):
    """Draw standard normals with a given correlation matrix (Cholesky).

    Generalizes the course's two-variable trick
    Z2 = rho * Z1 + sqrt(1 - rho^2) * N   (Fall 2025 HW 2, Heston lectures).

    Parameters
    ----------
    corr : (d, d) correlation matrix
    size : int, number of draws

    Returns
    -------
    ndarray, shape (size, d)
    """
    rng = np.random.default_rng() if rng is None else rng
    L = np.linalg.cholesky(np.asarray(corr, dtype=float))
    return rng.standard_normal((size, L.shape[0])) @ L.T


# ---------------------------------------------------------------------------
# 5. Black–Scholes prices and Greeks (Lectures 5–6, 9)
# ---------------------------------------------------------------------------

def bs_d1_d2(S, K, sigma, t, r, q=0.0):
    """d1 and d2 of the Black–Scholes formula with continuous yield q."""
    S, K, sigma, t = (np.asarray(a, dtype=float) for a in (S, K, sigma, t))
    vol_sqrt_t = sigma * np.sqrt(t)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * t) / vol_sqrt_t
    return d1, d1 - vol_sqrt_t


def bs_call(S, K, sigma, t, r, q=0.0):
    """European call price: S e^{-qt} Phi(d1) - K e^{-rt} Phi(d2)."""
    d1, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return S * np.exp(-q * t) * norm.cdf(d1) - K * np.exp(-r * t) * norm.cdf(d2)


def bs_put(S, K, sigma, t, r, q=0.0):
    """European put price: K e^{-rt} Phi(-d2) - S e^{-qt} Phi(-d1)."""
    d1, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return K * np.exp(-r * t) * norm.cdf(-d2) - S * np.exp(-q * t) * norm.cdf(-d1)


def bs_call_delta(S, K, sigma, t, r, q=0.0):
    """dC/dS = e^{-qt} Phi(d1)  (between 0 and 1)."""
    d1, _ = bs_d1_d2(S, K, sigma, t, r, q)
    return np.exp(-q * t) * norm.cdf(d1)


def bs_put_delta(S, K, sigma, t, r, q=0.0):
    """dP/dS = -e^{-qt} Phi(-d1)  (between -1 and 0).

    Fixes the sign error in the Fall 2026 L9 notebook.
    """
    d1, _ = bs_d1_d2(S, K, sigma, t, r, q)
    return -np.exp(-q * t) * norm.cdf(-d1)


def bs_gamma(S, K, sigma, t, r, q=0.0):
    """d2V/dS2 = e^{-qt} phi(d1) / (S sigma sqrt(t)); same for calls and puts."""
    d1, _ = bs_d1_d2(S, K, sigma, t, r, q)
    return np.exp(-q * t) * norm.pdf(d1) / (S * sigma * np.sqrt(t))


def bs_vega(S, K, sigma, t, r, q=0.0):
    """dV/dsigma = S e^{-qt} sqrt(t) phi(d1); same for calls and puts.

    Per unit of sigma (multiply by 0.01 for "per vol point").
    """
    d1, _ = bs_d1_d2(S, K, sigma, t, r, q)
    return S * np.exp(-q * t) * np.sqrt(t) * norm.pdf(d1)


def bs_call_theta(S, K, sigma, t, r, q=0.0):
    """Call theta, -dC/dt, per year."""
    d1, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return (-S * np.exp(-q * t) * norm.pdf(d1) * sigma / (2 * np.sqrt(t))
            - r * K * np.exp(-r * t) * norm.cdf(d2)
            + q * S * np.exp(-q * t) * norm.cdf(d1))


def bs_put_theta(S, K, sigma, t, r, q=0.0):
    """Put theta, -dP/dt, per year (can be positive for deep ITM puts)."""
    d1, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return (-S * np.exp(-q * t) * norm.pdf(d1) * sigma / (2 * np.sqrt(t))
            + r * K * np.exp(-r * t) * norm.cdf(-d2)
            - q * S * np.exp(-q * t) * norm.cdf(-d1))


def bs_call_rho(S, K, sigma, t, r, q=0.0):
    """dC/dr = K t e^{-rt} Phi(d2)."""
    _, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return K * t * np.exp(-r * t) * norm.cdf(d2)


def bs_put_rho(S, K, sigma, t, r, q=0.0):
    """dP/dr = -K t e^{-rt} Phi(-d2)."""
    _, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return -K * t * np.exp(-r * t) * norm.cdf(-d2)


def bs_vanna(S, K, sigma, t, r, q=0.0):
    """d2V/(dS dsigma) = -e^{-qt} phi(d1) d2 / sigma; same for calls and puts."""
    d1, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return -np.exp(-q * t) * norm.pdf(d1) * d2 / sigma


def bs_volga(S, K, sigma, t, r, q=0.0):
    """d2V/dsigma2 = vega d1 d2 / sigma; same for calls and puts."""
    d1, d2 = bs_d1_d2(S, K, sigma, t, r, q)
    return bs_vega(S, K, sigma, t, r, q) * d1 * d2 / sigma


# ---------------------------------------------------------------------------
# 6. Implied volatility (Lecture 10)
# ---------------------------------------------------------------------------

def bs_implied_vol(price, S, K, t, r, q=0.0, kind="call", lo=1e-6, hi=5.0,
                   tol=1e-10, max_iter=200):
    """Black–Scholes implied volatility, vectorized.

    Newton's method with a bisection fallback (the Summer 2026 L10–12
    hybrid): take a Newton step sigma + (price - model) / vega when it stays
    inside the current bracket [lo, hi]; otherwise bisect.

    Prices outside the no-arbitrage bounds return NaN.

    Parameters
    ----------
    price : float or array    observed option price(s)
    kind : "call" or "put"
    """
    price, S, K, t = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in (price, S, K, t)))
    shape = price.shape
    price, S, K, t = (a.ravel().copy() for a in (price, S, K, t))
    pricer = bs_call if kind == "call" else bs_put
    if kind == "call":
        lower = np.maximum(S * np.exp(-q * t) - K * np.exp(-r * t), 0.0)
        upper = S * np.exp(-q * t)
    else:
        lower = np.maximum(K * np.exp(-r * t) - S * np.exp(-q * t), 0.0)
        upper = K * np.exp(-r * t)
    valid = (price > lower) & (price < upper)

    a = np.full(price.shape, lo)
    b = np.full(price.shape, hi)
    sig = np.full(price.shape, 0.3)
    out = np.full(price.shape, np.nan)
    active = valid.copy()
    for _ in range(max_iter):
        if not active.any():
            break
        idx = np.flatnonzero(active)
        s = sig[idx]
        err = pricer(S[idx], K[idx], s, t[idx], r, q) - price[idx]
        done = np.abs(err) < tol
        out[idx[done]] = s[done]
        # shrink the bracket using the sign of the error (price is increasing in sigma)
        a[idx] = np.where(err < 0, s, a[idx])
        b[idx] = np.where(err > 0, s, b[idx])
        vega = bs_vega(S[idx], K[idx], s, t[idx], r, q)
        with np.errstate(divide="ignore", invalid="ignore"):
            newton = s - err / vega
        ok = np.isfinite(newton) & (newton > a[idx]) & (newton < b[idx])
        sig[idx] = np.where(ok, newton, 0.5 * (a[idx] + b[idx]))
        active[idx[done]] = False
    return out.reshape(shape) if shape else float(out[0])


# ---------------------------------------------------------------------------
# 7. Binomial trees and early exercise (Lecture 9)
# ---------------------------------------------------------------------------

def crr_parameters(sigma, dt, growth):
    """Cox–Ross–Rubinstein tree parameters.

    u = e^{sigma sqrt(dt)}, d = 1/u, p = (growth - d) / (u - d), where
    ``growth`` is the expected one-step price ratio E[S_{i+1}/S_i]
    (risk-neutral: e^{(r-q) dt}).

    Raises ValueError if p falls outside [0, 1]; that means dt is too large
    for the drift — increase n_steps.
    """
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.asarray(growth, dtype=float) - d) / (u - d)
    if np.any(p < 0) or np.any(p > 1):
        raise ValueError("CRR probability outside [0, 1]; use more steps (smaller dt).")
    return u, d, p


def binomial_optimal_stopping(S0, sigma, t, n_steps, payoff, r, drift=None,
                              q=0.0, holding_cost=0.0, american=True,
                              return_exercise=False):
    """Value of a payoff that can be collected at any step (or only at the end).

    EXTENSION of the course's ``bs_american_put`` (Fall 2026 L9): the same
    vectorized CRR backward induction, but with

    * any ``payoff(S)`` function (e.g. ``lambda S: S`` = "sell the grain"),
    * a ``drift`` that may differ from r and vary step by step (e.g. a
      seasonal expected price path), and
    * a proportional ``holding_cost`` (storage fees + spoilage, per year)
      paid while you wait.

    Model
    -----
    Price moves up by u or down by d each step with probability p_i chosen so
    E[S_{i+1}/S_i] = exp((drift_i - q) dt). Continuation values are
    discounted at exp(-(r + holding_cost) dt). With ``drift=None`` the drift
    is r (risk-neutral pricing) and ``payoff=lambda S: np.maximum(K - S, 0)``
    reproduces the course's American put exactly.

    Parameters
    ----------
    S0, sigma, t : float
    n_steps : int
    payoff : callable, payoff(S_array) -> array of values if stopped at S
    r : float              discount rate (opportunity cost of money)
    drift : None, float, or array of length n_steps
        Expected growth rate of the price (annualized). Element i applies to
        the step from time i*dt to (i+1)*dt.
    q : float              yield on the asset (enters the price drift)
    holding_cost : float   proportional cost of waiting, per year
    american : bool        False = payoff only at maturity (European)
    return_exercise : bool
        Also return, for each step i = 0..n_steps-1, the array of node prices
        at which stopping is optimal (empty if continuing is always better).

    Returns
    -------
    value : float
    (value, exercise_prices) if ``return_exercise``.
    """
    dt = t / n_steps
    drift_arr = np.broadcast_to(np.asarray(r if drift is None else drift, dtype=float), (n_steps,))
    u, d, p = crr_parameters(sigma, dt, np.exp((drift_arr - q) * dt))
    p = np.broadcast_to(p, (n_steps,))
    disc = np.exp(-(r + holding_cost) * dt)

    j = np.arange(-n_steps, n_steps + 1, 2)         # same node indexing as the course
    prices = S0 * u**j
    values = np.asarray(payoff(prices), dtype=float)
    exercise = [None] * n_steps
    for i in range(n_steps - 1, -1, -1):
        prices = prices[:-1] * u                      # node prices at step i
        cont = disc * (p[i] * values[1:] + (1 - p[i]) * values[:-1])
        if american:
            stop = np.asarray(payoff(prices), dtype=float)
            better = stop >= cont
            values = np.where(better, stop, cont)
            # a node counts as "exercise" only if stopping actually pays something
            exercise[i] = prices[better & (stop > 0)]
        else:
            values = cont
            exercise[i] = prices[:0]
    value = float(values[0])
    return (value, exercise) if return_exercise else value


def american_put(S0, K, sigma, t, r, q=0.0, n_steps=1000):
    """American put on a CRR tree (course ``bs_american_put``, F26 L9)."""
    return binomial_optimal_stopping(S0, sigma, t, n_steps,
                                     lambda S: np.maximum(K - S, 0.0), r, q=q)


def american_call(S0, K, sigma, t, r, q=0.0, n_steps=1000):
    """American call on a CRR tree (course ``bs_american_call``, F26 L9).

    With q = 0 early exercise is never optimal and this equals bs_call (the
    course function short-cuts to bs_call in that case; here the tree is
    always used so the equality can be tested).
    """
    return binomial_optimal_stopping(S0, sigma, t, n_steps,
                                     lambda S: np.maximum(S - K, 0.0), r, q=q)
