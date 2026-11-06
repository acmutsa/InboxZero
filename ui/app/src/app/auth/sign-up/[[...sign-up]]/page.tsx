import { SignUp } from "@clerk/nextjs";
import AuthPage from '@/components/AuthPage';
import SignUpForm from '@/components/SignUpForm';
import { demoMode } from '@/lib/auth-config';

export default function SignUpPage() {
  // Design reference: integrate this auth shell and styling with Clerk later.
  if (demoMode) {
    return (
      <AuthPage>
        <SignUpForm />
      </AuthPage>
    );
  }
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignUp />
    </div>
  );
}
