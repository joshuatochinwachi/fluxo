'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import Image from 'next/image';
import { Wallet, TrendingUp, Shield, Bell, Newspaper, RefreshCw, Layers } from 'lucide-react';
import {
  StatCard,
  RecentAlerts,
  PortfolioChart,
  TopYields,
} from '@/components/dashboard';
const PremiumInsights = dynamic(() => import('@/components/premium').then(mod => mod.PremiumInsights), {
  ssr: false,
  loading: () => (
    <Card className="relative overflow-hidden rounded-3xl border-primary/20">
      <div className="p-12 flex flex-col items-center justify-center space-y-4">
        <RefreshCw className="h-8 w-8 animate-spin text-primary/40" />
        <p className="text-[10px] font-black uppercase tracking-widest opacity-40 text-center">Loading Alpha Engine...</p>
      </div>
    </Card>
  )
});
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, Asset, YieldOpportunity } from '@/types';
import {
  useFluxo,
  usePortfolio,
  useAlerts,
  useYieldOpportunities,
  useRiskAnalysis
} from '@/hooks/useFluxo';
import { api, NewsItem } from '@/lib/api/client';
import { formatRelativeTime, formatCurrency, cn } from '@/lib/utils';

// Demo Data Fallbacks
const demoAssets: Asset[] = [
  { token_symbol: 'MNT', balance: 12500, value_usd: 15625, percentage: 45, token_address: '0x...', price: 1.25 },
  { token_symbol: 'ETH', balance: 2.5, value_usd: 6250, percentage: 18, token_address: '0x...', price: 2500 },
  { token_symbol: 'USDC', balance: 5000, value_usd: 5000, percentage: 14, token_address: '0x...', price: 1 },
  { token_symbol: 'WMNT', balance: 8000, value_usd: 10000, percentage: 23, token_address: '0x...', price: 1.25 },
];

const demoAlerts: Alert[] = [
  {
    alert_id: 'd1',
    title: 'High APY Opportunity',
    message: 'MNT/ETH pool on FusionX is currently yielding 42% APY. Consider rebalancing.',
    timestamp: new Date().toISOString(),
    overall_severity: 'low',
    delivered: false,
    wallet_address: '0x...',
    risk_level: 'low'
  },
  {
    alert_id: 'd2',
    title: 'Whale Movement Detected',
    message: 'Large transfer of 1M MNT to Binance observed. Monitoring exchange inflow.',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    overall_severity: 'medium',
    delivered: true,
    wallet_address: '0x...',
    risk_level: 'medium'
  }
];

