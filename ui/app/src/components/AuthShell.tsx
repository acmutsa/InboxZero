import Link from 'next/link';
import type { ReactNode } from 'react';
import { Card } from '@/components/ui/card';

export default function AuthShell({
  children,
  registration = false,
}: {
  children: ReactNode;
  registration?: boolean;
}) {
  return (
    <main className="gradient-page auth-page">
      <header className="simple-header">
        <Link href="/">Inbox Zero</Link>
      </header>
      <Card className={`auth-card${registration ? ' registration-card' : ''}`}>
        {children}
      </Card>
    </main>
  );
}
