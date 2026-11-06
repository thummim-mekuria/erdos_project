"""
Tests for quantkit.py. Run from this folder with:

    python -m unittest -v test_quantkit

Each test checks a function against something independent of it: a
closed-form identity, a finite difference, a Monte Carlo estimate, or a
known limiting case. Random tests use fixed seeds so they are reproducible.
"""

import unittest

import numpy as np
from scipy.stats import norm

import quantkit as qk

# A standard test case plus a grid of strikes/vols/maturities.
S, K, SIG, T, R, Q = 100.0, 95.0, 0.30, 0.75, 0.04, 0.02
GRID = [
    (100, 80, 0.2, 0.25, 0.03, 0.0),
    (100, 100, 0.3, 1.0, 0.05, 0.02),
    (100, 130, 0.5, 2.0, 0.01, 0.04),
    (250, 250, 0.3, 1.0, 0.039, 0.0),   # Summer 2026 BS exercise parameters
]


def fd(f, x, h):
    """Central finite difference of f at x."""
    return (f(x + h) - f(x - h)) / (2 * h)


class TestBlackScholes(unittest.TestCase):

    def test_put_call_parity(self):
        for s, k, sig, t, r, q in GRID:
            lhs = qk.bs_call(s, k, sig, t, r, q) - qk.bs_put(s, k, sig, t, r, q)
            rhs = s * np.exp(-q * t) - k * np.exp(-r * t)
            self.assertAlmostEqual(lhs, rhs, places=10)

    def test_q_zero_matches_course_formula(self):
        # The course's q-free formula, written out independently.
        d1 = (np.log(S / K) + (R + 0.5 * SIG**2) * T) / (SIG * np.sqrt(T))
        d2 = d1 - SIG * np.sqrt(T)
        course = S * norm.cdf(d1) - K * np.exp(-R * T) * norm.cdf(d2)
        self.assertAlmostEqual(qk.bs_call(S, K, SIG, T, R), course, places=12)

    def test_prices_against_monte_carlo(self):
        rng = np.random.default_rng(0)
        ST = qk.gbm_paths(S, SIG, T, R, 1, 400_000, q=Q, rng=rng)[:, -1]
        call, se_c = qk.mc_estimate(np.exp(-R * T) * np.maximum(ST - K, 0))
        put, se_p = qk.mc_estimate(np.exp(-R * T) * np.maximum(K - ST, 0))
        self.assertLess(abs(call - qk.bs_call(S, K, SIG, T, R, Q)), 4 * se_c)
        self.assertLess(abs(put - qk.bs_put(S, K, SIG, T, R, Q)), 4 * se_p)

    def test_greeks_against_finite_differences(self):
        for s, k, sig, t, r, q in GRID:
            h = 1e-4
            c = lambda x: qk.bs_call(x, k, sig, t, r, q)
            p = lambda x: qk.bs_put(x, k, sig, t, r, q)
            self.assertAlmostEqual(qk.bs_call_delta(s, k, sig, t, r, q), fd(c, s, h), places=6)
            self.assertAlmostEqual(qk.bs_put_delta(s, k, sig, t, r, q), fd(p, s, h), places=6)
            gamma_fd = fd(lambda x: qk.bs_call_delta(x, k, sig, t, r, q), s, h)
            self.assertAlmostEqual(qk.bs_gamma(s, k, sig, t, r, q), gamma_fd, places=6)
            vega_fd = fd(lambda v: qk.bs_call(s, k, v, t, r, q), sig, h)
            self.assertAlmostEqual(qk.bs_vega(s, k, sig, t, r, q), vega_fd, places=5)
            vega_put_fd = fd(lambda v: qk.bs_put(s, k, v, t, r, q), sig, h)
            self.assertAlmostEqual(qk.bs_vega(s, k, sig, t, r, q), vega_put_fd, places=5)
            # theta = -dV/dt
            th_c = -fd(lambda x: qk.bs_call(s, k, sig, x, r, q), t, h)
            th_p = -fd(lambda x: qk.bs_put(s, k, sig, x, r, q), t, h)
            self.assertAlmostEqual(qk.bs_call_theta(s, k, sig, t, r, q), th_c, places=5)
            self.assertAlmostEqual(qk.bs_put_theta(s, k, sig, t, r, q), th_p, places=5)
            rho_c = fd(lambda x: qk.bs_call(s, k, sig, t, x, q), r, h)
            rho_p = fd(lambda x: qk.bs_put(s, k, sig, t, x, q), r, h)
            self.assertAlmostEqual(qk.bs_call_rho(s, k, sig, t, r, q), rho_c, places=5)
            self.assertAlmostEqual(qk.bs_put_rho(s, k, sig, t, r, q), rho_p, places=5)
            vanna_fd = fd(lambda v: qk.bs_call_delta(s, k, v, t, r, q), sig, h)
            self.assertAlmostEqual(qk.bs_vanna(s, k, sig, t, r, q), vanna_fd, places=5)
            volga_fd = fd(lambda v: qk.bs_vega(s, k, v, t, r, q), sig, h)
            self.assertAlmostEqual(qk.bs_volga(s, k, sig, t, r, q), volga_fd, places=4)

    def test_greek_signs_and_relations(self):
        for s, k, sig, t, r, q in GRID:
            dc = qk.bs_call_delta(s, k, sig, t, r, q)
            dp = qk.bs_put_delta(s, k, sig, t, r, q)
            self.assertTrue(0 < dc < 1)
            self.assertTrue(-1 < dp < 0)                         # notebook bug: was positive
            self.assertAlmostEqual(dc - dp, np.exp(-q * t), places=12)
            self.assertGreater(qk.bs_gamma(s, k, sig, t, r, q), 0)
            self.assertGreater(qk.bs_vega(s, k, sig, t, r, q), 0)

    def test_arrays_broadcast(self):
        Ks = np.array([80.0, 100.0, 120.0])
        out = qk.bs_call(S, Ks, SIG, T, R)
        self.assertEqual(out.shape, (3,))
        self.assertTrue(np.all(np.diff(out) < 0))                # calls fall as K rises


