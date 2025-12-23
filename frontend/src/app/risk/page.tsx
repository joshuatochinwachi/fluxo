'use client';

import { useState, useEffect, useCallback } from 'react';
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
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { RiskFactor } from '@/types';

// Demo risk data
const demoRiskFactors: RiskFactor[] = [
  { name: 'Concentration Risk', score: 7.5, weight: 0.25, description: 'Portfolio heavily concentrated in 2 assets' },
  { name: 'Smart Contract Risk', score: 4.2, weight: 0.2, description: 'Most protocols are audited' },
  { name: 'Market Volatility', score: 6.8, weight: 0.2, description: 'High correlation with BTC movements' },
  { name: 'Liquidity Risk', score: 3.5, weight: 0.15, description: 'Good liquidity in major pairs' },
  { name: 'Protocol Risk', score: 5.0, weight: 0.2, description: 'Mix of established and newer protocols' },
];

const demoAuditStatus = [
  { protocol: 'Agni Finance', status: 'audited', auditor: 'Certik', date: '2024-08-15', score: 92 },
  { protocol: 'Lendle', status: 'audited', auditor: 'Trail of Bits', date: '2024-06-20', score: 88 },
  { protocol: 'FusionX', status: 'audited', auditor: 'PeckShield', date: '2024-09-01', score: 85 },
  { protocol: 'Merchant Moe', status: 'audited', auditor: 'OpenZeppelin', date: '2024-07-10', score: 95 },
  { protocol: 'iZUMi', status: 'pending', auditor: 'Certik', date: null, score: null },
  { protocol: 'KTX Finance', status: 'unaudited', auditor: null, date: null, score: null },
];

const getRiskLevel = (score: number) => {
  if (score <= 3) return { level: 'Low', color: 'text-green-500', bg: 'bg-green-500' };
  if (score <= 6) return { level: 'Medium', color: 'text-yellow-500', bg: 'bg-yellow-500' };
  if (score <= 8) return { level: 'High', color: 'text-orange-500', bg: 'bg-orange-500' };
  return { level: 'Critical', color: 'text-red-500', bg: 'bg-red-500' };
};

interface AuditResult {
  protocol: string;
  status: string;
  auditor: string | null;
  date: string | null;
  score: number | null;
}

