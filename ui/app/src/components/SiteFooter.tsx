import Link from 'next/link';
import footerStyles from '@/components/SiteFooter.module.css';

export default function SiteFooter({
  profile = false,
  sectionPath = '',
  showNavigation = true,
}: {
  profile?: boolean;
  sectionPath?: string;
  showNavigation?: boolean;
}) {
  const links = profile
    ? ['Profile', 'Accounts', 'Analytics']
    : ['Home', 'About', 'Services'];
  return (
    <footer className={footerStyles['site-footer']}>
      {showNavigation && (
        <nav aria-label="Footer navigation">
          <strong>Explore</strong>
          {links.map((label) => (
            <a key={label} href={`${sectionPath}#${label.toLowerCase()}`}>
              {label}
            </a>
          ))}
        </nav>
      )}
      <Link href="/" className={footerStyles['footer-brand']}>
        Inbox Zero
      </Link>
    </footer>
  );
}
