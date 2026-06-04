# Etch Mechanism Assumptions

## 1. Scope
This document defines first-version qualitative assumptions for Etch mechanism reasoning before the real simulator is integrated.

## 2. Supported Reasoning
The mechanism agent may reason about:
- plasma power impact,
- pressure impact,
- gas flow ratio impact,
- bias-related ion energy impact,
- selectivity and profile tendency,
- CD bias risk,
- microloading or pattern dependency hypothesis.

## 3. Unsupported Reasoning
The mechanism agent must not:
- generate fabricated simulation values,
- claim exact CD or etch rate prediction,
- claim validated process windows without data,
- override experimental or historical data results.

## 4. Output Confidence
Every conclusion should be labeled as:
- HIGH: supported by known mechanism and user-provided data,
- MEDIUM: mechanism-plausible but not experimentally verified,
- LOW: hypothesis only.
