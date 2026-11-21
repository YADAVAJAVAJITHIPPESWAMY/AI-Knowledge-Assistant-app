import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Shield,
  KeyRound,
  Trash2,
  Database,
  Lock,
  AlertTriangle,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/apiClient';
import { useAuth } from '../contexts/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  // Profile Form
  const [name, setName] = useState(user?.name || '');
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Password Form
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwdMsg, setPwdMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMsg(null);
    try {
      const updated = await api.put<any>('/api/auth/profile', { name });
      updateUser(updated);
      setProfileMsg({ type: 'success', text: 'Profile updated successfully.' });
    } catch (err: any) {
      setProfileMsg({ type: 'error', text: err.message || 'Failed to update profile.' });
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdMsg(null);
    if (newPassword.length < 8) {
      setPwdMsg({ type: 'error', text: 'New password must be at least 8 characters.' });
      return;
    }

    try {
      await api.post('/api/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPwdMsg({ type: 'success', text: 'Password successfully changed.' });
      setCurrentPassword('');
      setNewPassword('');
    } catch (err: any) {
      setPwdMsg({ type: 'error', text: err.message || 'Incorrect current password.' });
    }
  };

  const handleDeleteAccount = async () => {
    if (
      window.confirm(
        'WARNING: This will permanently delete your account, uploaded documents, vector embeddings, and conversation history. This action cannot be undone.\n\nAre you sure?'
      )
    ) {
      try {
        await api.delete('/api/auth/account');
        await logout();
        navigate('/');
      } catch (err: any) {
        alert(`Failed to delete account: ${err.message}`);
      }
    }
  };

  return (
    <div className="max-w-4xl space-y-8 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Account & Security Settings</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Manage your personal profile, credentials, vector storage privacy, and data isolation preferences.
        </p>
      </div>

      {/* Profile Details Card */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
          <User className="w-5 h-5 text-brand-600" />
          <h2 className="text-sm font-bold text-slate-900">Profile Information</h2>
        </div>

        {profileMsg && (
          <div
            className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
              profileMsg.type === 'success'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {profileMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            <span>{profileMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleUpdateProfile} className="space-y-4 max-w-md">
          <div>
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block mb-1">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block mb-1">
              Email Address
            </label>
            <input
              type="email"
              disabled
              value={user?.email || ''}
              className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl text-xs text-slate-500 cursor-not-allowed"
            />
            <span className="text-[10px] text-slate-400 mt-0.5 block">Email address cannot be changed.</span>
          </div>

          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-colors"
          >
            Save Changes
          </button>
        </form>
      </div>

      {/* Password Update Card */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
          <KeyRound className="w-5 h-5 text-brand-600" />
          <h2 className="text-sm font-bold text-slate-900">Change Password</h2>
        </div>

        {pwdMsg && (
          <div
            className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
              pwdMsg.type === 'success'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {pwdMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            <span>{pwdMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
          <div>
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block mb-1">
              Current Password
            </label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block mb-1">
              New Password
            </label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>

          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-colors"
          >
            Update Password
          </button>
        </form>
      </div>

      {/* Privacy and Data Safety Disclosure */}
      <div className="p-6 rounded-2xl bg-indigo-50/50 border border-indigo-100 shadow-sm space-y-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-indigo-600" />
          <h2 className="text-sm font-bold text-indigo-950">Data Privacy & AI Processing Notice</h2>
        </div>
        <p className="text-xs text-indigo-900/80 leading-relaxed">
          The AI Knowledge Assistant adheres to strict zero-leakage policies. Your uploaded files are stored in private S3 buckets or local encrypted storage. Vector embeddings are keyed exclusively to your authenticated user account. When AI questions are posed, only the top matched excerpts (not entire documents) are passed to the language model.
        </p>
      </div>

      {/* Danger Zone */}
      <div className="p-6 rounded-2xl bg-white border border-red-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-red-100">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <h2 className="text-sm font-bold text-red-900">Danger Zone</h2>
        </div>
        <p className="text-xs text-slate-600">
          Permanently delete your account and all associated documents, chunks, embeddings, and chat history.
        </p>
        <button
          onClick={handleDeleteAccount}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-sm transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          <span>Delete Account Permanently</span>
        </button>
      </div>
    </div>
  );
};
