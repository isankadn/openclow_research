# Review-Requested Diagnostics V1

## Scope
- Mathematics regular exams.
- 3-month pre-assessment window.
- Student-course and assessment fixed effects.
- Student-clustered standard errors.

## Results
- any_activity_plus_active_days / any_activity: beta=-0.085, CI [-0.154, -0.017], p=0.015, rows=10,968.
- any_activity_plus_active_days / log_active_days_given_activity: beta=+0.044, CI [+0.013, +0.075], p=0.006, rows=10,968.
- log_event_intensity_reparameterized / log_active_days: beta=+0.049, CI [+0.018, +0.081], p=0.002, rows=10,968.
- log_event_intensity_reparameterized / log_event_intensity: beta=-0.062, CI [-0.102, -0.022], p=0.002, rows=10,968.
- active_rows_event_intensity / log_active_days: beta=+0.036, CI [+0.009, +0.063], p=0.010, rows=8,904.
- active_rows_event_intensity / log_events_per_active_day: beta=-0.028, CI [-0.062, +0.006], p=0.104, rows=8,904.

## Interpretation
- The any-activity split checks whether the active-days signal is only an access/no-access contrast.
- The event-intensity models check whether concentrated activity remains negative after regularity is separated from event volume.
