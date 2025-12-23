'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { PriceChart } from '@/components/dashboard';
import {
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  formatCurrency,
  formatCompactNumber,
  formatPercentage,
  getChangeColor,
  cn,
} from '@/lib/utils';
import { MarketData } from '@/types';
import { useMarketData } from '@/hooks/useFluxo';

// Type assertion for market response data
interface MarketResponse {
  tokens?: MarketData[];
  data?: MarketData[];
  price_history?: Array<{ timestamp: string; price: number }>;
}

export default function MarketPage() {
  const { data, isLoading, error, refetch } = useMarketData();
  const [selectedTokenSymbol, setSelectedTokenSymbol] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<string[]>(['MNT', 'ETH', 'BTC']);
  const [isRefetching, setIsRefetching] = useState(false);

  // Extract market data from API response with useMemo
  const marketResponse = data as MarketResponse | null;
  const marketData = useMemo(() => 
    (marketResponse?.tokens || marketResponse?.data || []) as MarketData[],
    [marketResponse]
  );
  const priceHistory = useMemo(() =>
    (marketResponse?.price_history || []) as Array<{ timestamp: string; price: number }>,
    [marketResponse]
  );

  // Derive selected token from marketData and selectedTokenSymbol
  const selectedToken = useMemo(() => {
    if (selectedTokenSymbol) {
      return marketData.find(t => t.token_symbol === selectedTokenSymbol) || null;
    }
    // Default to first token if none selected
    return marketData.length > 0 ? marketData[0] : null;
  }, [marketData, selectedTokenSymbol]);

  const handleRefetch = async () => {
    setIsRefetching(true);
    await refetch();
    setIsRefetching(false);
  };

  const setSelectedToken = (token: MarketData | null) => {
    setSelectedTokenSymbol(token?.token_symbol || null);
  };

  const toggleFavorite = (symbol: string) => {
    setFavorites(prev =>
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  // Calculate market stats
  const totalMarketCap = marketData.reduce((sum, t) => sum + (t.market_cap || 0), 0);
  const total24hVolume = marketData.reduce((sum, t) => sum + (t.volume_24h || 0), 0);
  const gainersCount = marketData.filter(t => t.change_24h > 0).length;

  if (isLoading && marketData.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Market Data</h1>
            <p className="text-muted-foreground mt-1">Real-time cryptocurrency prices and trends</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading market data...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Market Data</h1>
            <p className="text-muted-foreground mt-1">Real-time cryptocurrency prices and trends</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <p className="text-muted-foreground mb-4">Failed to load market data</p>
            <Button variant="outline" onClick={() => refetch()}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentToken = selectedToken || marketData[0];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Data</h1>
          <p className="text-muted-foreground mt-1">Real-time cryptocurrency prices and trends</p>
        </div>
        <Button variant="outline" className="gap-2" onClick={handleRefetch} disabled={isRefetching}>
          <RefreshCw className={cn("h-4 w-4", isRefetching && "animate-spin")} />
          Refresh
        </Button>
      </div>

      {/* Market Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total Market Cap</p>
            <p className="text-2xl font-bold">{formatCompactNumber(totalMarketCap)}</p>
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3 text-green-500" />
              <span className="text-xs text-green-500">+2.4%</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">24h Volume</p>
            <p className="text-2xl font-bold">{formatCompactNumber(total24hVolume)}</p>
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3 text-green-500" />
              <span className="text-xs text-green-500">+5.8%</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Tokens Tracked</p>
            <p className="text-2xl font-bold">{marketData.length}</p>
            <div className="flex items-center gap-1 mt-1">
              <span className="text-xs text-muted-foreground">{gainersCount} gaining</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Fear & Greed</p>
            <p className="text-2xl font-bold">72</p>
            <Badge variant="success" className="mt-1">Greed</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Token List */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Markets</CardTitle>
              <CardDescription>Top cryptocurrencies by market cap</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="all">
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="favorites">Favorites</TabsTrigger>
                  <TabsTrigger value="gainers">Gainers</TabsTrigger>
                  <TabsTrigger value="losers">Losers</TabsTrigger>
                </TabsList>
                <TabsContent value="all" className="mt-4">
                  <ScrollArea className="h-[400px]">
                    {marketData.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                        <p>No market data available</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {marketData.map((token: MarketData, index: number) => (
                          <div
                            key={token.token_symbol}
                            className={`flex items-center gap-4 p-4 rounded-lg border transition-colors cursor-pointer ${
                              currentToken?.token_symbol === token.token_symbol
                                ? 'border-primary bg-primary/5'
                                : 'border-border/50 hover:bg-muted/50'
                            }`}
                            onClick={() => setSelectedToken(token)}
                          >
                            <span className="text-sm text-muted-foreground w-6">{index + 1}</span>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorite(token.token_symbol);
                              }}
                            >
                              <Star
                                className={`h-4 w-4 ${
                                  favorites.includes(token.token_symbol)
                                    ? 'fill-yellow-500 text-yellow-500'
                                    : 'text-muted-foreground'
                                }`}
                              />
                            </Button>
                            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                              <span className="font-bold text-primary text-sm">
                                {token.token_symbol.slice(0, 2)}
                              </span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium">{token.token_symbol}</p>
                              <p className="text-sm text-muted-foreground">
                                Vol: {formatCompactNumber(token.volume_24h)}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium">{formatCurrency(token.price)}</p>
                              <div className="flex items-center justify-end gap-1">
                                {token.change_24h >= 0 ? (
                                  <ArrowUpRight className={`h-3 w-3 ${getChangeColor(token.change_24h)}`} />
                                ) : (
                                  <ArrowDownRight className={`h-3 w-3 ${getChangeColor(token.change_24h)}`} />
                                )}
                                <span className={`text-xs ${getChangeColor(token.change_24h)}`}>
                                  {formatPercentage(token.change_24h)}
                                </span>
                              </div>
                            </div>
                            <div className="text-right hidden md:block">
                              <p className="text-sm text-muted-foreground">7d</p>
                              <span className={`text-xs ${getChangeColor(token.change_7d)}`}>
                                {formatPercentage(token.change_7d)}
                              </span>
                            </div>
                            <div className="text-right hidden lg:block">
                              <p className="text-sm text-muted-foreground">MCap</p>
                              <p className="text-xs">{formatCompactNumber(token.market_cap)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </TabsContent>
                <TabsContent value="favorites" className="mt-4">
                  <ScrollArea className="h-[400px]">
                    <div className="space-y-2">
                      {marketData
                        .filter((t: MarketData) => favorites.includes(t.token_symbol))
                        .map((token: MarketData) => (
                          <div
                            key={token.token_symbol}
                            className="flex items-center gap-4 p-4 rounded-lg border border-border/50 hover:bg-muted/50 cursor-pointer"
                            onClick={() => setSelectedToken(token)}
                          >
                            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                              <span className="font-bold text-primary text-sm">
                                {token.token_symbol.slice(0, 2)}
                              </span>
                            </div>
                            <div className="flex-1">
                              <p className="font-medium">{token.token_symbol}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium">{formatCurrency(token.price)}</p>
                              <span className={`text-xs ${getChangeColor(token.change_24h)}`}>
                                {formatPercentage(token.change_24h)}
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                </TabsContent>
                <TabsContent value="gainers" className="mt-4">
                  <ScrollArea className="h-[400px]">
                    <div className="space-y-2">
                      {marketData
                        .filter((t: MarketData) => t.change_24h > 0)
                        .sort((a: MarketData, b: MarketData) => b.change_24h - a.change_24h)
                        .map((token: MarketData) => (
                          <div
                            key={token.token_symbol}
                            className="flex items-center gap-4 p-4 rounded-lg border border-border/50 hover:bg-muted/50 cursor-pointer"
                            onClick={() => setSelectedToken(token)}
                          >
                            <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                              <TrendingUp className="h-5 w-5 text-green-500" />
                            </div>
                            <div className="flex-1">
                              <p className="font-medium">{token.token_symbol}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium">{formatCurrency(token.price)}</p>
                              <span className="text-xs text-green-500">
                                {formatPercentage(token.change_24h)}
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                </TabsContent>
                <TabsContent value="losers" className="mt-4">
                  <ScrollArea className="h-[400px]">
                    <div className="space-y-2">
                      {marketData
                        .filter((t: MarketData) => t.change_24h < 0)
                        .sort((a: MarketData, b: MarketData) => a.change_24h - b.change_24h)
                        .map((token: MarketData) => (
                          <div
                            key={token.token_symbol}
                            className="flex items-center gap-4 p-4 rounded-lg border border-border/50 hover:bg-muted/50 cursor-pointer"
                            onClick={() => setSelectedToken(token)}
                          >
                            <div className="h-10 w-10 rounded-full bg-red-500/10 flex items-center justify-center">
                              <TrendingDown className="h-5 w-5 text-red-500" />
                            </div>
                            <div className="flex-1">
                              <p className="font-medium">{token.token_symbol}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium">{formatCurrency(token.price)}</p>
                              <span className="text-xs text-red-500">
                                {formatPercentage(token.change_24h)}
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Selected Token Chart */}
        <div>
          <PriceChart
            data={priceHistory.length > 0 ? priceHistory : [{ timestamp: new Date().toISOString(), price: currentToken?.price || 0 }]}
            title={`${currentToken?.token_symbol || 'Token'} Price`}
            description="24-hour price history"
            loading={isLoading}
            color="#3B82F6"
          />
          {currentToken && (
            <Card className="mt-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">{currentToken.token_symbol} Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Price</span>
                    <span className="font-medium">{formatCurrency(currentToken.price)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">24h Change</span>
                    <span className={getChangeColor(currentToken.change_24h)}>
                      {formatPercentage(currentToken.change_24h)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">7d Change</span>
                    <span className={getChangeColor(currentToken.change_7d)}>
                      {formatPercentage(currentToken.change_7d)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Volume (24h)</span>
                    <span className="font-medium">{formatCompactNumber(currentToken.volume_24h)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Market Cap</span>
                    <span className="font-medium">{formatCompactNumber(currentToken.market_cap)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