const demoYields: YieldOpportunity[] = [
  { protocol: 'FusionX', pool: 'MNT/WMNT', apy: 12.5, tvl: 5000000, risk_score: 2, token_pair: ['MNT', 'WMNT'], network: 'mantle' },
  { protocol: 'Agni', pool: 'mETH/WETH', apy: 8.2, tvl: 12000000, risk_score: 1, token_pair: ['mETH', 'WETH'], network: 'mantle' },
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
  if (loading) {
    return (
      <Card className="border-border/50 bg-background/50 h-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-tight font-black">
            <Newspaper className="h-4 w-4 text-primary" />
            Daily Intel Digest
          </CardTitle>
          <CardDescription>Scanning global news sources...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-3/4 bg-primary/5" />
                <Skeleton className="h-3 w-full bg-primary/5" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50 bg-background/50 h-full overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between bg-primary/5 border-b border-border/50">
        <div>
          <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-tight font-black">
            <Newspaper className="h-4 w-4 text-primary" />
            Daily Intel Digest
          </CardTitle>
          <CardDescription className="text-[10px] font-bold">
            {news.length > 0 ? `${news.length} verified news vectors` : 'No recent news vectors detected'}
          </CardDescription>
        </div>
        <Button variant="ghost" size="icon" onClick={onRefresh} className="h-8 w-8 rounded-full hover:bg-primary/10">
          <RefreshCw className="h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[350px]">
          {news.length > 0 ? (
            <div className="divide-y divide-border/50">
              {news.map((item) => (
                <a
                  key={item.id}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-4 hover:bg-muted/30 transition-all font-medium"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-bold text-xs line-clamp-2 leading-snug">{item.title}</h4>
                    {item.relevance && item.relevance > 0.8 && (
                      <Badge className="shrink-0 text-[8px] bg-primary/10 text-primary border-none font-black uppercase tracking-widest">Hot</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-2 opacity-60">
                    <span className="text-[10px] uppercase font-black tracking-tight">{item.source}</span>
                    <span className="text-xs">•</span>
                    <span className="text-[10px] font-mono">
                      {formatRelativeTime(item.published_at)}
                    </span>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-12 text-center space-y-2 opacity-40">
              <Layers className="h-8 w-8" />
              <p className="text-[10px] uppercase font-black tracking-widest">Awaiting News Ingest</p>
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { isCheckingBackend, backendStatus, isWalletConnected } = useFluxo();
  const { data: portfolioData, isLoading: portfolioLoading } = usePortfolio();
  const { alerts: fetchedAlerts, isLoading: alertsLoading } = useAlerts();
  const { opportunities: fetchedYields, isLoading: yieldsLoading } = useYieldOpportunities();
  const { analysis: riskData, isLoading: riskLoading } = useRiskAnalysis();

  const [lastSyncTime, setLastSyncTime] = useState<string>('--:--:--');
  const [digest, setDigest] = useState<NewsItem[]>([]);
  const [digestLoading, setDigestLoading] = useState(true);
  const [digestError, setDigestError] = useState<string | null>(null);

  // Fallback Logic
  const alerts = fetchedAlerts.length > 0 ? fetchedAlerts : demoAlerts;
  const yields = fetchedYields.length > 0 ? fetchedYields : demoYields;

  const backendConnected = backendStatus.isConnected;

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

  useEffect(() => {
    setLastSyncTime(new Date().toLocaleTimeString());
    if (backendConnected) {
      fetchDigest();
    } else {
      setDigestLoading(false);
    }
  }, [backendConnected, fetchDigest]);

  // Real Data Mapping
  const assets: Asset[] = useMemo(() => {
    if (!portfolioData) return [];

    let rawAssets: any[] = [];
    if (Array.isArray(portfolioData)) {
      rawAssets = portfolioData;
    } else if (typeof portfolioData === 'object' && portfolioData !== null) {
      rawAssets = (portfolioData as any).assets || (portfolioData as any).result || (portfolioData as any).data || [];
    }

    const finalAssets = rawAssets.map((item: any) => ({
      token_address: item.token_address || item.address || '',
      token_symbol: item.token_symbol || item.symbol || 'TOKEN',
      balance: Number(item.balance) || 0,
      value_usd: Number(item.value_usd) || (Number(item.balance) * Number(item.price_usd || 0)) || 0,
      percentage: Number(item.percentage_of_portfolio) || 0,
      price: Number(item.price_usd) || 0,
    })).sort((a, b) => b.value_usd - a.value_usd);

    return finalAssets.length > 0 ? finalAssets : demoAssets;
  }, [portfolioData]);

  const totalValue = useMemo(() => assets.reduce((sum, a) => sum + a.value_usd, 0), [assets]);
  const unreadAlertsCount = alerts.filter(a => !a.delivered).length;

  // Format Risk Score
  const displayRisk = useMemo(() => {
    if (riskData?.risk_score) return `${riskData.risk_score.toFixed(1)} / 100`;
    if (riskData?.risk_level) return riskData.risk_level.toUpperCase();
    return '-- / 100';
  }, [riskData]);


  const loading = isCheckingBackend || alertsLoading || portfolioLoading || riskLoading;

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Intelligence Interface Header */}
      <div className="relative overflow-hidden rounded-3xl border border-primary/20 bg-gradient-to-br from-background via-muted/20 to-primary/5 p-8 md:p-12 shadow-2xl">
        <div className="absolute inset-0 pattern-grid opacity-10" />

        <div className="relative z-10 flex flex-col items-center text-center gap-6">
          <div className="relative group">
            <div className="absolute inset-0 bg-primary/30 blur-3xl rounded-full scale-150 group-hover:scale-175 transition-transform duration-700" />
            <div className="relative w-32 h-32 md:w-36 md:h-36 rounded-2xl overflow-hidden shadow-2xl border-4 border-primary/20 bg-background">
              <Image
                src="/fluxo-logo.jpg"
                alt="Fluxo Logo"
                fill
                className="object-cover"
                priority
              />
            </div>
          </div>

          <div className="flex flex-col items-center gap-2">
            <div className="flex items-center gap-3 bg-primary/10 px-4 py-1.5 rounded-full border border-primary/20">
              <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
              <span className="text-xl font-[family-name:var(--font-vt323)] text-primary uppercase tracking-[0.2em] drop-shadow-[0_0_8px_rgba(var(--primary),0.5)]">
                {backendConnected ? 'INTELLIGENCE ACTIVE' : 'RESTORE_OVERSIGHT_NODE'}
              </span>
            </div>
            <h1 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter leading-none mt-2 uppercase italic">
              Your private <span className="text-primary group-hover:animate-pulse">intelligence agent.</span>
            </h1>
            <p className="text-sm md:text-base text-muted-foreground max-w-xl font-medium mt-1 leading-relaxed opacity-80">
              Private intelligence monitoring. Portfolio tracking, risk analysis, and strategic execution.
            </p>
          </div>

          <div className="flex items-center gap-4">
            <Badge
              variant={backendConnected ? 'default' : 'outline'}
              className={cn(
                "rounded-full px-4 py-1.5 text-[10px] font-black uppercase tracking-widest border-none transition-all duration-500",
                backendConnected ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20" : "bg-muted text-muted-foreground opacity-50"
              )}
            >
              {backendConnected ? 'Systems Integrated' : 'Systems Restored'}
            </Badge>
            <span className="text-sm font-[family-name:var(--font-vt323)] text-muted-foreground uppercase tracking-widest px-3 py-1 bg-muted/30 rounded-lg">
              Last Sync: {lastSyncTime}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="VALUE LOCKED"
          value={formatCurrency(totalValue)}
          icon={<Wallet className="h-4 w-4 text-primary" />}
          loading={loading && assets === demoAssets}
          className="font-[family-name:var(--font-vt323)] text-3xl"
        />
        <StatCard
          title="ALPHA VECTORS"
          value={alerts.length.toString()}
          icon={<Bell className="h-4 w-4 text-primary" />}
          description={`${unreadAlertsCount} URGENT INTEL`}
          loading={loading && alerts === demoAlerts}
          className="font-[family-name:var(--font-vt323)] text-3xl"
        />
        <StatCard
          title="THREAT INDEX"
          value={displayRisk}
          icon={<Shield className="h-4 w-4 text-primary" />}
          loading={loading && !riskData}
          className="font-[family-name:var(--font-vt323)] text-3xl"
        />
        <StatCard
          title="YIELD NODES"
          value={yields.length.toString()}
          icon={<TrendingUp className="h-4 w-4 text-primary" />}
          description="ACTIVE STRATEGIES"
          loading={loading && yields === demoYields}
          className="font-[family-name:var(--font-vt323)] text-3xl"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-1">
        <PortfolioChart
          assets={assets}
          totalValue={totalValue}
          loading={loading && assets === demoAssets}
          title="ALLOCATION VECTORS"
        />
      </div>

      {/* Bottom Row - Alerts + Digest + Yields */}
      <div className="grid gap-6 lg:grid-cols-3">
        <RecentAlerts alerts={alerts.slice(0, 5)} loading={loading && alerts === demoAlerts} title="ALPHA LOG" />
        <DailyDigest
          news={digest}
          loading={digestLoading}
          error={digestError}
          onRefresh={fetchDigest}
        />
        <TopYields yields={yields.slice(0, 5)} loading={(loading || yieldsLoading) && yields === demoYields} title="YIELD NODES" />
      </div>

      {/* Premium Insights Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        <PremiumInsights />
        <Card className="relative overflow-hidden border-border/50 bg-background/50 rounded-3xl">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary/10 to-transparent rounded-bl-full" />
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-primary">
              <Shield className="h-4 w-4" />
              INFRA OVERSIGHT
            </CardTitle>
            <CardDescription className="text-[10px] font-bold">Node persistence and security metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 font-[family-name:var(--font-vt323)]">
              {[
                { label: 'Network Integration', value: 'Mantle Mainnet', status: 'verified' },
                { label: 'Security Clearance', value: 'High Level', status: 'secure' },
                { label: 'Data Latency', value: '< 2.4s', status: 'optimal' },
                { label: 'Wallet Persistence', value: 'Active Monitoring', status: 'live' }
              ].map((node) => (
                <div key={node.label} className="flex items-center justify-between p-4 rounded-2xl border border-border/50 bg-muted/20 group hover:bg-primary/5 transition-all">
                  <span className="text-xl uppercase tracking-widest text-muted-foreground opacity-60">{node.label}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl uppercase text-primary">{node.value}</span>
                    <div className="h-2 w-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(var(--primary),0.8)]" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
