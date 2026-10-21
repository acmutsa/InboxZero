'use client';
import GlassIcon from '@/components/GlassIcon';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function ProviderCard({
  provider,
  email,
  connected,
  onConnectedChange,
}: {
  provider: string;
  email: string;
  connected: boolean;
  onConnectedChange: (connected: boolean) => void;
}) {
  return (
    <Card
      className="provider-card glass-surface"
      data-tone={provider === 'Gmail' ? 'blue' : 'violet'}
    >
      <div className="provider-identity">
        <GlassIcon
          name="mail"
          tone={provider === 'Gmail' ? 'blue' : 'violet'}
        />
        <div>
          <h3>{provider}</h3>
          <p>{email}</p>
          <Badge
            variant="outline"
            className="provider-status"
            data-connected={connected}
            aria-live="polite"
          >
            <span aria-hidden="true">{connected ? '●' : '○'}</span>
            {connected ? 'Connected · Active' : 'Disconnected'}
          </Badge>
        </div>
      </div>
      <Button
        variant={connected ? 'outline' : 'default'}
        onClick={() => onConnectedChange(!connected)}
        aria-label={`${connected ? 'Disconnect' : 'Connect'} ${email}`}
      >
        {connected ? 'Disconnect' : 'Connect'}
      </Button>
    </Card>
  );
}
