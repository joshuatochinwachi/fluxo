'use client';

import { useState, useMemo, useCallback } from 'react';
import { useAccount } from 'wagmi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Bell,
  BellOff,
  Check,
  Trash2,
  Settings,
  TrendingUp,
  Wallet,
  Shield,
  MessageSquare,
  PiggyBank,
  AlertTriangle,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { formatRelativeTime, cn } from '@/lib/utils';
import { Alert } from '@/types';
import { useAlerts } from '@/hooks/useFluxo';

const alertIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  price: TrendingUp,
  whale: Wallet,
  risk: Shield,
  yield: PiggyBank,
  social: MessageSquare,
  portfolio: AlertTriangle,
};

const severityColors: Record<string, string> = {
  low: 'bg-green-500/10 text-green-500 border-green-500/20',
  medium: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  high: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  critical: 'bg-red-500/10 text-red-500 border-red-500/20',
};

export default function AlertsPage() {
  const { address, isConnected } = useAccount();
  const { alerts: alertsData, isLoading, error, refetch, markDelivered } = useAlerts();
  const [filter, setFilter] = useState<'all' | Alert['type']>('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  // Track locally marked alerts for optimistic updates
  const [markedAlertIds, setMarkedAlertIds] = useState<Set<string>>(new Set());

  // Derive alerts from API data with optimistic updates applied
  const localAlerts = useMemo(() => {
    const alerts = (alertsData as Alert[]) || [];
    return alerts.map(alert => ({
      ...alert,
      delivered: alert.delivered || markedAlertIds.has(alert.id),
    }));
  }, [alertsData, markedAlertIds]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetch();
    setIsRefreshing(false);
  };

  const markAsRead = useCallback(async (id: string) => {
    if (!address) return;
    // Optimistic update
    setMarkedAlertIds(prev => new Set(prev).add(id));
    try {
      await markDelivered(id, 'dashboard');
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
      // Keep optimistic update even on error
    }
  }, [address, markDelivered]);

  // Track dismissed alerts locally
  const [dismissedAlertIds, setDismissedAlertIds] = useState<Set<string>>(new Set());

  const deleteAlert = useCallback((id: string) => {
    setDismissedAlertIds(prev => new Set(prev).add(id));
  }, []);

  const markAllAsRead = useCallback(() => {
    const allIds = localAlerts.map(a => a.id);
    setMarkedAlertIds(prev => {
      const newSet = new Set(prev);
      allIds.forEach(id => newSet.add(id));
      return newSet;
    });
  }, [localAlerts]);

  // Filter out dismissed alerts
  const visibleAlerts = useMemo(() => 
    localAlerts.filter(a => !dismissedAlertIds.has(a.id)),
    [localAlerts, dismissedAlertIds]
  );

  const filteredAlerts = filter === 'all'
    ? visibleAlerts
    : visibleAlerts.filter(alert => alert.type === filter);

  const unreadCount = visibleAlerts.filter(a => !a.delivered).length;

  if (!isConnected) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Alerts</h1>
            <p className="text-muted-foreground mt-1">
              Connect your wallet to view alerts
            </p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Bell className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground text-center">
              Connect your wallet to receive personalized alerts about your portfolio,
              market movements, and opportunities.
            </p>
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
          <h1 className="text-3xl font-bold">Alerts</h1>
          <p className="text-muted-foreground mt-1">
            {isLoading ? 'Loading alerts...' : 
             unreadCount > 0 ? `${unreadCount} unread alerts` : 'All caught up!'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading || isRefreshing}>
            <RefreshCw className={cn("h-4 w-4 mr-2", (isLoading || isRefreshing) && "animate-spin")} />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={markAllAsRead} disabled={isLoading}>
            <Check className="h-4 w-4 mr-2" />
            Mark all read
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Alert Stats */}
      <div className="grid gap-4 md:grid-cols-6">
        {['all', 'price', 'whale', 'risk', 'yield', 'social'].map((type) => {
          const count = type === 'all'
            ? localAlerts.length
            : localAlerts.filter(a => a.type === type).length;
          const Icon = type === 'all' ? Bell : alertIcons[type];
          return (
            <Card
              key={type}
              className={cn(
                'cursor-pointer transition-colors',
                filter === type ? 'border-primary' : 'hover:border-primary/50'
              )}
              onClick={() => setFilter(type as typeof filter)}
            >
              <CardContent className="pt-4 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    <span className="text-sm capitalize">{type}</span>
                  </div>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Alerts List */}
      <Card>
        <CardHeader>
          <CardTitle>Alert History</CardTitle>
          <CardDescription>Your recent notifications and warnings</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
              <p className="text-muted-foreground">Loading alerts...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <AlertTriangle className="h-12 w-12 mb-4 text-destructive" />
              <p>Failed to load alerts</p>
              <Button variant="outline" size="sm" onClick={handleRefresh} className="mt-4">
                Try Again
              </Button>
            </div>
          ) : (
            <ScrollArea className="h-[500px]">
              {filteredAlerts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <BellOff className="h-12 w-12 mb-4" />
                  <p>No alerts found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredAlerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={cn(
                        'p-4 rounded-lg border transition-colors',
                        !alert.delivered
                          ? 'bg-primary/5 border-primary/20'
                          : 'border-border/50 hover:bg-muted/50'
                      )}
                    >
                      <div className="flex items-start gap-4">
                        <div
                          className={cn(
                            'flex h-10 w-10 items-center justify-center rounded-full border',
                            severityColors[alert.severity]
                          )}
                        >
                          {(() => {
                            const AlertIcon = alertIcons[alert.type];
                            return AlertIcon ? <AlertIcon className="h-4 w-4" /> : null;
                          })()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium">{alert.title}</p>
                            <Badge
                              variant={
                                alert.severity === 'critical' || alert.severity === 'high'
                                  ? 'danger'
                                  : alert.severity === 'medium'
                                  ? 'warning'
                                  : 'success'
                              }
                              className="text-[10px]"
                            >
                              {alert.severity}
                            </Badge>
                            {!alert.delivered && (
                              <Badge variant="default" className="text-[10px]">
                                New
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">{alert.message}</p>
                          <p className="text-xs text-muted-foreground mt-2">
                            {formatRelativeTime(alert.timestamp)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {!alert.delivered && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => markAsRead(alert.id)}
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => deleteAlert(alert.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
