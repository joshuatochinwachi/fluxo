'use client';

import { useState } from 'react';
import { useAccount } from 'wagmi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  Activity,
  Search,
  RefreshCw,
  ArrowUpRight,
  ExternalLink,
  Copy,
  Layers,
  Zap,
  Clock,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  formatCurrency,
  formatCompactNumber,
  formatRelativeTime,
  copyToClipboard,
  cn,
} from '@/lib/utils';
import { WhaleTransaction, Protocol } from '@/types';
import { useOnchainData, useWhaleTracking } from '@/hooks/useFluxo';

export default function OnchainPage() {
  const { } = useAccount();
  const [searchAddress, setSearchAddress] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const { protocols, isLoading: loadingOnchain, error: onchainError, refetchProtocols, refetchTransactions } = useOnchainData();
  const { movements: whaleMovements, isLoading: loadingWhales } = useWhaleTracking();

  const isLoading = loadingOnchain || loadingWhales;

  // Extract data from API responses
  const transactions = (whaleMovements || []) as WhaleTransaction[];
  const protocolList = (protocols || []) as Protocol[];
  const networkStats = {
    tps: 0,
    avgGas: 0,
    totalTxns: 0,
    activeAddresses: 0,
  } as { tps: number; avgGas: number; totalTxns: number; activeAddresses: number };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([refetchProtocols(), refetchTransactions()]);
    setIsRefreshing(false);
  };

  const totalTvl = protocolList.reduce((sum: number, p: Protocol) => sum + (p.tvl || 0), 0);

  if (isLoading && protocolList.length === 0 && transactions.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">On-Chain Analytics</h1>
            <p className="text-muted-foreground mt-1">Real-time blockchain data and whale tracking</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading on-chain data...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (onchainError) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">On-Chain Analytics</h1>
            <p className="text-muted-foreground mt-1">Real-time blockchain data and whale tracking</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <p className="text-muted-foreground mb-4">Failed to load on-chain data</p>
            <Button variant="outline" onClick={handleRefresh}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">On-Chain Analytics</h1>
          <p className="text-muted-foreground mt-1">Real-time blockchain data and whale tracking</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative flex-1 md:w-80">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search address or tx hash..."
              value={searchAddress}
              onChange={(e) => setSearchAddress(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
          </Button>
        </div>
      </div>

      {/* Network Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              <p className="text-sm text-muted-foreground">TPS</p>
            </div>
            <p className="text-2xl font-bold mt-2">{networkStats.tps || '--'}</p>
            <p className="text-xs text-green-500">Network healthy</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              <p className="text-sm text-muted-foreground">Avg Gas</p>
            </div>
            <p className="text-2xl font-bold mt-2">${networkStats.avgGas || '--'}</p>
            <p className="text-xs text-muted-foreground">Per transaction</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-purple-500" />
              <p className="text-sm text-muted-foreground">Total TVL</p>
            </div>
            <p className="text-2xl font-bold mt-2">{formatCompactNumber(totalTvl)}</p>
            <p className="text-xs text-green-500">+5.2% this week</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-orange-500" />
              <p className="text-sm text-muted-foreground">Active Addresses</p>
            </div>
            <p className="text-2xl font-bold mt-2">{formatCompactNumber(networkStats.activeAddresses || 0)}</p>
            <p className="text-xs text-muted-foreground">24h unique</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Whale Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Whale Transactions</CardTitle>
            <CardDescription>Large transfers ({'>'}$100k)</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              {transactions.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Activity className="h-8 w-8 mb-2" />
                  <p>No whale transactions detected</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {transactions.map((tx: WhaleTransaction) => (
                    <div
                      key={tx.id}
                      className="p-4 rounded-lg border border-border/50 transition-colors hover:bg-muted/50"
                    >
                      <div className="flex items-start gap-4">
                        <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
                          tx.type === 'transfer' ? 'bg-blue-500/10' : 'bg-purple-500/10'
                        }`}>
                          {tx.type === 'transfer' ? (
                            <ArrowUpRight className="h-5 w-5 text-blue-500" />
                          ) : (
                            <RefreshCw className="h-5 w-5 text-purple-500" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{formatCompactNumber(tx.amount)} {tx.token_symbol}</span>
                            <Badge variant="secondary" className="text-[10px]">{tx.type}</Badge>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span className="font-mono">{tx.from_address}</span>
                            <ArrowUpRight className="h-3 w-3" />
                            <span className="font-mono">{tx.to_address}</span>
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-sm font-medium">{formatCurrency(tx.value_usd)}</span>
                            <span className="text-xs text-muted-foreground">
                              {formatRelativeTime(tx.timestamp)}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => copyToClipboard(tx.transaction_hash)}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Protocols */}
        <Card>
          <CardHeader>
            <CardTitle>Mantle Protocols</CardTitle>
            <CardDescription>DeFi protocols by TVL</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              {protocolList.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Layers className="h-8 w-8 mb-2" />
                  <p>No protocol data available</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {protocolList
                    .sort((a: Protocol, b: Protocol) => (b.tvl || 0) - (a.tvl || 0))
                    .map((protocol: Protocol, index: number) => (
                    <div
                      key={protocol.slug}
                      className="p-4 rounded-lg border border-border/50 transition-colors hover:bg-muted/50"
                    >
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-muted-foreground w-6">#{index + 1}</span>
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <span className="font-bold text-primary text-sm">
                            {protocol.name.slice(0, 2).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{protocol.name}</p>
                            <Badge
                              variant={protocol.audit_status === 'audited' ? 'success' : 'warning'}
                              className="text-[10px]"
                            >
                              {protocol.audit_status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            APY: {protocol.apy_range?.[0] || 0}% - {protocol.apy_range?.[1] || 0}%
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{formatCompactNumber(protocol.tvl || 0)}</p>
                          <p className="text-xs text-muted-foreground">TVL</p>
                        </div>
                        <Button variant="ghost" size="icon">
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
