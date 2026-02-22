import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

const buttonVariants = {
  default: 'bg-[#B51A2B] text-white hover:bg-[#B51A2B]/80 hover:text-white',
  outline: 'border border-slate-700 bg-slate-800 text-white hover:bg-slate-700',
  ghost: 'text-slate-300 hover:bg-slate-700/50',
};

const buttonSizes = {
  default: 'px-4 py-2 text-sm',
  sm: 'px-3 py-1.5 text-xs',
  lg: 'px-6 py-3 text-base',
  icon: 'w-10 h-10 p-0',
};

const Button = forwardRef(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed',
        buttonVariants[variant],
        buttonSizes[size],
        className
      )}
      ref={ref}
      {...props}
    />
  )
);

Button.displayName = 'Button';

export { Button, buttonVariants, buttonSizes };