class TestNotebookBugsAreFixed(unittest.TestCase):
    """The four notebook variants found to be wrong, compared with quantkit."""

    def test_put_delta_sign(self):
        d1, _ = qk.bs_d1_d2(S, K, SIG, T, R)
        notebook = norm.cdf(-d1)                                  # F26 L9 version
        self.assertAlmostEqual(qk.bs_put_delta(S, K, SIG, T, R), -notebook, places=12)

    def test_vega_extra_sigma(self):
        d1, _ = qk.bs_d1_d2(S, K, SIG, T, R)
        notebook = S * SIG * np.sqrt(T) * norm.pdf(d1)            # Sp26 L9/L10 version
        self.assertAlmostEqual(qk.bs_vega(S, K, SIG, T, R), notebook / SIG, places=10)

    def test_gamma_missing_sigma(self):
        d1, _ = qk.bs_d1_d2(S, K, SIG, T, R)
        notebook = norm.pdf(d1) / (S * np.sqrt(T))                # Sp26 L11 Blank version
        self.assertAlmostEqual(qk.bs_gamma(S, K, SIG, T, R), notebook / SIG, places=12)


class TestImpliedVol(unittest.TestCase):

    def test_round_trip(self):
        # (a deep-ITM option at very low vol is priced at intrinsic value to machine
        #  precision, so its implied vol is undefined — keep the low vol near the money)
        sigs = np.array([0.05, 0.2, 0.5, 1.2])
        Ks = np.array([100.0, 80.0, 130.0, 100.0])
        for kind, pricer in (("call", qk.bs_call), ("put", qk.bs_put)):
            prices = pricer(S, Ks, sigs, T, R, Q)
            iv = qk.bs_implied_vol(prices, S, Ks, T, R, Q, kind=kind)
            np.testing.assert_allclose(iv, sigs, atol=1e-7)

    def test_scalar_and_arbitrage_bounds(self):
        p = qk.bs_call(S, K, 0.3, T, R)
        self.assertAlmostEqual(qk.bs_implied_vol(p, S, K, T, R), 0.3, places=7)
        self.assertTrue(np.isnan(qk.bs_implied_vol(S + 1.0, S, K, T, R)))   # above upper bound


