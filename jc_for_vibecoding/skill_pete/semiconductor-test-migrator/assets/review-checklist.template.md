# Migration Review Checklist

## Coverage and whitelist

- [ ] Required whitelist loaded and normalized.
- [ ] Every whitelisted test item has an owning function or implementation path.
- [ ] Support symbols for whitelist items are marked keep.

## Deletion safety

- [ ] Each deletion candidate has reverse-call evidence.
- [ ] Shared helpers are kept or explicitly reviewed.
- [ ] Classes, callbacks, exported APIs, macros, and generated files are reviewed before deletion.
- [ ] Build or static checks pass after each deletion batch.

## Tester-platform migration

- [ ] Source tester idioms are mapped to target tester-language patterns.
- [ ] Setup/measure/bin/datalog/cleanup behavior is preserved.
- [ ] Hardware resource and multisite assumptions are reviewed.

## Product parameters

- [ ] Product parameter source of truth is recorded.
- [ ] Old/new values, units, precision, bins, and datalog names are logged.
- [ ] Limit or bin changes have engineering approval.

## Final readiness

- [ ] Before and after manifests or commits are recorded.
- [ ] Change log is complete.
- [ ] Review blockers are resolved or waived.
- [ ] Release readiness summary is complete.
