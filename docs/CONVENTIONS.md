# Physical and numerical conventions

**Status: frozen in Stage 1; Stage-2 topology algorithms validated on 2026-06-29.**  These
conventions are the project-wide source of truth.  A notebook, figure, or numerical routine may
not silently override them.

## 1. Charge, magnetic field, gauge, and units

| Item | Frozen convention | Consequence |
|---|---|---|
| Elementary charge | `e > 0`, represented numerically by `e = 1` | The electron charge is `q_e = -e`. |
| Flux quantum | `Phi_0 = h/e = 2 pi hbar/e` | In natural units, `Phi_0 = 2 pi`. |
| Magnetic field | `B = +B z-hat` | Positive flux is oriented through the directed `+x,+y` plaquette. |
| Gauge | Landau gauge `A = (0, Bx, 0)` | Peierls phases occur on forward-y hoppings. |
| Lattice spacing | `a = 1` unless a model parameter overrides it | Momenta are reported in inverse-lattice-spacing units. |
| Natural units | `hbar = 1` | Energies are in hopping units and time is in inverse-hopping units. |

The central magnetic flux is

$$
\phi=\frac{\Phi}{\Phi_0}=\frac{p}{q},
\qquad \gcd(p,q)=1.
$$

For the primary teaching case, `p=1`, `q=3`, and `t_x=t_y=1`.

## 2. Parent Peierls Hamiltonian

All Harper-Hofstadter geometries are derived from one parent model:

$$
H=-t_x\sum_{m,n}\left(c^\dagger_{m+1,n}c_{m,n}+\mathrm{h.c.}\right)
-t_y\sum_{m,n}\left(
 e^{+i2\pi\phi m}c^\dagger_{m,n+1}c_{m,n}+\mathrm{h.c.}\right).
$$

Therefore, the matrix element for a forward-y hop is

$$
H_{(m,n+1),(m,n)}=-t_y e^{+i2\pi\phi m},
$$

and its reverse is the complex conjugate.  Forward-x hops are real and equal to `-t_x`.
The sign, gauge, and forward-hop direction above are never changed locally to improve a plot or
match an external convention.

## 3. Boundary and Bloch conventions

### Open geometry

The state-vector site index is

$$
i(m,n;L_y)=mL_y+n,
$$

with `m=0,...,Lx-1`, `n=0,...,Ly-1`.  A vector reshapes to an array with shape `(Lx, Ly)`.
This is the only supported array ordering for the real-space modules.

### Ribbon geometry

The y direction is periodic and the x direction is open.  The Fourier convention is

$$
c_{m,n}=\frac{1}{\sqrt{L_y}}\sum_{k_y}e^{+ik_yan}c_m(k_y),
$$

yielding

$$
H_{m,m}(k_y)=-2t_y\cos(k_ya-2\pi\phi m),
$$

plus nearest-neighbour x hopping `-t_x`.

### Magnetic Bloch geometry

Write the x coordinate as `m=qR+r`, with `r=0,...,q-1`, and use

$$
\psi_{R,r}=e^{+iqak_xR}u_r(\mathbf{k}).
$$

The magnetic Brillouin zone is

$$
k_x\in\left[-\frac{\pi}{qa},\frac{\pi}{qa}\right),
\qquad
k_y\in\left[-\frac{\pi}{a},\frac{\pi}{a}\right).
$$

The only phase linking the last and first magnetic-cell sites is

$$
H_{0,q-1}=-t_xe^{-iqak_x},
\qquad
H_{q-1,0}=-t_xe^{+iqak_x}.
$$

## 4. Berry, Chern, and Hall-response conventions

For periodic Bloch eigenstates `|u_n(k)>`, we use

$$
A_{n,\mu}(\mathbf{k})=i\langle u_n|\partial_{k_\mu}u_n\rangle,
\qquad
\Omega_n=\partial_{k_x}A_{n,y}-\partial_{k_y}A_{n,x},
$$

and

$$
C_n=\frac{1}{2\pi}\int_{\mathrm{MBZ}}\Omega_n(\mathbf{k})\,d^2k.
$$

Under this connection convention, the FHS implementation evaluates the discrete plaquette flux
with the **negative** principal phase of the oriented overlap product,

$$
\widetilde F_{12}(\mathbf{k})=-\operatorname{Arg}\!\left[
U_x(\mathbf{k})U_y(\mathbf{k}+\hat x)
U_x^{-1}(\mathbf{k}+\hat y)U_y^{-1}(\mathbf{k})
\right].
$$

This negative sign is required because the overlap
`<u(k)|u(k+dk)>` carries the phase `-A . dk` under the stated Berry-connection convention.
FHS returns a **plaquette flux**; the compatible density is

$$
\Omega_{\mathrm{FHS}}=\frac{\widetilde F_{12}}{\Delta k_x\Delta k_y}.
$$

The independent Stage-2 interband-Kubo density is

$$
\Omega_n(\mathbf{k})=-2\operatorname{Im}\sum_{m\ne n}
\frac{\langle n|\partial_{k_x}H|m\rangle
\langle m|\partial_{k_y}H|n\rangle}
{[E_m(\mathbf{k})-E_n(\mathbf{k})]^2}.
$$

For `phi=1/3`, the expected lower-to-upper band sequence is

$$
(C_1,C_2,C_3)=(-1,2,-1),
\qquad \sum_n C_n=0.
$$

With `q_e=-e` and `e>0`, the Hall-conductivity convention is

$$
\sigma_{xy}=-\frac{e^2}{h}\sum_{n\in\mathrm{occ}}C_n.
$$

## 5. Stage-1 and Stage-2 acceptance checklist

- [x] One parent Peierls Hamiltonian is documented and implemented.
- [x] Bloch, ribbon, and open geometries derive from that parent convention.
- [x] Hermiticity is checked on every constructed Hamiltonian.
- [x] The site-index convention supports rectangular lattices.
- [x] Analytic Bloch derivatives are implemented and tested against finite differences.
- [x] FHS links, plaquette fluxes, and Chern numbers are implemented with the frozen orientation.
- [x] Interband-Kubo curvature is implemented independently from FHS.
- [x] FHS/Kubo comparison uses compatible curvature densities on matching plaquettes.
- [x] Direct-gap, gauge-invariance, Chern-sum, and mesh-refinement checks are automated.
- [ ] Edge localization and real-space dynamics are deferred to later stages.
