# Window Robustness Modeling V1

## Scope
- Same strong candidate cells and assessment fixed-effect design as modeling V1.
- Repeats the global multivariable model for 3-, 6-, and 12-month pre-test xAPI windows.
- This first pass uses the all-strong-cells model; family-specific robustness should be run after this global pattern is reviewed.

## Main Strong-Cell Model Across Windows
### m3
- log_events: beta=+0.059, CI [+0.000, +0.133], p_boot=0.067, xapi_rate=76.8%
- log_active_days: beta=+0.083, CI [+0.031, +0.140], p_boot=0.000, xapi_rate=76.8%
- navigation_rate: beta=-0.113, CI [-0.171, -0.082], p_boot=0.000, xapi_rate=76.8%
- memo_rate: beta=-0.016, CI [-0.058, +0.016], p_boot=0.200, xapi_rate=76.8%
- marker_rate: beta=-0.003, CI [-0.021, +0.017], p_boot=0.733, xapi_rate=76.8%
- content_session_rate: beta=-0.025, CI [-0.037, -0.006], p_boot=0.000, xapi_rate=76.8%

### m6
- log_events: beta=+0.076, CI [+0.025, +0.137], p_boot=0.000, xapi_rate=79.8%
- log_active_days: beta=+0.068, CI [+0.022, +0.112], p_boot=0.033, xapi_rate=79.8%
- navigation_rate: beta=-0.117, CI [-0.148, -0.076], p_boot=0.000, xapi_rate=79.8%
- memo_rate: beta=-0.027, CI [-0.063, +0.007], p_boot=0.233, xapi_rate=79.8%
- marker_rate: beta=-0.014, CI [-0.034, +0.010], p_boot=0.267, xapi_rate=79.8%
- content_session_rate: beta=-0.026, CI [-0.049, -0.007], p_boot=0.000, xapi_rate=79.8%

### m12
- log_events: beta=+0.093, CI [+0.031, +0.141], p_boot=0.000, xapi_rate=81.1%
- log_active_days: beta=+0.053, CI [+0.010, +0.109], p_boot=0.033, xapi_rate=81.1%
- navigation_rate: beta=-0.124, CI [-0.154, -0.076], p_boot=0.000, xapi_rate=81.1%
- memo_rate: beta=-0.036, CI [-0.071, +0.007], p_boot=0.067, xapi_rate=81.1%
- marker_rate: beta=-0.017, CI [-0.036, +0.004], p_boot=0.100, xapi_rate=81.1%
- content_session_rate: beta=-0.023, CI [-0.042, -0.006], p_boot=0.000, xapi_rate=81.1%

## Interpretation
- A result is more credible if sign and magnitude are stable across windows, not only significant in one arbitrary window.
- Active-days stability would support a distributed-engagement interpretation.
- If raw event volume weakens while active days remains positive, the paper should frame behavior quality/regularity rather than click quantity.
