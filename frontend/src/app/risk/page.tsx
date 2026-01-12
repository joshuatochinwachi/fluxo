'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { useFluxo, useRiskAnalysis } from '@/hooks/useFluxo';
import { api } from '@/lib/api/client';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  FileText,
  Wallet,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { RiskFactor } from '@/types';

const getRiskLevel = (score: number) => {
  if (score <= 3) return { level: 'Low', color: 'text-green-500', bg: 'bg-green-500' };
  if (score <= 6) return { level: 'Medium', color: 'text-yellow-500', bg: 'bg-yellow-500' };
  if (score <= 8) return { level: 'High', color: 'text-orange-500', bg: 'bg-orange-500' };
  return { level: 'Critical', color: 'text-red-500', bg: 'bg-red-500' };
};




export default function RiskPage() {
  const { address, isWalletConnected, backendStatus, networkName } = useFluxo();
  const { analysis: riskResult, isLoading: isAnalyzing, refetch: analyze } = useRiskAnalysis();

  // Parse real risk factors from API response
  const riskFactors: RiskFactor[] = useMemo(() => {
    if (riskResult && typeof riskResult === 'object') {
      const factors = (riskResult as any).risk_factors;

      if (factors && typeof factors === 'object') {
        const factorEntries = Object.entries(factors);
        const totalFactors = factorEntries.length;

        return factorEntries.map(([name, score]) => ({
          name: name.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
          score: Number(score) || 0,
          weight: 1 / totalFactors,
          description: `Real-time ${name.replace(/_/g, ' ')} assessment`
        }));
      }
    }
    return [];
  }, [riskResult]);

  const recommendations = useMemo(() => {
    if (riskResult && (riskResult as any).recommendations) {
      const recs = (riskResult as any).recommendations as string[];
      if (Array.isArray(recs) && recs.length > 0) return recs;
    }
    return [];
  }, [riskResult]);

  const topHoldings = useMemo(() => {
    if (riskResult && (riskResult as any).top_holdings) {
      const holdings = (riskResult as any).top_holdings;
      if (Array.isArray(holdings)) return holdings;
    }
    return [];
  }, [riskResult]);

  const handleAnalyze = async () => {
    await analyze();
  };

  const overallScore = useMemo(() => {
    if (riskResult && (riskResult as any).risk_score) return (riskResult as any).risk_score;
    if (riskFactors.length > 0) {
      return riskFactors.reduce((sum, f) => sum + (f.score * (f.weight || 1 / riskFactors.length)), 0);
    }
    return 0;
  }, [riskResult, riskFactors]);

  const riskInfo = getRiskLevel(overallScore);

  if (!isWalletConnected) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 max-w-2xl mx-auto">
        <div className="h-24 w-24 bg-primary/10 rounded-full flex items-center justify-center shadow-2xl shadow-primary/20">
          <Shield className="h-12 w-12 text-primary animate-pulse" />
        </div>
        <div className="space-y-2">
          <h1 className="text-4xl font-black tracking-tighter uppercase">Risk Surveillance</h1>
          <p className="text-muted-foreground font-medium text-lg">
            Authorize your wallet to initialize the private risk assessment engine.
          </p>
        </div>
        <ConnectButton />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="relative overflow-hidden rounded-[2.5rem] bg-muted/20 border border-border/50 p-10 backdrop-blur-md group">
        <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
        <div className="absolute -bottom-12 -right-12 w-48 h-48 bg-primary/20 rounded-full blur-[80px] pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="px-4 py-1.5 border-primary/40 bg-primary/10 text-primary font-[family-name:var(--font-vt323)] text-xl tracking-widest uppercase">
                PROTECTION NODE v4.2
              </Badge>
              <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest opacity-60">SCAN ACTIVE</span>
              </div>
            </div>

            <h1 className="text-4xl md:text-6xl font-black tracking-tighter leading-none uppercase italic">
              Threat <span className="text-primary">Surveillance</span>
            </h1>
            <p className="max-w-xl text-sm md:text-base text-muted-foreground font-medium leading-relaxed opacity-80">
              Comprehensive wallet security analysis monitoring your portfolio health, risk exposure, and potential vulnerabilities in real-time.
            </p>
          </div>

          <div className="flex flex-col items-end gap-3">
            <Button
              className="rounded-2xl shadow-lg shadow-primary/20 font-black h-12 px-8 uppercase tracking-widest text-xs"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !backendStatus.isConnected}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Shield className="h-4 w-4 mr-2" />
                  Initialize Scan
                </>
              )}
            </Button>
            <span className="text-sm font-[family-name:var(--font-vt323)] text-muted-foreground uppercase tracking-widest px-3 py-1 bg-muted/30 rounded-lg">
              SYNC STATE: {backendStatus.isConnected ? 'INTEGRATED' : 'OFFLINE MODE'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Score & Metrics */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 border-border/50 bg-background/50 overflow-hidden rounded-3xl group">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row gap-10 items-center">
              <div className="relative">
                <div className={cn(
                  'h-48 w-48 rounded-full flex items-center justify-center border-8 border-background shadow-2xl transition-all duration-700',
                  riskResult ? riskInfo.bg + '/20' : 'bg-muted/10'
                )}>
                  <div className="text-center">
                    <p className={cn('text-6xl font-black tracking-tighter', riskResult ? riskInfo.color : 'text-muted-foreground/30')}>
                      {overallScore > 0 ? `${overallScore.toFixed(1)} / 100` : '--'}
                    </p>
                    <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Threat Index</p>
                  </div>
                </div>
              </div>

              <div className="flex-1 space-y-6">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Badge
                      className={cn(
                        "px-4 py-1 text-[10px] font-black uppercase tracking-widest border-none",
                        overallScore === 0 ? "bg-muted text-muted-foreground" :
                          riskInfo.level === 'Low' ? 'bg-green-500 text-white' :
                            riskInfo.level === 'Medium' ? 'bg-yellow-500 text-black' : 'bg-red-500 text-white'
                      )}
                    >
                      {riskResult ? `${riskInfo.level} Risk Profile` : 'Awaiting Analysis'}
                    </Badge>
                    {riskResult && (riskResult as any).market_condition && (
                      <Badge variant="outline" className="px-3 py-1 text-[9px] font-bold uppercase tracking-wider border-primary/30 text-primary">
                        {(riskResult as any).market_condition.replace(/_/g, ' ')}
                      </Badge>
                    )}
                  </div>
                  <h3 className="text-3xl font-black tracking-tighter uppercase leading-none">Portfolio Risk Exposure</h3>
                  <p className="text-sm text-muted-foreground font-medium mt-2 leading-relaxed">
                    Aggregate threat detection across {riskFactors.length || 'multiple'} vectors. This score represents your total probability of value impairment due to external smart contract failures or market anomalies.
                  </p>
                </div>

                <div className="flex gap-10 pt-4 border-t border-border/10">
                  <div className="space-y-1">
                    <p className="text-2xl font-black text-primary tracking-tighter">{recommendations.length}</p>
                    <p className="text-[10px] font-black text-muted-foreground uppercase tracking-tight">Active Recommendations</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-2xl font-black text-primary tracking-tighter">{topHoldings.length}</p>
                    <p className="text-[10px] font-black text-muted-foreground uppercase tracking-tight">Top Holdings</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actionable Recommendations */}
        <Card className="border-primary/20 bg-primary/5 rounded-3xl flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-black uppercase tracking-tight text-primary">
              <Zap className="h-4 w-4 fill-primary" />
              Strategic Directives
            </CardTitle>
            <CardDescription className="text-primary/70 font-bold text-[10px]">AI-generated risk mitigation steps</CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            <ScrollArea className="h-full">
              {recommendations.length > 0 ? (
                <div className="space-y-4">
                  {recommendations.map((rec, i) => (
                    <div key={i} className="flex gap-4 p-4 rounded-2xl border border-primary/10 shadow-sm list-item-glass">
                      <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-1">
                        <CheckCircle className="h-3 w-3 text-primary" />
                      </div>
                      <p className="text-xs font-bold leading-relaxed">{rec}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-48 text-center opacity-40">
                  <CheckCircle className="h-10 w-10 mb-2" />
                  <p className="text-[10px] font-black uppercase tracking-widest">No Threats Detected</p>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Top Holdings Section */}
      {topHoldings.length > 0 && (
        <Card className="border-border/50 bg-background/50 rounded-3xl">
          <CardHeader className="bg-muted/30 border-b border-border/50 p-6">
            <CardTitle className="text-sm font-black uppercase tracking-tight">Portfolio Concentration</CardTitle>
            <CardDescription className="text-[10px] font-bold">Top holdings by value and allocation percentage</CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              {topHoldings.map((holding: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 rounded-2xl border border-border/50 bg-muted/20 table-row-glass">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                      <span className="text-sm font-black text-primary">{holding.token?.slice(0, 2) || '??'}</span>
                    </div>
                    <div>
                      <p className="text-sm font-black uppercase tracking-tight">{holding.token || 'Unknown'}</p>
                      <p className="text-[10px] text-muted-foreground font-mono">{holding.token_address?.slice(0, 10)}...</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-black text-primary tracking-tighter">{holding.percentage?.toFixed(2)}%</p>
                    <p className="text-[10px] text-muted-foreground font-bold">${(holding.value_usd || 0).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Threat Vector Breakdown - Full Width */}
      <Card className="border-border/50 bg-background/50 rounded-3xl">
        <CardHeader className="bg-muted/30 border-b border-border/50 p-6">
          <CardTitle className="text-sm font-black uppercase tracking-tight">Threat Vector Breakdown</CardTitle>
          <CardDescription className="text-[10px] font-bold">Granular analysis of individual risk metrics</CardDescription>
        </CardHeader>
        <CardContent className="p-8">
          {isAnalyzing ? (
            <div className="grid gap-8 md:grid-cols-2">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="space-y-3">
                  <Skeleton className="h-4 w-40 bg-primary/5" />
                  <Skeleton className="h-2 w-full bg-primary/5" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid gap-8 md:grid-cols-2">
              {riskFactors.map((factor) => {
                const risk = getRiskLevel(factor.score);
                return (
                  <div key={factor.name} className="group/factor">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-black uppercase tracking-tight group-hover/factor:text-primary transition-colors">{factor.name}</span>
                        <Badge className="text-[9px] bg-muted text-muted-foreground border-none font-bold uppercase">
                          {(factor.weight * 100).toFixed(0)}% Impact
                        </Badge>
                      </div>
                      <span className={cn('text-lg font-black tracking-tighter', risk.color)}>
                        {factor.score.toFixed(1)}
                      </span>
                    </div>
                    <Progress
                      value={factor.score * 10}
                      className={cn('h-1.5 bg-muted/30', risk.bg)}
                    />
                    <p className="text-[11px] text-muted-foreground font-medium mt-2 leading-relaxed opacity-70">
                      {factor.description}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
