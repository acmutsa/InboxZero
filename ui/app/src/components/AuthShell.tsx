import FloatingNavbar from '@/components/FloatingNavbar';
import type { ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import authStyles from '@/components/AuthShell.module.css';

export default function AuthShell({
  children,
  registration = false,
  showHeader = true,
  brandOnly = true,
  className = '',
}: {
  children: ReactNode;
  registration?: boolean;
  showHeader?: boolean;
  brandOnly?: boolean;
  className?: string;
}) {
  return (
    <main className={`gradient-page ${authStyles['auth-page']} ${className}`}>
      {showHeader && (
        <FloatingNavbar sectionPath="/" brandOnly={brandOnly} />
      )}
      <Card className={`${authStyles['auth-card']}${registration ? ` ${authStyles['registration-card']}` : ""}`}>
        {children}
      </Card>
    </main>
  );
}
