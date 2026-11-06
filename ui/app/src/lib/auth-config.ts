/** Local visual preview only; production always uses Clerk authentication. */
export const demoMode =
  process.env.NODE_ENV === 'development' && process.env.DEMO_MODE === 'true';
