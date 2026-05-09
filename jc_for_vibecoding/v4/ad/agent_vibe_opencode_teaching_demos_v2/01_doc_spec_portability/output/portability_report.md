# 可移植性报告

## 自动生成内容

- rule_engine.js
- rule_engine.test.js

## 自动验证范围

- JavaScript 语法由 Node.js 执行验证。
- 样例测试验证当前规则表的 happy path 和少量边界。

## 人工确认点

- severity 大小写归一化是否符合业务预期
- 多规则命中时采用第一条是否正确
- age_hours 缺失时按 0 处理是否正确
