import { forwardRef } from 'react';

const Input = forwardRef(({ 
  label, 
  error, 
  type = 'text', 
  className = '',
  ...props 
}, ref) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-[var(--text-primary)]">
          {label}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={`
          w-full px-3 py-2 border border-[var(--border)] rounded-lg 
          bg-[var(--bg-surface)] text-[var(--text-primary)]
          placeholder-[var(--text-secondary)]
          focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
          ${error ? 'border-[var(--error)] focus:ring-[var(--error)]' : ''}
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className="text-sm text-[var(--error)]">{error}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
