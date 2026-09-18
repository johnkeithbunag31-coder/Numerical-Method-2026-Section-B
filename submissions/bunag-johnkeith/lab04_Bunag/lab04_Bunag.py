# ============================================================
# Civil Engineering Series Approximation
# HOW ACCURATE IS GOOD ENOUGH?
# Full integrated script: Parts 1 through 7
# ============================================================

import math
import matplotlib.pyplot as plt


# ============================================================
# PART 1: GEOMETRIC SERIES
# ============================================================

def geometric_sum(x, N):
    """S_N = 1 + x + x^2 + ... + x^N  (loop-based, no closed form)."""
    total = 0.0
    for k in range(N + 1):
        total += x ** k
    return total


# ============================================================
# PART 2: POWER SERIES
# ============================================================

def power_series(x, coefficients):
    """P_N(x) = a_0 + a_1*x + a_2*x^2 + ... + a_N*x^N."""
    result = 0.0
    for k, a_k in enumerate(coefficients):
        result += a_k * (x ** k)
    return result


# ============================================================
# PART 3: MACLAURIN SERIES FOR sin(theta)
# ============================================================

def sin_maclaurin(theta, N):
    """N-term Maclaurin approximation of sin(theta)."""
    result = 0.0
    for n in range(N):
        result += ((-1) ** n) * (theta ** (2 * n + 1)) / math.factorial(2 * n + 1)
    return result


# ============================================================
# PART 5: TAYLOR SERIES CENTERED AT a
# ============================================================

def sin_taylor(theta, a, N):
    """N-term Taylor approximation of sin(theta) centered at a."""
    result = 0.0
    sin_a = math.sin(a)
    cos_a = math.cos(a)
    for n in range(N):
        pattern = n % 4
        if pattern == 0:
            f_deriv = sin_a
        elif pattern == 1:
            f_deriv = cos_a
        elif pattern == 2:
            f_deriv = -sin_a
        else:
            f_deriv = -cos_a
        result += f_deriv * ((theta - a) ** n) / math.factorial(n)
    return result


# ============================================================
# CONSTANTS
# ============================================================

L = 20.0
angles_deg = [1, 2, 5, 10, 15, 20, 30]
term_counts = [1, 2, 3, 4]
a_rad = math.radians(10)


# ============================================================
# PART 1 OUTPUT: GEOMETRIC SERIES INVESTIGATION
# ============================================================

print("=" * 78)
print("PART 1: GEOMETRIC SERIES  S_N = 1 + x + x^2 + ... + x^N")
print("=" * 78)

print("\nSingle check: x = 0.5, N = 10")
approx = geometric_sum(0.5, 10)
exact = 1 / (1 - 0.5)
print(f"  Approximation:   {approx}")
print(f"  Exact (1/(1-x)): {exact}")
print(f"  Absolute error:  {abs(approx - exact):.3e}")
print(f"  Percent error:   {abs(approx - exact) / exact * 100:.6f}%")

for x in [0.5, 0.8, 0.9]:
    exact = 1 / (1 - x)
    print(f"\n--- x = {x}  (exact = {exact:.6f}) ---")
    print(f"{'N':>4} {'S_N':>15} {'Abs Error':>15} {'% Error':>12}")
    for N in [1, 2, 5, 10, 20, 50]:
        a = geometric_sum(x, N)
        ae = abs(a - exact)
        pe = ae / exact * 100
        print(f"{N:>4} {a:>15.8f} {ae:>15.2e} {pe:>12.6f}")


# ============================================================
# PART 2 OUTPUT: POWER SERIES VALIDATION
# ============================================================

print("\n" + "=" * 78)
print("PART 2: POWER SERIES  P_N(x) = a_0 + a_1*x + ... + a_N*x^N")
print("=" * 78)

ps = power_series(0.5, [1, 1, 1, 1, 1])
gs = geometric_sum(0.5, 4)
print("\nSanity check (coeffs = [1,1,1,1,1] at x = 0.5):")
print(f"  Power series:     {ps}")
print(f"  Geometric series: {gs}")
print(f"  Match? {abs(ps - gs) < 1e-12}")

