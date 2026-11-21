import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Lightbulb,
  Settings,
  LogOut,
  BrainCircuit,
  Sparkles,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { label: 'AI Chat', icon: MessageSquare, path: '/chat' },
    { label: 'My Documents', icon: FileText, path: '/documents' },
    { label: 'Knowledge Insights', icon: Lightbulb, path: '/insights' },
    { label: 'Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-navy-900/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 bg-navy-900 border-r border-slate-800 text-slate-300 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-6 h-16 border-b border-slate-800/80 bg-navy-900/50">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-500 to-brand-purple text-white shadow-lg shadow-brand-500/20">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight leading-none flex items-center gap-1.5">
              Knowledge AI
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                RAG
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 mt-0.5">Personal Knowledge Base</p>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Menu
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-brand-500/20 to-brand-purple/20 text-white border border-brand-500/30 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon className={`w-5 h-5 ${isActive ? 'text-brand-400' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-4 h-4 text-brand-400" />}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* AI Grounding Status Card */}
        <div className="px-4 py-3 mx-3 mb-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span className="text-xs font-semibold text-slate-200">Grounded Mode</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Responses cite your uploaded documents with verifiable page and slide references.
          </p>
        </div>

        {/* User Profile & Logout */}
        <div className="p-3 border-t border-slate-800/80 bg-navy-900/60">
          <div className="flex items-center justify-between p-2 rounded-xl bg-slate-800/40">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-brand-purple text-white text-xs font-bold shrink-0">
                {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-medium text-slate-200 truncate">{user?.name || 'User'}</p>
                <p className="text-[11px] text-slate-400 truncate">{user?.email || ''}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-700/50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