class TestBinomial(unittest.TestCase):

    def test_european_tree_converges_to_bs(self):
        for s, k, sig, t, r, q in GRID:
            tree = qk.binomial_optimal_stopping(s, sig, t, 2000, lambda x: np.maximum(k - x, 0),
                                                r, q=q, american=False)
            self.assertAlmostEqual(tree, float(qk.bs_put(s, k, sig, t, r, q)), delta=0.01)

    def test_american_put_at_least_european(self):
        for s, k, sig, t, r, q in GRID:
            self.assertGreaterEqual(qk.american_put(s, k, sig, t, r, q, 500) + 1e-12,
                                    float(qk.bs_put(s, k, sig, t, r, q)) - 0.01)
        # deep ITM, high rate: early exercise premium must be clearly positive
        self.assertGreater(qk.american_put(100, 140, 0.2, 1, 0.08) - qk.bs_put(100, 140, 0.2, 1, 0.08), 0.5)

    def test_american_call_no_dividend_equals_european(self):
        for s, k, sig, t, r, _ in GRID:
            self.assertAlmostEqual(qk.american_call(s, k, sig, t, r, 0.0, 2000),
                                   float(qk.bs_call(s, k, sig, t, r)), delta=0.01)

    def test_matches_course_american_put(self):
        # Course code (Fall 2026 L9, bs_american_put), copied verbatim in logic.
        def course(S0, K, sigma, t, r, q=0, n_steps=1000):
            dt = t / n_steps
            u = np.exp(sigma * np.sqrt(dt)); d = 1 / u
            p = (np.exp((r - q) * dt) - d) / (u - d)
            prices = S0 * u ** np.arange(-n_steps, n_steps + 1, 2)
            vals = np.maximum(K - prices, 0)
            for _ in range(n_steps):
                prices = prices[:-1] * u
                vals = np.maximum((p * vals[1:] + (1 - p) * vals[:-1]) * np.exp(-r * dt), K - prices)
            return vals[0]
        self.assertAlmostEqual(qk.american_put(150, 145, 0.4, 1, 0.04, 0.02),
                               course(150, 145, 0.4, 1, 0.04, 0.02), places=10)

    def test_storage_limiting_cases(self):
        sell = lambda x: x
        # Price grows no faster than the cost of waiting -> sell now, value = S0.
        v = qk.binomial_optimal_stopping(30.0, 0.25, 0.5, 200, sell, r=0.10, drift=0.10, holding_cost=0.05)
        self.assertAlmostEqual(v, 30.0, places=10)
        # Price grows faster than the cost of waiting -> hold to maturity.
        v = qk.binomial_optimal_stopping(30.0, 0.25, 0.5, 200, sell, r=0.10, drift=0.40, holding_cost=0.05)
        self.assertAlmostEqual(v, 30.0 * np.exp((0.40 - 0.10 - 0.05) * 0.5), places=8)

    def test_exercise_region_returned(self):
        v, ex = qk.binomial_optimal_stopping(100, 0.3, 1, 50, lambda x: np.maximum(110 - x, 0),
                                             0.06, return_exercise=True)
        self.assertEqual(len(ex), 50)
        # put exercise region is low prices: every exercised node is below the strike
        self.assertTrue(all(np.all(e < 110) for e in ex))

    def test_bad_steps_raise(self):
        with self.assertRaises(ValueError):
            qk.binomial_optimal_stopping(100, 0.01, 1, 2, lambda x: x, 0.05, drift=2.0)