export default function RiskPage() {
  const { address, isWalletConnected, backendStatus, networkName } = useFluxo();
  const { analyze, isAnalyzing, result: riskResult, error: riskError } = useRiskAnalysis();
  const [auditResults, setAuditResults] = useState<AuditResult[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);

  // Parse risk factors from result
  const riskFactors: RiskFactor[] = riskResult && typeof riskResult === 'object' && 'factors' in riskResult
    ? (riskResult as { factors: RiskFactor[] }).factors
    : demoRiskFactors;
  
  const isUsingDemo = !isWalletConnected || !backendStatus.isConnected || !riskResult;

  // Fetch audit check
  const fetchAuditCheck = useCallback(async () => {
    if (!address || !backendStatus.isConnected) return;
    
    setAuditLoading(true);
    try {
      const response = await api.risk.auditCheck(address, networkName);
      if (response.data && Array.isArray(response.data)) {
        setAuditResults(response.data as AuditResult[]);
      }
    } catch (err) {
      console.error('Failed to fetch audit check:', err);
    } finally {
      setAuditLoading(false);
    }
  }, [address, backendStatus.isConnected, networkName]);

  useEffect(() => {
    if (isWalletConnected && backendStatus.isConnected) {
      fetchAuditCheck();
    }
  }, [isWalletConnected, backendStatus.isConnected, fetchAuditCheck]);

  const handleAnalyze = async () => {
    await analyze();
    await fetchAuditCheck();
  };

  const displayAudits = auditResults.length > 0 ? auditResults : demoAuditStatus;
  const overallScore = riskFactors.reduce(
    (sum, factor) => sum + factor.score * factor.weight,
    0
  );
  const riskInfo = getRiskLevel(overallScore);

  // Show connect wallet prompt if not connected
  if (!isWalletConnected) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4">
          <h1 className="text-3xl font-bold">Risk Analysis</h1>
          <p className="text-muted-foreground">AI-powered portfolio risk assessment</p>
        </div>
        
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-6">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Wallet className="h-8 w-8 text-primary" />
            </div>
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Connect Your Wallet</h3>
              <p className="text-muted-foreground max-w-md">
                Connect your wallet to get AI-powered risk analysis of your portfolio.
              </p>
            </div>
            <ConnectButton />
          </CardContent>
        </Card>

        {/* Demo preview */}
        <div className="opacity-60">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-lg font-medium">Demo Preview</h2>
            <Badge variant="outline">Sample Data</Badge>
          </div>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-6">
                <div className="h-24 w-24 rounded-full flex items-center justify-center bg-yellow-500/10">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-yellow-500">5.6</p>
                    <p className="text-xs text-muted-foreground">/ 10</p>
                  </div>
                </div>
                <div>
                  <Badge variant="warning" className="mb-2">Medium Risk</Badge>
                  <h3 className="text-xl font-semibold">Overall Portfolio Risk</h3>
                  <p className="text-sm text-muted-foreground mt-1">Connect wallet to analyze your portfolio</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Risk Analysis</h1>
          <p className="text-muted-foreground mt-1">AI-powered portfolio risk assessment</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={backendStatus.isConnected ? 'success' : 'warning'}>
            {backendStatus.isConnected ? '● Live' : '○ Demo Mode'}
          </Badge>
          <Button onClick={handleAnalyze} disabled={isAnalyzing || !backendStatus.isConnected}>
            {isAnalyzing ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Shield className="h-4 w-4 mr-2" />
                Analyze
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {riskError && (
        <Card className="border-red-500/50 bg-red-500/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-500">
              <AlertTriangle className="h-5 w-5" />
              <span>{riskError}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overall Risk Score */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-6">
              {isAnalyzing ? (
                <Skeleton className="h-24 w-24 rounded-full" />
              ) : (
                <div className={cn(
                  'h-24 w-24 rounded-full flex items-center justify-center',
                  riskInfo.bg + '/10'
                )}>
                  <div className="text-center">
                    <p className={cn('text-3xl font-bold', riskInfo.color)}>
                      {overallScore.toFixed(1)}
                    </p>
                    <p className="text-xs text-muted-foreground">/ 10</p>
                  </div>
                </div>
              )}
              <div>
                <Badge
                  variant={
                    riskInfo.level === 'Low' ? 'success' :
                    riskInfo.level === 'Medium' ? 'warning' : 'danger'
                  }
                  className="mb-2"
                >
                  {riskInfo.level} Risk
                </Badge>
                <h3 className="text-xl font-semibold">Overall Portfolio Risk</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Based on {riskFactors.length} risk factors weighted by importance
                  {isUsingDemo && <Badge variant="outline" className="text-[10px] ml-2">Demo</Badge>}
                </p>
              </div>
            </div>
            <div className="flex gap-8">
              <div className="text-center">
                <div className="flex items-center gap-1 justify-center">
                  <TrendingDown className="h-4 w-4 text-green-500" />
                  <span className="text-2xl font-bold text-green-500">-0.8</span>
                </div>
                <p className="text-xs text-muted-foreground">vs last week</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">3</p>
                <p className="text-xs text-muted-foreground">Recommendations</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Factors & Audits */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Risk Factors */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Factors</CardTitle>
            <CardDescription>Breakdown of portfolio risk components</CardDescription>
          </CardHeader>
          <CardContent>
            {isAnalyzing ? (
              <div className="space-y-6">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-2 w-full" />
                    <Skeleton className="h-3 w-64" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-6">
                {riskFactors.map((factor) => {
                  const risk = getRiskLevel(factor.score);
                  return (
                    <div key={factor.name}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{factor.name}</span>
                          <Badge variant="secondary" className="text-[10px]">
                            {(factor.weight * 100).toFixed(0)}% weight
                          </Badge>
                        </div>
                        <span className={cn('font-bold', risk.color)}>
                          {factor.score.toFixed(1)}
                        </span>
                      </div>
                      <Progress
                        value={factor.score * 10}
                        className={cn('h-2', risk.bg)}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        {factor.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Protocol Audits */}
        <Card>
          <CardHeader>
            <CardTitle>Protocol Audits</CardTitle>
            <CardDescription>
              Security audit status of your protocols
              {auditResults.length === 0 && <Badge variant="outline" className="text-[10px] ml-2">Demo</Badge>}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-87.5">
              {auditLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex items-center gap-4 p-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                      <Skeleton className="h-6 w-12" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {displayAudits.map((protocol) => (
                    <div
                      key={protocol.protocol}
                      className="flex items-center gap-4 p-3 rounded-lg border border-border/50"
                    >
                      <div className={cn(
                        'h-10 w-10 rounded-full flex items-center justify-center',
                        protocol.status === 'audited' ? 'bg-green-500/10' :
                        protocol.status === 'pending' ? 'bg-yellow-500/10' : 'bg-red-500/10'
                      )}>
                        {protocol.status === 'audited' ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : protocol.status === 'pending' ? (
                          <RefreshCw className="h-5 w-5 text-yellow-500" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{protocol.protocol}</p>
                          <Badge
                            variant={
                              protocol.status === 'audited' ? 'success' :
                              protocol.status === 'pending' ? 'warning' : 'danger'
                            }
                            className="text-[10px]"
                          >
                            {protocol.status}
                          </Badge>
                        </div>
                        {protocol.auditor && (
                          <p className="text-sm text-muted-foreground">
                            {protocol.auditor} {protocol.date && `• ${protocol.date}`}
                          </p>
                        )}
                      </div>
                      {protocol.score && (
                        <div className="text-right">
                          <p className="font-bold text-green-500">{protocol.score}</p>
                          <p className="text-xs text-muted-foreground">Score</p>
                        </div>
                      )}
                      {protocol.status === 'audited' && (
                        <Button variant="ghost" size="icon">
                          <FileText className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>AI Recommendations</CardTitle>
          <CardDescription>Suggestions to reduce your portfolio risk</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div>
                <p className="font-medium">Diversify your holdings</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Your portfolio is 86% concentrated in MNT and ETH. Consider spreading across more assets to reduce concentration risk.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
              <Shield className="h-5 w-5 text-blue-500 mt-0.5" />
              <div>
                <p className="font-medium">Review unaudited protocols</p>
                <p className="text-sm text-muted-foreground mt-1">
                  You have exposure to KTX Finance which is unaudited. Consider moving funds to audited alternatives.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-4 rounded-lg bg-green-500/5 border border-green-500/20">
              <TrendingUp className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <p className="font-medium">Consider stablecoin allocation</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Adding 10-20% stablecoin allocation could help reduce volatility during market downturns.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
