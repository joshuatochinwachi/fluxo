'use client';

import { useState, useMemo, useCallback, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
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
  Plus,
  Search,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  Info,
  ChevronDown,
  ChevronUp,
  Zap,
} from 'lucide-react';
import { formatRelativeTime, cn, formatAddress } from '@/lib/utils';
import { Alert, AlertAgentSection } from '@/types';
import { useFluxo, useAlerts } from '@/hooks/useFluxo';

const severityConfig: Record<string, { color: string; icon: any; label: string }> = {
  low: { color: 'bg-green-500/10 text-green-500 border-green-500/20', icon: ShieldCheck, label: 'Low' },
  medium: { color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20', icon: Info, label: 'Medium' },
  high: { color: 'bg-orange-500/10 text-orange-500 border-orange-500/20', icon: ShieldAlert, label: 'High' },
  critical: { color: 'bg-red-500/10 text-red-500 border-red-500/20', icon: AlertTriangle, label: 'Critical' },
};

function AgentSection({ section }: { section: AlertAgentSection }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const severity = (section.severity?.toLowerCase() || 'low') as keyof typeof severityConfig;
  const config = severityConfig[severity] || severityConfig.low;

  const renderValue = (val: any): string => {
    if (val === null || val === undefined) return '-';
    if (typeof val === 'number') return val.toLocaleString();
    if (Array.isArray(val)) {
      if (val.length === 0) return 'None';
      return val.map(v => {
        if (typeof v === 'object' && v !== null) {
          // Try common keys for token/asset display
          return v.symbol || v.name || v.token || v.label || '{...}';
        }
        return String(v);
      }).join(', ');
    }
    if (typeof val === 'object' && val !== null) {
      // Try common keys for token/asset display
      return val.symbol || val.name || val.token || val.label || JSON.stringify(val);
    }
    return String(val);
  };

  return (
    <div className="border border-border/50 rounded-2xl overflow-hidden bg-muted/5 group/section">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-primary/5 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <Badge variant="outline" className={cn("text-[8px] uppercase font-black tracking-tight", config.color)}>
            {section.agent_name}
          </Badge>
          <span className="text-xs font-black uppercase tracking-tight group-hover/section:text-primary transition-colors">{section.section_title}</span>
        </div>
        {isExpanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
      </button>

      {isExpanded && (
        <div className="p-4 pt-0 space-y-3 animate-in fade-in slide-in-from-top-1 duration-200">
          <p className="text-xs text-muted-foreground font-medium leading-relaxed whitespace-pre-wrap px-1">
            {section.message}
          </p>

          {section.key_metrics && Object.keys(section.key_metrics).length > 0 && (
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border/10 px-1">
              {Object.entries(section.key_metrics).map(([key, val]) => (
                <div key={key} className="flex flex-col gap-1">
                  <span className="text-[9px] uppercase tracking-widest text-muted-foreground font-black opacity-60">{key.replace(/_/g, ' ')}</span>
                  <span className="text-[10px] font-mono font-black text-primary truncate" title={renderValue(val)}>
                    {renderValue(val)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AlertsPage() {
  const { isWalletConnected } = useFluxo();
  const {
    alerts,
    trackedWallets,
    isLoading,
    error,
    refetch,
    addTrackWallet,
    removeTrackWallet,
    markDelivered
  } = useAlerts();

  const [newWallet, setNewWallet] = useState('');
  const [filter, setFilter] = useState<'all' | Alert['overall_severity']>('all');
  const [searchTarget, setSearchTarget] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetch();
    setIsRefreshing(false);
  };

  const handleAddTrack = async () => {
    if (!newWallet || !newWallet.startsWith('0x')) return;
    try {
      await addTrackWallet(newWallet);
      setNewWallet('');
    } catch (err) {
      console.error('Failed to add wallet:', err);
    }
  };

  const filteredAlerts = useMemo(() => {
    let result = [...alerts];
    if (filter !== 'all') {
      result = result.filter(a => a.overall_severity === filter);
    }
    if (searchTarget) {
      const lowerSearch = searchTarget.toLowerCase();
      result = result.filter(a =>
        a.wallet_address.toLowerCase().includes(lowerSearch) ||
        a.title.toLowerCase().includes(lowerSearch) ||
        a.message.toLowerCase().includes(lowerSearch) ||
        a.overall_severity.toLowerCase().includes(lowerSearch)
      );
    }
    return result.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [alerts, filter, searchTarget]);

  const unreadCount = alerts.filter(a => !a.delivered).length;

  if (!isWalletConnected) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 animate-in fade-in duration-700">
        <div className="h-20 w-20 bg-primary/10 rounded-full flex items-center justify-center shadow-lg shadow-primary/20">
          <Bell className="h-10 w-10 text-primary animate-pulse" />
        </div>
        <div className="max-w-md space-y-2">
          <h1 className="text-3xl font-black tracking-tighter">On-Chain Alert Hub</h1>
          <p className="text-muted-foreground font-medium">
            Connect your wallet to start tracking high-risk movements and whale activity across the Mantle network.
          </p>
        </div>
        <Button size="lg" className="rounded-full px-8 font-bold shadow-xl shadow-primary/20">
          Open Observer Portal
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header Section */}
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between bg-muted/30 p-8 rounded-3xl border border-border/50 backdrop-blur-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
          <ShieldAlert className="h-48 w-48 rotate-12" />
        </div>

        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 px-4 py-1.5 font-[family-name:var(--font-vt323)] text-lg uppercase tracking-widest">
              MONITORING ENGINE v4.0.2
            </Badge>
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tighter uppercase italic">Alpha <span className="text-primary">Oversight</span></h1>
          <p className="text-muted-foreground font-medium max-w-lg">
            {unreadCount > 0
              ? `Awaiting processing of ${unreadCount} high-priority intelligence vectors.`
              : `System secure. Active surveillance on ${trackedWallets.length} nodes with 0 critical deviations.`}
          </p>
        </div>

        <div className="flex flex-wrap gap-3 relative z-10">
          <Button variant="outline" className="rounded-2xl border-border/50 hover:bg-muted/50 transition-all font-bold" onClick={handleRefresh} disabled={isLoading || isRefreshing}>
            <RefreshCw className={cn("h-4 w-4 mr-2", (isLoading || isRefreshing) && "animate-spin")} />
            Recalibrate Node
          </Button>
          <Button className="rounded-2xl shadow-lg shadow-primary/20 font-black">
            <Check className="h-4 w-4 mr-2" />
            Dismiss All Vectors
          </Button>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Watchlist Sidebar */}
        <div className="space-y-6">
          <Card className="border-border/50 bg-background/50 backdrop-blur-md overflow-hidden rounded-3xl shadow-sm">
            <CardHeader className="border-b border-border/50 bg-muted/10 pb-6">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="h-5 w-5 text-primary" />
                Observation Targets
              </CardTitle>
              <CardDescription>Track wallets for movement intel</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="0x... address"
                  value={newWallet}
                  onChange={(e) => setNewWallet(e.target.value)}
                  className="rounded-xl border-border/50 font-mono text-xs h-11 bg-background/50"
                />
                <Button size="icon" className="rounded-xl shrink-0 h-11 w-11 shadow-primary/10 shadow-md" onClick={handleAddTrack}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-2 mt-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1 mb-2">Active Tracker Units</p>
                <div className="space-y-2">
                  {trackedWallets.length > 0 ? (
                    trackedWallets.map((w) => (
                      <div key={w} className="flex items-center justify-between p-3 rounded-2xl border border-border/50 bg-muted/20 group hover:bg-muted/40 transition-all">
                        <div className="flex items-center gap-3 overflow-hidden">
                          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                            <Wallet className="h-4 w-4 text-primary" />
                          </div>
                          <span className="text-xs font-mono font-bold truncate">{formatAddress(w)}</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-all"
                          onClick={() => removeTrackWallet(w)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 opacity-40 border border-dashed border-border/50 rounded-2xl">
                      <p className="text-[10px] uppercase font-black tracking-widest">No Active Units</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-background/50 backdrop-blur-md rounded-3xl overflow-hidden shadow-sm">
            <div className="p-6 bg-primary/5 border-b border-border/50 flex items-center justify-between">
              <h3 className="text-[10px] font-black flex items-center gap-2 uppercase tracking-widest text-primary">
                <Settings className="h-4 w-4" />
                INFRA PULSE
              </h3>
              <Badge variant="outline" className="text-[9px] text-green-500 border-green-500/20 bg-green-500/5 px-2 py-0 border-none font-black animate-pulse">NODE ACTIVE</Badge>
            </div>
            <CardContent className="p-6 space-y-4 font-[family-name:var(--font-vt323)]">
              <div className="flex items-center justify-between text-xl">
                <span className="text-muted-foreground opacity-60">HEARTBEAT</span>
                <span className="text-primary uppercase">15 MIN CYCLE</span>
              </div>
              <div className="flex items-center justify-between text-xl">
                <span className="text-muted-foreground opacity-60">UI POLLING</span>
                <span className="text-primary uppercase">30 SEC LIVE</span>
              </div>
              <div className="flex items-center justify-between text-xl">
                <span className="text-muted-foreground opacity-60">DELIVERY</span>
                <span className="text-primary uppercase">WEBHOOKS STABLE</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Alerts Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between px-2 gap-4">
            <div className="flex gap-1.5 overflow-x-auto pb-2 md:pb-0 scrollbar-hide font-[family-name:var(--font-vt323)]">
              {(['all', 'critical', 'high', 'medium', 'low'] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => setFilter(s)}
                  className={cn(
                    "px-6 py-2 rounded-full text-xl uppercase tracking-widest border transition-all whitespace-nowrap shadow-sm",
                    filter === s
                      ? "bg-primary text-primary-foreground border-primary scale-110"
                      : "bg-background border-border/50 text-muted-foreground hover:border-primary/50"
                  )}
                >
                  {s}
                </button>
              ))}
            </div>
            <div className="relative shrink-0 hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
              <Input
                placeholder="Search intel..."
                value={searchTarget}
                onChange={(e) => setSearchTarget(e.target.value)}
                className="rounded-full pl-9 pr-4 h-10 bg-background/50 border-border/50 text-xs w-64 shadow-inner"
              />
            </div>
          </div>

          <ScrollArea className="h-[750px] pr-4">
            <div className="space-y-6">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-32 w-full bg-muted/20 animate-pulse rounded-3xl border border-border/50" />
                ))
              ) : filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => {
                  const config = severityConfig[alert.overall_severity] || severityConfig.low;
                  const Icon = config.icon;
                  return (
                    <Card
                      key={alert.alert_id}
                      className={cn(
                        "group border-border/50 bg-background/50 hover:bg-muted/5 transition-all rounded-3xl overflow-hidden relative shadow-sm list-item-glass",
                        !alert.delivered && "border-primary/40 ring-1 ring-primary/10 shadow-primary/5 shadow-lg"
                      )}
                    >
                      {!alert.delivered && (
                        <div className="absolute top-0 left-0 w-1.5 h-full bg-primary" />
                      )}
                      <CardContent className="p-6">
                        <div className="flex items-start gap-5">
                          <div className={cn("p-4 rounded-2xl shrink-0 shadow-lg", config.color)}>
                            <Icon className="h-7 w-7" />
                          </div>

                          <div className="flex-1 space-y-4">
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                              <div className="flex items-center gap-3">
                                <h3 className="font-black text-xl tracking-tight group-hover:text-primary transition-colors">{alert.title}</h3>
                                <Badge variant="outline" className={cn("text-[10px] uppercase font-black tracking-tight", config.color)}>
                                  {config.label}
                                </Badge>
                                {!alert.delivered && (
                                  <Badge className="bg-primary text-primary-foreground text-[9px] font-black tracking-widest border-none">NEW INTEL</Badge>
                                )}
                              </div>
                              <span className="text-[10px] font-mono text-muted-foreground font-black bg-muted/50 px-3 py-1 rounded-full uppercase tracking-widest w-fit">
                                {formatRelativeTime(alert.timestamp)}
                              </span>
                            </div>

                            <p className="text-sm text-muted-foreground font-medium leading-relaxed max-w-2xl whitespace-pre-wrap">
                              {alert.message.split('\n').map((line, i) => (
                                <span key={i} className={cn("block", line.includes('0 alert(s) - CRITICAL') && "text-green-500 font-bold")}>
                                  {line.replace(/0 alert\(s\) - CRITICAL/g, '0 alert(s) - STABLE')}
                                </span>
                              ))}
                            </p>

                            {/* Detailed Sections (Agent Sections) */}
                            {alert.agent_sections && alert.agent_sections.length > 0 && (
                              <div className="space-y-3 mt-4 pt-4 border-t border-border/50">
                                <p className="text-[10px] font-black uppercase tracking-widest text-primary/60">Deep Intel Modules</p>
                                <div className="grid gap-3">
                                  {alert.agent_sections.map((section, idx) => (
                                    <AgentSection key={`${section.agent_name}-${idx}`} section={section} />
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Recommendations Overlay */}
                            {alert.recommendations && alert.recommendations.length > 0 && (
                              <div className="mt-4 p-5 rounded-2xl bg-primary/5 border border-primary/20 space-y-3 shadow-inner">
                                <div className="flex items-center gap-2">
                                  <Zap className="h-4 w-4 text-primary fill-primary" />
                                  <span className="text-[11px] font-black uppercase tracking-tight text-primary">Strategic Recommendations</span>
                                </div>
                                <ul className="space-y-2">
                                  {alert.recommendations.map((rec, idx) => (
                                    <li key={idx} className="text-xs font-bold flex items-start gap-3 text-muted-foreground/80">
                                      <Check className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                                      {rec}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            <div className="flex flex-wrap items-center gap-4 mt-6 text-[10px] font-black pt-4 border-t border-border/10">
                              <div className="flex items-center gap-2 text-primary hover:bg-primary/5 px-2 py-1 rounded-lg transition-colors cursor-pointer border border-primary/20">
                                <Wallet className="h-3.5 w-3.5" />
                                {formatAddress(alert.wallet_address)}
                              </div>
                              <a
                                href={`https://explorer.mantle.xyz/address/${alert.wallet_address}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-all cursor-pointer bg-muted/30 px-2 py-1 rounded-lg"
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                                EXPLORER UNIT
                              </a>

                              <div className="flex-1" />

                              {!alert.delivered && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-9 px-4 rounded-full text-primary hover:bg-primary/10 font-black text-[10px] border border-primary/20 bg-primary/5 animate-pulse"
                                  onClick={() => markDelivered(alert.alert_id, alert.wallet_address)}
                                >
                                  ANALYZE & DISMISS
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              ) : (
                <div className="flex flex-col items-center justify-center py-32 text-center space-y-6 bg-muted/10 rounded-[3rem] border border-dashed border-border/50 animate-in fade-in zoom-in-95 duration-500">
                  <div className="h-20 w-20 bg-muted/50 rounded-full flex items-center justify-center border border-border/50 shadow-inner">
                    <BellOff className="h-10 w-10 text-muted-foreground/30" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-black text-xl tracking-tight">Intelligence Silence</h3>
                    <p className="text-[11px] font-black text-muted-foreground uppercase tracking-widest">Adjust filters or register new tracker units</p>
                  </div>
                  <Button variant="outline" className="rounded-2xl font-bold px-6" onClick={handleRefresh}>
                    Recalibrate Node
                  </Button>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  );
}
