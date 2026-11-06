/** Shared sample content for the static landing preview and profile workspace. */
export const previewMessages = [
  {
    id: 'alex',
    sender: 'Alex Morgan',
    email: 'alex@studio.dev',
    subject: 'Project update',
    body: 'Could you share the latest update before our check-in?',
    reply: 'Hi Alex, I’ll share the latest update before our check-in.',
    provider: 'Gmail',
    status: 'Draft ready · 9:42 AM',
  },
  {
    id: 'studio',
    sender: 'Studio team',
    email: 'team@studio.dev',
    subject: 'Friday catch-up',
    body: 'Are you free for a quick catch-up on Friday at 10 AM?',
    reply: 'Friday at 10 AM works for me. Looking forward to it.',
    provider: 'Gmail',
    status: 'Calendar checked · 9:15 AM',
  },
  {
    id: 'digest',
    sender: 'Weekly digest',
    email: 'digest@studio.dev',
    subject: 'This week’s highlights',
    body: 'A curated collection of product news and design ideas.',
    reply: '',
    provider: 'Outlook',
    status: 'Newsletter · Yesterday',
  },
  {
    id: 'jamie',
    sender: 'Jamie Park',
    email: 'jamie@studio.dev',
    subject: 'Design feedback',
    body: 'I’ve added my comments to the latest designs.',
    reply: 'Thanks, Jamie. I’ll review your comments and follow up.',
    provider: 'Outlook',
    status: 'Needs review · Yesterday',
  },
  {
    id: 'taylor',
    sender: 'Taylor Reed',
    email: 'taylor@studio.dev',
    subject: 'Next steps',
    body: 'Here is the summary from our meeting. Could you send the next steps?',
    reply: 'Thanks for the summary. I’ll send the next steps today.',
    provider: 'Outlook',
    status: 'Needs review · Yesterday',
  },
];
export type PreviewMessage = (typeof previewMessages)[number];

export const previewInbox = previewMessages.filter((message) => message.id !== 'taylor');
export const previewDrafts = previewMessages.filter((message) => message.reply);
export const previewUnreadIds = ['alex', 'studio', 'jamie'];

