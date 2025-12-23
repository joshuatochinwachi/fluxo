'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import {
  PiggyBank,
  Shield,
  TrendingUp,
  ExternalLink,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import {
  formatCompactNumber,
  formatPercentage,
  cn,
} from '@/lib/utils';
import { YieldOpportunity } from '@/types';
import { useYieldOpportunities } from '@/hooks/useFluxo';

const getRiskLabel = (score: number) => {
  if (score <= 3) return { label: 'Low Risk', variant: 'success' as const };
  if (score <= 6) return { label: 'Medium Risk', variant: 'warning' as const };
  return { label: 'High Risk', variant: 'danger' as const };
};

export default function YieldPage() {
  const { opportunities, isLoading, error, refetch } = useYieldOpportunities();
  const [sortBy, setSortBy] = useState<'apy' | 'tvl' | 'risk'>('apy');
  const [filterRisk, setFilterRisk] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [isRefetching, setIsRefetching] = useState(false);

  // Extract yields from API response
  const yields = (opportunities || []) as YieldOpportunity[];

  const handleRefetch = async () => {
    setIsRefetching(true);
    await refetch();
    setIsRefetching(false);
  };

  const filteredYields = yields
    .filter((y: YieldOpportunity) => {
      if (filterRisk === 'all') return true;
      if (filterRisk === 'low') return y.risk_score <= 3;
      if (filterRisk === 'medium') return y.risk_score > 3 && y.risk_score <= 6;
      return y.risk_score > 6;
    })
    .sort((a: YieldOpportunity, b: YieldOpportunity) => {
      if (sortBy === 'apy') return b.apy - a.apy;
      if (sortBy === 'tvl') return b.tvl - a.tvl;
      return a.risk_score - b.risk_score;
    });

  const avgApy = yields.length > 0 
    ? yields.reduce((sum: number, y: YieldOpportunity) => sum + y.apy, 0) / yields.length 
    : 0;
  const totalTvl = yields.reduce((sum: number, y: YieldOpportunity) => sum + y.tvl, 0);
  const protocolCount = new Set(yields.map((y: YieldOpportunity) => y.protocol)).size;
  const lowRiskCount = yields.filter((y: YieldOpportunity) => y.risk_score <= 3).length;

  if (isLoading && yields.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Yield Opportunities</h1>
            <p className="text-muted-foreground mt-1">Find the best DeFi yields on Mantle</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Scanning yield opportunities...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Yield Opportunities</h1>
            <p className="text-muted-foreground mt-1">Find the best DeFi yields on Mantle</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <p className="text-muted-foreground mb-4">Failed to load yield opportunities</p>
            <Button variant="outline" onClick={() => refetch()}>
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
          <h1 className="text-3xl font-bold">Yield Opportunities</h1>
          <p className="text-muted-foreground mt-1">Find the best DeFi yields on Mantle</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleRefetch} disabled={isRefetching}>
            <RefreshCw className={cn("h-4 w-4 mr-2", isRefetching && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <PiggyBank className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">Total TVL</p>
            </div>
            <p className="text-2xl font-bold mt-2">{formatCompactNumber(totalTvl)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <p className="text-sm text-muted-foreground">Avg APY</p>
            </div>
            <p className="text-2xl font-bold mt-2">{formatPercentage(avgApy, 1).replace('+', '')}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-500" />
              <p className="text-sm text-muted-foreground">Protocols</p>
            </div>
            <p className="text-2xl font-bold mt-2">{protocolCount}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <p className="text-sm text-muted-foreground">Low Risk Pools</p>
            </div>
            <p className="text-2xl font-bold mt-2">{lowRiskCount}</p>
          </CardContent>
        </Card>
      </div>

      {/* Yield List */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Available Pools</CardTitle>
              <CardDescription>DeFi yield opportunities sorted by {sortBy.toUpperCase()}</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Tabs value={filterRisk} onValueChange={(v) => setFilterRisk(v as typeof filterRisk)}>
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="low">Low Risk</TabsTrigger>
                  <TabsTrigger value="medium">Medium</TabsTrigger>
                  <TabsTrigger value="high">High Risk</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 mb-4 pb-4 border-b">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <Button
              variant={sortBy === 'apy' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('apy')}
            >
              APY
            </Button>
            <Button
              variant={sortBy === 'tvl' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('tvl')}
            >
              TVL
            </Button>
            <Button
              variant={sortBy === 'risk' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('risk')}
            >
              Risk
            </Button>
          </div>
          <ScrollArea className="h-[500px]">
            {filteredYields.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <PiggyBank className="h-12 w-12 mb-4" />
                <p>No yield opportunities found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredYields.map((opportunity: YieldOpportunity, index: number) => {
                  const risk = getRiskLabel(opportunity.risk_score);
                  return (
                    <div
                      key={`${opportunity.protocol}-${opportunity.pool}-${index}`}
                      className="p-4 rounded-lg border border-border/50 transition-colors hover:bg-muted/50"
                    >
                      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                            <span className="font-bold text-primary">
                              {opportunity.protocol.slice(0, 2).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium">{opportunity.protocol}</p>
                              <ExternalLink className="h-3 w-3 text-muted-foreground" />
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {opportunity.token_pair?.join(' / ') || opportunity.pool}
                            </p>
                          </div>
                        </div>
                        <div className="flex flex-wrap items-center gap-6">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-green-500">
                              {formatPercentage(opportunity.apy, 1).replace('+', '')}
                            </p>
                            <p className="text-xs text-muted-foreground">APY</p>
                          </div>
                          <div className="text-center">
                            <p className="text-lg font-medium">{formatCompactNumber(opportunity.tvl)}</p>
                            <p className="text-xs text-muted-foreground">TVL</p>
                          </div>
                          <div className="text-center min-w-[100px]">
                            <div className="flex items-center gap-2 mb-1">
                              <Progress value={opportunity.risk_score * 10} className="h-2" />
                              <span className="text-sm">{opportunity.risk_score}/10</span>
                            </div>
                            <Badge variant={risk.variant} className="text-[10px]">
                              {risk.label}
                            </Badge>
                          </div>
                          <Button size="sm">Deposit</Button>
                        </div>
                      </div>
                      {opportunity.risk_score >= 6 && (
                        <div className="flex items-center gap-2 mt-3 p-2 rounded bg-yellow-500/10 text-yellow-500 text-sm">
                          <AlertTriangle className="h-4 w-4" />
                          <span>Higher risk - DYOR before investing</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
