---
name: regression-ready-package-fixes
description: Use when fixing bugs in a code package subject to API, testing, and changelog checks.
---
- Add type annotations to every parameter and return value of each public function touched or added.
- Write a dedicated regression test for each fixed bug; include at least three tests when the task requires that minimum.
- Record every fix under the changelog’s unreleased heading using the required bullet format.
- Run the full test suite and check the required files and annotations explicitly; passing existing tests alone does not verify these deliverables.
- Make targeted assertions match the intended output exactly, and investigate any failed assertion rather than reporting success based only on the test suite.
