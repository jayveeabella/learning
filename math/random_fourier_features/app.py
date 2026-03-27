"""
Random Fourier Features — Interactive Streamlit Explainer
Rahimi & Recht, NeurIPS 2007
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Random Fourier Features",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color palette ─────────────────────────────────────────────────────────────
TRUE_C = "#e63946"   # red    – exact / ground truth
RFF_C  = "#457b9d"   # blue   – RFF approximation
SPEC_C = "#2a9d8f"   # teal   – spectral density

# ── Sidebar ───────────────────────────────────────────────────────────────────
SECTIONS = [
    "Executive Summary",
    "Kernel Methods",
    "Scalability Problem",
    "Bochner's Theorem",
    "The RFF Algorithm",
    "Interactive Visualizations",
    "RBF & Spectral Duality",
    "Error Guarantees",
    "Extensions & History",
    "Sources",
]

with st.sidebar:
    st.markdown("## 🌊 RFF Explorer")
    st.markdown("*Random Fourier Features*")
    st.divider()
    section = st.radio("", SECTIONS, label_visibility="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Executive Summary
# ─────────────────────────────────────────────────────────────────────────────
if section == "Executive Summary":
    st.title("Random Fourier Features")
    st.markdown("### Scaling Kernel Machines to Millions of Points")
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        **The problem:** Kernel methods — SVMs, Gaussian Processes, Kernel PCA —
        are powerful nonlinear models that implicitly compute inner products in
        infinite-dimensional feature spaces. But they require an $n \\times n$ kernel
        matrix, costing **$O(n^3)$** to train. At $n = 10^5$ this is infeasible.

        **The solution (Rahimi & Recht, 2007):** For any *shift-invariant* kernel,
        construct a random $D$-dimensional feature map $z: \\mathbb{R}^d \\to \\mathbb{R}^D$
        so that the dot product approximates the kernel:
        """)
        st.latex(r"""
        k(\mathbf{x}, \mathbf{y})
        \;\approx\;
        z(\mathbf{x})^\top z(\mathbf{y}),
        \qquad
        z(\mathbf{x}) = \frac{1}{\sqrt{D}}
        \begin{bmatrix}
        \sqrt{2}\cos(\boldsymbol{\omega}_1^\top \mathbf{x} + b_1)\\
        \vdots\\
        \sqrt{2}\cos(\boldsymbol{\omega}_D^\top \mathbf{x} + b_D)
        \end{bmatrix}
        """)
        st.markdown("""
        Training a linear model on these features approximates the corresponding kernel
        machine — reducing cost to **$O(nD)$**, linear in $n$ when $D \\ll n$.
        """)
        st.info("**Award:** NeurIPS 2017 Test of Time Award")

        st.markdown("#### The Central Identity")
        st.latex(r"""
        k(\mathbf{x} - \mathbf{y})
        = \underbrace{
            \mathbb{E}_{\boldsymbol{\omega} \sim p(\boldsymbol{\omega})}
            \!\left[\cos(\boldsymbol{\omega}^\top(\mathbf{x}-\mathbf{y}))\right]
          }_{\text{Bochner's theorem (1932)}}
        \;\approx\;
        \underbrace{z(\mathbf{x})^\top z(\mathbf{y})}_{\text{D-sample Monte Carlo}}
        """)

    with col2:
        st.markdown("#### Complexity at $n = 10^5$, $D = 10^3$")
        df_cplx = pd.DataFrame({
            "Method": ["Exact Kernel", "Nyström (m=10³)", "RFF (D=10³)"],
            "Training": ["O(n³) ~ 10¹⁵", "O(nm²) ~ 10¹¹", "O(nD) ~ 10⁸"],
            "Memory": ["O(n²) ~ 10¹⁰", "O(nm) ~ 10⁸",  "O(nD) ~ 10⁸"],
            "Feasible?": ["❌", "⚠️", "✅"],
        })
        st.table(df_cplx)

        # Quick scaling chart
        fig0, ax0 = plt.subplots(figsize=(4.5, 3))
        ns = np.logspace(2, 6, 100)
        ax0.loglog(ns, ns**3,        color=TRUE_C, lw=2.5, label="Exact O(n³)")
        ax0.loglog(ns, ns * 1000,    color=RFF_C,  lw=2.5, label="RFF O(nD), D=1k")
        ax0.axvline(1e5, color="gray", ls="--", alpha=0.5, label="n=100k")
        ax0.set_xlabel("n")
        ax0.set_ylabel("Operations")
        ax0.set_title("Compute scaling")
        ax0.legend(fontsize=8)
        ax0.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig0)
        plt.close(fig0)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Kernel Methods
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Kernel Methods":
    st.title("🔑 Kernel Methods: A Refresher")
    st.divider()

    tab_def, tab_trick, tab_kernels, tab_viz = st.tabs([
        "Definition", "Kernel Trick", "Common Kernels", "Visualization"
    ])

    with tab_def:
        st.markdown("### What is a kernel?")
        st.markdown("""
        A **kernel function** $k : \\mathcal{X} \\times \\mathcal{X} \\to \\mathbb{R}$
        measures similarity between two data points. The fundamental property:
        """)
        st.latex(r"k(\mathbf{x}, \mathbf{x}') = \langle \phi(\mathbf{x}), \phi(\mathbf{x}') \rangle_{\mathcal{H}}")
        st.markdown("""
        where $\\phi: \\mathcal{X} \\to \\mathcal{H}$ is a (possibly implicit) map into a
        Hilbert space $\\mathcal{H}$. You compute the similarity without constructing $\\phi$.

        **Validity — Positive Semi-Definiteness (PSD):**
        The Gram matrix $K \\in \\mathbb{R}^{n \\times n}$ with $K_{ij} = k(x_i, x_j)$ must satisfy:
        """)
        st.latex(r"\mathbf{c}^\top K \mathbf{c} \geq 0 \quad \forall \mathbf{c} \in \mathbb{R}^n")
        st.markdown("""
        **Mercer's Theorem (1909):** A continuous symmetric function is a valid kernel iff its
        Gram matrix is PSD for every finite set of points. Equivalently, it has a spectral expansion:
        """)
        st.latex(r"k(\mathbf{x}, \mathbf{x}') = \sum_{i=1}^\infty \lambda_i \psi_i(\mathbf{x})\psi_i(\mathbf{x}')")
        st.markdown("with $\\lambda_i \\geq 0$. This decomposition is the formal bridge to Random Fourier Features.")

    with tab_trick:
        st.markdown("### The Kernel Trick")
        st.markdown("""
        Many ML algorithms depend only on **inner products** between points.
        Replacing $\\langle x_i, x_j \\rangle$ with $k(x_i, x_j)$ lifts the algorithm into
        a high-dimensional feature space at cost $O(d)$ per evaluation.

        **Concrete example — degree-2 polynomial kernel:**
        Let $\\mathbf{x} = (x_1, x_2)$. Define the explicit feature map:
        """)
        st.latex(r"\phi(\mathbf{x}) = (x_1^2,\; x_2^2,\; \sqrt{2}\,x_1 x_2)")
        st.markdown("Then:")
        st.latex(
            r"\langle \phi(\mathbf{x}), \phi(\mathbf{x}') \rangle"
            r"= x_1^2{x_1'}^2 + x_2^2{x_2'}^2 + 2x_1x_2x_1'x_2'"
            r"= (\mathbf{x} \cdot \mathbf{x}')^2"
        )
        st.markdown("""
        A 3D inner product computed via one 2D dot product.
        For degree-$d$ in $p$ dimensions the feature space has $O(p^d)$ dimensions but the kernel
        costs $O(p)$.

        **The RBF kernel** pushes this to the extreme: its implicit feature space is
        **infinite-dimensional**, yet $k(\\mathbf{x},\\mathbf{x}') = \\exp(-\\|\\mathbf{x}-\\mathbf{x}'\\|^2/2\\sigma^2)$
        evaluates in $O(d)$.
        """)

    with tab_kernels:
        st.markdown("### Common Kernels")
        df_k = pd.DataFrame({
            "Kernel": ["RBF / Gaussian", "Polynomial", "Laplacian", "Matérn"],
            "k(x, x')": [
                "exp(−‖x−x'‖² / 2σ²)",
                "(x·x' + c)^d",
                "exp(−‖x−x'‖₁ / σ)",
                "Bessel-based (length scale ℓ, smoothness ν)",
            ],
            "Feature dim": ["∞", "O(p^d)", "∞", "∞"],
            "Shift-invariant?": ["✅", "❌", "✅", "✅"],
            "RFF applicable?": ["✅", "❌", "✅", "✅"],
            "Character": [
                "Smooth, universal approximator",
                "Interaction terms, NLP",
                "Robust, heavy-tailed",
                "Tunable smoothness",
            ],
        })
        st.dataframe(df_k, use_container_width=True, hide_index=True)
        st.info(
            "**Shift-invariance** — $k(\\mathbf{x},\\mathbf{y}) = k(\\mathbf{x}-\\mathbf{y})$ — "
            "is the key prerequisite for Bochner's theorem and RFF."
        )

    with tab_viz:
        st.markdown("### RBF Kernel Similarity Heatmap")
        st.markdown(
            "Shows $k(x, x') = \\exp(-|x-x'|^2 / 2\\sigma^2)$ for $x, x' \\in [-3, 3]$. "
            "Warm = similar; cool = dissimilar."
        )
        col_s, col_v = st.columns([1, 3])
        with col_s:
            sigma_km = st.slider("σ (bandwidth)", 0.3, 3.0, 1.0, 0.1, key="km_s")
            st.markdown(f"**σ = {sigma_km}**  \nLarger σ → similarity decays more slowly.")

        grid = np.linspace(-3, 3, 250)
        X1, X2 = np.meshgrid(grid, grid)
        K_viz = np.exp(-(X1 - X2) ** 2 / (2 * sigma_km ** 2))

        fig_k, ax_k = plt.subplots(figsize=(5, 4))
        im = ax_k.imshow(K_viz, extent=[-3, 3, -3, 3], origin="lower",
                         cmap="RdYlBu_r", vmin=0, vmax=1)
        ax_k.set_xlabel("x")
        ax_k.set_ylabel("x'")
        ax_k.set_title(f"RBF kernel (σ={sigma_km:.1f})")
        plt.colorbar(im, ax=ax_k, label="k(x, x')")
        plt.tight_layout()
        with col_v:
            st.pyplot(fig_k)
        plt.close(fig_k)
        st.caption("The diagonal is always 1 (a point is maximally similar to itself).")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Scalability Problem
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Scalability Problem":
    st.title("⚡ The Scalability Problem")
    st.divider()

    st.markdown("Every kernel method builds the Gram matrix $K_{ij} = k(\\mathbf{x}_i, \\mathbf{x}_j)$:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Storage requirements (float64)")
        ns = [1_000, 10_000, 100_000, 1_000_000]
        gb = [n ** 2 * 8 / 1e9 for n in ns]
        df_s = pd.DataFrame({
            "n": [f"{n:,}" for n in ns],
            "Matrix": [f"{n}×{n}" for n in ns],
            "Size (GB)": [f"{g:.3f}" if g < 1 else f"{g:.0f}" for g in gb],
            "Feasible?": ["✅" if g < 4 else ("⚠️" if g < 40 else "❌") for g in gb],
        })
        st.table(df_s)

        st.markdown("#### Method-specific training cost")
        df_cost = pd.DataFrame({
            "Method": ["Kernel SVM", "Gaussian Process", "Kernel PCA"],
            "Training": ["O(n² – n³)", "O(n³) Cholesky", "O(n²k)"],
            "Prediction": ["O(n_sv · d)", "O(n) per point", "O(nk)"],
        })
        st.table(df_cost)

    with col2:
        st.markdown("#### Compute cost comparison (log scale)")
        fig_sc, ax_sc = plt.subplots(figsize=(5.5, 4))
        ns_p = np.logspace(2, 6, 200)
        ax_sc.loglog(ns_p, ns_p ** 3,       color=TRUE_C, lw=2.5, label="Exact: O(n³)")
        ax_sc.loglog(ns_p, ns_p * 1_000,    color=RFF_C,  lw=2.5, label="RFF: O(nD), D=1k")
        ax_sc.loglog(ns_p, ns_p * (1_000 ** 2), color=SPEC_C, lw=2, ls="--",
                     label="Nyström: O(nm²), m=1k")
        ax_sc.axvline(1e5, color="gray", ls=":", alpha=0.6)
        ax_sc.text(1.2e5, 1e5, "n=100k", fontsize=8, color="gray")
        ax_sc.set_xlabel("Training points n")
        ax_sc.set_ylabel("Operations (log scale)")
        ax_sc.set_title("Compute scaling comparison")
        ax_sc.legend(fontsize=9)
        ax_sc.grid(True, alpha=0.3, which="both")
        plt.tight_layout()
        st.pyplot(fig_sc)
        plt.close(fig_sc)

    st.success(
        "**Random Fourier Features** attacks this at the root: approximate "
        "$k(\\mathbf{x}, \\mathbf{y}) \\approx z(\\mathbf{x})^\\top z(\\mathbf{y})$ "
        "with an explicit $D$-dimensional map. Training a linear model on $z$ costs "
        "$O(nD)$ — **linear in $n$** for fixed $D$."
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Bochner's Theorem
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Bochner's Theorem":
    st.title("📐 Bochner's Theorem")
    st.markdown("*The theoretical foundation of Random Fourier Features*")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Shift-Invariant Kernels")
        st.markdown(
            "A kernel is **shift-invariant** (stationary) if it depends only on the "
            "difference between its inputs:"
        )
        st.latex(r"k(\mathbf{x}, \mathbf{y}) = k(\mathbf{x} - \mathbf{y})")

        with st.expander("⚠️ Notation clarification — why does k appear with both one and two inputs?"):
            st.markdown("""
            This is a deliberate **notation overload** — the same symbol $k$ is used for two
            related but distinct functions:

            - **Left side** $k(\\mathbf{x}, \\mathbf{y})$ — kernel as a function of *two* inputs (the standard signature)
            - **Right side** $k(\\mathbf{x} - \\mathbf{y})$ — kernel as a function of *one* input (the difference vector)

            The statement $k(\\mathbf{x}, \\mathbf{y}) = k(\\mathbf{x} - \\mathbf{y})$ is asserting that
            the value of the two-argument kernel **depends only on the difference** $\\mathbf{x} - \\mathbf{y}$,
            not on $\\mathbf{x}$ and $\\mathbf{y}$ individually. So you can equivalently define a
            single-argument function that takes the difference as its sole input.

            **Concrete example — RBF kernel:**
            """)
            st.latex(
                r"k(\mathbf{x}, \mathbf{y})"
                r"= \exp\!\left(-\frac{\|\mathbf{x} - \mathbf{y}\|^2}{2\sigma^2}\right)"
                r"= \exp\!\left(-\frac{\|\boldsymbol{\Delta}\|^2}{2\sigma^2}\right)"
                r"= k(\boldsymbol{\Delta}), \quad \boldsymbol{\Delta} = \mathbf{x} - \mathbf{y}"
            )
            st.markdown("""
            $\\mathbf{x}$ and $\\mathbf{y}$ only ever appear as the combination $\\mathbf{x} - \\mathbf{y}$,
            so the single-argument form is equivalent.

            **Counter-example — polynomial kernel** (not shift-invariant):
            """)
            st.latex(r"k(\mathbf{x}, \mathbf{y}) = (\mathbf{x} \cdot \mathbf{y})^2")
            st.markdown("""
            This depends on the *dot product*, not the difference, so it **cannot** be written as
            $k(\\mathbf{x} - \\mathbf{y})$ — Bochner's theorem does not apply.

            **Intuition:** shift-invariance means the kernel behaves like a *distance meter* — it only
            cares how far apart two points are, not where they sit in space. Translating both
            points by the same vector leaves the similarity unchanged.
            """)

        st.markdown("RBF, Laplacian, and Matérn kernels all have this property. Polynomial kernels do not.")

        st.markdown("### Bochner's Theorem (1932)")
        st.info(
            "A continuous, bounded, shift-invariant function $k(\\boldsymbol{\\Delta})$ on "
            "$\\mathbb{R}^d$ is **positive semi-definite iff** it is the Fourier transform of "
            "a non-negative measure $p(\\boldsymbol{\\omega})$:"
        )
        st.latex(
            r"k(\mathbf{x} - \mathbf{y})"
            r"= \int_{\mathbb{R}^d} p(\boldsymbol{\omega})\,"
            r"e^{i\boldsymbol{\omega}^\top(\mathbf{x}-\mathbf{y})}\, d\boldsymbol{\omega}"
        )
        st.markdown(
            "When $k(\\mathbf{0})=1$, the measure $p(\\boldsymbol{\\omega})$ is a proper "
            "**probability distribution** — the **spectral density** of the kernel."
        )
        st.markdown(
            "For real, symmetric $p(\\boldsymbol{\\omega})$ the imaginary parts cancel, "
            "giving the cosine form:"
        )
        st.latex(
            r"k(\mathbf{x} - \mathbf{y})"
            r"= \mathbb{E}_{\boldsymbol{\omega} \sim p}\!"
            r"\left[\cos\!\left(\boldsymbol{\omega}^\top(\mathbf{x} - \mathbf{y})\right)\right]"
        )
        st.success(
            "**Key implication:** the kernel is an *expectation of cosines* under the spectral "
            "distribution. Sample from $p(\\boldsymbol{\\omega})$, average the cosines — "
            "you get the kernel. That is RFF."
        )

    with col2:
        st.markdown("### Audio analogy")
        st.markdown("""
        Just as any audio signal decomposes into pure sinusoids via its Fourier spectrum,
        any stationary kernel decomposes into sinusoidal basis functions weighted by
        $p(\\boldsymbol{\\omega})$.

        The spectral density is the kernel's *frequency fingerprint* — it says how much
        weight each frequency receives.
        """)
        st.divider()
        st.markdown("### Spectral densities")
        df_sp = pd.DataFrame({
            "Kernel": ["RBF/Gaussian", "Laplacian", "Matérn", "Cauchy"],
            "p(ω)": ["N(0, σ⁻²I)", "Product Cauchy", "Student-t", "Product Laplace"],
        })
        st.table(df_sp)

    st.divider()
    st.markdown("### Interactive: kernel ↔ spectral density (uncertainty principle)")
    st.markdown(
        "The RBF kernel has $p(\\omega) = \\mathcal{N}(0, \\sigma^{-2})$. "
        "Adjust $\\sigma$ to see **wide kernel ↔ narrow spectrum** and vice-versa."
    )

    col_s, col_v = st.columns([1, 3])
    with col_s:
        sigma_b = st.slider("σ (kernel bandwidth)", 0.3, 3.0, 1.0, 0.1, key="b_s")
        st.markdown(
            f"**σ = {sigma_b:.1f}**  \n"
            f"Spectral std = 1/σ = **{1/sigma_b:.2f}**  \n\n"
            f"Large σ → smooth kernel → low-freq spectrum  \n"
            f"Small σ → sharp kernel → high-freq spectrum"
        )

    omega_b = np.linspace(-6, 6, 500)
    spec_b  = (sigma_b / np.sqrt(2 * np.pi)) * np.exp(-sigma_b ** 2 * omega_b ** 2 / 2)
    delta_b = np.linspace(-5, 5, 500)
    kern_b  = np.exp(-delta_b ** 2 / (2 * sigma_b ** 2))

    fig_b, (ax_b1, ax_b2) = plt.subplots(1, 2, figsize=(10, 3.5))
    ax_b1.plot(delta_b, kern_b, color=TRUE_C, lw=2.5)
    ax_b1.fill_between(delta_b, kern_b, alpha=0.15, color=TRUE_C)
    ax_b1.set(title=f"RBF kernel k(Δ),  σ={sigma_b:.1f}", xlabel="Δ = x − x'", ylabel="k(Δ)")
    ax_b1.set_ylim(-0.05, 1.1)
    ax_b1.grid(True, alpha=0.3)

    ax_b2.plot(omega_b, spec_b, color=SPEC_C, lw=2.5)
    ax_b2.fill_between(omega_b, spec_b, alpha=0.15, color=SPEC_C)
    ax_b2.set(title=f"Spectral density p(ω) = N(0, {1/sigma_b:.2f}²)",
              xlabel="frequency ω", ylabel="p(ω)")
    ax_b2.grid(True, alpha=0.3)

    plt.suptitle(
        "Wide kernel ↔ narrow spectrum    |    Narrow kernel ↔ wide spectrum",
        fontstyle="italic", fontsize=10
    )
    plt.tight_layout()
    with col_v:
        st.pyplot(fig_b)
    plt.close(fig_b)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: The RFF Algorithm
# ─────────────────────────────────────────────────────────────────────────────
elif section == "The RFF Algorithm":
    st.title("🎲 The RFF Algorithm")
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### Step-by-step derivation")

        st.markdown("**Step 1 — Bochner in complex form:**")
        st.latex(
            r"k(\mathbf{x}-\mathbf{y})"
            r"= \mathbb{E}_{\boldsymbol{\omega}\sim p}"
            r"\left[e^{i\boldsymbol{\omega}^\top \mathbf{x}}\, e^{-i\boldsymbol{\omega}^\top \mathbf{y}}\right]"
        )

        st.markdown("**Step 2 — Simplify to real cosines** (symmetric $p$, imaginary parts cancel):")
        st.latex(
            r"k(\mathbf{x}-\mathbf{y})"
            r"= \mathbb{E}_{\boldsymbol{\omega}\sim p}"
            r"\left[\cos\!\left(\boldsymbol{\omega}^\top(\mathbf{x}-\mathbf{y})\right)\right]"
        )

        st.markdown("**Step 3 — Random phase trick** ($b \\sim U[0, 2\\pi]$):")
        st.latex(
            r"\mathbb{E}_{b}\!\left["
            r"2\cos(\boldsymbol{\omega}^\top\mathbf{x}+b)\cos(\boldsymbol{\omega}^\top\mathbf{y}+b)"
            r"\right] = \cos(\boldsymbol{\omega}^\top(\mathbf{x}-\mathbf{y}))"
        )
        st.markdown(
            "*Proof:* expand via $\\cos\\alpha\\cos\\beta = \\tfrac{1}{2}[\\cos(\\alpha-\\beta)+\\cos(\\alpha+\\beta)]$. "
            "The $\\cos(\\alpha+\\beta)$ term integrates to zero over $U[0,2\\pi]$. ∎"
        )

        st.markdown("**Step 4 — The central result (combining steps 2 & 3):**")
        st.success("**Rahimi & Recht 2007 — key identity:**")
        st.latex(
            r"\boxed{"
            r"k(\mathbf{x}, \mathbf{y})"
            r"= \mathbb{E}_{\substack{\boldsymbol{\omega}\sim p \\ b\sim U[0,2\pi]}}"
            r"\!\left["
            r"\underbrace{\sqrt{2}\cos(\boldsymbol{\omega}^\top\mathbf{x}+b)}_{z_\omega(\mathbf{x})}"
            r"\cdot"
            r"\underbrace{\sqrt{2}\cos(\boldsymbol{\omega}^\top\mathbf{y}+b)}_{z_\omega(\mathbf{y})}"
            r"\right]"
            r"}"
        )

        st.markdown("**Step 5 — Monte Carlo with $D$ samples:**")
        st.latex(
            r"z(\mathbf{x}) = \frac{1}{\sqrt{D}}"
            r"\begin{bmatrix}"
            r"\sqrt{2}\cos(\boldsymbol{\omega}_1^\top \mathbf{x} + b_1)\\"
            r"\vdots\\"
            r"\sqrt{2}\cos(\boldsymbol{\omega}_D^\top \mathbf{x} + b_D)"
            r"\end{bmatrix},"
            r"\quad"
            r"\boldsymbol{\omega}_j \sim p(\boldsymbol{\omega}),\; b_j \sim U[0,2\pi]"
        )
        st.latex(r"z(\mathbf{x})^\top z(\mathbf{y}) \approx k(\mathbf{x},\mathbf{y})")

    with col2:
        st.markdown("### Pseudocode")
        st.code(
            """\
# Given: kernel k, dataset X (n×d), D features
# Output: feature matrix Z (n×D)

# 1. Identify spectral density p(ω):
#    RBF      → p(ω) = N(0, σ⁻²I)
#    Laplace  → p(ω) = Cauchy
#    Matérn ν → p(ω) = Student-t

# 2. Sample random frequencies and phases
omega = sample(p_omega, shape=(d, D))   # (d, D)
b     = uniform(0, 2π, shape=(D,))      # (D,)

# 3. Build feature map
projections = X @ omega + b   # (n, D)
Z = sqrt(2 / D) * cos(projections)

# 4. Train any linear model on Z
#    → approximates the kernel machine
model = LinearSVM().fit(Z, y)

# Predict new point x*:
z_star = sqrt(2/D) * cos(x_star @ omega + b)
y_pred = model.predict(z_star)
""",
            language="python",
        )

        st.markdown("### scikit-learn")
        st.code(
            """\
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ("rff", RBFSampler(gamma=0.5, n_components=1000)),
    ("clf", SGDClassifier()),
])
pipe.fit(X_train, y_train)
""",
            language="python",
        )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Interactive Visualizations
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Interactive Visualizations":
    st.title("📊 Interactive Visualizations")
    st.markdown("*Build intuition by interacting with the mathematics directly.*")
    st.divider()

    v1, v2, v3, v4 = st.tabs([
        "① Cosine Averaging",
        "② Kernel Matrix Approximation",
        "③ Frequency Sampling",
        "④ Feature Functions",
    ])

    # ── Viz 1: Cosine Averaging Convergence ──────────────────────────────────
    with v1:
        st.markdown("### The Kernel as an Average of Cosines")
        st.markdown(
            "Bochner: $k(\\Delta) = \\mathbb{E}_{\\omega \\sim p}[\\cos(\\omega \\cdot \\Delta)]$. "
            "For the RBF kernel, sample $\\omega_j \\sim \\mathcal{N}(0, \\sigma^{-2})$ and compute "
            "the running average. Watch it converge to the true kernel (red dashed)."
        )

        col_c, col_p = st.columns([1, 3])
        with col_c:
            D_v1   = st.slider("D (samples)", 1, 500, 20, key="v1_D")
            sig_v1 = st.slider("σ", 0.5, 2.0, 1.0, 0.25, key="v1_s")
            seed1  = int(st.number_input("Random seed", 0, 999, 42, key="v1_sd"))
            st.markdown(f"**D = {D_v1}**  \nStd error ∝ 1/√D ≈ {1/np.sqrt(D_v1):.3f}")

        rng1    = np.random.RandomState(seed1)
        omegas1 = rng1.randn(D_v1) / sig_v1
        delta1  = np.linspace(-4, 4, 400)
        cosines1 = np.cos(np.outer(omegas1, delta1))   # (D, 400)
        approx1  = cosines1.mean(axis=0)
        true1    = np.exp(-delta1 ** 2 / (2 * sig_v1 ** 2))

        fig1, (ax1t, ax1b) = plt.subplots(
            2, 1, figsize=(9, 6), gridspec_kw={"height_ratios": [3, 1]}
        )

        n_show = min(D_v1, 30)
        alpha  = max(0.05, 0.8 / max(n_show, 1))
        for j in range(n_show):
            ax1t.plot(delta1, cosines1[j], color=RFF_C, alpha=alpha, lw=0.8)

        ax1t.plot(delta1, approx1, color=RFF_C, lw=2.5, label=f"RFF average (D={D_v1})")
        ax1t.plot(delta1, true1,   color=TRUE_C, lw=2.5, ls="--", label=f"True RBF kernel (σ={sig_v1})")
        ax1t.axhline(0, color="gray", ls=":", lw=0.8, alpha=0.5)
        ax1t.set(xlim=(-4, 4), ylim=(-0.6, 1.4), ylabel="Value",
                 title=f"Monte Carlo approximation of RBF kernel — {D_v1} cosines averaged")
        ax1t.legend(fontsize=10)
        ax1t.grid(True, alpha=0.3)

        err1 = np.abs(approx1 - true1)
        ax1b.fill_between(delta1, err1, color="orange", alpha=0.7, label="|approx − true|")
        ax1b.set(xlim=(-4, 4), xlabel="Δ = x − y", ylabel="|error|")
        ax1b.legend(fontsize=9)
        ax1b.grid(True, alpha=0.3)

        plt.tight_layout()
        with col_p:
            st.pyplot(fig1)
        plt.close(fig1)
        st.caption(
            "Faint blue = individual cosine samples. Bold blue = their average. "
            "Red dashed = target kernel. The average converges as D grows."
        )

    # ── Viz 2: Kernel Matrix Approximation ───────────────────────────────────
    with v2:
        st.markdown("### True Kernel Matrix vs. RFF Approximation")
        st.markdown(
            "50 random 2D points. Left: exact RBF kernel matrix $K$. "
            "Right: RFF approximation $\\mathbf{Z}\\mathbf{Z}^\\top$ for increasing $D$. "
            "MAE = mean absolute error entry-wise."
        )

        col_c2, _ = st.columns([2, 1])
        with col_c2:
            sig_v2 = st.slider("σ", 0.3, 2.0, 1.0, 0.1, key="v2_s")
            seed2  = int(st.number_input("Random seed", 0, 999, 7, key="v2_sd"))

        rng2  = np.random.RandomState(seed2)
        n_pts = 50
        X2    = rng2.randn(n_pts, 2)

        diff2  = X2[:, None, :] - X2[None, :, :]
        K_true = np.exp(-np.sum(diff2 ** 2, axis=-1) / (2 * sig_v2 ** 2))

        D_list = [1, 10, 100, 1000]
        fig2, axes2 = plt.subplots(1, 5, figsize=(15, 3.2))

        im2 = axes2[0].imshow(K_true, cmap="RdBu_r", vmin=0, vmax=1)
        axes2[0].set_title("True K\n(exact)", fontsize=10, color=TRUE_C)
        axes2[0].axis("off")

        for i, D2 in enumerate(D_list):
            w2 = rng2.randn(2, D2) / sig_v2
            b2 = rng2.uniform(0, 2 * np.pi, D2)
            Z2 = np.sqrt(2 / D2) * np.cos(X2 @ w2 + b2)
            K_hat = Z2 @ Z2.T
            mae   = float(np.mean(np.abs(K_hat - K_true)))
            axes2[i + 1].imshow(K_hat, cmap="RdBu_r", vmin=0, vmax=1)
            axes2[i + 1].set_title(f"RFF D={D2}\nMAE={mae:.3f}", fontsize=10, color=RFF_C)
            axes2[i + 1].axis("off")

        plt.colorbar(im2, ax=axes2.tolist(), shrink=0.8, label="k(xᵢ, xⱼ)")
        plt.suptitle("Kernel matrix approximation vs. D", fontsize=12, y=1.02)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
        st.caption("As D increases, the RFF approximation becomes visually indistinguishable from the truth.")

    # ── Viz 3: Frequency Sampling Geometry ───────────────────────────────────
    with v3:
        st.markdown("### Frequency Sampling Geometry")
        st.markdown(
            "Each RFF draw samples $\\boldsymbol{\\omega} \\sim \\mathcal{N}(\\mathbf{0}, \\sigma^{-2}\\mathbf{I})$. "
            "In 2D this is an isotropic Gaussian cloud — all directions equally likely, "
            "reflecting the **rotational invariance** of the RBF kernel."
        )

        col_c3, col_p3 = st.columns([1, 2])
        with col_c3:
            sig_v3 = st.slider("σ (kernel bandwidth)", 0.3, 3.0, 1.0, 0.1, key="v3_s")
            D_v3   = st.slider("D (# frequencies)", 50, 500, 200, 50, key="v3_D")
            spec_std = 1 / sig_v3
            st.markdown(
                f"**Spectral std = 1/σ = {spec_std:.2f}**  \n"
                f"Large σ → tight cloud (low-freq)  \n"
                f"Small σ → spread cloud (high-freq)"
            )

        rng3    = np.random.RandomState(42)
        omegas3 = rng3.randn(D_v3, 2) / sig_v3

        theta3  = np.linspace(0, 2 * np.pi, 300)
        fig3, ax3 = plt.subplots(figsize=(5, 5))
        ax3.scatter(omegas3[:, 0], omegas3[:, 1], alpha=0.5, s=18, color=SPEC_C, zorder=3)
        for r, ls, lbl in [(spec_std, "-", "1σ"), (2 * spec_std, "--", "2σ")]:
            ax3.plot(r * np.cos(theta3), r * np.sin(theta3),
                     color="gray", ls=ls, alpha=0.6, lw=1.5, label=lbl)
        ax3.set_aspect("equal")
        ax3.set(title=f"Sampled frequencies ω ~ N(0, {spec_std:.2f}²·I)\nD={D_v3}",
                xlabel="ω₁", ylabel="ω₂")
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        plt.tight_layout()
        with col_p3:
            st.pyplot(fig3)
        plt.close(fig3)
        st.caption("Each dot = one sampled frequency. The isotropic cloud reflects RBF's rotational symmetry — no direction is preferred.")

    # ── Viz 4: Feature Functions ──────────────────────────────────────────────
    with v4:
        st.markdown("### Individual Random Feature Functions")
        st.markdown(
            "Each $(\\omega_j, b_j)$ defines one feature: "
            "$z_j(x) = \\sqrt{2}\\cos(\\omega_j x + b_j)$.  \n"
            "High $|\\omega|$ → rapid oscillations.  Low $|\\omega|$ → slow variation.  "
            "The spectral density controls how often each frequency appears."
        )

        col_c4, col_p4 = st.columns([1, 3])
        with col_c4:
            sig_v4 = st.slider("σ", 0.3, 3.0, 1.0, 0.1, key="v4_s")
            n_f4   = st.slider("# features shown", 3, 12, 6, key="v4_n")
            seed4  = int(st.number_input("Seed", 0, 999, 0, key="v4_sd"))

        rng4    = np.random.RandomState(seed4)
        omegas4 = rng4.randn(n_f4) / sig_v4
        biases4 = rng4.uniform(0, 2 * np.pi, n_f4)
        x4      = np.linspace(-3, 3, 400)
        colors4 = [plt.cm.tab10(i / 10) for i in range(n_f4)]

        fig4, (ax4l, ax4r) = plt.subplots(1, 2, figsize=(11, 4.5))

        for j in range(n_f4):
            y_j = np.sqrt(2) * np.cos(omegas4[j] * x4 + biases4[j])
            ax4l.plot(x4, y_j, color=colors4[j], lw=1.8, label=f"ω={omegas4[j]:.2f}")
        ax4l.set(xlabel="x", ylabel=r"$\sqrt{2}\cos(\omega x + b)$",
                 title="Individual feature functions", ylim=(-2, 2))
        ax4l.legend(fontsize=7, ncol=2)
        ax4l.grid(True, alpha=0.3)

        omega_r = np.linspace(-8 / sig_v4, 8 / sig_v4, 400)
        spec_r  = (sig_v4 / np.sqrt(2 * np.pi)) * np.exp(-sig_v4 ** 2 * omega_r ** 2 / 2)
        ax4r.hist(omegas4, bins=max(n_f4 // 2, 3), density=True,
                  color=SPEC_C, alpha=0.55, label="Sampled ω (this run)")
        ax4r.plot(omega_r, spec_r, color=TRUE_C, lw=2, label="True p(ω)")
        ax4r.set(xlabel="frequency ω", ylabel="density", title="Frequency distribution")
        ax4r.legend(fontsize=10)
        ax4r.grid(True, alpha=0.3)

        plt.tight_layout()
        with col_p4:
            st.pyplot(fig4)
        plt.close(fig4)
        st.caption("Left: feature functions. Right: their frequencies vs. the spectral density. With many samples the histogram converges to the Gaussian curve.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: RBF & Spectral Duality
# ─────────────────────────────────────────────────────────────────────────────
elif section == "RBF & Spectral Duality":
    st.title("🔬 RBF & Spectral Self-Duality")
    st.divider()

    st.markdown("### Why is $p(\\boldsymbol{\\omega}) = \\mathcal{N}(\\mathbf{0}, \\sigma^{-2}\\mathbf{I})$ for the RBF kernel?")
    st.markdown("We need $p$ such that:")
    st.latex(
        r"\exp\!\left(-\frac{\|\boldsymbol{\Delta}\|^2}{2\sigma^2}\right)"
        r"= \int p(\boldsymbol{\omega})\, e^{i\boldsymbol{\omega}^\top\boldsymbol{\Delta}}\, d\boldsymbol{\omega}"
    )
    st.markdown("This is a Fourier inversion problem. The key fact: **the Gaussian is self-dual under the Fourier transform**:")
    st.latex(r"\mathcal{F}\left\{e^{-t^2/2\sigma^2}\right\}(\omega) = \sigma\sqrt{2\pi}\; e^{-\sigma^2\omega^2/2}")
    st.markdown("Normalizing to a probability density:")
    st.latex(
        r"p(\omega) = \mathcal{N}\!\left(0,\, \frac{1}{\sigma^2}\right)"
        r"\quad \Longrightarrow \quad"
        r"\mathbb{E}_{\omega \sim \mathcal{N}(0,\sigma^{-2})}[\cos(\omega\Delta)] = e^{-\Delta^2/2\sigma^2}"
    )
    st.markdown("In $d$ dimensions with the isotropic RBF kernel:")
    st.latex(
        r"\boxed{p(\boldsymbol{\omega}) = \mathcal{N}(\mathbf{0},\, \sigma^{-2}\mathbf{I}_d)}"
        r"\quad \iff \quad"
        r"\boldsymbol{\omega} = \tfrac{1}{\sigma}\mathbf{z},\; \mathbf{z}\sim\mathcal{N}(\mathbf{0},\mathbf{I})"
    )

    st.divider()
    st.markdown("### The Uncertainty Principle")
    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "**Large σ** (wide, smooth kernel)  \n"
            "→ Long-range correlations  \n"
            "→ Low-frequency structure  \n"
            "→ Spectral density **narrow** (small variance σ⁻²)"
        )
    with col2:
        st.warning(
            "**Small σ** (narrow, sharp kernel)  \n"
            "→ Short-range correlations only  \n"
            "→ High-frequency structure  \n"
            "→ Spectral density **wide** (large variance σ⁻²)"
        )
    st.markdown("*This is the time-frequency uncertainty principle: wide in space ↔ narrow in frequency.*")

    # Side-by-side plot for several σ values
    st.divider()
    st.markdown("### Visual: kernel and spectral density for multiple σ values")
    sigmas_show = [0.5, 1.0, 2.0]
    fig_sd, axes_sd = plt.subplots(2, 3, figsize=(12, 5))
    delta_sd = np.linspace(-5, 5, 400)
    omega_sd = np.linspace(-8, 8, 400)
    for col_idx, sg in enumerate(sigmas_show):
        k_sd  = np.exp(-delta_sd ** 2 / (2 * sg ** 2))
        p_sd  = (sg / np.sqrt(2 * np.pi)) * np.exp(-sg ** 2 * omega_sd ** 2 / 2)
        axes_sd[0, col_idx].plot(delta_sd, k_sd, color=TRUE_C, lw=2)
        axes_sd[0, col_idx].fill_between(delta_sd, k_sd, alpha=0.15, color=TRUE_C)
        axes_sd[0, col_idx].set(title=f"Kernel σ={sg}", ylim=(-0.05, 1.1))
        axes_sd[0, col_idx].grid(True, alpha=0.3)

        axes_sd[1, col_idx].plot(omega_sd, p_sd, color=SPEC_C, lw=2)
        axes_sd[1, col_idx].fill_between(omega_sd, p_sd, alpha=0.15, color=SPEC_C)
        axes_sd[1, col_idx].set(title=f"Spectrum std={1/sg:.2f}")
        axes_sd[1, col_idx].grid(True, alpha=0.3)

    axes_sd[0, 0].set_ylabel("k(Δ)", fontsize=11)
    axes_sd[1, 0].set_ylabel("p(ω)", fontsize=11)
    for ax in axes_sd[1]:
        ax.set_xlabel("ω")
    for ax in axes_sd[0]:
        ax.set_xlabel("Δ")
    plt.suptitle("Kernel (top row) and its spectral density (bottom row) for three bandwidths",
                 fontsize=12)
    plt.tight_layout()
    st.pyplot(fig_sd)
    plt.close(fig_sd)

    st.divider()
    st.markdown("### Spectral distributions for all common kernels")
    df_spec = pd.DataFrame({
        "Kernel": ["Gaussian/RBF", "Laplacian", "Matérn ν=1/2", "Matérn ν=3/2", "Cauchy"],
        "k(Δ)": [
            "exp(−‖Δ‖²/2σ²)",
            "exp(−‖Δ‖₁/σ)",
            "exp(−‖Δ‖/ℓ)",
            "(1+√3‖Δ‖/ℓ) exp(−√3‖Δ‖/ℓ)",
            "∏ᵢ (1+Δᵢ²/σ²)⁻¹",
        ],
        "p(ω)": [
            "N(0, σ⁻²I) — Gaussian",
            "∏ᵢ Cauchy(0, σ⁻¹)",
            "∏ᵢ Cauchy(0, ℓ⁻¹)",
            "Student-t(3) scaled by √3/ℓ",
            "∏ᵢ Laplace(0, σ⁻¹)",
        ],
    })
    st.table(df_spec)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Error Guarantees
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Error Guarantees":
    st.title("📏 Error Guarantees")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Unbiasedness")
        st.latex(r"\mathbb{E}\!\left[z(\mathbf{x})^\top z(\mathbf{y})\right] = k(\mathbf{x},\mathbf{y})")
        st.markdown("No systematic error — only random noise that vanishes as D → ∞.")

        st.markdown("### Variance decay")
        st.latex(r"\text{Var}\!\left[z(\mathbf{x})^\top z(\mathbf{y})\right] = O\!\left(\tfrac{1}{D}\right)")
        st.markdown("Variance halves every time you double D.")

        st.markdown("### Pointwise concentration (Hoeffding's inequality)")
        st.markdown(
            "Since $z_\\omega(\\mathbf{x}) \\in [-\\sqrt{2},\\sqrt{2}]$, "
            "the product is bounded in $[-2,2]$. Hoeffding gives:"
        )
        st.latex(
            r"\Pr\!\left[\,\left|z(\mathbf{x})^\top z(\mathbf{y}) - k(\mathbf{x},\mathbf{y})\right|"
            r"\geq \varepsilon\,\right]"
            r"\leq 2\exp\!\left(-\frac{D\varepsilon^2}{4}\right)"
        )
        st.markdown("To achieve error $\\leq \\varepsilon$ with probability $\\geq 1-\\delta$:")
        st.latex(r"D \geq \frac{4}{\varepsilon^2}\ln\frac{2}{\delta}")
        st.success("$D$ is **independent of input dimension $d$ and dataset size $n$**.")

        st.markdown("### Uniform bound (Claim 1, Rahimi & Recht)")
        st.markdown("For all pairs on a compact domain $\\mathcal{M}$:")
        st.latex(
            r"D = O\!\left(\frac{d}{\varepsilon^2}\ln\frac{\sigma_p\,\text{diam}(\mathcal{M})}{\varepsilon\delta}\right)"
        )
        st.markdown("For uniform accuracy over all pairs, $D$ scales linearly with $d$.")

    with col2:
        delta_err = st.select_slider(
            "Failure probability δ",
            options=[0.01, 0.05, 0.10, 0.20],
            value=0.05,
        )
        eps_rng = np.linspace(0.02, 0.5, 200)
        D_req   = (4 / eps_rng ** 2) * np.log(2 / delta_err)

        fig_e, ax_e = plt.subplots(figsize=(6, 4))
        ax_e.semilogy(eps_rng, D_req, color=RFF_C, lw=2.5)
        ax_e.axhline(100,  color="gray", ls=":",  alpha=0.6, label="D=100")
        ax_e.axhline(1000, color="gray", ls="--", alpha=0.6, label="D=1000")
        ax_e.set(xlabel="Error tolerance ε", ylabel="Required D (log scale)",
                 title=f"D needed for pointwise |error| ≤ ε\n(failure prob δ={delta_err})")
        ax_e.legend(fontsize=9)
        ax_e.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_e)
        plt.close(fig_e)

        st.markdown("### Std deviation vs. D")
        D_rng = np.arange(1, 1001)
        fig_c, ax_c = plt.subplots(figsize=(6, 3.5))
        ax_c.loglog(D_rng, 1 / np.sqrt(D_rng), color=RFF_C, lw=2.5, label="std dev ∝ 1/√D")
        ax_c.set(xlabel="D (# features)", ylabel="Std dev",
                 title="Estimator standard deviation vs. D")
        ax_c.legend(fontsize=10)
        ax_c.grid(True, alpha=0.3, which="both")
        plt.tight_layout()
        st.pyplot(fig_c)
        plt.close(fig_c)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Extensions & History
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Extensions & History":
    st.title("🏛 Extensions & History")
    st.divider()

    tab_h, tab_e = st.tabs(["History", "Extensions"])

    with tab_h:
        st.markdown("""
        ### The Original Paper

        **"Random Features for Large-Scale Kernel Machines"**
        Ali Rahimi and Benjamin Recht, NeurIPS 2007

        By 2007 kernel SVMs were the gold standard for classification.
        But training at $n > 10^5$ was computationally out of reach.
        Rahimi & Recht provided the first theoretically grounded, practically efficient solution:
        approximate the *kernel function itself* rather than trying to speed up the linear algebra.

        The paper won the **NeurIPS 2017 Test of Time Award** (10 years later) and has since
        accumulated thousands of citations spanning kernel approximation, GP regression,
        deep kernel learning, and attention in Transformers.

        ---

        ### The "Alchemy" Talk (NeurIPS 2017)

        Rahimi used his Test of Time acceptance speech to argue that ML had become
        **"alchemy"** — practitioners producing impressive results through trial-and-error
        without understanding *why* things work.

        > *"We are building systems that govern healthcare and mediate our civic dialogue...
        > I would like to live in a society where systems are built on top of verifiable,
        > rigorous, thorough knowledge and not alchemy."*

        He called for ablation studies, simple toy problems, and theorems that can be
        transmitted to the next generation of researchers.

        The talk provoked an immediate rebuttal from Yann LeCun, who called the alchemy
        analogy "insulting" and argued that engineering advances without complete theoretical
        understanding is normal across all fields.

        Full text: https://archives.argmin.net/2017/12/05/kitchen-sinks/
        """)

    with tab_e:
        st.markdown("### Extensions to Vanilla RFF")
        df_ext = pd.DataFrame({
            "Method": [
                "Orthogonal RFF",
                "Quasi-Random RFF",
                "Structured RFF (FastFood)",
                "Deep Kernel Learning",
                "Performers (Attention)",
            ],
            "Key Idea": [
                "Make ωⱼ mutually orthogonal via Gram-Schmidt",
                "Replace i.i.d. samples with Sobol / Halton sequences",
                "Use Hadamard transforms → O(D log D) features",
                "Learn the spectral density p(ω) from data",
                "RFF to approximate softmax attention in O(n) time",
            ],
            "Benefit": [
                "Strictly lower variance → fewer features needed",
                "Faster convergence O(D⁻¹) vs O(D⁻¹/²)",
                "10× faster feature computation",
                "Kernel adapts to data distribution",
                "Linear-time Transformers",
            ],
            "Reference": [
                "Yu et al. 2016",
                "Avron et al. 2016",
                "Le et al. 2013",
                "Wilson et al. 2016",
                "Choromanski et al. 2021",
            ],
        })
        st.dataframe(df_ext, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: Sources
# ─────────────────────────────────────────────────────────────────────────────
elif section == "Sources":
    st.title("📚 Sources")
    st.divider()
    st.markdown("""
    ### Primary

    1. **Rahimi, A. & Recht, B. (2007).** Random Features for Large-Scale Kernel Machines.
       *NeurIPS 2007.* [PDF](https://people.eecs.berkeley.edu/~brecht/papers/07.rah.rec.nips.pdf)

    2. **Recht, B. (2017).** Reflections on Random Kitchen Sinks (NeurIPS 2017 Test of Time talk).
       [archives.argmin.net](https://archives.argmin.net/2017/12/05/kitchen-sinks/)

    ### Tutorials & Blogs

    3. **Gundersen, G. (2019).** Random Fourier Features.
       [gregorygundersen.com](https://gregorygundersen.com/blog/2019/12/23/random-fourier-features/)

    4. **Jones, A.** Approximating Kernels with Random Projections (with convergence animation).
       [andrewcharlesjones.github.io](https://andrewcharlesjones.github.io/journal/bochners-theorem.html)

    5. **Random Walks Book** — RFF chapter with GP variance analysis.
       [random-walks.org](https://random-walks.org/book/papers/rff/rff.html)

    6. **Emiruz (2024).** RBF Kernel Approximation with Random Fourier Features.
       [emiruz.com](https://emiruz.com/post/2024-04-29-random-fourier/)

    ### Papers

    7. **Li, Z. et al. (2019).** Towards a Unified Analysis of Random Fourier Features. *ICML 2019.*
       [PDF](http://proceedings.mlr.press/v97/li19k/li19k.pdf)

    8. **Sutherland, D. & Schneider, J. (2015).** On the Error of Random Fourier Features. *UAI 2015.*
       [PDF](https://auai.org/uai2015/proceedings/papers/168.pdf)

    9. **Choromanski, K. et al. (2021).** Rethinking Attention with Performers. *ICLR 2021.*

    ### Reference

    10. Wikipedia — [Random Feature](https://en.wikipedia.org/wiki/Random_feature)
    11. Wikipedia — [Bochner's Theorem](https://en.wikipedia.org/wiki/Bochner%27s_theorem)
    12. scikit-learn — [RBFSampler](https://scikit-learn.org/stable/modules/generated/sklearn.kernel_approximation.RBFSampler.html)
    13. Gatsby UCL — [Intro to RKHS (Gretton)](https://www.gatsby.ucl.ac.uk/~gretton/coursefiles/lecture4_introToRKHS.pdf)
    """)
