# Mechanism Agent Known Limitations

## Current Status (Phase 0)
- No real simulator is connected.
- All mechanism output is qualitative and hypothesis-based.
- No numerical prediction (etch rate, CD, profile) can be generated.
- No validated process window boundaries from simulation.

## What to Expect
- The mechanism agent provides directional reasoning only.
- All conclusions should be treated as hypotheses requiring experimental or data validation.
- When the real simulator is connected, the following tools will replace the mock:
  - `etch-simulator-run`
  - `etch-simulator-status`
  - `etch-simulator-result`
  - `etch-simulator-explain`

## Risk
- Treating mechanism hypotheses as validated conclusions is the most dangerous failure mode.
- The integration agent should never give Level A or B solely based on mechanism reasoning.
- Cross-check with historical data or DOE before committing to mechanism-based suggestions.
