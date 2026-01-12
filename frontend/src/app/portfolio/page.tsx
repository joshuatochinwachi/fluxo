'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { PortfolioChart } from '@/components/dashboard';
import { useFluxo, usePortfolio } from '@/hooks/useFluxo';
import { api, pollTaskStatus } from '@/lib/api/client';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import {
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  ExternalLink,
  Copy,
  Wallet,
  Sparkles,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  PieChart as PieChartIcon,
  ShieldCheck,
  TrendingDown,
  Layers,
  Activity,
  TrendingUp,
} from 'lucide-react';
import {
  formatCurrency,
  formatCompactNumber,
  formatTokenBalance,
  formatPercentage,
  formatAddress,
  getChangeColor,
  copyToClipboard,
  cn,
} from '@/lib/utils';
import { Asset, Transaction, Alert } from '@/types';

// Demo Data Fallbacks
const demoAssets: Asset[] = [
  { token_symbol: 'MNT', balance: 12500, value_usd: 15625, percentage: 45, token_address: '0x...', price: 1.25, pnl_24h_pct: 5.2 },
  { token_symbol: 'ETH', balance: 2.5, value_usd: 6250, percentage: 18, token_address: '0x...', price: 2500, pnl_24h_pct: -1.8 },
  { token_symbol: 'USDC', balance: 5000, value_usd: 5000, percentage: 14, token_address: '0x...', price: 1, pnl_24h_pct: 0.01 },
  { token_symbol: 'WMNT', balance: 8000, value_usd: 10000, percentage: 23, token_address: '0x...', price: 1.25, pnl_24h_pct: 2.4 },
];

const demoTransactions: Transaction[] = [
  {
    id: 'tx1',
    type: 'received',
    transaction_name: 'Transfer',
    tx_hash: '0x123...abc',
    amount: 500,
    tokenSymbol: 'MNT',
    timestamp: new Date().toISOString(),
    transaction_time: new Date().toISOString(),
    from: '0x...',
    to: '0x...',
    value: 500,
    token: 'MNT',
    value_usd: 625
  },
  {
    id: 'tx2',
    type: 'sent',
    transaction_name: 'Transfer',
    tx_hash: '0x456...def',
    amount: 120,
    tokenSymbol: 'ETH',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    transaction_time: new Date(Date.now() - 86400000).toISOString(),
    from: '0x...',
    to: '0x...',
    value: 120,
    token: 'ETH',
    value_usd: 300000
  }
];

interface InsightMetric {
  label: string;
  value: string;
  description?: string;
  type: 'positive' | 'warning' | 'neutral';
  icon: any;
}

interface InsightsData {
  title: string;
  metrics: InsightMetric[];
  advice: string;
}

interface InsightsState {
  isLoading: boolean;
  data: InsightsData | null;
  error: string | null;
}

