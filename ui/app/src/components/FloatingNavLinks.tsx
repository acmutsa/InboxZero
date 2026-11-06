'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import navigationStyles from '@/components/FloatingNavbar.module.css';

export default function FloatingNavLinks({
  tabs,
  sectionPath = '',
}: {
  tabs: readonly string[];
  sectionPath?: string;
}) {
  const [active, setActive] = useState(tabs[0].toLowerCase());
  const activeRef = useRef(active);
  const linksRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sectionPath) return;
    let frame = 0;
    const update = () => {
      frame = 0;
      const sections = tabs.map((tab) =>
        document.getElementById(tab.toLowerCase()),
      );
      const navigationBottom = linksRef.current
        ?.closest('nav')?.getBoundingClientRect().bottom ?? 80;
      let current = sections
        .filter(
          (section) =>
            section &&
            section.getBoundingClientRect().top <= Math.max(
              navigationBottom + 24,
              window.innerHeight * 0.25,
              parseFloat(getComputedStyle(section).scrollMarginTop) || 0,
            ) + 2,
        )
        .at(-1);
      // A short final section can reach the end of the page before its
      // heading reaches the navbar's activation line.
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      const lastSection = sections.filter((section) => section !== null).at(-1);
      if (maxScroll > 0 && window.scrollY >= maxScroll - 2 && lastSection) {
        const bounds = lastSection.getBoundingClientRect();
        if (bounds.top < window.innerHeight && bounds.bottom > navigationBottom) {
          current = lastSection;
        }
      }
      if (current && current.id !== activeRef.current) {
        activeRef.current = current.id;
        setActive(current.id);
      }
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    window.addEventListener('hashchange', onScroll);
    const observer = new ResizeObserver(onScroll);
    observer.observe(document.body);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      window.removeEventListener('hashchange', onScroll);
      observer.disconnect();
    };
  }, [tabs, sectionPath]);

  return (
    <div ref={linksRef} className={navigationStyles['nav-tabs']} style={{ gridTemplateColumns: `repeat(${tabs.length}, minmax(0, 1fr))` }}>
      {tabs.map((tab) => (
        <Link
          key={tab}
          href={`${sectionPath}#${tab.toLowerCase()}`}
          aria-current={!sectionPath && active === tab.toLowerCase() ? 'location' : undefined}
        >
          {tab}
        </Link>
      ))}
    </div>
  );
}
