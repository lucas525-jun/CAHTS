import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/chats', label: 'Chats', icon: MessageSquare },
  ];

  return (
    <nav className="w-20 border-r border-border bg-sidebar flex flex-col items-center py-6 gap-4">
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
    </nav>
  );
};
