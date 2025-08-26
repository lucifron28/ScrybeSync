import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { registerSchema } from '../schemas/authSchemas';
import { authService } from '../services/authService';
import useAuthStore from '../store/authStore';
import Button from '../components/UI/Button';
import Input from '../components/UI/Input';
import Alert from '../components/UI/Alert';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, loading: storeLoading } = useAuthStore();
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(registerSchema),
  });

  if (isAuthenticated && !storeLoading) {
    return <Navigate to="/dashboard" replace />;
  }

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    setSubmitError('');
    setSubmitSuccess('');

    try {
      await authService.register(data);
      setSubmitSuccess('Account created successfully! Please sign in.');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      const errorMessage = error.response?.data;
      
      if (typeof errorMessage === 'object') {
        const errorMessages = Object.entries(errorMessage)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join('\n');
        setSubmitError(errorMessages);
      } else {
        setSubmitError(errorMessage || 'Registration failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-[var(--text-primary)]">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">
            Or{' '}
            <Link
              to="/login"
              className="font-medium text-[var(--primary)] hover:opacity-80 transition-opacity"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>

        <div className="bg-[var(--bg-surface)] rounded-lg shadow-lg p-8 border border-[var(--border)]">
          {submitError && (
            <Alert variant="error" className="mb-6">
              <div className="whitespace-pre-line">{submitError}</div>
            </Alert>
          )}

          {submitSuccess && (
            <Alert variant="success" className="mb-6">
              {submitSuccess}
            </Alert>
          )}

          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="First Name"
                type="text"
                autoComplete="given-name"
                {...register('first_name')}
                error={errors.first_name?.message}
              />

              <Input
                label="Last Name"
                type="text"
                autoComplete="family-name"
                {...register('last_name')}
                error={errors.last_name?.message}
              />
            </div>

            <Input
              label="Username"
              type="text"
              autoComplete="username"
              {...register('username')}
              error={errors.username?.message}
            />

            <Input
              label="Email Address"
              type="email"
              autoComplete="email"
              {...register('email')}
              error={errors.email?.message}
            />

            <Input
              label="Password"
              type="password"
              autoComplete="new-password"
              {...register('password')}
              error={errors.password?.message}
            />

            <Input
              label="Confirm Password"
              type="password"
              autoComplete="new-password"
              {...register('confirm_password')}
              error={errors.confirm_password?.message}
            />

            <div className="flex items-center">
              <input
                id="accept-terms"
                name="accept-terms"
                type="checkbox"
                className="h-4 w-4 text-[var(--primary)] focus:ring-[var(--primary)] border-[var(--border)] rounded"
                required
              />
              <label htmlFor="accept-terms" className="ml-2 block text-sm text-[var(--text-secondary)]">
                I agree to the{' '}
                <Link to="/terms" className="text-[var(--primary)] hover:opacity-80">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-[var(--primary)] hover:opacity-80">
                  Privacy Policy
                </Link>
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isSubmitting}
              disabled={isSubmitting || submitSuccess}
              className="w-full"
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </Button>
          </form>
        </div>

        <div className="text-center">
          <p className="text-xs text-[var(--text-secondary)]">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-medium text-[var(--primary)] hover:opacity-80 transition-opacity"
            >
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
