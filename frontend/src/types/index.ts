/**
 * Fluxo Type Definitions
 */

// Common Types
export interface Asset {
  token_address: string;
  token_symbol: string;
  balance: number;
  value_usd: number;
  percentage: number;
  price?: number;
  change_24h?: number;
}

export interface Portfolio {
  wallet: string;
  network: string;
  total_value_usd: number;
  assets: Asset[];
  timestamp: string;
}

export interface Alert {
  id: string;
  type: 'price' | 'whale' | 'risk' | 'yield' | 'social' | 'portfolio';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  delivered: boolean;
  wallet_address?: string;
  data?: Record<string, unknown>;
}

export interface RiskAnalysis {
  wallet: string;
  overall_risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  factors: RiskFactor[];
  recommendations: string[];
  timestamp: string;
}

export interface RiskFactor {
  name: string;
  score: number;
  weight: number;
  description: string;
}

export interface SocialSentiment {
  token_symbol: string;
  overall_sentiment: number;
  sentiment_label: 'very_negative' | 'negative' | 'neutral' | 'positive' | 'very_positive';
  platforms: PlatformSentiment[];
  trending_topics: string[];
  timestamp: string;
}

export interface PlatformSentiment {
  platform: string;
  sentiment: number;
  volume: number;
  change_24h: number;
}

export interface YieldOpportunity {
  protocol: string;
  pool: string;
  apy: number;
  tvl: number;
  risk_score: number;
  token_pair: string[];
  network: string;
}

export interface WhaleTransaction {
  id: string;
  from_address: string;
  to_address: string;
  token_symbol: string;
  amount: number;
  value_usd: number;
  timestamp: string;
  transaction_hash: string;
  type: 'transfer' | 'swap' | 'mint' | 'burn';
}

export interface Protocol {
  name: string;
  slug: string;
  tvl: number;
  apy_range: [number, number];
  risk_score: number;
  audit_status: 'audited' | 'unaudited' | 'pending';
  chains: string[];
}

export interface MarketData {
  token_symbol: string;
  price: number;
  change_24h: number;
  change_7d: number;
  volume_24h: number;
  market_cap: number;
  timestamp: string;
}

// Task Status Types
export type TaskStatus = 'pending' | 'processing' | 'success' | 'failure';

export interface TaskResult<T = unknown> {
  task_id: string;
  status: TaskStatus;
  result?: T;
  error?: string;
  progress?: number;
  message?: string;
}

// Navigation Types
export interface NavItem {
  title: string;
  href: string;
  icon: string;
  badge?: string | number;
}
