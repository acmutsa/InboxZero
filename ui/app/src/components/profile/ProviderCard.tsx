'use client';
import { Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import providerStyles from '@/components/profile/ProviderCard.module.css';

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
      className={`${providerStyles['provider-card']} glass-surface`}
      data-tone={provider === 'Gmail' ? 'blue' : 'violet'}
      data-connected={connected}
    >
      <div className={providerStyles['provider-identity']}>
        <span className={providerStyles['provider-icon']} aria-hidden="true"><Mail /></span>
        <div>
          <div className={providerStyles['provider-title']}>
            <h3>{provider}</h3>
            <Badge
              variant="outline"
              className={providerStyles['provider-status']}
              data-connected={connected}
              aria-live="polite"
            >
              <span aria-hidden="true">{connected ? '●' : '○'}</span>
              {connected ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
          <p title={email}>{email}</p>
        </div>
      </div>
      <Button
        variant="ghost"
        onClick={() => onConnectedChange(!connected)}
        aria-label={`${connected ? 'Disconnect' : 'Connect'} ${email}`}
      >
        {connected ? 'Disconnect' : 'Connect'}
      </Button>
    </Card>
  );
}
