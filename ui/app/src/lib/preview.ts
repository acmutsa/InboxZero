/** UI preview state only: never persist passwords or authentication tokens. */
export function savePreviewValue(key: string, value: string) {
  try {
    sessionStorage.setItem(key, value);
    window.dispatchEvent(new Event('storage'));
  } catch {
    /* The preview still works when browser storage is disabled. */
  }
}
