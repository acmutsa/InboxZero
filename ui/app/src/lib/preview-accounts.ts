export type PreviewAccount = {
  provider: string;
  email: string;
  connected: boolean;
};

export const sampleAccounts: PreviewAccount[] = [
  { provider: 'Gmail', email: 'maya@studio.dev', connected: true },
  { provider: 'Outlook', email: 'maya@outlook.com', connected: true },
];
