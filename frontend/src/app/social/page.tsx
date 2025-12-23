'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  MessageSquare,
  TrendingUp,
  TrendingDown,
  Twitter,
  Search,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Hash,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { formatCompactNumber, cn } from '@/lib/utils';
import { useSocialSentiment } from '@/hooks/useFluxo';

const getSentimentColor = (sentiment: number) => {
  if (sentiment >= 0.6) return 'text-green-500';
  if (sentiment >= 0.4) return 'text-yellow-500';
  return 'text-red-500';
};

const getSentimentBg = (sentiment: number) => {
  if (sentiment >= 0.6) return 'bg-green-500';
  if (sentiment >= 0.4) return 'bg-yellow-500';
  return 'bg-red-500';
};

interface PlatformData {
  platform: string;
  sentiment: number;
  volume: number;
  change_24h: number;
}

interface TrendingToken {
  symbol: string;
  sentiment: number;
  mentions: number;
  change: number;
}

interface RecentPost {
  platform: string;
  author: string;
  content: string;
  sentiment: string;
  time: string;
}

export default function SocialPage() {
  const [searchToken, setSearchToken] = useState('MNT');
  const [activeToken, setActiveToken] = useState('MNT');
  const { analyze, isAnalyzing, result, error } = useSocialSentiment();
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Initial load
  useEffect(() => {
    const init = async () => {
      await analyze('24h');
      setIsInitialLoad(false);
    };
    init();
  }, [analyze]);

  const handleAnalyze = async () => {
    setActiveToken(searchToken);
    await analyze('24h');
  };

  // Extract data from API response
  const sentiment = result as {
    token_symbol?: string;
    overall_sentiment?: number;
    sentiment_label?: string;
    platforms?: PlatformData[];
    trending_topics?: string[];
    trending_tokens?: TrendingToken[];
    recent_posts?: RecentPost[];
    timestamp?: string;
  } | null;

  const overallSentiment = sentiment?.overall_sentiment ?? 0.5;
  const sentimentLabel = sentiment?.sentiment_label ?? 'neutral';
  const platforms = sentiment?.platforms ?? [];
  const trendingTopics = sentiment?.trending_topics ?? [];
  const trendingTokens = sentiment?.trending_tokens ?? [];
  const recentPosts = sentiment?.recent_posts ?? [];
  const totalVolume = platforms.reduce((sum: number, p: PlatformData) => sum + (p.volume || 0), 0);

  if (isInitialLoad && isAnalyzing) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Social Sentiment</h1>
            <p className="text-muted-foreground mt-1">AI-powered social media analysis</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Analyzing social sentiment...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error && !result) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Social Sentiment</h1>
            <p className="text-muted-foreground mt-1">AI-powered social media analysis</p>
          </div>
        </div>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-24">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <p className="text-muted-foreground mb-4">Failed to load sentiment data</p>
            <Button variant="outline" onClick={() => analyze('24h')}>
              Try Again
            </Button>
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
          <h1 className="text-3xl font-bold">Social Sentiment</h1>
          <p className="text-muted-foreground mt-1">AI-powered social media analysis</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative flex-1 md:w-60">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search token..."
              value={searchToken}
              onChange={(e) => setSearchToken(e.target.value)}
              className="pl-10"
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
            />
          </div>
          <Button onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <MessageSquare className="h-4 w-4 mr-2" />
                Analyze
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Overall Sentiment */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-6">
              <div className={cn(
                'h-24 w-24 rounded-full flex items-center justify-center',
                getSentimentBg(overallSentiment) + '/10'
              )}>
                <div className="text-center">
                  <p className={cn('text-3xl font-bold', getSentimentColor(overallSentiment))}>
                    {(overallSentiment * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Badge
                    variant={
                      sentimentLabel === 'positive' || sentimentLabel === 'very_positive'
                        ? 'success'
                        : sentimentLabel === 'neutral'
                        ? 'secondary'
                        : 'danger'
                    }
                  >
                    {sentimentLabel.replace('_', ' ')}
                  </Badge>
                </div>
                <h3 className="text-xl font-semibold">{activeToken} Sentiment</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Based on {formatCompactNumber(totalVolume)} posts across {platforms.length} platforms
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <div className="flex items-center gap-1 justify-center">
                  <ThumbsUp className="h-4 w-4 text-green-500" />
                  <span className="text-2xl font-bold">{Math.round(overallSentiment * 100)}%</span>
                </div>
                <p className="text-xs text-muted-foreground">Positive</p>
              </div>
              <div className="text-center">
                <div className="flex items-center gap-1 justify-center">
                  <ThumbsDown className="h-4 w-4 text-red-500" />
                  <span className="text-2xl font-bold">{Math.round((1 - overallSentiment) * 100)}%</span>
                </div>
                <p className="text-xs text-muted-foreground">Negative</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Platform Breakdown & Trending */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Platform Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Platform Analysis</CardTitle>
            <CardDescription>Sentiment breakdown by social platform</CardDescription>
          </CardHeader>
          <CardContent>
            {platforms.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <MessageSquare className="h-8 w-8 mb-2" />
                <p>No platform data available</p>
              </div>
            ) : (
              <div className="space-y-6">
                {platforms.map((platform: PlatformData) => (
                  <div key={platform.platform}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Twitter className="h-4 w-4" />
                        <span className="font-medium">{platform.platform}</span>
                        <Badge variant="secondary" className="text-[10px]">
                          {formatCompactNumber(platform.volume || 0)} posts
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={cn('font-bold', getSentimentColor(platform.sentiment || 0))}>
                          {((platform.sentiment || 0) * 100).toFixed(0)}%
                        </span>
                        {(platform.change_24h || 0) >= 0 ? (
                          <TrendingUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-500" />
                        )}
                      </div>
                    </div>
                    <Progress
                      value={(platform.sentiment || 0) * 100}
                      className="h-2"
                    />
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trending Topics */}
        <Card>
          <CardHeader>
            <CardTitle>Trending Topics</CardTitle>
            <CardDescription>Most discussed topics related to {activeToken}</CardDescription>
          </CardHeader>
          <CardContent>
            {trendingTopics.length > 0 ? (
              <div className="flex flex-wrap gap-2 mb-6">
                {trendingTopics.map((topic: string) => (
                  <Badge key={topic} variant="secondary" className="px-3 py-1">
                    <Hash className="h-3 w-3 mr-1" />
                    {topic}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm mb-6">No trending topics available</p>
            )}
            <div className="space-y-4">
              <h4 className="font-medium text-sm text-muted-foreground">Trending Tokens</h4>
              {trendingTokens.length === 0 ? (
                <p className="text-sm text-muted-foreground">No trending tokens data</p>
              ) : (
                trendingTokens.map((token: TrendingToken) => (
                  <div
                    key={token.symbol}
                    className="flex items-center gap-4 p-3 rounded-lg border border-border/50"
                  >
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="font-bold text-primary text-xs">{token.symbol.slice(0, 2)}</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{token.symbol}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatCompactNumber(token.mentions || 0)} mentions
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={cn('font-bold', getSentimentColor(token.sentiment || 0))}>
                        {((token.sentiment || 0) * 100).toFixed(0)}%
                      </p>
                      <div className="flex items-center justify-end gap-1">
                        {(token.change || 0) >= 0 ? (
                          <TrendingUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-500" />
                        )}
                        <span className={cn('text-xs', (token.change || 0) >= 0 ? 'text-green-500' : 'text-red-500')}>
                          {(token.change || 0) >= 0 ? '+' : ''}{token.change || 0}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Posts */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Posts</CardTitle>
          <CardDescription>Latest social media mentions</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px]">
            {recentPosts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <MessageSquare className="h-8 w-8 mb-2" />
                <p>No recent posts available</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentPosts.map((post: RecentPost, index: number) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg border border-border/50"
                  >
                    <div className="flex items-start gap-4">
                      <div className={cn(
                        'h-8 w-8 rounded-full flex items-center justify-center',
                        post.sentiment === 'positive' ? 'bg-green-500/10' :
                        post.sentiment === 'negative' ? 'bg-red-500/10' : 'bg-gray-500/10'
                      )}>
                        {post.sentiment === 'positive' ? (
                          <ThumbsUp className="h-4 w-4 text-green-500" />
                        ) : post.sentiment === 'negative' ? (
                          <ThumbsDown className="h-4 w-4 text-red-500" />
                        ) : (
                          <Minus className="h-4 w-4 text-gray-500" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{post.author}</span>
                          <Badge variant="secondary" className="text-[10px]">
                            {post.platform}
                          </Badge>
                          <span className="text-xs text-muted-foreground">{post.time}</span>
                        </div>
                        <p className="text-sm">{post.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