print("\nArbitrary polynomial: 3 - 2x + 0.5x^2 + 0x^3 + 1x^4 at x = 2.0")
print(f"  P(2.0) = {power_series(2.0, [3, -2, 0.5, 0, 1])}")


# ============================================================
# PART 3 OUTPUT: MACLAURIN AT 10 DEGREES
# ============================================================

print("\n" + "=" * 78)
print("PART 3: MACLAURIN APPROXIMATION OF sin(theta)")
print("=" * 78)

theta = math.radians(10)
exact = math.sin(theta)
print(f"\ntheta = 10 deg = {theta:.6f} rad")
print(f"Exact sin(10 deg) = {exact:.10f}")
print(f"{'N':>4} {'Approx':>15} {'Abs Error':>15} {'% Error':>12}")
for N in term_counts:
    a = sin_maclaurin(theta, N)
    ae = abs(a - exact)
    pe = ae / abs(exact) * 100
    print(f"{N:>4} {a:>15.10f} {ae:>15.3e} {pe:>12.6f}")


# ============================================================
# PART 4 OUTPUT: ENGINEERING INVESTIGATION (Maclaurin tables)
# ============================================================

print("\n" + "=" * 78)
print("PART 4: ENGINEERING INVESTIGATION  y = L * sin(theta), L = 20 m")
print("=" * 78)

for N in term_counts:
    print(f"\n--- N = {N} term(s), MACLAURIN ---")
    print(f"{'Angle':>7} {'Exact y':>15} {'Approx y':>15} "
          f"{'Abs Error':>15} {'% Error':>12}")
    for deg in angles_deg:
        theta = math.radians(deg)
        exact_y = L * math.sin(theta)
        approx_y = L * sin_maclaurin(theta, N)
        ae = abs(approx_y - exact_y)
        pe = ae / abs(exact_y) * 100
        print(f"{deg:>6}d {exact_y:>15.10f} {approx_y:>15.10f} "
              f"{ae:>15.3e} {pe:>12.6f}")


# ============================================================
# PART 5 OUTPUT: TAYLOR TABLES CENTERED AT a = 10 DEG
# ============================================================

print("\n" + "=" * 78)
print("PART 5: TAYLOR TABLES CENTERED AT a = 10 deg")
print("=" * 78)

for N in term_counts:
    print(f"\n--- N = {N} term(s), TAYLOR(a=10 deg) ---")
    print(f"{'Angle':>7} {'Exact y':>15} {'Approx y':>15} "
          f"{'Abs Error':>15} {'% Error':>12}")
    for deg in angles_deg:
        theta = math.radians(deg)
        exact_y = L * math.sin(theta)
        approx_y = L * sin_taylor(theta, a_rad, N)
        ae = abs(approx_y - exact_y)
        pe = ae / abs(exact_y) * 100
        print(f"{deg:>6}d {exact_y:>15.10f} {approx_y:>15.10f} "
              f"{ae:>15.3e} {pe:>12.6f}")


# ============================================================
# PART 6 OUTPUT: MACLAURIN vs TAYLOR COMPARISON
# ============================================================

print("\n" + "=" * 78)
print("PART 6: MACLAURIN (a=0) vs TAYLOR (a=10 deg) - % ERROR COMPARISON")
print("=" * 78)

for N in term_counts:
    print(f"\n--- N = {N} term(s) ---")
    print(f"{'Angle':>7} {'Maclaurin %Err':>18} {'Taylor %Err':>15} {'Winner':>12}")
    for deg in angles_deg:
        theta = math.radians(deg)
        exact_y = L * math.sin(theta)
        m = L * sin_maclaurin(theta, N)
        t = L * sin_taylor(theta, a_rad, N)
        mp = abs(m - exact_y) / abs(exact_y) * 100
        tp = abs(t - exact_y) / abs(exact_y) * 100
        winner = "Maclaurin" if mp < tp else ("Taylor" if tp < mp else "tie")
        print(f"{deg:>6}d {mp:>18.6e} {tp:>15.6e} {winner:>12}")


# ============================================================
# PART 7: PLOTS
# ============================================================

