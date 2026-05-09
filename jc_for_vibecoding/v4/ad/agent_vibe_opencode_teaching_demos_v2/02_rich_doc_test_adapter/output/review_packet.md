# Review Packet

## 自动生成说明

以下代码通过文档抽取和环境包适配生成。语法可自动检查，验证逻辑必须人工确认。

## 人工确认点

- RESET_STABILITY: ready 拉高的精确周期需要 owner 确认
- WRITE_READ_BACK: 地址 0x10 是否适用于所有配置需要确认
- JITTER_TOLERANCE: 50 ppm 阈值来自示例，不代表最终规格

## 自动验证不覆盖
- 时序逻辑是否符合真实设计。
- 阈值是否来自正式规范。
- 环境包 API 的语义是否与旧指令完全一致。
