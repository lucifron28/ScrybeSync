const Button = ({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  loading = false,
  className = '',
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-[var(--primary)] text-[var(--on-primary)] hover:opacity-90 focus:ring-[var(--primary)]',
    secondary: 'bg-[var(--secondary)] text-[var(--on-secondary)] hover:opacity-90 focus:ring-[var(--secondary)]',
    outline: 'border border-[var(--border)] text-[var(--text-primary)] hover:bg-[var(--bg-surface-elevated)] focus:ring-[var(--primary)]',
    ghost: 'text-[var(--text-primary)] hover:bg-[var(--bg-surface-elevated)] focus:ring-[var(--primary)]',
    danger: 'bg-[var(--error)] text-white hover:opacity-90 focus:ring-[var(--error)]',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

export default Button;
