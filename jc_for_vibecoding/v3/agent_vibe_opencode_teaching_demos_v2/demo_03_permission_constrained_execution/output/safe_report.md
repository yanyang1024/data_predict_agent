# Safe Query Report

## Manifest

- dataset: training_metrics
- source: approved safe export
- fields: ['date', 'step', 'value', 'owner', 'status']
- window_days: 14
- row_count: 14
- direct_protected_data_access: False
- policy_file: configs/policy.json

## Summary

- Rows: 14
- Average value: 91.21
- Status counts: {'ok': 9, 'watch': 5}

## Safety Note

This report was generated from an approved safe export. It did not read protected_data and it does not modify configuration.