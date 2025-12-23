'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { formatCompactNumber, formatPercentage } from '@/lib/utils';
import { YieldOpportunity } from '@/types';
import { ExternalLink, Shield } from 'lucide-react';

interface TopYieldsProps {
  yields: YieldOpportunity[];
  loading?: boolean;
  className?: string;
}

const getRiskBadgeVariant = (score: number): 'success' | 'warning' | 'danger' => {
  if (score <= 3) return 'success';
  if (score <= 6) return 'warning';
  return 'danger';
};

export function TopYields({ yields, loading = false, className }: TopYieldsProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Top Yield Opportunities</CardTitle>
          <CardDescription>Best DeFi yields across protocols</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-lg border border-border/50">
                <div className="h-10 w-10 animate-pulse rounded-lg bg-muted" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-24 animate-pulse rounded bg-muted" />
                  <div className="h-3 w-16 animate-pulse rounded bg-muted" />
                </div>
                <div className="h-6 w-16 animate-pulse rounded bg-muted" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Top Yield Opportunities</CardTitle>
        <CardDescription>Best DeFi yields across protocols</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[320px] pr-4">
          {yields.length === 0 ? (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              No yield opportunities found
            </div>
          ) : (
            <div className="space-y-3">
              {yields.map((opportunity, index) => (
                <div
                  key={`${opportunity.protocol}-${opportunity.pool}-${index}`}
                  className="flex items-center gap-4 p-3 rounded-lg border border-border/50 transition-colors hover:bg-muted/50 cursor-pointer"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <span className="text-sm font-bold text-primary">
                      {opportunity.protocol.slice(0, 2).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium truncate">{opportunity.protocol}</p>
                      <ExternalLink className="h-3 w-3 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {opportunity.token_pair.join(' / ')} • TVL: {formatCompactNumber(opportunity.tvl)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-green-500">
                      {formatPercentage(opportunity.apy, 1).replace('+', '')} APY
                    </p>
                    <div className="flex items-center gap-1 justify-end mt-0.5">
                      <Shield className="h-3 w-3" />
                      <Badge variant={getRiskBadgeVariant(opportunity.risk_score)} className="text-[10px]">
                        Risk: {opportunity.risk_score}/10
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