class TestSimulation(unittest.TestCase):

    def test_gbm_moments(self):
        rng = np.random.default_rng(1)
        mu, n_steps = 0.05, 52
        paths, times = qk.gbm_paths(100, 0.3, 1.0, 0.03, n_steps, 200_000, mu=mu, q=0.01,
                                    rng=rng, return_times=True)
        self.assertEqual(paths.shape, (200_000, n_steps + 1))
        self.assertTrue(np.all(paths[:, 0] == 100))
        self.assertAlmostEqual(times[-1], 1.0)
        mean, se = qk.mc_estimate(paths[:, -1])
        self.assertLess(abs(mean - 100 * np.exp(0.05 + 0.03 - 0.01)), 4 * se)
        step_sd = np.std(np.log(paths[:, 1:] / paths[:, :-1]))
        self.assertAlmostEqual(step_sd, 0.3 * np.sqrt(1 / n_steps), places=3)

    def test_markov_stationary_fraction(self):
        rng = np.random.default_rng(2)
        alpha, beta = 3.0, 4.0
        s = qk.markov_vol_states(4000, 520, alpha=alpha, beta=beta, dt=1 / 52,
                                 start_state="stationary", rng=rng)
        self.assertAlmostEqual(s.mean(), alpha / (alpha + beta), delta=0.01)

    def test_markov_discrete_matrix(self):
        rng = np.random.default_rng(3)
        P = np.array([[0.95, 0.05], [0.08, 0.92]])
        s = qk.markov_vol_states(2000, 400, P=P, rng=rng)
        lows = s[:, :-1] == 0
        stay_low = np.mean(s[:, 1:][lows] == 0)
        self.assertAlmostEqual(stay_low, 0.95, delta=0.005)

    def test_regime_paths_shape(self):
        rng = np.random.default_rng(4)
        s = qk.markov_vol_states(10, 52, alpha=3, beta=4, dt=1 / 52, rng=rng)
        paths = qk.gbm_paths(100, np.where(s == 0, 0.2, 0.6), 1.0, 0.05, 52, 10, rng=rng)
        self.assertEqual(paths.shape, (10, 53))

    def test_correlated_normals(self):
        rng = np.random.default_rng(5)
        corr = np.array([[1.0, 0.6, -0.2], [0.6, 1.0, 0.1], [-0.2, 0.1, 1.0]])
        z = qk.correlated_normals(corr, 300_000, rng=rng)
        np.testing.assert_allclose(np.corrcoef(z.T), corr, atol=0.01)


class TestReturnsAndDiagnostics(unittest.TestCase):

    def test_vol_recovers_sigma(self):
        rng = np.random.default_rng(6)
        path = qk.gbm_paths(100, 0.25, 20.0, 0.0, 20 * 52, 1, rng=rng)[0]
        self.assertAlmostEqual(qk.annualized_vol(qk.log_returns(path), 52), 0.25, delta=0.01)

    def test_pandas_inputs(self):
        import pandas as pd
        s = pd.Series([100, 101, 99, 102, 104, 103], dtype=float)
        lr = qk.log_returns(s)
        self.assertEqual(len(lr), 5)
        self.assertAlmostEqual(lr.iloc[0], np.log(101 / 100))
        rv = qk.rolling_vol(lr, 3, periods_per_year=52)
        self.assertEqual(len(rv), 3)

    def test_normality(self):
        rng = np.random.default_rng(7)
        self.assertFalse(qk.test_normality(rng.standard_normal(500))["reject_normal"])
        fat = qk.test_normality(rng.standard_t(3, 500))
        self.assertTrue(fat["reject_normal"])
        self.assertGreater(fat["excess_kurtosis"], 1)

    def test_ljung_box(self):
        rng = np.random.default_rng(8)
        white = qk.ljung_box(rng.standard_normal(1000), lags=10)
        self.assertGreater(white["lb_pvalue"][-1], 0.05)
        e = rng.standard_normal(1000)
        ar = np.zeros(1000)
        for i in range(1, 1000):
            ar[i] = 0.5 * ar[i - 1] + e[i]
        self.assertLess(qk.ljung_box(ar, lags=5)["lb_pvalue"][0], 1e-10)

    def test_ljung_box_formula(self):
        x = np.array([1.0, 3.0, 2.0, 5.0, 4.0, 6.0, 5.0, 8.0])
        n, xc = len(x), x - x.mean()
        rho1 = np.sum(xc[1:] * xc[:-1]) / np.sum(xc**2)
        self.assertAlmostEqual(qk.ljung_box(x, 1)["lb_stat"][0], n * (n + 2) * rho1**2 / (n - 1))


