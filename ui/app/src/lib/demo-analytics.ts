/** Fixed preview data; shared by charts and summary cards. */
export const emailCategories = [
  { category: 'Important', gmail: 128, outlook: 92 },
  { category: 'Newsletter', gmail: 84, outlook: 58 },
  { category: 'Receipt', gmail: 46, outlook: 34 },
  { category: 'Scheduling', gmail: 32, outlook: 28 },
  { category: 'Notification', gmail: 70, outlook: 46 },
  { category: 'Spam', gmail: 20, outlook: 12 },
];
export const gmailTotal = emailCategories.reduce(
  (sum, row) => sum + row.gmail,
  0,
);
export const outlookTotal = emailCategories.reduce(
  (sum, row) => sum + row.outlook,
  0,
);
export const emailTotal = gmailTotal + outlookTotal;
export const draftCounts = { gmail: 106, outlook: 76 };
export const draftTotal = draftCounts.gmail + draftCounts.outlook;
export const draftPercentage = Math.round((draftTotal / emailTotal) * 100);
export const draftRequirements = [
  { name: 'required', count: draftTotal, fill: 'var(--color-required)' },
  {
    name: 'notRequired',
    count: emailTotal - draftTotal,
    fill: 'var(--color-notRequired)',
  },
];
