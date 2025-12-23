'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Wallet,
  TrendingUp,
  Bell,
  Shield,
  MessageSquare,
  PiggyBank,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface NavItem {
  title: string;
  href: string;
  icon: React.ReactNode;
  badge?: string | number;
}

const mainNavItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/',
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    title: 'Portfolio',
    href: '/portfolio',
    icon: <Wallet className="h-5 w-5" />,
  },
  {
    title: 'Market Data',
    href: '/market',
    icon: <TrendingUp className="h-5 w-5" />,
  },
  {
    title: 'Yield',
    href: '/yield',
    icon: <PiggyBank className="h-5 w-5" />,
  },
  {
    title: 'Alerts',
    href: '/alerts',
    icon: <Bell className="h-5 w-5" />,
  },
  {
    title: 'Risk',
    href: '/risk',
    icon: <Shield className="h-5 w-5" />,
  },
  {
    title: 'Social',
    href: '/social',
    icon: <MessageSquare className="h-5 w-5" />,
  },
  {
    title: 'On-Chain',
    href: '/onchain',
    icon: <Activity className="h-5 w-5" />,
  },
];

const bottomNavItems: NavItem[] = [
  {
    title: 'Settings',
    href: '/settings',
    icon: <Settings className="h-5 w-5" />,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen border-r border-[#8E3CC8]/20 bg-card transition-all duration-300',
        collapsed ? 'w-[70px]' : 'w-[240px]'
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-4">
          {!collapsed && (
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/images/fluxo-logo-main.jpg"
                alt="Fluxo Logo"
                width={32}
                height={32}
                className="rounded-md object-cover"
              />
              <span className="font-semibold text-xl font-[family-name:var(--font-space-grotesk)] bg-gradient-to-r from-[#8E3CC8] to-[#C77DFF] bg-clip-text text-transparent">
                Fluxo
              </span>
            </Link>
          )}
          {collapsed && (
            <Image
              src="/images/fluxo-logo-main.jpg"
              alt="Fluxo Logo"
              width={32}
              height={32}
              className="rounded-md object-cover mx-auto"
            />
          )}
        </div>

        <Separator className="bg-[#8E3CC8]/20" />

        {/* Navigation */}
        <ScrollArea className="flex-1 px-3 py-4">
          <nav className="space-y-1">
            {mainNavItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200',
                  pathname === item.href
                    ? 'bg-[#5B1A8B]/15 text-[#C77DFF] border-l-2 border-[#8E3CC8]'
                    : 'text-muted-foreground hover:bg-[#8E3CC8]/10 hover:text-[#C77DFF]',
                  collapsed && 'justify-center px-2'
                )}
              >
                {item.icon}
                {!collapsed && <span>{item.title}</span>}
                {!collapsed && item.badge && (
                  <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-[#5B1A8B] text-[10px] font-medium text-white">
                    {item.badge}
                  </span>
                )}
              </Link>
            ))}
          </nav>
        </ScrollArea>

        <Separator className="bg-[#8E3CC8]/20" />

        {/* Bottom Navigation */}
        <div className="px-3 py-4 space-y-1">
          {bottomNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200',
                pathname === item.href
                  ? 'bg-[#5B1A8B]/15 text-[#C77DFF] border-l-2 border-[#8E3CC8]'
                  : 'text-muted-foreground hover:bg-[#8E3CC8]/10 hover:text-[#C77DFF]',
                collapsed && 'justify-center px-2'
              )}
            >
              {item.icon}
              {!collapsed && <span>{item.title}</span>}
            </Link>
          ))}

          {/* Collapse Button */}
          <Button
            variant="ghost"
            size="sm"
            className={cn('w-full justify-center', collapsed && 'px-2')}
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4" />
                <span className="ml-2">Collapse</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </aside>
  );
}
