'use client';

import { useState } from 'react';
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
import { useX402 } from '@/hooks/useFluxo';
import { cn } from '@/lib/utils';

interface PremiumInsight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'alpha';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  timestamp: string;
  actionable?: string;
}

interface PremiumInsightsProps {
  className?: string;
}

export function PremiumInsights({ className }: PremiumInsightsProps) {
  const { isConnected } = useAccount();
  const { executePayment, isProcessing, error: paymentError } = useX402();
  
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [insights, setInsights] = useState<PremiumInsight[]>([]);

  // Mock premium insights (in production, these would come from a paid API endpoint)
  // Using static timestamps to avoid impure Date.now() calls during render
  const mockPremiumInsights: PremiumInsight[] = [
    {
      id: '1',
      type: 'alpha',
      title: 'Early DEX Liquidity Signal',
      description: 'Detected significant liquidity inflow to a new Mantle DEX pool. Historical patterns suggest 40% price appreciation within 48 hours.',
      impact: 'high',
      timestamp: '1 hour ago',
      actionable: 'Consider early position with tight stop-loss',
    },
    {
      id: '2',
      type: 'opportunity',
      title: 'Yield Arbitrage Available',
      description: 'Lending rate differential of 8.2% detected between Agni Finance and Lendle. Estimated APY boost: 15-20%.',
      impact: 'high',
      timestamp: '2 hours ago',
      actionable: 'Move stablecoins to higher-yield protocol',
    },
    {
      id: '3',
      type: 'risk',
      title: 'Smart Money Exit Alert',
      description: '3 whale wallets have reduced MNT exposure by 25% in the last 24h. Average entry was $0.42.',
      impact: 'medium',
      timestamp: '3 hours ago',
      actionable: 'Review position sizing and set trailing stops',
    },
    {
      id: '4',
      type: 'trend',
      title: 'Social Momentum Shift',
      description: 'Sentiment score improved from 0.45 to 0.72. Historically correlates with 15% price moves within 7 days.',
      impact: 'medium',
      timestamp: '4 hours ago',
    },
  ];

  const handleUnlock = async () => {
    try {
      await executePayment();
      setIsUnlocked(true);
      setInsights(mockPremiumInsights);
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

  // Locked State
  if (!isUnlocked) {
    return (
      <Card className={cn("relative overflow-hidden", className)}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-muted-foreground" />
              <CardTitle>Premium Insights</CardTitle>
            </div>
            <Badge variant="secondary" className="gap-1">
              <DollarSign className="h-3 w-3" />
              $0.01/request
            </Badge>
          </div>
          <CardDescription>
            AI-powered alpha signals, whale movements, and actionable opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Blurred Preview */}
          <div className="relative">
            <div className="blur-sm pointer-events-none select-none">
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 rounded-lg border border-border/50 bg-muted/30">
                    <div className="flex items-start gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10" />
                      <div className="flex-1">
                        <div className="h-4 w-3/4 bg-muted rounded mb-2" />
                        <div className="h-3 w-full bg-muted/50 rounded" />
                        <div className="h-3 w-2/3 bg-muted/50 rounded mt-1" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Unlock Overlay */}
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm">
              <div className="text-center max-w-sm px-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <Lock className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Unlock Premium Insights</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Get AI-powered alpha signals, early opportunity detection, and actionable trading insights powered by x402 micropayments.
                </p>
                
                {!isConnected ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                      <Wallet className="h-4 w-4" />
                      <span>Connect wallet to unlock</span>
                    </div>
                    <Button disabled className="w-full">
                      <Lock className="h-4 w-4 mr-2" />
                      Wallet Required
                    </Button>
                  </div>
                ) : (
                  <Button 
                    onClick={handleUnlock} 
                    disabled={isProcessing}
                    className="w-full"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Processing Payment...
                      </>
                    ) : (
                      <>
                        <Unlock className="h-4 w-4 mr-2" />
                        Unlock for $0.01
                      </>
                    )}
                  </Button>
                )}

                {paymentError && (
                  <p className="text-sm text-destructive mt-3">{paymentError}</p>
                )}

                <p className="text-xs text-muted-foreground mt-4">
                  Powered by x402 payment protocol • Base Sepolia
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
    <Card className={cn(className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <CardTitle>Premium Insights</CardTitle>
          </div>
          <Badge variant="success" className="gap-1">
            <Unlock className="h-3 w-3" />
            Unlocked
          </Badge>
        </div>
        <CardDescription>
          {insights.length} actionable insights detected
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-100 pr-4">
          <div className="space-y-4">
            {insights.map((insight) => (
              <div
                key={insight.id}
                className="p-4 rounded-lg border border-border/50 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center shrink-0">
                    {getInsightIcon(insight.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium">{insight.title}</p>
                      <Badge 
                        variant="secondary" 
                        className={cn("text-[10px]", getImpactColor(insight.impact))}
                      >
                        {insight.impact} impact
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {insight.description}
                    </p>
                    {insight.actionable && (
                      <div className="flex items-center gap-2 text-sm text-primary">
                        <ArrowRight className="h-3 w-3" />
                        <span>{insight.actionable}</span>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-2">
                      {insight.timestamp}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

export default PremiumInsights;
