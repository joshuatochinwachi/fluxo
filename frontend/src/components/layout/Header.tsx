'use client';

import { Bell, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useState } from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useFluxo, useAlerts } from '@/hooks/useFluxo';
import { cn } from '@/lib/utils';
import Link from 'next/link';

export function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const { isWalletConnected } = useFluxo();
  const { alerts } = useAlerts();

  const unreadCount = alerts.filter(a => !a.delivered).length;

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-[#8E3CC8]/20 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-6">
      {/* Search */}
      <div className="flex-1 flex items-center gap-4 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search tokens, protocols..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-[#F4F1F7]/50 dark:bg-[#1E1B24]/50 border-[#8E3CC8]/20 focus:border-[#8E3CC8]/50 focus:ring-[#8E3CC8]/20"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <Link href="/alerts">
          <Button variant="ghost" size="icon" className="relative group">
            <Bell className={cn("h-5 w-5 transition-transform group-hover:rotate-12", unreadCount > 0 && "text-primary")} />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-black text-white shadow-lg shadow-primary/20 animate-in zoom-in duration-300">
                {unreadCount}
              </span>
            )}
          </Button>
        </Link>

        {/* Wallet Connection - RainbowKit */}
        <ConnectButton
          chainStatus="icon"
          showBalance={false}
          accountStatus={{
            smallScreen: 'avatar',
            largeScreen: 'full',
          }}
        />

        {/* User Avatar - Fluxo Logo */}
        <Avatar className="h-9 w-9 border border-primary/20 bg-background overflow-hidden">
          <AvatarImage src="/fluxo-logo.jpg" alt="Fluxo" className="object-cover" />
          <AvatarFallback className="bg-gradient-to-br from-[#5B1A8B] to-[#8E3CC8] text-white font-medium">
            U
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
