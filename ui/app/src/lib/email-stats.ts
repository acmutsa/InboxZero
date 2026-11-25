import type { ApiClient } from '@/lib/api/api';
import type {
  CategoryStatsResponse,
  EmailAccount,
  EmailProvider,
} from '@/lib/api/types';

type AccountStats = {
  provider: EmailProvider;
  categories: CategoryStatsResponse;
  drafts: number;
};

export type EmailStats = ReturnType<typeof summarizeStats>;

/**
 * Loads category and draft counts for every connected account. One account
 * failing doesn't hide the others' stats; it's listed in `failed` instead.
 */
export async function loadAccountStats(client: ApiClient, accounts: EmailAccount[]) {
  const results = await Promise.allSettled(
    accounts.map(async (account): Promise<AccountStats> => {
      const [categories, { drafts }] = await Promise.all([
        client.getCategoryStats(account.id),
        client.getDraftStats(account.id),
      ]);
      return { provider: account.provider, categories, drafts };
    }),
  );
  const stats: AccountStats[] = [];
  const failed: string[] = [];
  results.forEach((result, index) => {
    if (result.status === 'fulfilled') stats.push(result.value);
    else failed.push(accounts[index].email_account);
  });
  return { stats, failed };
}

/** Combines per-account stats into per-provider totals for the charts. */
export function summarizeStats(accounts: AccountStats[]) {
  const byCategory = new Map<string, { category: string; gmail: number; outlook: number }>();
  const emailCounts = { gmail: 0, outlook: 0 };
  const draftCounts = { gmail: 0, outlook: 0 };

  for (const { provider, categories, drafts } of accounts) {
    draftCounts[provider] += drafts;
    for (const { category, count } of categories) {
      const row = byCategory.get(category) ?? { category, gmail: 0, outlook: 0 };
      row[provider] += count;
      byCategory.set(category, row);
      emailCounts[provider] += count;
    }
  }

  const emailTotal = emailCounts.gmail + emailCounts.outlook;
  const draftTotal = draftCounts.gmail + draftCounts.outlook;
  const noDraftTotal = Math.max(emailTotal - draftTotal, 0);

  return {
    emailCategories: [...byCategory.values()],
    gmailTotal: emailCounts.gmail,
    outlookTotal: emailCounts.outlook,
    emailTotal,
    draftCounts,
    noDraftCounts: {
      gmail: Math.max(emailCounts.gmail - draftCounts.gmail, 0),
      outlook: Math.max(emailCounts.outlook - draftCounts.outlook, 0),
    },
    draftTotal,
    noDraftTotal,
    draftPercentage: emailTotal ? Math.round((draftTotal / emailTotal) * 100) : 0,
    draftRequirements: [
      { name: 'required', count: draftTotal, fill: 'var(--color-required)' },
      { name: 'notRequired', count: noDraftTotal, fill: 'var(--color-notRequired)' },
    ],
  };
}
