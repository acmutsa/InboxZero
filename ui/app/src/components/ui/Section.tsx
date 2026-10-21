import type { ReactNode } from 'react';
export function Section({
  id,
  eyebrow,
  title,
  description,
  children,
  className = '',
}: {
  id: string;
  eyebrow?: string;
  title: string;
  description?: string;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <section
      id={id}
      className={`section ${className}`}
      aria-labelledby={`${id}-heading`}
    >
      <div className="section-inner">
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2 id={`${id}-heading`}>{title}</h2>
        {description && <p className="section-description">{description}</p>}
        {children}
      </div>
    </section>
  );
}