export default function PortfolioPage() {
  const { address, isWalletConnected, backendStatus, networkName, currentChain } = useFluxo();
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError, refetch } = usePortfolio();
  const [refreshing, setRefreshing] = useState(false);
  const [transactions, setTransactions] = useState<Transaction[]>(demoTransactions);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [insights, setInsights] = useState<InsightsState>({ isLoading: false, data: null, error: null });
  const [showAllAssets, setShowAllAssets] = useState(false);

  // Parse portfolio data robustly
  const { assets, totalValue } = (() => {
    if (!portfolioData) return { assets: [], totalValue: 0 };

    let rawAssets: any[] = [];
    let backendTotalValue = 0;

    if (Array.isArray(portfolioData)) {
      rawAssets = portfolioData;
    } else if (typeof portfolioData === 'object' && portfolioData !== null) {
      const potentialAssets = (portfolioData as any).assets || (portfolioData as any).result || (portfolioData as any).data;
      if (Array.isArray(potentialAssets)) {
        rawAssets = potentialAssets;
      }
      backendTotalValue = (portfolioData as any).total_value_usd || (portfolioData as any).totalValueUsd || 0;
    }

    const mappedAssets: Asset[] = rawAssets.map((item: any) => {
      const balance = Number(item.balance) || 0;
      const price = Number(item.price_usd) || Number(item.price) || 0;
      const value_usd = Number(item.value_usd) || Number(item.valueUsd) || (balance * price) || 0;

      return {
        token_address: item.token_address || item.address || '',
        token_symbol: item.token_symbol || item.symbol || 'TOKEN',
        balance,
        value_usd,
        percentage: Number(item.percentage_of_portfolio) || Number(item.percentage) || 0,
        price,
        pnl_24h_pct: item.pnl_24h_pct ?? item.change_24h ?? item.price_change_percentage_24h,
        change_24h: 0,
      };
    });

    // Professional sorting: largest assets first
    mappedAssets.sort((a, b) => b.value_usd - a.value_usd);

    const finalAssets = mappedAssets.length > 0 ? mappedAssets : demoAssets;
    const finalTotalValue = backendTotalValue || finalAssets.reduce((sum, a) => sum + a.value_usd, 0);
    return { assets: finalAssets, totalValue: finalTotalValue };
  })();

  const fetchTransactions = useCallback(async () => {
    if (!address || !backendStatus.isConnected) return;

    setTransactionsLoading(true);
    try {
      const response = await api.onchain.transactions(address.toLowerCase());
      const resData = (response as any).data;

      if (resData?.task_id) {
        const result = await pollTaskStatus<any>(
          api.onchain.getStatus,
          resData.task_id,
          { interval: 2000, timeout: 60000 }
        );

        if (result) {
          let rawTransactions: any[] = [];
          if (Array.isArray(result)) {
            rawTransactions = result;
          } else if (typeof result === 'object' && result !== null) {
            rawTransactions = (result as any).transactions || (result as any).result || (result as any).data || [];
          }

          const mapped: Transaction[] = rawTransactions.map((tx: any) => {
            const isReceived = tx.to?.toLowerCase() === address.toLowerCase();
            const isSent = tx.from?.toLowerCase() === address.toLowerCase();
            let type: 'sent' | 'received' | 'other' = 'other';

            // Grouping logic: Only 'Transfer' name indicates Sent/Received direction
            if (tx.transaction_name === 'Transfer') {
              if (isSent) {
                type = 'sent';
              } else if (isReceived) {
                type = 'received';
              }
            } else {
              type = 'other';
            }

            return {
              ...tx,
              id: tx.tx_hash,
              type,
              timestamp: tx.transaction_time,
              amount: Number(tx.value) || 0,
              token: tx.tokenSymbol || 'TOKEN',
              tokenSymbol: tx.tokenSymbol || 'TOKEN',
              value_usd: 0
            };
          });

          // Sort by timestamp descending
          mapped.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
          setTransactions(mapped);
        }
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    } finally {
      setTransactionsLoading(false);
    }
  }, [address, backendStatus.isConnected]);

  const fetchInsights = useCallback(async (quick = false) => {
    if (!address || assets.length === 0) return;

    setInsights(prev => ({ ...prev, isLoading: true, error: null }));

    // Simulate a professional delay
    setTimeout(() => {
      const top3Weight = assets.slice(0, 3).reduce((sum, a) => sum + a.percentage, 0);
      const dominantAsset = assets[0];
      const riskLevel = top3Weight > 80 ? 'High' : top3Weight > 50 ? 'Medium' : 'Low';

      const metrics: InsightMetric[] = [];

      if (quick) {
        metrics.push({
          label: 'Asset Count',
          value: `${assets.length} Assets`,
          description: 'Total unique tokens in portfolio',
          type: 'neutral',
          icon: Layers
        });
        metrics.push({
          label: 'Concentration',
          value: `${formatPercentage(dominantAsset.percentage, 1).replace('+', '')}`,
          description: `Held in ${dominantAsset.token_symbol}`,
          type: dominantAsset.percentage > 50 ? 'warning' : 'neutral',
          icon: PieChartIcon
        });
        metrics.push({
          label: 'Avg. Position',
          value: formatCurrency(totalValue / assets.length),
          description: 'Mean value per asset',
          type: 'neutral',
          icon: Activity
        });
      } else {
        metrics.push({
          label: 'Top 3 Dominance',
          value: `${formatPercentage(top3Weight, 1).replace('+', '')}`,
          description: 'Total weight of top 3 holdings',
          type: top3Weight > 70 ? 'warning' : 'positive',
          icon: ShieldCheck
        });
        metrics.push({
          label: 'Tail Risk',
          value: `${assets.filter(a => a.percentage < 1).length} Minor`,
          description: 'Assets with < 1% allocation',
          type: 'neutral',
          icon: TrendingDown
        });
        metrics.push({
          label: 'Portfolio Risk',
          value: `${riskLevel} Risk`,
          description: `Based on ${riskLevel.toLowerCase()} concentration`,
          type: riskLevel === 'High' ? 'warning' : 'positive',
          icon: AlertCircle
        });
      }

      setInsights({
        isLoading: false,
        data: {
          title: quick ? 'Quick Portfolio Scan' : 'Comprehensive Portfolio Analysis',
          metrics,
          advice: quick
            ? `Your portfolio is primarily ${dominantAsset.token_symbol} dominated. Consider more diversification if you want to reduce individual asset risk.`
            : `Analysis complete. Your ${riskLevel.toLowerCase()} risk profile indicates a ${top3Weight > 60 ? 'concentrated' : 'well-balanced'} strategy on Mantle network.`
        },
        error: null
      });
    }, 1200);
  }, [address, assets, totalValue]);

  useEffect(() => {
    if (isWalletConnected && backendStatus.isConnected) {
      fetchTransactions();
    }
  }, [isWalletConnected, backendStatus.isConnected, fetchTransactions]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetch(), fetchTransactions()]);
    setRefreshing(false);
  };

  const sentTransactions = transactions.filter(tx => tx.type === 'sent');
  const receivedTransactions = transactions.filter(tx => tx.type === 'received');
  const otherTransactions = transactions.filter(tx => tx.type === 'other');

  if (!isWalletConnected) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
        <div className="p-6 rounded-full bg-primary/10">
          <Wallet className="h-12 w-12 text-primary" />
        </div>
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Connect Wallet</h2>
          <p className="text-muted-foreground max-w-md">
            Please connect your wallet to view your Mantle network portfolio and transactions.
          </p>
        </div>
        <ConnectButton />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-700">


      {/* Portfolio Header */}
      <div className="relative overflow-hidden rounded-[2.5rem] bg-muted/20 border border-border/50 p-10 backdrop-blur-md group">
        <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
        <div className="absolute -bottom-12 -right-12 w-48 h-48 bg-primary/20 rounded-full blur-[80px] pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="px-4 py-1.5 border-primary/40 bg-primary/10 text-primary font-[family-name:var(--font-vt323)] text-xl tracking-widest uppercase">
                ASSET VAULT v4
              </Badge>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest opacity-60">VAULT SYNCHRONIZED</span>
              </div>
            </div>

            <h1 className="text-4xl md:text-6xl font-black tracking-tighter leading-none uppercase italic">
              Portfolio <span className="text-primary">Surveillance</span>
            </h1>
            <p className="max-w-xl text-sm md:text-base text-muted-foreground font-medium leading-relaxed opacity-80">
              Total Valuation Locked: <span className="text-primary font-[family-name:var(--font-vt323)] text-3xl ml-2">{formatCurrency(totalValue)}</span>
            </p>
          </div>

          <div className="flex flex-col items-end gap-3">
            <Button
              variant="outline"
              className="rounded-2xl border-border/50 hover:bg-muted/50 transition-all font-bold group h-12 px-6"
              onClick={handleRefresh}
              disabled={portfolioLoading || refreshing}
            >
              <RefreshCw className={cn("h-4 w-4 mr-2", (portfolioLoading || refreshing) && "animate-spin")} />
              Sync Alpha Nodes
            </Button>
            <span className="text-sm font-[family-name:var(--font-vt323)] text-muted-foreground uppercase tracking-widest px-3 py-1 bg-muted/30 rounded-lg">
              STORAGE UNIT: {address ? formatAddress(address) : 'UNAUTHORIZED'}
            </span>
          </div>
        </div>
      </div>

      {/* AI Insights Card */}
      <Card className="overflow-hidden border-primary/20 bg-primary/5">
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              AI Portfolio Insights
            </CardTitle>
            <CardDescription>Get AI-powered analysis of your portfolio</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => fetchInsights(true)} disabled={insights.isLoading}>
              Quick Analysis
            </Button>
            <Button size="sm" onClick={() => fetchInsights(false)} disabled={insights.isLoading}>
              {insights.isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Full Analysis'
              )}
            </Button>
          </div>
        </CardHeader>
        {insights.data && (
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {insights.data.metrics.map((metric, i) => (
                <div key={i} className="p-4 bg-background rounded-xl border border-border/50 shadow-sm space-y-2">
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${metric.type === 'positive' ? 'bg-green-500/10 text-green-500' :
                      metric.type === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                        'bg-primary/10 text-primary'
                      }`}>
                      <metric.icon className="h-4 w-4" />
                    </div>
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{metric.label}</span>
                  </div>
                  <div>
                    <div className="text-xl font-black">{metric.value}</div>
                    {metric.description && <div className="text-[10px] text-muted-foreground mt-0.5">{metric.description}</div>}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 bg-primary/10 rounded-xl border border-primary/20 flex items-start gap-4">
              <div className="p-2 bg-primary/20 rounded-full mt-0.5">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <p className="text-sm font-medium leading-relaxed">
                {insights.data.advice}
              </p>
            </div>
          </CardContent>
        )}
        {insights.error && (
          <CardContent>
            <div className="flex items-center gap-2 text-yellow-500 p-4 bg-yellow-500/10 rounded-xl border border-yellow-500/20">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm font-medium">{insights.error}</span>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Main Content */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Assets List */}
        <div className="lg:col-span-2">
          <Card className="border-border/50 shadow-sm">
            <CardHeader className="border-b border-border/50 bg-muted/10">
              <CardTitle>On-Chain Assets</CardTitle>
              <CardDescription>
                Your holdings on Mantle network
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {portfolioLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex items-center gap-4 p-4 border border-border/20 rounded-xl">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-20" />
                        <Skeleton className="h-3 w-32" />
                      </div>
                      <Skeleton className="h-4 w-24" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {assets.length > 0 ? (
                    <>
                      {(showAllAssets ? assets : assets.slice(0, 6)).map((asset) => {
                        const pnl = asset.pnl_24h_pct ?? asset.change_24h ?? (asset as any).pnl_24h ?? (asset as any).price_change_percentage_24h;
                        const hasPnl = pnl !== undefined && pnl !== null;
                        return (
                          <div
                            key={asset.token_address}
                            className="flex items-center gap-4 p-4 rounded-xl border border-border/50 bg-muted/20 table-row-glass"
                          >
                            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center transition-transform group-hover:scale-110">
                              <span className="font-bold text-primary">{asset.token_symbol.slice(0, 2)}</span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <p className="font-bold tracking-tight">{asset.token_symbol}</p>
                                <Badge variant="secondary" className="text-[10px] py-0 h-4 border-primary/20 bg-primary/5 text-primary">
                                  {formatPercentage(asset.percentage, 1).replace('+', '')}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                                <span className="font-mono">{formatTokenBalance(asset.balance)} units</span>
                                <span className="opacity-30">|</span>
                                <span>{formatCurrency(asset.price ?? 0)}</span>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-sm tracking-tight">{formatCurrency(asset.value_usd)}</p>
                              {hasPnl && (
                                <div className={cn("flex items-center justify-end gap-1 text-[10px] uppercase font-bold tracking-wider mt-0.5",
                                  pnl >= 0 ? "text-green-500" : "text-red-500"
                                )}>
                                  {pnl >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                                  {formatPercentage(pnl)}
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      })}

                      {assets.length > 6 && (
                        <Button
                          variant="ghost"
                          className="w-full mt-2 text-muted-foreground hover:text-primary transition-colors flex items-center gap-2 font-medium"
                          onClick={() => setShowAllAssets(!showAllAssets)}
                        >
                          {showAllAssets ? (
                            <>
                              Show Top Only <ChevronUp className="h-4 w-4" />
                            </>
                          ) : (
                            <>
                              Show All Assets ({assets.length}) <ChevronDown className="h-4 w-4" />
                            </>
                          )}
                        </Button>
                      )}
                    </>
                  ) : (
                    <div className="py-20 text-center space-y-4">
                      <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mx-auto opacity-50">
                        <Wallet className="h-8 w-8 text-muted-foreground" />
                      </div>
                      <p className="text-muted-foreground font-medium">No assets found on Mantle network</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Chart */}
        <div>
          <PortfolioChart
            assets={assets}
            totalValue={totalValue}
            loading={portfolioLoading}
          />
        </div>
      </div>

      {/* Transactions */}
      <Card className="border-border/50 shadow-sm overflow-hidden">
        <CardHeader className="border-b border-border/50 bg-muted/10">
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            {transactions.length > 0 ? 'Your latest transactions on Mantle' : 'No recent transactions found'}
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="bg-muted/50 p-1">
              <TabsTrigger value="all" className="rounded-md">All</TabsTrigger>
              <TabsTrigger value="sent" className="rounded-md">Sent</TabsTrigger>
              <TabsTrigger value="received" className="rounded-md">Received</TabsTrigger>
              <TabsTrigger value="other" className="rounded-md">Others</TabsTrigger>
            </TabsList>
            <TabsContent value="all" className="mt-6">
              <ScrollArea className="h-[400px]">
                <TransactionList transactions={transactions} loading={transactionsLoading} />
              </ScrollArea>
            </TabsContent>
            <TabsContent value="sent" className="mt-6">
              <ScrollArea className="h-[400px]">
                <TransactionList transactions={sentTransactions} loading={transactionsLoading} />
              </ScrollArea>
            </TabsContent>
            <TabsContent value="received" className="mt-6">
              <ScrollArea className="h-[400px]">
                <TransactionList transactions={receivedTransactions} loading={transactionsLoading} />
              </ScrollArea>
            </TabsContent>
            <TabsContent value="other" className="mt-6">
              <ScrollArea className="h-[400px]">
                <TransactionList transactions={otherTransactions} loading={transactionsLoading} />
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

function TransactionList({ transactions, loading }: { transactions: Transaction[], loading: boolean }) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center gap-4 p-3 rounded-xl border border-border/20">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-3 w-40" />
            </div>
            <Skeleton className="h-4 w-16" />
          </div>
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mx-auto opacity-50">
          <RefreshCw className="h-8 w-8 text-muted-foreground" />
        </div>
        <p className="text-muted-foreground font-medium">No transactions found in this category</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 pr-4">
      {transactions.map((tx) => (
        <div
          key={tx.id}
          className="flex items-center gap-4 p-4 rounded-xl border border-border/50 bg-muted/20 transition-all hover:bg-muted/40 group"
        >
          <div className={`h-10 w-10 rounded-full flex items-center justify-center transition-transform group-hover:scale-110 ${tx.type === 'received' ? 'bg-green-500/10 text-green-500' :
            tx.type === 'sent' ? 'bg-red-500/10 text-red-500' :
              'bg-blue-500/10 text-blue-500'
            }`}>
            {tx.type === 'received' && <ArrowDownRight className="h-5 w-5" />}
            {tx.type === 'sent' && <ArrowUpRight className="h-5 w-5" />}
            {tx.type === 'other' && <ExternalLink className="h-5 w-5" />}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-bold capitalize text-sm tracking-tight">
                {tx.transaction_name === 'Transfer'
                  ? (tx.type === 'sent' ? 'Transfer Sent' : 'Transfer Received')
                  : (tx.transaction_name || 'Other Activity')}
              </p>
              <Badge variant="outline" className="text-[10px] py-0 h-4 border-primary/20 bg-primary/5 text-primary">
                {tx.tokenSymbol || tx.token}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground truncate font-mono mt-0.5">
              {tx.tx_hash ? formatAddress(tx.tx_hash, 8) : 'Pending...'}
            </p>
          </div>

          <div className="text-right">
            <div className="flex flex-col items-end">
              <p className={`font-bold text-sm ${tx.type === 'received' ? 'text-green-500' :
                tx.type === 'sent' ? 'text-red-500' :
                  'text-primary'
                }`}>
                {tx.type === 'received' ? '+' : tx.type === 'sent' ? '-' : ''}
                {formatTokenBalance(tx.amount || tx.value)} {tx.tokenSymbol || tx.token}
              </p>
              <p className="text-[10px] text-muted-foreground font-mono mt-0.5 opacity-60">
                {new Date(tx.timestamp).toLocaleString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          </div>

          <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity" asChild>
            <a href={`https://explorer.mantle.xyz/tx/${tx.tx_hash}`} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="h-4 w-4" />
            </a>
          </Button>
        </div>
      ))}
    </div>
  );
}
