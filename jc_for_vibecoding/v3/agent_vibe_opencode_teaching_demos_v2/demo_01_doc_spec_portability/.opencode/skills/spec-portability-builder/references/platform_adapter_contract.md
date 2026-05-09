# Platform Adapter Contract

Each target implementation must:

- expose a single `calculate(order)` or equivalent entry point;
- accept JSON-compatible input;
- return fields defined by the output contract;
- avoid hidden global state;
- be validated against the same golden cases.
