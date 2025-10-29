# How to Clear Browser Cache

The question count now shows **0** from the API, but your browser is showing the old cached value.

## Quick Fix:

### On Mac:
**Press:** `Cmd + Shift + R`

### On Windows/Linux:
**Press:** `Ctrl + Shift + R`

### Or manually clear cache:
1. Open Developer Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

## What Was Fixed:
- The question count now reflects actual stored Q&A pairs in the database (not a cumulative counter)
- Default Project should show **0 questions** (no Q&A stored yet)
- Tech Venture AI project should show **0 questions** (reset from 172)

After the hard refresh, the count should be correct!