class TestEfficientAmerican(unittest.TestCase):
    """F26 L10: batch tree, premium-interpolation pricer, American IV."""

    def test_vectorized_matches_single_tree(self):
        cases = [(100, 100, .3, 1., .04, .01), (100, 110, .2, .5, .04, .01),
                 (90, 100, .4, 2., .04, 0.), (250, 260, .4, 1., .02, .015)]
        cols = [np.array(c) for c in zip(*cases)]
        for kind, single in (("put", qk.american_put), ("call", qk.american_call)):
            batch = qk.american_vectorized(*cols, kind=kind, n_steps=400)
            for (s, k, sig, t, r, q), b in zip(cases, batch):
                self.assertAlmostEqual(b, single(s, k, sig, t, r, q, n_steps=400), places=10)

    def test_homogeneity(self):
        # L10: V(S, K) = K V(S/K, 1)
        a = qk.american_vectorized(250, 260, .4, 1, .04, .015)
        b = 260 * qk.american_vectorized(250 / 260, 1, .4, 1, .04, .015)
        self.assertAlmostEqual(a, b, places=8)

    def test_fast_pricer_accuracy(self):
        r, q = .04, .015
        f = qk.make_american_pricer(r, q, n_steps=200)
        rng = np.random.default_rng(0)
        n = 300
        s, k = rng.uniform(180, 200, n), rng.uniform(180, 200, n)
        sig, t = rng.uniform(.21, .5, n), rng.uniform(.1, 1.5, n)
        fast = f(s, k, sig, t)
        slow = qk.american_vectorized(s, k, sig, t, r, q, n_steps=1000)
        self.assertLess(np.mean((fast - slow) ** 2), 1e-3)   # course: 3.2e-4
        self.assertLess(np.max(np.abs(fast - slow)), 0.25)
        self.assertTrue(np.isnan(f(100, 100, 2.0, 1.0)))     # off-grid -> NaN

    def test_american_iv_round_trip(self):
        f = qk.make_american_pricer(.02, 0., n_steps=200)
        k = np.linspace(230, 280, 50)
        iv = qk.implied_vol_bisect(f(250, k, .4, 1 / 3), 250, k, 1 / 3, f)
        np.testing.assert_allclose(iv, .4, atol=1e-7)


