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
import { cn, formatRelativeTime, getRiskColor } from '@/lib/utils';
import { Alert } from '@/types';
import { AlertTriangle, TrendingUp, Wallet, MessageSquare, PiggyBank } from 'lucide-react';

interface RecentAlertsProps {
  alerts: Alert[];
  loading?: boolean;
  className?: string;
  title?: string;
}

const alertIcons: Record<string, React.ReactNode> = {
  price: <TrendingUp className="h-4 w-4" />,
  whale: <Wallet className="h-4 w-4" />,
  risk: <AlertTriangle className="h-4 w-4" />,
  yield: <PiggyBank className="h-4 w-4" />,
  social: <MessageSquare className="h-4 w-4" />,
  portfolio: <Wallet className="h-4 w-4" />,
};

const severityVariants: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  critical: 'danger',
};

export function RecentAlerts({ alerts, loading = false, className, title = "Recent Alerts" }: RecentAlertsProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>Latest notifications and warnings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="h-8 w-8 animate-pulse rounded-full bg-muted" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
                  <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
                </div>
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
        <CardTitle>{title}</CardTitle>
        <CardDescription>Latest notifications and warnings</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] pr-4">
          {alerts.length === 0 ? (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              No alerts yet
            </div>
          ) : (
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div
                  key={alert.alert_id}
                  className="flex items-start gap-3 rounded-lg border border-border/50 p-3 transition-colors hover:bg-muted/50"
                >
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-full',
                      getRiskColor(alert.overall_severity).replace('text-', 'bg-') + '/10',
                      getRiskColor(alert.overall_severity)
                    )}
                  >
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium truncate">{alert.title}</p>
                      <Badge variant={severityVariants[alert.overall_severity]} className="text-[10px]">
                        {alert.overall_severity}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mt-0.5">
                      {alert.message}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatRelativeTime(alert.timestamp)}
                    </p>
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
