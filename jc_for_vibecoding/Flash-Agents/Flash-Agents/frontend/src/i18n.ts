import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

void i18n.use(initReactI18next).init({
  lng: localStorage.getItem('flash.lang') || 'zh-CN',
  fallbackLng: 'zh-CN',
  interpolation: { escapeValue: false },
  resources: {
    'zh-CN': {
      translation: {
        appName: 'Flash-Agents',
        login: '登录',
        logout: '退出',
        send: '发送',
        placeholder: '输入任务，让 Agent 在隔离工作区执行...',
        skills: '技能',
        admin: '管理',
        chat: '对话'
      }
    },
    en: {
      translation: {
        appName: 'Flash-Agents',
        login: 'Login',
        logout: 'Logout',
        send: 'Send',
        placeholder: 'Ask an agent to work in an isolated workspace...',
        skills: 'Skills',
        admin: 'Admin',
        chat: 'Chat'
      }
    }
  }
});

export default i18n;
