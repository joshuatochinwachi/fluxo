'use client';

import { useState, useMemo, useEffect } from 'react';
import { useAccount } from 'wagmi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Lock,
  Unlock,
  Zap,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  DollarSign,
  Loader2,
  Wallet,
  CheckCircle,
  ArrowRight,
} from 'lucide-react';
import { useX402, useYieldOpportunities, useAlerts } from '@/hooks/useFluxo';
import { cn, formatCurrency, formatRelativeTime } from '@/lib/utils';

interface PremiumInsight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'alpha';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  timestamp: string;
  actionable?: string;
}

const demoInsights: PremiumInsight[] = [
  {
    id: 'demo-1',
    type: 'alpha',
    title: 'x402 Momentum Signal',
    description: 'Autonomous agents have identified a massive liquidity shift towards Mantle native protocols. FusionX and Agni are showing early breakout patterns.',
    impact: 'high',
    timestamp: new Date().toISOString(),
    actionable: 'Monitor FusionX LP pairs for volume spikes'
  },
  {
    id: 'demo-2',
    type: 'trend',
    title: 'Mantle Governance Alpha',
    description: 'Upcoming protocol upgrade proposal detected. Historic data suggests 15-20% volatility in MNT price action during such events.',
    impact: 'medium',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    actionable: 'Hedging recommended for large MNT positions'
  }
];

interface PremiumInsightsProps {
  className?: string;
}

