import React from 'react';
import { Menu, ShieldCheck, Search, Bell } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface HeaderProps {
  onMenuToggle: () => void;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle, title }) => {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 md:px-8 bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        {title && <h2 className="text-lg font-semibold text-slate-800">{title}</h2>}
      </div>

      <div className="flex items-center gap-4">
        {/* Status Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Vector Index Active</span>
        </div>

        {/* Security Isolation Indicator */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500">
          <ShieldCheck className="w-4 h-4 text-brand-500" />
          <span>Isolated Storage</span>
        </div>

        {/* User greeting */}
        <div className="text-xs text-slate-600 font-medium hidden sm:block">
          Hi, <span className="font-semibold text-slate-900">{user?.name}</span>
        </div>
      </div>
    </header>
  );
};