class TestHeston(unittest.TestCase):
    """F26 L12."""
    P = dict(v0=.04, kappa=2., theta=.06, xi=.6, rho=-.7)

    def test_black_scholes_limit(self):
        # Remark 2 in L12: xi -> 0 and v0 = theta gives Black-Scholes
        k = np.linspace(50, 140, 10)
        h = qk.heston_call(100, k, 1, .02, .09, 2, .09, 1e-6, 0., .01)
        np.testing.assert_allclose(h, qk.bs_call(100, k, .3, 1, .02, .01), atol=1e-4)

    def test_matches_original_heston_1993_formula(self):
        """Independent check: Heston's original P1/P2 two-integral formula."""
        from scipy.integrate import quad

        def heston93(S, K, t, r, v0, kap, th, xi, rho, q):
            def f(phi, j):
                u, b = (.5, kap - rho * xi) if j == 1 else (-.5, kap)
                e = b - rho * xi * phi * 1j
                d = np.sqrt(e ** 2 - xi ** 2 * (2 * u * phi * 1j - phi ** 2))
                g = (e + d) / (e - d)
                C = (r - q) * phi * 1j * t + kap * th / xi ** 2 * (
                    (e + d) * t - 2 * np.log((1 - g * np.exp(d * t)) / (1 - g)))
                D = (e + d) / xi ** 2 * (1 - np.exp(d * t)) / (1 - g * np.exp(d * t))
                return np.exp(C + D * v0 + 1j * phi * np.log(S))
            P = [.5 + quad(lambda ph: np.real(np.exp(-1j * ph * np.log(K)) * f(ph, j) / (1j * ph)),
                           1e-8, 200, limit=500)[0] / np.pi for j in (1, 2)]
            return S * np.exp(-q * t) * P[0] - K * np.exp(-r * t) * P[1]

        for args in [(100, 100, 1, .03, .04, 2, .06, .6, -.7, 0),
                     (100, 120, .5, .02, .09, 1.5, .05, .4, -.3, .01),
                     (200, 180, .25, .02, .25, 1, .1225, .9, -.1, .01)]:
            self.assertAlmostEqual(qk.heston_call(*args), heston93(*args), places=6)

    def test_parity_bounds_and_smile(self):
        S, r, q, t = 200., .02, .01, .5
        k = np.linspace(100, 275, 30)
        c = qk.heston_call(S, k, t, r, .25, 1, .35 ** 2, .9, -.1, q)
        p = qk.heston_put(S, k, t, r, .25, 1, .35 ** 2, .9, -.1, q)
        np.testing.assert_allclose(c - p, S * np.exp(-q * t) - k * np.exp(-r * t), atol=1e-10)
        self.assertTrue(np.all(np.diff(c) < 0))
        self.assertTrue(np.all(c >= np.maximum(S * np.exp(-q * t) - k * np.exp(-r * t), 0) - 1e-9))
        # negative rho -> implied vol decreases with strike (skew)
        iv = qk.bs_implied_vol(qk.heston_call(100, [80, 100, 120], 1, .02, **self.P), 100,
                               np.array([80, 100, 120]), 1, .02)
        self.assertTrue(iv[0] > iv[1] > iv[2])

    def test_monte_carlo_agrees_with_formula(self):
        rng = np.random.default_rng(1)
        S, v = qk.heston_paths(100, t=1, r=.03, n_steps=500, n_sims=100_000, rng=rng, **self.P)
        pay = np.exp(-.03) * np.maximum(S[:, -1] - 100, 0)
        se = pay.std() / np.sqrt(len(pay))
        self.assertLess(abs(pay.mean() - qk.heston_call(100, 100, 1, .03, **self.P)), 3 * se)
        # risk-neutral martingale: E[S_T] = S0 e^{rT}
        self.assertAlmostEqual(S[:, -1].mean() / (100 * np.exp(.03)), 1, delta=4e-3)
        # E[v_T] = theta + (v0 - theta) e^{-kappa T} (exact for this Euler scheme up to truncation)
        ev = self.P["theta"] + (self.P["v0"] - self.P["theta"]) * np.exp(-self.P["kappa"])
        self.assertAlmostEqual(v[:, -1].mean(), ev, delta=1e-3)

    def test_calibration_recovers_parameters(self):
        true = (.04, 2., .06, .6, -.7)
        k = np.tile(np.linspace(80, 120, 9), 3)
        t = np.repeat([.25, .5, 1.], 9)
        prices = qk.heston_call(100, k, t, .02, *true)
        for fit in ("price", "iv"):
            res = qk.heston_calibrate(100, k, t, prices, .02, fit=fit, x0=(.09, 1., .09, .3, -.3))
            fitted = qk.heston_call(100, k, t, .02, *res.x)
            self.assertLess(np.max(np.abs(fitted - prices)), 1e-3, fit)
            self.assertAlmostEqual(res.x[0], true[0], delta=2e-3)   # v0 is well identified


class TestNewNotebookBugs(unittest.TestCase):
    """Fall 2026 L10: bs_euro_put_delta returned +e^{-qt} Phi(-d1)."""

    def test_put_delta_negative_with_dividends(self):
        self.assertLess(qk.bs_put_delta(100, 100, .3, 1, .04, .01), 0)


if __name__ == "__main__":
    unittest.main()
