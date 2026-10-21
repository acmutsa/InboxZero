import AuthShell from '@/components/AuthShell';
import RegistrationForm from '@/components/RegistrationForm';
export default function RegistrationPage() {
  return (
    <AuthShell registration>
      <RegistrationForm />
    </AuthShell>
  );
}
