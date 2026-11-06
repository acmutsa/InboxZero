import type { ReactNode } from 'react';
import sectionStyles from './Section.module.css';

export function Section({
  id,
  title,
  description,
  children,
  className = '',
}: {
  id: string;
  title: string;
  description?: string;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <section
      id={id}
      className={`${sectionStyles['section']} ${className}`}
      aria-labelledby={`${id}-heading`}
    >
      <div className={sectionStyles['section-inner']}>
        <h2 id={`${id}-heading`}>{title}</h2>
        {description && <p className={sectionStyles['section-description']}>{description}</p>}
        {children}
      </div>
    </section>
  );
}
