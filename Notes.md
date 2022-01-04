# Notes

Potential speedups:
Remove sets from A*, only use queue? 
  No performance gains, only memory
Use custom copy instead of pickle 
  Debatable gains, pickle is really fast
Algorithm changes? (which?)
Add path invalidator
  We wouldn't have to recheck paths for 90% of cases, but the 10% of the cases
  are the optimal moves, so it's debabatable.
  Still solid gains since we have to check all of them anyways.
Cache AI?
  Easier said than done, making it non-spaghetti seems like a pain.

