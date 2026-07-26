# PROJECT.md — Guidelines de Développement TailScale — Optimisation Karpathy
Bias: caution over speed on non-trivial work. Use judgment on trivial tasks.

## 1. Think Before Coding
- Don't assume. Don't hide confusion. Surface tradeoffs.
- Before implementing: State your assumptions explicitly.
- If uncertain, ask. If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First
- Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked. No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes
- Touch only what you must. Clean up only your own mess.
- When editing existing code: Don't "improve" adjacent code, comments, or formatting. Don't refactor things that aren't broken. Match existing style.
- Remove imports/variables/functions that YOUR changes made unused. Don't remove pre-existing dead code unless asked.

## 4. Goal-Driven Execution
- Transform vague tasks into verifiable goals.
- Write a test that reproduces a bug before fixing it, then make it pass. Ensure tests pass before and after refactoring.
