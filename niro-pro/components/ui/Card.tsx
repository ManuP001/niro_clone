import { clsx } from "clsx";
import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  header?: ReactNode;
}

export default function Card({ children, className, header }: CardProps) {
  return (
    <div className={clsx("bg-white rounded-xl shadow-sm border border-gray-100", className)}>
      {header && <div className="px-6 py-4 border-b border-gray-100">{header}</div>}
      <div className="p-6">{children}</div>
    </div>
  );
}