# ---- Deliverable 2: Convergence plot ----
fig, ax = plt.subplots(figsize=(9, 5))
for deg in [1, 5, 10, 20, 30]:
    theta = math.radians(deg)
    exact_y = L * math.sin(theta)
    errs = [abs(L * sin_maclaurin(theta, N) - exact_y) / abs(exact_y) * 100
            for N in range(1, 7)]
    ax.semilogy(range(1, 7), errs, marker='o', label=f'{deg} deg')
ax.axhline(0.1, color='red', linestyle='--', label='0.1% target')
ax.set_xlabel('Number of Maclaurin terms (N)')
ax.set_ylabel('% Error (log scale)')
ax.set_title('Convergence: % Error vs Number of Terms')
ax.legend()
ax.grid(True, which='both', alpha=0.3)
plt.tight_layout()
plt.savefig('plot2_convergence.png', dpi=150, bbox_inches='tight')
plt.show()


# ---- Deliverable 3: Function comparison plot ----
degs = list(range(0, 61))
ths = [math.radians(d) for d in degs]

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(degs, [L * math.sin(t) for t in ths], 'k-', lw=2, label='Exact')
ax.plot(degs, [L * sin_maclaurin(t, 1) for t in ths], '--', label='Maclaurin N=1')
ax.plot(degs, [L * sin_maclaurin(t, 2) for t in ths], '--', label='Maclaurin N=2')
ax.plot(degs, [L * sin_maclaurin(t, 4) for t in ths], '--', label='Maclaurin N=4')
ax.plot(degs, [L * sin_taylor(t, a_rad, 2) for t in ths], ':', label='Taylor(a=10) N=2')
ax.plot(degs, [L * sin_taylor(t, a_rad, 4) for t in ths], ':', label='Taylor(a=10) N=4')
ax.set_xlabel('Angle (degrees)')
ax.set_ylabel('y = L * sin(theta)  [m]')
ax.set_title('Function Comparison: y = 20 * sin(theta)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plot3_function_comparison.png', dpi=150, bbox_inches='tight')
plt.show()


# ---- Deliverable 4: Error comparison plot (absolute + percentage) ----
N_test = 3
mac_abs, tay_abs, mac_pct, tay_pct = [], [], [], []
for deg in angles_deg:
    theta = math.radians(deg)
    exact_y = L * math.sin(theta)
    m = L * sin_maclaurin(theta, N_test)
    t = L * sin_taylor(theta, a_rad, N_test)
    mac_abs.append(abs(m - exact_y))
    tay_abs.append(abs(t - exact_y))
    mac_pct.append(abs(m - exact_y) / abs(exact_y) * 100)
    tay_pct.append(abs(t - exact_y) / abs(exact_y) * 100)

x = list(range(len(angles_deg)))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

ax1.bar([i - width/2 for i in x], mac_abs, width, label='Maclaurin (a=0)')
ax1.bar([i + width/2 for i in x], tay_abs, width, label='Taylor (a=10)')
ax1.set_xticks(x)
ax1.set_xticklabels([f'{d} deg' for d in angles_deg])
ax1.set_yscale('log')
ax1.set_xlabel('Angle')
ax1.set_ylabel('Absolute Error  [m]  (log scale)')
ax1.set_title(f'Absolute Error at N={N_test}')
ax1.legend()
ax1.grid(True, which='both', axis='y', alpha=0.3)

