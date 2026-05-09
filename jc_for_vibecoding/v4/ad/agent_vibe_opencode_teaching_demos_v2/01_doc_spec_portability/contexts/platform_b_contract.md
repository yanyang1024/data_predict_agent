# 平台 B 契约

目标平台 B 是一个 Node.js 服务模块。生成代码必须满足：

1. 文件名：`rule_engine.js`。
2. 导出：`module.exports = { classify }`。
3. 函数签名：`classify(ticket)`。
4. 不允许访问网络、文件系统、数据库。
5. 不允许引入第三方 npm 包。
6. 必须对缺失字段做默认值处理。
7. 测试文件使用 Node.js 内置 `assert`。

## 验证方式

```bash
node output/platform_b/rule_engine.test.js
```
