import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import { AuthProvider } from './AuthContext';
import { AgentProvider } from './AgentContext';
import { ToastProvider } from './ToastContext';

function ThemeProvider({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen bg-slate-50 text-slate-950">{children}</div>;
}

function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      <ErrorBoundary>
        <ThemeProvider>
          <ToastProvider>
            <AuthProvider>
              <AgentProvider>
                <WorkspaceProvider>{children}</WorkspaceProvider>
              </AgentProvider>
            </AuthProvider>
          </ToastProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </I18nextProvider>
  );
}
