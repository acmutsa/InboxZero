'use client';

import { useEffect, useRef, useState } from 'react';

export default function FloatingNavLinks({
  tabs,
}: {
  tabs: readonly string[];
}) {
  const [active, setActive] = useState(tabs[0].toLowerCase());
  const activeRef = useRef(active);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      const sections = tabs.map((tab) =>
        document.getElementById(tab.toLowerCase()),
      );
      const current = sections
        .filter(
          (section) =>
            section &&
            section.getBoundingClientRect().top <= window.innerHeight * 0.35,
        )
        .at(-1);
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
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    };
  }, [tabs]);

  return (
    <div className="nav-tabs">
      <span
        className="nav-highlight"
        style={{
          width: `${100 / tabs.length}%`,
          transform: `translateX(${
            Math.max(
              0,
              tabs.findIndex((tab) => tab.toLowerCase() === active),
            ) * 100
          }%)`,
        }}
        aria-hidden="true"
      />
      {tabs.map((tab) => (
        <a
          key={tab}
          href={`#${tab.toLowerCase()}`}
          aria-current={active === tab.toLowerCase() ? 'location' : undefined}
        >
          {tab}
        </a>
      ))}
    </div>
  );
}
