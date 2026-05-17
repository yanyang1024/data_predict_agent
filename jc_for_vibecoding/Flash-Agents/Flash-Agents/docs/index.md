# 文档索引

Flash-Agents 的文档按读者角色组织。第一次接触项目时，建议先读 `README.md`，再根据职责进入对应文档。

## 面向开发者

- [开发者指南](./developer-guide.md)：模块说明、现阶段完成情况、二次开发入口、扩展 Agent/Skill/API/前端组件的方法。
- [架构说明](./architecture.md)：系统链路、数据模型、租户隔离、端口策略。
- [API 概览](./api.md)：后端 HTTP API 与 SSE 入口。
- [OpenCode 执行引擎契约](./opencode-contract.md)：平台和外部 OpenCode 实例之间的接口约定。
- [安全设计](./security.md)：路径防护、ZIP 防护、Token、systemd/bwrap 隔离边界。

## 面向运维

- [部署指南](./deployment.md)：依赖、后端、前端、MariaDB、systemd user service 部署步骤。
- [运维故障处理手册](./ops-runbook.md)：认证、数据库、SSE、OpenCode、systemd、bwrap、文件和技能等常见问题排查。

## 面向应用用户

- [用户使用教程](./user-guide.md)：登录、选择 Agent、发起任务、查看文件、上传技能、管理后台使用。

## 当前边界

项目当前是一个可运行的企业多 Agent 平台参考实现。主链路已经包括认证、多租户、会话、SSE、OpenCode 实例管理、工作区文件、技能和管理后台；生产化仍建议补充数据库迁移体系、实例状态持久化、正式监控告警和完整端到端测试。
