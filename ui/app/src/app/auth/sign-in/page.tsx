import AuthShell from '@/components/AuthShell';
import SignUpForm from '@/components/SignUpForm';
export default function SignInPage() {
  return (
    <AuthShell>
      <SignUpForm signIn />
    </AuthShell>
  );
}