export function PremiumInsights({ className }: PremiumInsightsProps) {
  const { isConnected } = useAccount();
  const { executePayment, isExecuting: isProcessing, error: paymentError } = useX402();
  const { opportunities: realYields } = useYieldOpportunities();
  const { alerts: realAlerts } = useAlerts();

  const [isUnlocked, setIsUnlocked] = useState(false);
  const [streamId, setStreamId] = useState<string>('');
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
    setStreamId(Math.random().toString(36).substring(7).toUpperCase());
  }, []);

  // Derive Real Premium Insights from backend data
  const premiumInsights: PremiumInsight[] = useMemo(() => {
    const list: PremiumInsight[] = [];

    // 1. High Yield Alpha
    const topYield = [...realYields].sort((a, b) => b.apy - a.apy)[0];
    if (topYield) {
      list.push({
        id: 'yield-alpha',
        type: 'opportunity',
        title: `High APY Signal: ${topYield.protocol}`,
        description: `Premium yield vector detected on ${topYield.network}. ${topYield.pool} is currently returning ${topYield.apy.toFixed(1)}% APY with a risk score of ${topYield.risk_score || 'Low'}.`,
        impact: 'high',
        timestamp: 'LIVE',
        actionable: `Deposit into ${topYield.protocol} ${topYield.pool} pool`,
      });
    }

    // 2. Critical Alert Alpha
    const criticalAlert = realAlerts.find(a => a.overall_severity === 'critical');
    if (criticalAlert) {
      list.push({
        id: 'risk-alpha',
        type: 'risk',
        title: `Critical Movement Alert`,
        description: criticalAlert.message,
        impact: 'high',
        timestamp: criticalAlert.timestamp,
        actionable: 'Review wallet exposure immediately',
      });
    }

    // 3. General "Alpha" trend if we have data
    if (realAlerts.length > 5) {
      list.push({
        id: 'trend-alpha',
        type: 'alpha',
        title: 'Network Momentum Detected',
        description: `Unusual activity cluster detected across ${new Set(realAlerts.map(a => a.wallet_address)).size} tracked nodes in the last hour.`,
        impact: 'medium',
        timestamp: 'ACTIVE',
        actionable: 'Monitor for further breakout signals',
      });
    }

    return list.length > 0 ? list : demoInsights;
  }, [realYields, realAlerts]);

  const handleUnlock = async () => {
    try {
      await executePayment({});
      setIsUnlocked(true);
    } catch (err) {
      console.error('Payment failed:', err);
    }
  };

  const getInsightIcon = (type: PremiumInsight['type']) => {
    switch (type) {
      case 'alpha':
        return <Zap className="h-5 w-5 text-yellow-500" />;
      case 'opportunity':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'risk':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'trend':
        return <Lightbulb className="h-5 w-5 text-blue-500" />;
    }
  };

  const getImpactColor = (impact: PremiumInsight['impact']) => {
    switch (impact) {
      case 'high':
        return 'text-red-500 bg-red-500/10';
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/10';
      case 'low':
        return 'text-green-500 bg-green-500/10';
    }
  };

  // Hydration Guard
  if (!hasMounted) {
    return (
      <Card className={cn("relative overflow-hidden rounded-3xl border-primary/20", className)}>
        <div className="p-12 flex flex-col items-center justify-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary/40" />
          <p className="text-[10px] font-black uppercase tracking-widest opacity-40 text-center">Initialising Decryption Engine...</p>
        </div>
      </Card>
    );
  }

  // Locked State
  if (!isUnlocked) {
    return (
      <Card className={cn("relative overflow-hidden rounded-3xl border-primary/20", className)}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-primary" />
              <CardTitle className="text-sm font-black uppercase tracking-tight">Premium Intelligence</CardTitle>
            </div>
            <Badge variant="outline" className="gap-1 border-primary/20 bg-primary/5 text-primary text-[9px] font-black uppercase">
              <DollarSign className="h-3 w-3" />
              $0.01/STREAM
            </Badge>
          </div>
          <CardDescription className="text-[10px] font-bold">
            Actionable alpha signals derived from deep-chain monitoring
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <div className="blur-xl pointer-events-none select-none opacity-20">
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 rounded-2xl border border-border/50 bg-muted/20 h-24" />
                ))}
              </div>
            </div>

            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="text-center max-w-sm px-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4 border border-primary/20 shadow-xl">
                  <Lock className="h-7 w-7 text-primary" />
                </div>
                <h3 className="text-lg font-black tracking-tighter uppercase leading-none mb-2">Initialize Alpha Stream</h3>
                <p className="text-[11px] text-muted-foreground font-medium mb-6 leading-relaxed">
                  Gain exclusive access to critical yield vectors and high-impact risk signals processed by our backend agents in real-time.
                </p>

                {!isConnected ? (
                  <div className="space-y-3">
                    <Button disabled className="w-full h-11 rounded-xl bg-muted text-muted-foreground font-black uppercase tracking-widest text-[10px]">
                      <Wallet className="h-4 w-4 mr-2" />
                      Link Node Required
                    </Button>
                  </div>
                ) : (
                  <Button
                    onClick={handleUnlock}
                    disabled={isProcessing}
                    className="w-full h-12 rounded-xl bg-primary shadow-lg shadow-primary/20 font-black uppercase tracking-widest text-[10px] text-primary-foreground"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Verifying Request...
                      </>
                    ) : (
                      <>
                        <Unlock className="h-4 w-4 mr-2" />
                        Decrypt Stream ($0.01)
                      </>
                    )}
                  </Button>
                )}

                <p
                  className="text-[9px] font-black text-muted-foreground mt-4 uppercase tracking-widest opacity-50"
                  suppressHydrationWarning
                >
                  x402 Protocol • Stream ID: {streamId || 'INITIALIZING_ALPHA_ENGINE...'}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Unlocked State
  return (
    <Card className={cn("rounded-3xl border-green-500/20 bg-green-500/5", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <CardTitle className="text-sm font-black uppercase tracking-tight">Active Alpha Stream</CardTitle>
          </div>
          <Badge variant="outline" className="gap-1 border-green-500/20 bg-green-500/10 text-green-500 text-[9px] font-black uppercase">
            <Unlock className="h-3 w-3" />
            LIVE_DECRYPTED
          </Badge>
        </div>
        <CardDescription className="text-[10px] font-bold text-green-600/70">
          {premiumInsights.length || 'Evaluating'} premium vectors initialized
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] pr-4">
          <div className="space-y-4">
            {premiumInsights.length > 0 ? premiumInsights.map((insight) => (
              <div
                key={insight.id}
                className="p-5 rounded-2xl border border-green-500/20 bg-background/50 hover:bg-background transition-all shadow-sm group/insight"
              >
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center shrink-0 border border-border/50">
                    {getInsightIcon(insight.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-black text-xs uppercase tracking-tight group-hover/insight:text-primary transition-colors">{insight.title}</p>
                      <Badge
                        variant="outline"
                        className={cn("text-[8px] font-black uppercase border-none", getImpactColor(insight.impact))}
                      >
                        {insight.impact} EFFECT
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground font-medium mb-3 leading-relaxed">
                      {insight.description}
                    </p>
                    {insight.actionable && (
                      <div className="flex items-center gap-2 text-[10px] font-black text-primary uppercase tracking-tight bg-primary/5 px-3 py-1.5 rounded-lg border border-primary/10 w-fit">
                        <ArrowRight className="h-3 w-3" />
                        <span>Directive: {insight.actionable}</span>
                      </div>
                    )}
                    <p className="text-[9px] font-black text-muted-foreground mt-3 uppercase tracking-widest opacity-40">
                      TELEMETRY: {formatRelativeTime(insight.timestamp)}
                    </p>
                  </div>
                </div>
              </div>
            )) : (
              <div className="flex flex-col items-center justify-center py-20 text-center space-y-3 opacity-40">
                <Zap className="h-10 w-10 animate-pulse" />
                <p className="text-[10px] font-black uppercase tracking-widest">Aggregating Alpha Vectors...</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

export default PremiumInsights;
