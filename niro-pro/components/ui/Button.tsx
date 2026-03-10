"use client";
import { clsx } from "clsx";
import { Loader2 } from "lucide-react";
import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        "inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-300",
        {
          "bg-violet-600 hover:bg-violet-700 text-white": variant === "primary",
          "border border-gray-200 bg-white hover:bg-gray-50 text-gray-700": variant === "secondary",
          "text-gray-500 hover:text-gray-700 hover:bg-gray-100": variant === "ghost",
          "bg-red-600 hover:bg-red-700 text-white": variant === "danger",
          "px-3 py-1.5 text-sm": size === "sm",
          "px-4 py-2 text-sm": size === "md",
          "px-6 py-3 text-base": size === "lg",
          "opacity-60 cursor-not-allowed": disabled || loading,
        },
        className
      )}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  );
}
