import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Settings, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

export const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/chats', label: 'Chats', icon: MessageSquare },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <nav className="w-20 border-r border-border bg-sidebar flex flex-col items-center py-6">
      {/* Main navigation items */}
      <div className="flex-1 flex flex-col gap-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'w-14 h-14 rounded-xl flex items-center justify-center transition-all',
                'hover:bg-sidebar-accent',
                isActive && 'bg-sidebar-primary text-sidebar-primary-foreground'
              )}
              title={item.label}
            >
              <Icon className="h-6 w-6" />
            </Link>
          );
        })}
      </div>

      {/* Logout button at bottom */}
      <button
        onClick={handleLogout}
        className={cn(
          'w-14 h-14 rounded-xl flex items-center justify-center transition-all',
          'hover:bg-red-500/10 hover:text-red-500',
          'text-muted-foreground'
        )}
        title="Logout"
      >
        <LogOut className="h-6 w-6" />
      </button>
    </nav>
  );
};
