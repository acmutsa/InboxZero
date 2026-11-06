'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import styles from './EmailCharts.module.css';

function ChartPlaceholder() {
  return (
    <>
      <div className={styles['chart-card']} aria-hidden="true" />
      <div className={styles['draft-analysis']} aria-hidden="true" />
    </>
  );
}

const EmailCharts = dynamic(() => import('./EmailCharts'), {
  loading: ChartPlaceholder,
});

export default function ActivityCharts() {
  const ref = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setReady(true);
        observer.disconnect();
      }
    }, { rootMargin: '200px' });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={styles.charts}>
      {ready ? <EmailCharts /> : <ChartPlaceholder />}
    </div>
  );
}