ax2.bar([i - width/2 for i in x], mac_pct, width, label='Maclaurin (a=0)')
ax2.bar([i + width/2 for i in x], tay_pct, width, label='Taylor (a=10)')
ax2.axhline(0.1, color='red', linestyle='--', label='0.1% target')
ax2.set_xticks(x)
ax2.set_xticklabels([f'{d} deg' for d in angles_deg])
ax2.set_yscale('log')
ax2.set_xlabel('Angle')
ax2.set_ylabel('% Error  (log scale)')
ax2.set_title(f'Percentage Error at N={N_test}')
ax2.legend()
ax2.grid(True, which='both', axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('plot4_error_comparison.png', dpi=150, bbox_inches='tight')
plt.show()


# ============================================================
# WRITTEN ANSWERS: PARTS 1, 3, 4, 5, 6, 7
# ============================================================

print("\n" + "=" * 78)
print("WRITTEN ANSWERS")
print("=" * 78)


# ---------------- PART 1 ANSWER ----------------
print("""
PART 1 INVESTIGATION - GEOMETRIC SERIES
--------------------------------------------------------------------
Q: Compare partial sums with the exact value for x = 0.5, 0.8, 0.9.
   How does the number of terms affect accuracy?  Why does
   convergence speed differ?

HOW THE NUMBER OF TERMS AFFECTS ACCURACY:
  For every x, adding more terms strictly improves the approximation.
  But the rate of improvement is dramatically different depending
  on x.

    x = 0.5: Already 0.049% error at N = 10 (below the 0.1% target).
             At N = 20 error is 4.8e-5 %; at N = 50 it hits
             floating-point precision (~1e-16).
    x = 0.8: Much slower.  At N = 10 the error is still 8.59%.
             You need roughly N = 50 to get to 0.0011%.
    x = 0.9: Extremely slow.  Even at N = 50 the error is 0.46% -
             still 4x above the 0.1% target.  Reaching 0.1% with
             x = 0.9 would require on the order of N = 200 terms.

WHY CONVERGENCE SPEED DIFFERS:
  The truncation error of the geometric partial sum is
        Error = x^(N+1) / (1 - x).
  Two effects combine as x approaches 1:

    (1) The numerator x^(N+1) shrinks more slowly.  At x = 0.5,
        each extra term multiplies the remaining tail by 0.5; the
        tail collapses quickly.  At x = 0.9, each extra term only
        multiplies by 0.9 - slow shrinkage.

    (2) The denominator (1 - x) grows.  The exact target 1/(1-x)
        is 2 for x=0.5, 5 for x=0.8, and 10 for x=0.9.  A larger
        target means the same absolute error becomes a smaller
        percentage - but this benefit is far outweighed by (1).

ENGINEERING IMPLICATION:
  Geometric-series convergence is very sensitive to how close x is
  to the edge of the interval of convergence.  Near the center
  (x small), a handful of terms is enough.  Near the boundary
  (x -> 1), even hundreds of terms may not meet a tight tolerance.
  The same sensitivity will reappear with sin(theta): the further
  theta is from the expansion point, the more terms are needed -
  or the more we need to move the expansion point.
""")


# ---------------- PART 2 NOTE ----------------
print("""
PART 2 - POWER SERIES
--------------------------------------------------------------------
No investigation question is posed for this part.  The function
power_series(x, coefficients) provides the general machinery for
evaluating any finite power series and is reused implicitly by the
Maclaurin and Taylor implementations.  Validation: passing five
1's as coefficients at x = 0.5 reproduces geometric_sum(0.5, 4)
exactly (1.9375), and the arbitrary polynomial
3 - 2x + 0.5x^2 + 0x^3 + 1x^4 evaluated at x = 2 gives 17.0 -
both confirmed in the output above.
""")


# ---------------- PART 3 ANSWER ----------------
print("""
PART 3 INVESTIGATION - MACLAURIN AT 10 DEG
--------------------------------------------------------------------
Q: For theta = 10 deg, calculate approximations using 1, 2, 3, and
   4 terms.  Compare each to the exact value.  What is the error
   at each step?

Exact sin(10 deg) = 0.1736481777

   TERMS        APPROX          ABS ERROR       % ERROR
     1      0.1745329252      8.847e-04      0.509506 %
     2      0.1736468290      1.349e-06      0.000777 %
     3      0.1736481786      9.784e-10      0.000001 %
     4      0.1736481777      4.140e-13      0.000000 %

ERROR AT EACH STEP:
  N = 1 (theta alone): 0.5095% - the familiar small-angle
       approximation sin(theta) ~= theta.  Not accurate enough for
       a 0.1% engineering target.
  N = 2 (adds -theta^3/3!): 0.000777% - error drops by a factor of
       about 650.  Already >100x better than the 0.1% target.
  N = 3 (adds +theta^5/5!): 0.0000006% - another factor of ~1400.
       Far beyond any realistic engineering precision.
  N = 4 (adds -theta^7/7!): ~4e-13 absolute - floating-point
       rounding level.  Further terms are pointless.

KEY OBSERVATIONS:
  1. Each extra term reduces the error by roughly 2-3 orders of
     magnitude.  This is the signature of very fast convergence,
     driven by the factorial denominators 3!, 5!, 7!.
  2. The improvement is dramatic, not linear.  1 -> 2 terms takes
     the error from 0.5% to under 0.001%; 3 terms is overkill.
  3. Engineering sweet spot for theta = 10 deg is N = 2.
  4. The sign of the error alternates: N=1 overestimates, N=2
     underestimates slightly, N=3 overestimates again.  This is
     the alternating-series behaviour of the Maclaurin expansion
     of sin.

ENGINEERING IMPLICATION:
  For small angles - the regime where civil and structural
  engineering typically operates - a two-term Maclaurin series
  meets a 0.1% accuracy requirement with margin to spare.  The
  one-term approximation sin(theta) ~= theta is only adequate
  for very small angles (roughly under 3-4 deg).
""")


# ---------------- PART 4 ANSWER ----------------
print("""
PART 4 ANALYSIS - ENGINEERING INVESTIGATION
--------------------------------------------------------------------
Q1. How does the error change as the angle increases?
    The error grows monotonically - and faster than linearly - as
    theta increases, for every fixed N.  At N = 2, for example:
        1 deg  ->  ~0 %
        2 deg  ->  ~0 %
        5 deg  ->  0.0003 %
        10 deg ->  0.00078 %
        15 deg ->  0.0039 %
        20 deg ->  0.0124 %
        30 deg ->  0.063 %
    At N = 1 (small-angle approx sin(theta) ~= theta), the error is
    dramatic: 0.005% at 1 deg, 0.127% at 5 deg, 0.510% at 10 deg,
    4.65% at 30 deg.  Reason: the leading error term is the first
    omitted term.  For N = 1 that is theta^3/3! - a cubic, so the
    error scales like theta^3.  Tripling theta from 10 to 30 deg
    multiplies the error by ~27, consistent with (30/10)^3 = 27.

Q2. How does the error change as you add more terms?
    Every additional term reduces the error by orders of magnitude.
    At theta = 30 deg:
        N = 1 ->  4.65 %
        N = 2 ->  0.063 %       (factor ~74 improvement)
        N = 3 ->  0.00043 %     (factor ~146 improvement)
        N = 4 ->  0.000002 %    (factor ~215 improvement)
    The improvement factors grow with N because the factorial
    denominators (1/3!, 1/5!, 1/7!) shrink faster than the powers
    of theta grow.  The approximation oscillates around the true
    value - N = 1 overestimates, N = 2 underestimates, N = 3
    overestimates - consistent with the alternating-series
    behaviour.

Q3. For small angles (< 5 deg), how many terms are sufficient?
    For the 0.1 % target:
        1 deg: N = 1 already passes (0.0051 %)
        2 deg: N = 1 already passes (0.0203 %)
        3 deg: N = 1 borderline (~0.07 %)
        5 deg: N = 1 FAILS (0.127 %); N = 2 passes at 0.0003 %
    So for a uniform answer covering everything up to 5 deg, use
    N = 2.  For angles strictly below ~3 deg, N = 1 (the classic
    small-angle approximation) is adequate.

Q4. For larger angles (> 20 deg), how many terms are needed?
    20 deg: N = 1 fails (2.05 %).  N = 2 passes at 0.0124 %.
    30 deg: N = 1 fails (4.65 %).  N = 2 passes at 0.063 %.
    So N = 2 covers all angles up to 30 deg with margin.  For a
    wider envelope, N = 3 is safe up to at least 60 deg.

SUMMARY TABLE (minimum N for 0.1 % over the angle range):
    0 -  3 deg  ->  N = 1
    0 - 30 deg  ->  N = 2
    0 - 60 deg  ->  N = 3
    0 - 90 deg  ->  N = 4

The single most important takeaway: two terms of the Maclaurin
series meet the 0.1 % target across the entire angle range tested.
""")


# ---------------- PART 5 ANSWER ----------------
print("""
PART 5 COMPARISON - MACLAURIN (a=0) vs TAYLOR (a=10 deg)
--------------------------------------------------------------------
Q: Which performs better near 10 deg?  Which is better far from 10 deg?

AT THE EXPANSION POINT (theta = 10 deg):
  Taylor is EXACT at its center for any N >= 1 (error = 0).
  Maclaurin is tiny but nonzero there (2.4e-10 % at N = 4).  So
  exactly at 10 deg, Taylor wins - trivially, by construction.

NEAR 10 deg (say 5 deg or 15 deg):
  Surprisingly, Maclaurin still wins numerically.
     At 15 deg (5 deg from Taylor's center, 15 deg from
     Maclaurin's center):
        Maclaurin N = 4: 6.15e-09 %
        Taylor   N = 4: 1.78e-04 %   ->  Maclaurin wins by ~29,000x
     At 5 deg:
        Maclaurin N = 4: 9.17e-13 %
        Taylor   N = 4: 4.34e-04 %   ->  Maclaurin wins by ~4.7e8 x
  Only EXACTLY at 10 deg does Taylor win.  A few degrees away,
  Maclaurin is already better.

FAR FROM 10 deg (1 deg or 30 deg):
  Maclaurin wins decisively.
     At 1 deg:  Maclaurin 1.59e-14 %;  Taylor 2.07e-02 %.
                Factor ~1e12 difference.
     At 30 deg: Maclaurin 1.63e-06 %;  Taylor 2.99e-02 %.
                Factor ~18,000 difference.

WHY DOES MACLAURIN WIN EVEN NEAR 10 deg?
  The standard guideline "center the Taylor series near the angle
  of interest" is a general rule of thumb, but it depends on the
  function's coefficient structure.  For sin, the Maclaurin
  coefficients are
        1, -1/3!, +1/5!, -1/7!, ...
      = 1, -0.1667, +0.0083, -0.0002, ...
  and shrink extremely fast because of the factorials.  Two terms
  already give 0.001 % at 10 deg; three terms give 1e-7 %.
  The Taylor-at-10 coefficients, by contrast, are built from
  sin(10 deg) ~= 0.174 and cos(10 deg) ~= 0.985, which decay far
  more slowly.  The (theta - 10)^n factor being small near 10 deg
  doesn't compensate for the slower coefficient decay.

ENGINEERING TAKEAWAY:
  The Maclaurin series for sin is exceptionally well-behaved -
  adding an off-center expansion actually HURTS accuracy over
  most of the range.  This does NOT mean the guideline is wrong
  in general (for functions with poles or slowly-decaying
  coefficients, centering near the angle of interest usually does
  dominate).  It means you must VERIFY numerically rather than
  trust the heuristic - which this activity demonstrated.
""")


# ---------------- PART 6 ANSWER ----------------
print("""
PART 6 ANALYSIS - CONCEPTUAL DISCUSSION QUESTIONS
--------------------------------------------------------------------
Q1. Does adding more terms always improve the approximation?
    Not always - but for the functions in this activity, yes.
    Adding a term improves the approximation only inside the
    interval of convergence.  Outside it (e.g. geometric series
    with |x| >= 1), adding terms makes the sum diverge.  Even
    inside the interval, some series approach the limit in
    alternation, so the error may temporarily increase before
    decreasing - but on average and in the limit, adding terms
    always brings you closer to the truth.  For our specific
    functions (geometric with |x| < 1, Maclaurin/Taylor of sin),
    adding terms strictly reduces the error, by orders of
    magnitude per term.  The reason is that both are analytic with
    infinite radius of convergence and rapidly-decaying
    coefficients.

Q2. Why is the Maclaurin approximation most accurate near zero?
    Because the Maclaurin series is CONSTRUCTED to be exact at
    zero.  The N-term Maclaurin approximation matches the value,
    first derivative, second derivative, ..., and N-th derivative
    of f exactly at theta = 0.  Any error therefore comes from the
    omitted terms, and each omitted term carries a factor of
    theta^(N+1).  When theta is small, theta^(N+1) is extremely
    small, so the error is tiny.  As theta grows, theta^(N+1)
    grows - so the same N gives worse accuracy farther from zero.

Q3. Why can changing the Taylor expansion point improve accuracy?
    Because the Taylor series is exact at its expansion point, and
    the local accuracy follows the expansion point around.  If
    your application operates around theta = 10 deg, expanding at
    10 deg guarantees that the value and the first N derivatives
    match at 10 deg; the leading error term is proportional to
    (theta - 10)^(N+1), which is tiny when theta is near 10 deg.
    HOWEVER - the word "can" matters.  In this activity we found
    that Maclaurin actually beats Taylor-at-10 at almost every
    angle, including near 10 deg, because "center near interest"
    is only one of the factors determining accuracy; the other is
    the coefficient-decay rate, and for sin the Maclaurin
    coefficients decay much faster.

Q4. How does the distance from the expansion point affect accuracy?
    For fixed N, error grows as distance |theta - a| grows -
    roughly proportional to |theta - a|^(N+1).  Example with
    Taylor centered at 10 deg, N = 4:
        theta = 10 deg (distance 0):   error = 0
        theta = 15 deg (distance 5):   error = 1.78e-04 %
        theta = 20 deg (distance 10):  error = 2.35e-03 %
        theta = 30 deg (distance 20):  error = 2.99e-02 %
    Error clearly grows with distance.  But the actual magnitudes
    depend on the coefficient structure of the series - for
    Maclaurin, the coefficients decay so fast that even at 30 deg
    the error stays below 1e-6 %.  Distance from center is one
    factor; coefficient structure is another; for sin the second
    factor dominates.

Q5. What is the critical angle for the sin(theta) ~= theta approx?
    The critical angle is where the one-term approximation stops
    meeting the required tolerance.  For a 0.1 % target, the
    critical angle is approximately 4.4 degrees.

    Theoretical estimate:  relative error ~= |theta^3/3!| / |theta|
                                       = theta^2 / 6
    Setting theta^2 / 6 = 0.001 gives
        theta = sqrt(0.006) = 0.0775 rad ~= 4.44 deg.

    Numerical check (our tables):
        theta = 2 deg:  0.0203 %  (passes 0.1 %)
        theta = 5 deg:  0.127 %   (fails 0.1 %)
        crossover between 3 and 5 deg, close to 4.4 deg.

    For different tolerances:
        1 %    tolerance  ->  critical angle ~ 14 deg
        0.01 % tolerance  ->  critical angle ~ 1.4 deg
    So "the critical angle" depends on the required tolerance.  For
    a 0.1 % engineering specification, it is approximately 4.4 deg.
""")


# ---------------- PART 7 ANSWER ----------------
print("""
PART 7 - FINAL ENGINEERING RECOMMENDATION
--------------------------------------------------------------------
DECISION PROBLEM:
  Compute y = 20 * sin(theta) for theta in [1, 30] deg with less
  than 0.1 % error.  Choose between Maclaurin series, Taylor
  series centered closer to the angle of interest, or the exact
  sine function.

RECOMMENDATION:
  Use the MACLAURIN SERIES with N = 2 terms:

        y = 20 * sin(theta)  ~=  20 * (theta - theta^3 / 6)
        (theta in radians)

1. NUMBER OF TERMS REQUIRED
   Two terms.  y ~= 20(theta - theta^3/6) meets the 0.1 % tolerance
   across the entire 1 - 30 deg test range.  A third term gives a
   large safety margin; a fourth is unnecessary for this range.

2. PERCENTAGE ERROR ACHIEVED
   Worst case is at 30 deg:
        theta =  1 deg :  ~0 %
        theta =  2 deg :  ~0 %
        theta =  5 deg :  0.0003 %
        theta = 10 deg :  0.00078 %
        theta = 15 deg :  0.0039 %
        theta = 20 deg :  0.0124 %
        theta = 30 deg :  0.063 %    <- worst case
   0.063 % at 30 deg is ~1.6x below the 0.1 % target.  At the
   smallest angles the N = 2 result is machine-precision exact.

3. CONVERGENCE BEHAVIOUR
   The Maclaurin series for sin converges exceptionally fast.
   Each added term reduces the error by 2 - 3 orders of magnitude,
   because the coefficients 1, -1/3!, 1/5!, -1/7!, ... shrink
   factorially.  On a log-scale convergence plot the error falls
   on nearly straight lines - the signature of exponential
   convergence.  This is why N = 2 does so much work: the second
   term alone drops the error by ~650x at 10 deg.

4. COMPUTATIONAL SIMPLICITY vs ACCURACY TRADEOFF
   The N = 2 Maclaurin approximation requires:
        - one multiplication (theta^2 or theta^3)
        - one division by 6
        - one subtraction
   three arithmetic operations total.

   METHOD              COST            % ERR AT 30 deg
   Maclaurin N = 2     3 ops           0.063 %   PASS
   Maclaurin N = 3     5 ops           0.00043 % PASS
   Taylor(a=10) N = 4  ~8 ops + sin/cos 0.030 %  PASS
   math.sin            library call    exact

   For a one-off calculation, math.sin is simplest.  In an
   embedded / real-time context (surveying instrument, slope
   monitor, data logger performing thousands of evaluations per
   second) the N = 2 polynomial is measurably cheaper and
   numerically indistinguishable at the required tolerance.

5. VALID ANGLE RANGE
   N = 2 meets 0.1 % for theta up to 30 deg (the largest angle
   tested).  If the design envelope is expanded:
        0 -  3 deg  ->  N = 1
        0 - 30 deg  ->  N = 2   <-- recommended
        0 - 60 deg  ->  N = 3
        0 - 90 deg  ->  N = 4

WHY NOT TAYLOR CENTERED NEAR 10 DEG?
  Counterintuitive result:  at the same N, Maclaurin beats
  Taylor-at-10 at 6 of the 7 angles tested - including at 15 deg,
  which is closer to Taylor's center (10 deg) than to Maclaurin's
  (0 deg).
        theta   Maclaurin N=4    Taylor N=4     Winner
         1 deg   1.6e-14 %       2.1e-02 %      Maclaurin
         5 deg   9.2e-13 %       4.3e-04 %      Maclaurin
        10 deg   2.4e-10 %       0 %            Taylor (center)
        15 deg   6.2e-09 %       1.8e-04 %      Maclaurin
        20 deg   6.2e-08 %       2.4e-03 %      Maclaurin
        30 deg   1.6e-06 %       3.0e-02 %      Maclaurin
  At 30 deg, Maclaurin is ~18,000x more accurate.  The reason:
  Maclaurin coefficients decay factorially fast; Taylor-at-10
  coefficients (built from sin 10 ~= 0.174, cos 10 ~= 0.985)
  decay much more slowly.  The "center near interest" guideline
  is valid in general but not absolute, and for sin specifically
  it is dominated by the coefficient-decay advantage.

WHY NOT THE EXACT SINE FUNCTION?
  For a single calculation, math.sin is correct and risk-free.
  In a high-throughput or embedded context, math.sin is a
  relatively expensive library call.  The N = 2 Maclaurin
  polynomial is three arithmetic operations and, at this
  tolerance, produces results indistinguishable from exact.
  Engineering decision:  use N = 2 Maclaurin in production;
  reserve math.sin for validation and testing.

SUMMARY TABLE
        Method                Maclaurin series
        Terms                 N = 2
        Formula               y ~= 20(theta - theta^3/6)
        Worst-case % error    0.063 % (at 30 deg)
        Target                < 0.1 %   PASS
        Valid angle range     1 - 30 deg
        Safety margin         ~1.6x at worst case
        Extension to 60 deg   use N = 3

FINAL RECOMMENDATION:
  For y = 20 * sin(theta) with theta in [1, 30] deg and a 0.1 %
  error tolerance, use the two-term Maclaurin approximation.
  It is the simplest, cheapest, and most accurate option in this
  range - outperforming Taylor-at-10 despite the latter's
  theoretically favorable expansion point, and approaching
  math.sin in accuracy at a fraction of the computational cost.
""")


# ============================================================
# END
# ============================================================

print("=" * 78)
print("All deliverables generated.  Plots saved as PNG files.")
print("=" * 78)