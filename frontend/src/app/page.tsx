'use client';

import { useEffect, useState, useCallback } from 'react';
import Image from 'next/image';
import { Wallet, TrendingUp, Shield, Bell, Newspaper, RefreshCw } from 'lucide-react';
import {
  StatCard,
  RecentAlerts,
  PortfolioChart,
  PriceChart,
  TopYields,
} from '@/components/dashboard';
import { PremiumInsights } from '@/components/premium';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, Asset, YieldOpportunity } from '@/types';
import { api, NewsItem } from '@/lib/api/client';
import { formatRelativeTime } from '@/lib/utils';

// Demo data - used as fallback when backend is unavailable
const demoAlerts: Alert[] = [
  {
    id: '1',
    type: 'whale',
    severity: 'high',
    title: 'Large MNT Transfer Detected',
    message: '500,000 MNT moved from whale wallet to exchange',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    delivered: false,
  },
  {
    id: '2',
    type: 'price',
    severity: 'medium',
    title: 'ETH Price Alert',
    message: 'ETH crossed $3,500 threshold',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    delivered: true,
  },
  {
    id: '3',
    type: 'risk',
    severity: 'low',
    title: 'Portfolio Risk Update',
    message: 'Your portfolio risk score improved to 6.2',
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    delivered: true,
  },
  {
    id: '4',
    type: 'yield',
    severity: 'medium',
    title: 'New Yield Opportunity',
    message: 'USDC-MNT pool on Agni Finance now offering 18% APY',
    timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    delivered: false,
  },
];

const demoAssets: Asset[] = [
  { token_address: '0x1', token_symbol: 'MNT', balance: 10000, value_usd: 8500, percentage: 42.5 },
  { token_address: '0x2', token_symbol: 'ETH', balance: 2.5, value_usd: 8750, percentage: 43.75 },
  { token_address: '0x3', token_symbol: 'USDC', balance: 2000, value_usd: 2000, percentage: 10 },
  { token_address: '0x4', token_symbol: 'USDT', balance: 750, value_usd: 750, percentage: 3.75 },
];

const demoYields: YieldOpportunity[] = [
  { protocol: 'Agni Finance', pool: 'USDC-MNT', apy: 18.5, tvl: 5200000, risk_score: 4, token_pair: ['USDC', 'MNT'], network: 'mantle' },
  { protocol: 'Lendle', pool: 'ETH Supply', apy: 12.3, tvl: 8500000, risk_score: 3, token_pair: ['ETH'], network: 'mantle' },
  { protocol: 'FusionX', pool: 'MNT-ETH', apy: 24.8, tvl: 2100000, risk_score: 6, token_pair: ['MNT', 'ETH'], network: 'mantle' },
  { protocol: 'Merchant Moe', pool: 'USDT-USDC', apy: 8.2, tvl: 12000000, risk_score: 2, token_pair: ['USDT', 'USDC'], network: 'mantle' },
  { protocol: 'iZUMi', pool: 'MNT-USDC', apy: 21.5, tvl: 3400000, risk_score: 5, token_pair: ['MNT', 'USDC'], network: 'mantle' },
];

const demoPriceHistory = Array.from({ length: 24 }, (_, i) => ({
  timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
  price: 19500 + Math.random() * 1000 - 500 + i * 15,
}));

// Demo news for when backend is unavailable
const demoNews: NewsItem[] = [
  {
    id: '1',
    title: 'Bitcoin Surpasses $100K Milestone, Setting New All-Time High',
    summary: 'Bitcoin has officially crossed the $100,000 mark for the first time in history, marking a significant milestone in cryptocurrency adoption.',
    url: '#',
    source: 'CoinDesk',
    published_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    relevance: 0.95,
    categories: ['Bitcoin', 'Markets'],
    tags: ['BTC', 'ATH', 'Price'],
  },
  {
    id: '2',
    title: 'Ethereum L2 Networks See Record Transaction Volume',
    summary: 'Layer 2 solutions on Ethereum processed over 10 million transactions in the past 24 hours, demonstrating growing adoption.',
    url: '#',
    source: 'The Block',
    published_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    relevance: 0.88,
    categories: ['Ethereum', 'Layer 2'],
    tags: ['ETH', 'Arbitrum', 'Optimism'],
  },
  {
    id: '3',
    title: 'DeFi TVL Reaches New Heights Across Multiple Chains',
    summary: 'Total value locked in DeFi protocols has surged to new highs, with Mantle Network showing particularly strong growth.',
    url: '#',
    source: 'DeFi Pulse',
    published_at: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
    relevance: 0.82,
    categories: ['DeFi', 'TVL'],
    tags: ['DeFi', 'Mantle', 'Yield'],
  },
  {
    id: '4',
    title: 'Institutional Investors Increase Crypto Allocations',
    summary: 'Major financial institutions continue to expand their cryptocurrency portfolios, signaling growing mainstream acceptance.',
    url: '#',
    source: 'Bloomberg Crypto',
    published_at: new Date(Date.now() - 1000 * 60 * 360).toISOString(),
    relevance: 0.75,
    categories: ['Institutional', 'Adoption'],
    tags: ['Institutional', 'Investment'],
  },
];

