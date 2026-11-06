import type { ReactNode } from 'react';
import AuthShell from '@/components/AuthShell';
import styles from './AuthPage.module.css';

export default function AuthPage({ children, brandOnly = true }: { children: ReactNode; brandOnly?: boolean }) {
  return (
    <div className={styles.page}>
      <AuthShell className={styles.content} brandOnly={brandOnly}>
        {children}
      </AuthShell>
    </div>
  );
}
