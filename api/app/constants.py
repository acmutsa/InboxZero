"""Application-wide constants."""

DEFAULT_CATEGORIES: tuple[dict[str, str], ...] = (
    {
        "category_name": "Important",
        "category_description": "Time-sensitive emails or emails that need a reply or action.",
    },
    {
        "category_name": "Work",
        "category_description": "Emails about jobs, projects, clients, and colleagues.",
    },
    {
        "category_name": "Personal",
        "category_description": "Emails from friends and family.",
    },
    {
        "category_name": "Finance",
        "category_description": "Receipts, invoices, bills, and bank statements.",
    },
    {
        "category_name": "Newsletters",
        "category_description": "Subscribed newsletters, digests, and blog updates.",
    },
    {
        "category_name": "Promotions",
        "category_description": "Marketing emails, sales, and offers.",
    },
    {
        "category_name": "Other",
        "category_description": "Emails that do not fit any other category.",
    },
)
