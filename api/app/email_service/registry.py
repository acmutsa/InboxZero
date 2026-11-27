from app.db.schema import EmailAccount
from app.db.schema import EmailServiceProvider
from app.email_service.gmail.provider import GmailProvider
from app.email_service.outlook.provider import OutlookProvider
from app.email_service.provider import EmailProvider
from app.email_service.types.error import UnsupportedProviderError

PROVIDERS: dict[EmailServiceProvider, type[EmailProvider]] = {
    EmailServiceProvider.gmail: GmailProvider,
    EmailServiceProvider.outlook: OutlookProvider,
}


def get_email_provider(account: EmailAccount) -> EmailProvider:
    provider_class = PROVIDERS.get(account.provider)
    if provider_class is None:
        raise UnsupportedProviderError(f"No email provider for {account.provider}")
    return provider_class(account)
