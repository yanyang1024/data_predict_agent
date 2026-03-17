# HiagentWebSDK 嵌入指南

本文档详细介绍如何在 Web 应用中嵌入和使用 `HiagentWebSDK` 智能客服组件。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [详细嵌入流程](#详细嵌入流程)
3. [配置参数说明](#配置参数说明)
4. [高级用法](#高级用法)
5. [常见问题](#常见问题)
6. [示例项目说明](#示例项目说明)

---

## 🚀 快速开始

### 最简单的嵌入方式

将以下代码复制到您网页的 `</body>` 标签之前：

```html
<!-- 1. 引入 SDK 脚本 -->
<script src="http://hostip:port/resources/product/llm/public/sdk/embedLite.js"></script>

<!-- 2. 初始化 SDK -->
<script>
  new HiagentWebSDK.WebLiteClient({
    appKey: "your_appkey",
    baseUrl: "your_app_url"
  });
</script>
```

> **注意**：将 `hostip:port`、`your_appkey` 和 `your_app_url` 替换为实际的值。

---

## 📖 详细嵌入流程

### 步骤 1：获取 SDK 配置信息

在嵌入 SDK 之前，您需要从 Hiagent 控制台获取以下信息：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `SDK URL` | SDK 脚本的访问地址 | `http://192.168.1.100:8080/resources/product/llm/public/sdk/embedLite.js` |
| `appKey` | 应用唯一标识 | `ak_1234567890abcdef` |
| `baseUrl` | 服务基础地址 | `https://your-domain.hiagent.com` |

**获取方式**：
1. 登录 Hiagent 控制台
2. 进入「应用管理」页面
3. 创建或选择已有应用
4. 在「接入配置」中查看 SDK 配置信息

### 步骤 2：在 HTML 中引入 SDK

#### 方式一：直接嵌入（推荐）

在您的 HTML 文件底部（`</body>` 标签之前）添加以下代码：

```html
<body>
  <!-- 您的页面内容 -->
  
  <!-- SDK 脚本放在这里 -->
  <script src="http://hostip:port/resources/product/llm/public/sdk/embedLite.js"></script>
  <script>
    new HiagentWebSDK.WebLiteClient({
      appKey: "your_appkey",
      baseUrl: "your_app_url"
    });
  </script>
</body>
```

#### 方式二：模块化引入（现代前端框架）

如果您使用 React、Vue、Angular 等现代前端框架：

**React 示例：**
```jsx
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // 动态加载 SDK 脚本
    const script = document.createElement('script');
    script.src = 'http://hostip:port/resources/product/llm/public/sdk/embedLite.js';
    script.onload = () => {
      // SDK 加载完成后初始化
      new window.HiagentWebSDK.WebLiteClient({
        appKey: "your_appkey",
        baseUrl: "your_app_url"
      });
    };
    document.body.appendChild(script);
    
    return () => {
      // 清理
      document.body.removeChild(script);
    };
  }, []);

  return <div>您的应用内容</div>;
}

export default App;
```

**Vue 3 示例：**
```vue
<template>
  <div>您的应用内容</div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

onMounted(() => {
  // 检查 SDK 是否已加载
  if (!window.HiagentWebSDK) {
    const script = document.createElement('script');
    script.src = 'http://hostip:port/resources/product/llm/public/sdk/embedLite.js';
    script.onload = initSDK;
    document.body.appendChild(script);
  } else {
    initSDK();
  }
});

const initSDK = () => {
  new window.HiagentWebSDK.WebLiteClient({
    appKey: "your_appkey",
    baseUrl: "your_app_url"
  });
};
</script>
```

### 步骤 3：验证集成是否成功

1. 打开浏览器开发者工具（F12）
2. 查看 Console 面板，确认没有报错信息
3. 在页面上应该能看到智能客服的入口按钮（通常是右下角的一个悬浮按钮）
4. 点击按钮，测试是否能正常打开对话窗口

---

## ⚙️ 配置参数说明

### 基础配置

```javascript
{
  appKey: "your_appkey",      // 必填：应用唯一标识
  baseUrl: "your_app_url"     // 必填：服务基础地址
}
```

### 高级配置（可选）

```javascript
{
  // 基础配置
  appKey: "your_appkey",
  baseUrl: "your_app_url",
  
  // 界面配置
  position: "right",          // 按钮位置："right" | "left"
  theme: "light",             // 主题："light" | "dark"
  language: "zh-CN",          // 语言："zh-CN" | "en-US"
  
  // 功能配置
  autoOpen: false,            // 是否自动打开对话窗口
  showAvatar: true,           // 是否显示机器人头像
  welcomeMessage: "您好，有什么可以帮助您？",  // 欢迎语
  
  // 用户配置
  userId: "user_123",         // 当前用户ID（用于识别用户）
  userName: "张三",           // 用户昵称
  userInfo: {                 // 扩展用户信息
    phone: "13800138000",
    email: "user@example.com"
  },
  
  // 回调函数
  onReady: function() {       // SDK 加载完成回调
    console.log('SDK 已就绪');
  },
  onOpen: function() {        // 对话窗口打开回调
    console.log('对话窗口已打开');
  },
  onClose: function() {       // 对话窗口关闭回调
    console.log('对话窗口已关闭');
  },
  onMessage: function(msg) {  // 收到消息回调
    console.log('收到消息:', msg);
  }
}
```

---

## 🔧 高级用法

### 1. 延迟加载 SDK（性能优化）

如果 SDK 对页面加载速度有影响，可以使用延迟加载：

```html
<script>
  // 页面加载完成后再加载 SDK
  window.addEventListener('load', function() {
    // 延迟 2 秒加载
    setTimeout(function() {
      var script = document.createElement('script');
      script.src = 'http://hostip:port/resources/product/llm/public/sdk/embedLite.js';
      script.onload = function() {
        new HiagentWebSDK.WebLiteClient({
          appKey: "your_appkey",
          baseUrl: "your_app_url"
        });
      };
      document.body.appendChild(script);
    }, 2000);
  });
</script>
```

### 2. 根据用户登录状态动态配置

```html
<script>
  // 假设您的应用有一个全局的 user 对象
  var currentUser = {
    id: "user_12345",
    name: "张三",
    isVip: true
  };
  
  new HiagentWebSDK.WebLiteClient({
    appKey: "your_appkey",
    baseUrl: "your_app_url",
    userId: currentUser.id,
    userName: currentUser.name,
    userInfo: {
      vip: currentUser.isVip,
      loginTime: new Date().toISOString()
    }
  });
</script>
```

### 3. 在单页应用（SPA）中处理路由切换

```javascript
// 监听路由变化，更新 SDK 上下文
window.addEventListener('popstate', function() {
  if (window.HiagentWebSDK && window.HiagentWebSDK.updateContext) {
    HiagentWebSDK.updateContext({
      currentPage: window.location.pathname,
      pageTitle: document.title
    });
  }
});
```

### 4. 自定义触发按钮

如果您想使用自己的按钮来触发客服窗口：

```html
<!-- 自定义按钮 -->
<button id="customChatBtn">联系客服</button>

<script>
  // 初始化 SDK，但隐藏默认按钮
  new HiagentWebSDK.WebLiteClient({
    appKey: "your_appkey",
    baseUrl: "your_app_url",
    hideDefaultButton: true  // 隐藏默认按钮
  });
  
  // 绑定自定义按钮
  document.getElementById('customChatBtn').addEventListener('click', function() {
    if (window.HiagentWebSDK && window.HiagentWebSDK.openChat) {
      HiagentWebSDK.openChat();
    }
  });
</script>
```

---

## ❓ 常见问题

### Q1: SDK 加载失败怎么办？

**可能原因和解决方法：**

1. **URL 错误**
   - 检查 `src` 地址是否正确
   - 确认 `hostip:port` 已替换为实际地址
   - 确保网络可以访问该地址

2. **跨域问题（CORS）**
   - 联系后端开发人员配置 CORS
   - 或在同源域名下部署 SDK

3. **网络问题**
   - 检查网络连接
   - 尝试使用 HTTPS 代替 HTTP

### Q2: 如何调试 SDK？

在初始化配置中添加 `debug: true`：

```javascript
new HiagentWebSDK.WebLiteClient({
  appKey: "your_appkey",
  baseUrl: "your_app_url",
  debug: true  // 开启调试模式
});
```

然后在浏览器开发者工具的 Console 面板查看详细的日志信息。

### Q3: SDK 支持哪些浏览器？

| 浏览器 | 最低版本 |
|--------|----------|
| Chrome | 60+ |
| Firefox | 60+ |
| Safari | 12+ |
| Edge | 79+ |
| IE | 不支持 |

### Q4: 如何更新 SDK？

SDK 更新通常有两种方式：

1. **自动更新**：如果 SDK URL 不变，只需刷新页面即可获取最新版本
2. **手动更新**：修改 URL 中的版本号（如果有）

### Q5: 移动端适配如何？

SDK 默认支持移动端适配，无需额外配置。如果需要针对移动端特殊处理：

```javascript
new HiagentWebSDK.WebLiteClient({
  appKey: "your_appkey",
  baseUrl: "your_app_url",
  // 移动端特定配置
  mobile: {
    fullScreen: true,      // 移动端全屏显示
    position: 'bottom'     // 移动端底部固定
  }
});
```

---

## 📁 示例项目说明

本示例项目包含以下文件：

```
webapp-example/
├── index.html      # 主页面，包含完整的 SDK 嵌入示例
└── README.md       # 本文档
```

### 运行示例项目

由于 SDK 需要特定的后端服务支持，本地直接打开 HTML 文件可能无法正常工作。建议：

1. 在本地启动一个 Web 服务器：
   ```bash
   # Python 3
   python -m http.server 8080
   
   # Node.js
   npx serve .
   ```

2. 在浏览器中访问 `http://localhost:8080`

3. 填写正确的 `appKey` 和 `baseUrl`

4. 点击「初始化 SDK」按钮

---

## 📞 技术支持

如有问题，请联系：

- **技术支持邮箱**：support@hiagent.com
- **官方文档**：https://docs.hiagent.com
- **控制台**：https://console.hiagent.com

---

## 📝 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2024-XX-XX | 1.0.0 | 初始版本 |
