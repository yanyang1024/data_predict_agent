# Demo 03 - 权限约束执行

## 教学目标

展示重要数据和配置不能让 Agent 直接读取或修改。正确做法是用封装好的脚本和参数约束 Agent 的执行空间。

```text
User request
  -> OpenCode permission boundary
  -> approved_query.py with whitelist and row/window limits
  -> safe exported data + manifest
  -> render_safe_report.py
  -> optional proposal patch, not direct config edit
```

## 运行

安全查询：

```bash
python3 scripts/approved_query.py \
  --dataset training_metrics \
  --window-days 14 \
  --fields date,step,value,owner \
  --output output/query_result.csv \
  --manifest output/query_manifest.json

python3 scripts/render_safe_report.py \
  --input output/query_result.csv \
  --manifest output/query_manifest.json \
  --output output/safe_report.md
```

安全配置变更建议：

```bash
python3 scripts/propose_config_change.py \
  --parameter row_limit \
  --value 200 \
  --reason "teaching demo wants a larger sample" \
  --output output/config_change_proposal.json
```

权限测试：

```bash
python3 tests/test_permission_boundary.py
```

## 讲师提示

重点讲：

- 不要让 Agent 直接读 `protected_data/`；
- 不要让 Agent 直接改生产配置；
- 给 Agent 的不是数据库权限，而是 approved CLI；
- manifest 记录了实际查询范围和字段；
- 配置修改只能生成 proposal，不能直接写回。
