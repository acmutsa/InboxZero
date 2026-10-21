import Link from 'next/link';

export default function SiteFooter({ profile = false }: { profile?: boolean }) {
  const links = profile
    ? ['Profile', 'Accounts', 'Analytics']
    : ['Home', 'About', 'Services'];
  return (
    <footer className="site-footer">
      <nav aria-label="Footer navigation">
        <strong>Explore</strong>
        {links.map((label) => (
          <a key={label} href={`#${label.toLowerCase()}`}>
            {label}
          </a>
        ))}
      </nav>
      <Link href="/" className="footer-brand">
        Inbox Zero
      </Link>
    </footer>
  );
}
