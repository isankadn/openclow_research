# Active-Day Construct Robustness V1

## Scope
- Mathematics regular exams.
- Adjusted 3-month student-course + assessment fixed-effect model.
- Alternative active-day definitions are computed from same-course daily xAPI aggregates in the same complete-calendar-month window.

## Results
- any_event_day: beta=+0.080, CI [+0.039, +0.122], p=0.000, rows=10,968.
- two_plus_event_day: beta=+0.077, CI [+0.036, +0.118], p=0.000, rows=10,968.
- three_plus_event_day: beta=+0.085, CI [+0.044, +0.125], p=0.000, rows=10,968.
- meaningful_non_open_close_day: beta=+0.078, CI [+0.038, +0.119], p=0.000, rows=10,968.

## Interpretation
- The active-days result remains positive when an active day requires at least two events, at least three events, or at least one non-open/close event.
