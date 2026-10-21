'use client';

import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FloatingNavLinks from '@/components/FloatingNavLinks';

const landingTabs = ['Home', 'About', 'Services'];

export default function FloatingNavbar() {
  return (
    <nav className="floating-nav" aria-label="Main navigation">
      <FloatingNavLinks tabs={landingTabs} />
      <Button asChild className="nav-cta">
        <Link href="/auth/sign-up">
          <span>Get started</span>
          <ArrowUpRight aria-hidden="true" />
        </Link>
      </Button>
    </nav>
  );
}
