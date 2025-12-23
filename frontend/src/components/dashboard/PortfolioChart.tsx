'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { Asset } from '@/types';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface PortfolioChartProps {
  assets: Asset[];
  totalValue: number;
  loading?: boolean;
  className?: string;
}

// Fluxo brand-compliant color palette (purples only)
const COLORS = [
  '#5B1A8B', // Deep Intelligence Purple
  '#6A1BB1', // Royal Violet  
  '#8E3CC8', // Mid Violet
  '#C77DFF', // Soft Lavender
  '#E3A8FF', // Signal Lilac
  '#9D4EDD', // Additional purple
  '#7B2CBF', // Additional purple
  '#4A148C', // Dark purple
];

export function PortfolioChart({
  assets,
  totalValue,
  loading = false,
  className,
}: PortfolioChartProps) {
  const chartData = assets.map((asset, index) => ({
    name: asset.token_symbol,
    value: asset.value_usd,
    percentage: asset.percentage,
    fill: COLORS[index % COLORS.length],
  }));

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="font-[family-name:var(--font-space-grotesk)]">Portfolio Allocation</CardTitle>
          <CardDescription>Asset distribution by value</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="h-48 w-48 animate-pulse rounded-full bg-muted" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="font-[family-name:var(--font-space-grotesk)]">Portfolio Allocation</CardTitle>
        <CardDescription>
          Total Value: {formatCurrency(totalValue)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {assets.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No assets found
          </div>
        ) : (
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="rounded-lg border bg-background p-3 shadow-md">
                          <p className="font-medium">{data.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {formatCurrency(data.value)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {formatPercentage(data.percentage, 1).replace('+', '')}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend
                  formatter={(value: string) => (
                    <span className="text-sm text-foreground">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
