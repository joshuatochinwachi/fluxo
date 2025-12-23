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
import { api } from '@/lib/api/client';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import {
  RefreshCw,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  ExternalLink,
  Copy,
  Wallet,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import {
  formatCurrency,
  formatCompactNumber,
  formatPercentage,
  formatAddress,
  getChangeColor,
  copyToClipboard,
} from '@/lib/utils';
import { Asset } from '@/types';

// Demo data fallback
const demoAssets: Asset[] = [
  { token_address: '0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8', token_symbol: 'MNT', balance: 10000, value_usd: 8500, percentage: 42.5, price: 0.85, change_24h: 3.2 },
  { token_address: '0xdEAddEaDdeadDEadDEADDEAddEADDEAddead1111', token_symbol: 'ETH', balance: 2.5, value_usd: 8750, percentage: 43.75, price: 3500, change_24h: -1.5 },
  { token_address: '0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9', token_symbol: 'USDC', balance: 2000, value_usd: 2000, percentage: 10, price: 1, change_24h: 0.01 },
  { token_address: '0x201EBa5CC46D216Ce6DC03F6a759e8E766e956aE', token_symbol: 'USDT', balance: 750, value_usd: 750, percentage: 3.75, price: 1, change_24h: -0.02 },
];

const demoTransactions = [
  { id: '1', type: 'receive', token: 'MNT', amount: 500, value_usd: 425, from: '0x123...abc', timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString() },
  { id: '2', type: 'send', token: 'ETH', amount: 0.5, value_usd: 1750, to: '0x456...def', timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString() },
  { id: '3', type: 'swap', tokenIn: 'USDC', tokenOut: 'MNT', amountIn: 1000, amountOut: 1176, timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString() },
  { id: '4', type: 'receive', token: 'USDT', amount: 250, value_usd: 250, from: '0x789...ghi', timestamp: new Date(Date.now() - 1000 * 60 * 360).toISOString() },
];

interface InsightsState {
  isLoading: boolean;
  data: Record<string, unknown> | null;
  error: string | null;
}

export default function PortfolioPage() {
  const { address, isWalletConnected, backendStatus, networkName, currentChain } = useFluxo();
  const { data: portfolioData, isLoading: portfolioLoading, refetch } = usePortfolio();
  const [refreshing, setRefreshing] = useState(false);
  const [transactions, setTransactions] = useState<typeof demoTransactions>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [insights, setInsights] = useState<InsightsState>({ isLoading: false, data: null, error: null });

  // Parse portfolio data
  const assets: Asset[] = portfolioData && typeof portfolioData === 'object' && 'assets' in portfolioData
    ? (portfolioData as { assets: Asset[] }).assets
    : demoAssets;
  
  const isUsingDemo = !isWalletConnected || !backendStatus.isConnected || !portfolioData;

  // Fetch transactions when wallet is connected
  const fetchTransactions = useCallback(async () => {
    if (!address || !backendStatus.isConnected) return;
    
    setTransactionsLoading(true);
    try {
      const response = await api.onchain.transactions(address);
      if (response.data && Array.isArray(response.data)) {
        setTransactions(response.data as typeof demoTransactions);
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    } finally {
      setTransactionsLoading(false);
    }
  }, [address, backendStatus.isConnected]);

  // Fetch AI insights
  const fetchInsights = useCallback(async (quick = false) => {
    if (!address || !backendStatus.isConnected) return;
    
    setInsights(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = quick
        ? await api.portfolio.quickInsights(address)
        : await api.portfolio.getInsights(address, networkName);
      
      setInsights({
        isLoading: false,
        data: response.data as Record<string, unknown>,
        error: null,
      });
    } catch (err) {
      setInsights({
        isLoading: false,
        data: null,
        error: err instanceof Error ? err.message : 'Failed to get insights',
      });
    }
  }, [address, backendStatus.isConnected, networkName]);

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

  const totalValue = assets.reduce((sum, asset) => sum + asset.value_usd, 0);
  const totalChange = assets.reduce((sum, asset) => sum + (asset.change_24h || 0) * asset.percentage / 100, 0);
  const displayTransactions = transactions.length > 0 ? transactions : demoTransactions;

  // Show connect wallet prompt if not connected
  if (!isWalletConnected) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4">
          <h1 className="text-3xl font-bold">Portfolio</h1>
          <p className="text-muted-foreground">Track and manage your assets</p>
        </div>
        
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-6">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Wallet className="h-8 w-8 text-primary" />
            </div>
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Connect Your Wallet</h3>
              <p className="text-muted-foreground max-w-md">
                Connect your wallet to view your portfolio, track your assets, and get AI-powered insights.
              </p>
            </div>
            <ConnectButton />
          </CardContent>
        </Card>

        {/* Show demo data preview */}
        <div className="opacity-60">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-lg font-medium">Demo Preview</h2>
            <Badge variant="outline">Sample Data</Badge>
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Assets</CardTitle>
                  <CardDescription>Connect wallet to see your holdings</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {demoAssets.slice(0, 2).map((asset) => (
                      <div key={asset.token_address} className="flex items-center gap-4 p-4 rounded-lg border border-border/50 opacity-75">
                        <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="font-bold text-primary">{asset.token_symbol.slice(0, 2)}</span>
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{asset.token_symbol}</p>
                          <p className="text-sm text-muted-foreground">{formatCompactNumber(asset.balance)} tokens</p>
                        </div>
                        <p className="font-medium">{formatCurrency(asset.value_usd)}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
            <PortfolioChart assets={demoAssets} totalValue={20000} loading={false} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolio</h1>
          <p className="text-muted-foreground mt-1">Track and manage your assets</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={backendStatus.isConnected ? 'success' : 'warning'}>
            {backendStatus.isConnected ? '● Live' : '○ Demo Mode'}
          </Badge>
          <Button
            variant="outline"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Wallet Info */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">W</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm">{formatAddress(address || '', 6)}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => address && copyToClipboard(address)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-6 w-6" asChild>
                    <a 
                      href={`https://explorer.mantle.xyz/address/${address}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">{currentChain?.name || 'Mantle Network'}</p>
              </div>
            </div>
            <div className="text-right">
              {portfolioLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-8 w-32 ml-auto" />
                  <Skeleton className="h-4 w-24 ml-auto" />
                </div>
              ) : (
                <>
                  <p className="text-3xl font-bold">{formatCurrency(totalValue)}</p>
                  <div className="flex items-center justify-end gap-1 mt-1">
                    {totalChange >= 0 ? (
                      <TrendingUp className={`h-4 w-4 ${getChangeColor(totalChange)}`} />
                    ) : (
                      <TrendingDown className={`h-4 w-4 ${getChangeColor(totalChange)}`} />
                    )}
                    <span className={`text-sm font-medium ${getChangeColor(totalChange)}`}>
                      {formatPercentage(totalChange)} (24h)
                    </span>
                    {isUsingDemo && <Badge variant="outline" className="text-[10px] ml-2">Demo</Badge>}
                  </div>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Insights Section */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              AI Portfolio Insights
            </CardTitle>
            <CardDescription>Get AI-powered analysis of your portfolio</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchInsights(true)}
              disabled={insights.isLoading || !backendStatus.isConnected}
            >
              Quick Analysis
            </Button>
            <Button
              size="sm"
              onClick={() => fetchInsights(false)}
              disabled={insights.isLoading || !backendStatus.isConnected}
            >
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
          <CardContent>
            <div className="p-4 bg-background rounded-lg border">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(insights.data, null, 2)}
              </pre>
            </div>
          </CardContent>
        )}
        {insights.error && (
          <CardContent>
            <div className="flex items-center gap-2 text-yellow-500">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{insights.error}</span>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Assets List */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Assets</CardTitle>
              <CardDescription>
                {isUsingDemo ? 'Sample holdings (connect backend for real data)' : 'Your token holdings'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {portfolioLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex items-center gap-4 p-4">
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
                <div className="space-y-4">
                  {assets.map((asset) => (
                    <div
                      key={asset.token_address}
                      className="flex items-center gap-4 p-4 rounded-lg border border-border/50 transition-colors hover:bg-muted/50"
                    >
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <span className="font-bold text-primary">{asset.token_symbol.slice(0, 2)}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{asset.token_symbol}</p>
                          <Badge variant="secondary" className="text-[10px]">
                            {formatPercentage(asset.percentage, 1).replace('+', '')}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {formatCompactNumber(asset.balance)} tokens
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{formatCurrency(asset.value_usd)}</p>
                        <div className="flex items-center justify-end gap-1">
                          {(asset.change_24h || 0) >= 0 ? (
                            <ArrowUpRight className={`h-3 w-3 ${getChangeColor(asset.change_24h || 0)}`} />
                          ) : (
                            <ArrowDownRight className={`h-3 w-3 ${getChangeColor(asset.change_24h || 0)}`} />
                          )}
                          <span className={`text-xs ${getChangeColor(asset.change_24h || 0)}`}>
                            {formatPercentage(asset.change_24h || 0)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
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
      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
          <CardDescription>
            {transactions.length > 0 ? 'Your latest activity' : 'Sample transactions (connect for real data)'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all">
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="send">Sent</TabsTrigger>
              <TabsTrigger value="receive">Received</TabsTrigger>
              <TabsTrigger value="swap">Swaps</TabsTrigger>
            </TabsList>
            <TabsContent value="all" className="mt-4">
              <ScrollArea className="h-[300px]">
                {transactionsLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="flex items-center gap-4 p-3">
                        <Skeleton className="h-8 w-8 rounded-full" />
                        <div className="flex-1 space-y-2">
                          <Skeleton className="h-4 w-20" />
                          <Skeleton className="h-3 w-32" />
                        </div>
                        <Skeleton className="h-4 w-16" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {displayTransactions.map((tx) => (
                      <div
                        key={tx.id}
                        className="flex items-center gap-4 p-3 rounded-lg border border-border/50"
                      >
                        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                          tx.type === 'receive' ? 'bg-green-500/10' :
                          tx.type === 'send' ? 'bg-red-500/10' : 'bg-blue-500/10'
                        }`}>
                          {tx.type === 'receive' && <ArrowDownRight className="h-4 w-4 text-green-500" />}
                          {tx.type === 'send' && <ArrowUpRight className="h-4 w-4 text-red-500" />}
                          {tx.type === 'swap' && <RefreshCw className="h-4 w-4 text-blue-500" />}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium capitalize">{tx.type}</p>
                          <p className="text-sm text-muted-foreground">
                            {tx.type === 'swap' 
                              ? `${tx.amountIn} ${tx.tokenIn} → ${tx.amountOut} ${tx.tokenOut}`
                              : `${tx.amount} ${tx.token}`
                            }
                          </p>
                        </div>
                        <div className="text-right">
                          {tx.value_usd && (
                            <p className="font-medium">{formatCurrency(tx.value_usd)}</p>
                          )}
                          <p className="text-xs text-muted-foreground">
                            {new Date(tx.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
