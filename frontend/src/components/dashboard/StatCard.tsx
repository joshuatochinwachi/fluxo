'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cn, formatCurrency, formatPercentage, getChangeColor } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  description?: string;
  className?: string;
  loading?: boolean;
}

export function StatCard({
  title,
  value,
  change,
  changeLabel = 'vs last period',
  icon,
  description,
  className,
  loading = false,
}: StatCardProps) {
  const formattedValue = typeof value === 'number' ? formatCurrency(value) : value;

  return (
    <Card className={cn('border-border/50 bg-background/50 relative overflow-hidden group stat-glass', className)}>
      {/* Subtle accent line at top */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#5B1A8B] to-[#8E3CC8]" />
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon && <div className="text-[#8E3CC8]">{icon}</div>}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <div className="h-8 w-24 animate-pulse rounded bg-muted" />
            <div className="h-4 w-16 animate-pulse rounded bg-muted" />
          </div>
        ) : (
          <>
            <div className="text-2xl font-bold font-[family-name:var(--font-space-grotesk)]">{formattedValue}</div>
            {change !== undefined && (
              <div className="flex items-center gap-1 mt-1">
                {change > 0 ? (
                  <TrendingUp className={cn('h-4 w-4', getChangeColor(change))} />
                ) : change < 0 ? (
                  <TrendingDown className={cn('h-4 w-4', getChangeColor(change))} />
                ) : (
                  <Minus className="h-4 w-4 text-[#8E3CC8]" />
                )}
                <span className={cn('text-sm font-medium', getChangeColor(change))}>
                  {formatPercentage(change)}
                </span>
                <span className="text-xs text-muted-foreground">{changeLabel}</span>
              </div>
            )}
            {description && (
              <CardDescription className="mt-1">{description}</CardDescription>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
