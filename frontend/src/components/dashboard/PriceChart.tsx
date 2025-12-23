'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { formatCurrency } from '@/lib/utils';

interface PriceChartProps {
  data: Array<{
    timestamp: string;
    price: number;
    volume?: number;
  }>;
  title?: string;
  description?: string;
  loading?: boolean;
  className?: string;
  type?: 'line' | 'area';
  color?: string;
}

export function PriceChart({
  data,
  title = 'Price History',
  description,
  loading = false,
  className,
  type = 'area',
  color = '#8E3CC8', // Default to Fluxo Mid Violet
}: PriceChartProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="font-[family-name:var(--font-space-grotesk)]">{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent>
          <div className="h-[300px] animate-pulse rounded bg-muted" />
        </CardContent>
      </Card>
    );
  }

  const formatXAxis = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="font-[family-name:var(--font-space-grotesk)]">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No data available
          </div>
        ) : (
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              {type === 'area' ? (
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={color} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-[#8E3CC8]/10" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatXAxis}
                    className="text-xs"
                    stroke="currentColor"
                    tick={{ fill: 'currentColor' }}
                  />
                  <YAxis
                    tickFormatter={(value) => formatCurrency(value)}
                    className="text-xs"
                    stroke="currentColor"
                    tick={{ fill: 'currentColor' }}
                    width={80}
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="rounded-lg border bg-background p-3 shadow-md">
                            <p className="text-sm text-muted-foreground">{label}</p>
                            <p className="font-medium">
                              {formatCurrency(payload[0].value as number)}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke={color}
                    fillOpacity={1}
                    fill="url(#colorPrice)"
                    strokeWidth={2}
                  />
                </AreaChart>
              ) : (
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatXAxis}
                    className="text-xs"
                    stroke="currentColor"
                    tick={{ fill: 'currentColor' }}
                  />
                  <YAxis
                    tickFormatter={(value) => formatCurrency(value)}
                    className="text-xs"
                    stroke="currentColor"
                    tick={{ fill: 'currentColor' }}
                    width={80}
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="rounded-lg border bg-background p-3 shadow-md">
                            <p className="text-sm text-muted-foreground">{label}</p>
                            <p className="font-medium">
                              {formatCurrency(payload[0].value as number)}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke={color}
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              )}
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
