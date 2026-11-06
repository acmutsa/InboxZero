import { SignIn } from "@clerk/nextjs";
import AuthPage from '@/components/AuthPage';
import SignUpForm from '@/components/SignUpForm';
import { demoMode } from '@/lib/auth-config';

export default function SignInPage() {
  // Design reference: integrate this auth shell and styling with Clerk later.
  if (demoMode) {
    return (
      <AuthPage brandOnly>
        <SignUpForm signIn />
      </AuthPage>
    );
  }
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn />
    </div>
  );
}
