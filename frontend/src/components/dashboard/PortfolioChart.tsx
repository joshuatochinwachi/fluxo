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
import { formatCurrency, formatPercentage, cn } from '@/lib/utils';

interface PortfolioChartProps {
  assets: Asset[];
  totalValue: number;
  loading?: boolean;
  className?: string;
  title?: string;
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
  title = "Portfolio Allocation",
}: PortfolioChartProps) {
  // Process chart data: Sort and Group
  const chartData = (() => {
    if (!assets || assets.length === 0) return [];

    // 1. Sort by value descending
    const sorted = [...assets].sort((a, b) => b.value_usd - a.value_usd);

    // 2. Identify top 6 assets
    const topAssets = sorted.slice(0, 6);
    const otherAssets = sorted.slice(6);

    // 3. Further group if an asset is < 2% of total value
    const finalTop: any[] = [];
    const grouped: any[] = [];

    topAssets.forEach(asset => {
      const pct = totalValue > 0 ? (asset.value_usd / totalValue) * 100 : 0;
      if (pct < 2 && finalTop.length > 2) {
        grouped.push(asset);
      } else {
        finalTop.push({
          name: asset.token_symbol,
          value: asset.value_usd,
          percentage: pct,
        });
      }
    });

    grouped.push(...otherAssets);

    const data = [...finalTop];

    if (grouped.length > 0) {
      const othersValue = grouped.reduce((sum, a) => sum + a.value_usd, 0);
      data.push({
        name: 'Others',
        value: othersValue,
        percentage: totalValue > 0 ? (othersValue / totalValue) * 100 : 0,
      });
    }

    return data.map((item, index) => ({
      ...item,
      fill: COLORS[index % COLORS.length],
    }));
  })();

  if (loading) {
    return (
      <Card className={cn(className, "chart-glass")}>
        <CardHeader>
          <CardTitle className="font-[family-name:var(--font-space-grotesk)]">{title}</CardTitle>
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
    <Card className={cn(className, "chart-glass")}>
      <CardHeader>
        <CardTitle className="font-[family-name:var(--font-space-grotesk)]">{title}</CardTitle>
        <CardDescription>
          Total Value: {formatCurrency(totalValue)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No assets found
          </div>
        ) : (
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {chartData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="rounded-lg border bg-background p-3 shadow-md">
                          <p className="font-medium text-purple-400">{data.name}</p>
                          <p className="text-sm font-bold">
                            {formatCurrency(data.value)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatPercentage(data.percentage, 1).replace('+', '')}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={120}
                  content={({ payload }) => (
                    <ul className="flex flex-wrap justify-center gap-x-4 gap-y-2 pt-4">
                      {payload?.map((entry: any, index: number) => (
                        <li key={`item-${index}`} className="flex items-center gap-2">
                          <div
                            className="h-2 w-2 rounded-full"
                            style={{ backgroundColor: entry.color }}
                          />
                          <span className="text-xs font-medium text-foreground whitespace-nowrap">
                            {entry.value}: {formatPercentage(chartData[index].percentage, 1).replace('+', '')}
                          </span>
                        </li>
                      ))}
                    </ul>
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
