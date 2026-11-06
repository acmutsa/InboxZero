'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';
import { ArrowUpRight } from 'lucide-react';
import FloatingNavLinks from '@/components/FloatingNavLinks';
import navigationStyles from '@/components/FloatingNavbar.module.css';

const landingTabs = ['Home', 'About', 'Services'];

export default function FloatingNavbar({
  tabs = landingTabs,
  action,
  label = 'Main navigation',
  sectionPath = '',
  brandOnly = false,
}: {
  tabs?: readonly string[];
  action?: ReactNode;
  label?: string;
  sectionPath?: string;
  brandOnly?: boolean;
}) {
  const brand = (
    <Link href="/" className={navigationStyles['nav-brand']} aria-label="Inbox Zero home">
      <span>Inbox Zero</span>
    </Link>
  );

  return (
    <header className={navigationStyles['nav-header']} data-brand-only={brandOnly}>
      {brandOnly && brand}
      {!brandOnly && <nav className={navigationStyles['floating-nav']} aria-label={label}>
      {brand}
      <FloatingNavLinks tabs={tabs} sectionPath={sectionPath} />
      <div className={navigationStyles['nav-actions']}>{action ?? (
        <Link href="/auth/sign-up" className={navigationStyles['nav-cta']}>
            <span>Get started</span>
            <ArrowUpRight aria-hidden="true" />
        </Link>
      )}</div>
      </nav>}
    </header>
  );
}
