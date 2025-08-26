import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { loginSchema } from '../schemas/authSchemas';
import { authService } from '../services/authService';
import useAuthStore from '../store/authStore';
import Button from '../components/UI/Button';
import Input from '../components/UI/Input';
import Alert from '../components/UI/Alert';

const LoginPage = () => {
  const navigate = useNavigate();
  const { setAuth, isAuthenticated, loading: storeLoading } = useAuthStore();
  const [submitError, setSubmitError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(loginSchema),
  });

  // Redirect if already authenticated
  if (isAuthenticated && !storeLoading) {
    return <Navigate to="/dashboard" replace />;
  }

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    setSubmitError('');

    try {
      const response = await authService.login(data);
      setAuth(response.user, response.access_token);
      navigate('/dashboard');
    } catch (error) {
      setSubmitError(
        error.response?.data?.error || 
        'Login failed. Please check your credentials.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-[var(--text-primary)]">
            Sign in to ScrybeSync
          </h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">
            Or{' '}
            <Link
              to="/register"
              className="font-medium text-[var(--primary)] hover:opacity-80 transition-opacity"
            >
              create a new account
            </Link>
          </p>
        </div>

        <div className="bg-[var(--bg-surface)] rounded-lg shadow-lg p-8 border border-[var(--border)]">
          {submitError && (
            <Alert variant="error" className="mb-6">
              {submitError}
            </Alert>
          )}

          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <Input
              label="Username"
              type="text"
              autoComplete="username"
              {...register('username')}
              error={errors.username?.message}
            />

            <Input
              label="Password"
              type="password"
              autoComplete="current-password"
              {...register('password')}
              error={errors.password?.message}
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-[var(--primary)] focus:ring-[var(--primary)] border-[var(--border)] rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-[var(--text-secondary)]">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <Link
                  to="/forgot-password"
                  className="font-medium text-[var(--primary)] hover:opacity-80 transition-opacity"
                >
                  Forgot your password?
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isSubmitting}
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>
        </div>

        <div className="text-center">
          <p className="text-xs text-[var(--text-secondary)]">
            By signing in, you agree to our{' '}
            <Link to="/terms" className="text-[var(--primary)] hover:opacity-80">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link to="/privacy" className="text-[var(--primary)] hover:opacity-80">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