// News Digest Component
function DailyDigest({ 
  news, 
  loading, 
  error,
  onRefresh 
}: { 
  news: NewsItem[]; 
  loading: boolean; 
  error: string | null;
  onRefresh: () => void;
}) {
  // Use demo news when backend is unavailable
  const displayNews = error || news.length === 0 ? demoNews : news;
  const isUsingDemo = error !== null || news.length === 0;

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            Daily Digest
          </CardTitle>
          <CardDescription>Loading latest news...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            Daily Digest
            {isUsingDemo && (
              <Badge variant="outline" className="text-[10px] ml-2">Demo</Badge>
            )}
          </CardTitle>
          <CardDescription>
            {isUsingDemo ? 'Sample news (connect backend for live data)' : `${news.length} stories from crypto news`}
          </CardDescription>
        </div>
        <Button variant="ghost" size="icon" onClick={onRefresh}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px]">
          <div className="space-y-4">
            {displayNews.map((item) => (
              <a
                key={item.id}
                href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 rounded-lg border border-border/50 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-medium text-sm line-clamp-2">{item.title}</h4>
                    {item.relevance && item.relevance > 0.8 && (
                      <Badge variant="default" className="shrink-0 text-[10px]">Hot</Badge>
                    )}
                  </div>
                  {item.summary && (
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {item.summary}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-muted-foreground">{item.source}</span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeTime(item.published_at)}
                    </span>
                  </div>
                  {item.tags && item.tags.length > 0 && (
                    <div className="flex gap-1 mt-2 flex-wrap">
                      {item.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-[10px]">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </a>
              ))}
            </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>('--:--:--');
  
  // Data states
  const [alerts, setAlerts] = useState<Alert[]>(demoAlerts);
  const [assets] = useState<Asset[]>(demoAssets);
  const [yields] = useState<YieldOpportunity[]>(demoYields);
  const [priceHistory] = useState(demoPriceHistory);
  const [digest, setDigest] = useState<NewsItem[]>([]);
  const [digestLoading, setDigestLoading] = useState(true);
  const [digestError, setDigestError] = useState<string | null>(null);

  // Check backend connectivity
  const checkBackend = useCallback(async () => {
    try {
      await api.system.health();
      setBackendConnected(true);
      setLastSyncTime(new Date().toLocaleTimeString());
      return true;
    } catch {
      setBackendConnected(false);
      return false;
    }
  }, []);

  // Fetch digest
  const fetchDigest = useCallback(async () => {
    setDigestLoading(true);
    setDigestError(null);
    try {
      const data = await api.digest.get();
      if (data && Array.isArray(data)) {
        setDigest(data);
      }
    } catch (err) {
      setDigestError(err instanceof Error ? err.message : 'Failed to fetch digest');
    } finally {
      setDigestLoading(false);
    }
  }, []);

  // Fetch alerts
  const fetchAlerts = useCallback(async () => {
    try {
      const response = await api.alerts.list();
      if (response.data && Array.isArray(response.data)) {
        setAlerts(response.data as Alert[]);
      }
    } catch {
      // Keep demo data on error
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    const init = async () => {
      // Set initial sync time on client
      setLastSyncTime(new Date().toLocaleTimeString());
      
      const connected = await checkBackend();
      
      if (connected) {
        // Fetch all data in parallel
        await Promise.all([
          fetchDigest(),
          fetchAlerts(),
        ]);
      } else {
        setDigestLoading(false);
        setDigestError('Backend not connected');
      }
      
      setLoading(false);
    };

    init();
  }, [checkBackend, fetchDigest, fetchAlerts]);

  const totalValue = assets.reduce((sum, asset) => sum + asset.value_usd, 0);
  const unreadAlerts = alerts.filter(a => !a.delivered).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Intelligence Interface Header */}
      <div className="relative overflow-hidden rounded-lg border border-[#8E3CC8]/20 bg-gradient-to-br from-[#1E1B24] to-[#2A2534] p-8 md:p-12">
        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 pattern-grid opacity-30" />
        
        <div className="relative z-10 flex flex-col items-center text-center gap-6">
          {/* Fluxo Logo */}
          <div className="relative">
            {/* Logo Glow Effect */}
            <div className="absolute inset-0 bg-[#8E3CC8]/30 blur-3xl rounded-full scale-150" />
            <div className="relative w-32 h-32 md:w-40 md:h-40 rounded-2xl overflow-hidden shadow-2xl shadow-[#8E3CC8]/40">
              <Image
                src="/fluxo-logo.jpg"
                alt="Fluxo Logo"
                fill
                className="object-cover"
                priority
              />
            </div>
          </div>
          
          {/* Content */}
          <div className="flex flex-col items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="h-2.5 w-2.5 rounded-full bg-[#C77DFF] animate-pulse-subtle" />
              <span className="text-sm font-bold text-[#C77DFF] uppercase tracking-widest font-[family-name:var(--font-space-grotesk)]">
                Intelligence Active
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-black text-white font-[family-name:var(--font-vt323)] tracking-wide">
              Your private intelligence agent.
            </h1>
            <p className="text-base md:text-lg text-white max-w-xl font-[family-name:var(--font-space-grotesk)]">
              Private intelligence monitoring. Portfolio tracking, risk analysis, and strategic execution.
            </p>
          </div>
          
          {/* Status */}
          <div className="flex items-center gap-4">
            <Badge 
              variant={backendConnected ? 'default' : 'outline'}
              className={backendConnected ? 'bg-[#5B1A8B] font-bold' : 'border-[#8E3CC8]/50 text-[#C77DFF] font-bold'}
            >
              {backendConnected ? '● Systems Online' : '○ Demo Mode'}
            </Badge>
            <span className="text-xs font-medium text-[#8E3CC8]">
              Last sync: {lastSyncTime}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Portfolio Value"
          value={totalValue}
          change={5.2}
          icon={<Wallet className="h-4 w-4" />}
          loading={loading}
        />
        <StatCard
          title="24h P&L"
          value={1045}
          change={2.8}
          changeLabel="today"
          icon={<TrendingUp className="h-4 w-4" />}
          loading={loading}
        />
        <StatCard
          title="Risk Score"
          value="6.2 / 10"
          change={-0.8}
          changeLabel="improved"
          icon={<Shield className="h-4 w-4" />}
          loading={loading}
        />
        <StatCard
          title="Active Alerts"
          value={alerts.length.toString()}
          icon={<Bell className="h-4 w-4" />}
          description={`${unreadAlerts} unread`}
          loading={loading}
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <PortfolioChart
          assets={assets}
          totalValue={totalValue}
          loading={loading}
        />
        <PriceChart
          data={priceHistory}
          title="Portfolio Performance"
          description="24-hour value history"
          loading={loading}
          color="#8E3CC8"
        />
      </div>

      {/* Bottom Row - Alerts + Digest + Yields */}
      <div className="grid gap-6 lg:grid-cols-3">
        <RecentAlerts alerts={alerts.slice(0, 5)} loading={loading} />
        <DailyDigest 
          news={digest} 
          loading={digestLoading} 
          error={digestError}
          onRefresh={fetchDigest}
        />
        <TopYields yields={yields} loading={loading} />
      </div>

      {/* Premium Insights Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        <PremiumInsights />
        <Card className="relative overflow-hidden">
          {/* Accent gradient */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-[#5B1A8B]/10 to-transparent rounded-bl-full" />
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-space-grotesk)]">
              <Shield className="h-5 w-5 text-[#8E3CC8]" />
              Security Status
            </CardTitle>
            <CardDescription>Wallet and protocol security overview</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-md border border-[#8E3CC8]/20 bg-[#F4F1F7]/50 dark:bg-[#1E1B24]/50">
                <span className="text-sm">Connected Protocols</span>
                <Badge variant="secondary">4 verified</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-md border border-[#8E3CC8]/20 bg-[#F4F1F7]/50 dark:bg-[#1E1B24]/50">
                <span className="text-sm">Smart Contract Audits</span>
                <Badge variant="success">All audited</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-md border border-[#8E3CC8]/20 bg-[#F4F1F7]/50 dark:bg-[#1E1B24]/50">
                <span className="text-sm">Risk Exposure</span>
                <Badge variant="warning">Medium</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-md border border-[#8E3CC8]/20 bg-[#F4F1F7]/50 dark:bg-[#1E1B24]/50">
                <span className="text-sm">Wallet Health</span>
                <Badge variant="success">Good</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
