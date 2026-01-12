/**
 * Fluxo API Client
 * Comprehensive API client for all backend endpoints
 */

const API_BASE_URL = '/api/proxy';
import { Transaction, Alert } from '@/types';

// ============= Types =============

export interface APIResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
}

export interface TaskResponse {
  agent: string;
  task_id: string;
}

export interface TaskStatus<T = unknown> {
  task_id: string;
  status: string;
  result?: T;
  progress?: number;
  message?: string;
  error?: string;
}

export interface PortfolioAsset {
  user_address: string;
  token_address: string;
  token_symbol: string;
  balance: number;
  value_usd: number;
  price_usd: number;
  percentage_of_portfolio: number;
}

export interface PortfolioData {
  task_id: string | null;
  check_status: string;
}

export interface RiskAnalysis {
  overall_score: number;
  factors: Array<{
    name: string;
    score: number;
    weight: number;
  }>;
  recommendations: string[];
}

export interface SocialSentiment {
  overall_score: number;
  trending_topics: string[];
  sentiment_breakdown: {
    positive: number;
    neutral: number;
    negative: number;
  };
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

export interface WhaleMovement {
  tx_hash: string;
  from_address: string;
  to_address: string;
  value_usd: number;
  token_symbol: string;
  timestamp: string;
}

// Redundant types removed - imported from @/types
export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  relevance: number;
  categories: string[];
  tags: string[];
}

interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
  next?: {
    revalidate?: number | false;
    tags?: string[];
  };
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private buildUrl(endpoint: string, params?: Record<string, string | number | boolean | undefined>): string {
    const baseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const baseUrlStr = `${baseUrl}${cleanEndpoint}`;
    let url: URL;
    try {
      url = new URL(baseUrlStr);
    } catch {
      // Handle relative URLs (like /api/proxy)
      const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';
      url = new URL(baseUrlStr, origin);
    }
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    return url.toString();
  }

  async request<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const { params, ...fetchConfig } = config;
    const url = this.buildUrl(endpoint, params);

    const response = await fetch(url, {
      ...fetchConfig,
      headers: {
        'Content-Type': 'application/json',
        ...fetchConfig.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.detail || error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  async post<T>(endpoint: string, data?: unknown, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      params,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new APIClient(API_BASE_URL);

// Export typed API functions for each domain
export const api = {
  // Portfolio
  portfolio: {
    get: (address: string) =>
      apiClient.get<APIResponse<PortfolioData>>('/api/v1/agent/portfolio', { address }),
    getInsights: (walletAddress: string, network: string = 'mantle') =>
      apiClient.post<APIResponse>('/api/v1/agent/portfolio/insights', { wallet_address: walletAddress, network }),
    quickInsights: (walletAddress: string) =>
      apiClient.post<APIResponse>('/api/v1/agent/insights/quick', null, { wallet_address: walletAddress }),
    getStatus: (taskId: string) =>
      apiClient.get<TaskStatus<PortfolioAsset[]>>(`/api/v1/agent/status/portfolio/${taskId}`),
    health: () => apiClient.get<{ service: string; status: string }>('/api/v1/agent/health'),
  },

  // Market Data
  market: {
    getData: () => apiClient.get<{ agent: string; task_id: string }>('/agent/market/market_data'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/market/market_data/status/${taskId}`),
  },

  // Alerts & Monitoring API
  alerts: {
    // 1. Add Wallet to Tracking (POST /api/alerts/add/track-wallet)
    addTrackWallet: (walletAddress: string) =>
      apiClient.post<APIResponse>(`/api/alerts/add/track-wallet?wallet_address=${walletAddress}`),

    // 2. Remove Wallet from Tracking (DELETE /api/alerts/remove/track-wallet)
    removeTrackWallet: (walletAddress: string) =>
      apiClient.delete<APIResponse>(`/api/alerts/remove/track-wallet?wallet_address=${walletAddress}`),

    // 3. Fetch Alerts (GET /api/alerts/fetch)
    fetchAlerts: (walletAddress?: string, limit: number = 50) =>
      apiClient.get<APIResponse>(`/api/alerts/fetch`, {
        wallet_address: walletAddress,
        limit
      }),

    // 4. Fetch Undelivered Alerts (GET /api/alerts/undelivered)
    fetchUndelivered: (walletAddress: string) =>
      apiClient.get<APIResponse>(`/api/alerts/undelivered`, { wallet_address: walletAddress }),

    // 5. Mark Alert as Delivered (POST /api/alerts/mark-delivered/{alert_id})
    markDelivered: (alertId: string, walletAddress: string, deliveryMethod: string) =>
      apiClient.post<APIResponse>(`/api/alerts/mark-delivered/${alertId}?wallet_address=${walletAddress}&delivery_method=${deliveryMethod}`),

    // 6. Fetch Tracked Wallets (GET /api/alerts/fetch/tracked-wallets)
    fetchTrackedWallets: () =>
      apiClient.get<APIResponse>('/api/alerts/fetch/tracked-wallets'),

    // Legacy/Internal helpers (can be kept if needed but focusing on the 6 above)
    coordinate: (walletAddress: string, analysisTypes?: string[]) =>
      apiClient.post<APIResponse>('/api/alerts/coordinate', null, {
        wallet_address: walletAddress,
        analysis_types: analysisTypes?.join(',')
      }),
    health: () =>
      apiClient.get<APIResponse>('/api/alerts/health'),
  },


  // Risk Analysis
  risk: {
    analyze: (walletAddress: string, marketCorrelation?: number) =>
      apiClient.post<APIResponse>('/api/agent/risk/analyze', null, { wallet_address: walletAddress, market_correlation: marketCorrelation }),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/api/agent/risk/status/${taskId}`),
    auditCheck: (walletAddress: string, network: string = 'mantle') =>
      apiClient.post<APIResponse>('/api/agent/risk/audit-check', { wallet_address: walletAddress, network }),
    protocol: (protocolName: string) =>
      apiClient.get<APIResponse>(`/api/agent/risk/protocol/${protocolName}`),
    health: () => apiClient.get<APIResponse>('/api/agent/risk/health'),
  },

  // Social Sentiment
  social: {
    analyze: (timeframe: string = '24h') =>
      apiClient.post<APIResponse>('/agent/social/analyze', null, { timeframe }),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/social/status/${taskId}`),
    sentiment: (tokenSymbol: string) =>
      apiClient.post<APIResponse>('/agent/social/sentiment', null, { token_symbol: tokenSymbol }),
    narratives: (tokenSymbol: string) => apiClient.get<APIResponse>(`/agent/social/narratives/${tokenSymbol}`),
    platforms: (tokenSymbol: string) =>
      apiClient.get<APIResponse>(`/agent/social/platforms/${tokenSymbol}`),
    supportedPlatforms: () => apiClient.get<APIResponse>('/agent/social/supported-platforms'),
    health: () => apiClient.get<APIResponse>('/agent/social/social'),
  },

  // On-chain Data
  onchain: {
    get: () => apiClient.get<{ agent: string; task_id: string }>('/api/agent/onchain/'),
    protocols: () => apiClient.get<APIResponse>('/api/agent/onchain/protocols'),
    transactions: (walletAddress: string) =>
      apiClient.get<APIResponse<{ task_id: string; check_status: string }>>('/api/agent/onchain/transactions', { wallet_address: walletAddress }),
    getStatus: (taskId: string) => apiClient.get<TaskStatus<Transaction[]>>(`/api/agent/onchain/status/${taskId}`),
  },

  // Whale Tracking (Note: Whale router needs to be mounted in backend main.py)
  whale: {
    track: (timeframe: string = '24h', minValueUsd: number = 100000) =>
      apiClient.post<APIResponse>('/agent/whale/track', null, { timeframe, min_value_usd: minValueUsd }),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/whale/status/${taskId}`),
    health: () => apiClient.get<APIResponse>('/agent/whale/whale'),
  },

  // x402 Payment Protocol
  x402: {
    get: () => apiClient.get<TaskResponse>('/agent/x402'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/x402/status/${taskId}`),
  },

  // Automation Agent
  automation: {
    get: () => apiClient.get<TaskResponse>('/agent/automation/automation'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/automation/automation/status/${taskId}`),
  },

  // Execution Agent
  execution: {
    get: () => apiClient.get<TaskResponse>('/agent/execution/execution'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/execution/execution/status/${taskId}`),
  },

  // Macro Analysis Agent
  macro: {
    get: () => apiClient.get<TaskResponse>('/agent/macro/macro'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/macro/macro/status/${taskId}`),
  },

  // Daily Digest
  digest: {
    get: () => apiClient.get<NewsItem[]>('/api/v1/daily/digest'),
  },

  // System
  system: {
    health: () => apiClient.get<{ status: string }>('/api/v1/system/health'),
    rootHealth: () => apiClient.get<APIResponse>('/health'),
    root: () => apiClient.get<{ success: boolean; message: string; version: string }>('/'),
    analyzeComplete: (walletAddress: string) =>
      apiClient.post<APIResponse>('/api/v1/system/analyze-complete', null, { wallet_address: walletAddress }),
    batchAnalyze: (walletAddresses: string[]) =>
      apiClient.post<APIResponse>('/api/v1/system/batch-analyze', null, { wallet_addresses: walletAddresses.join(',') }),
    status: () => apiClient.get<APIResponse>('/api/v1/system/status'),
  },

  // Governance
  governance: {
    get: () => apiClient.get<TaskResponse>('/agent/governance/governance'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/governance/governance/status/${taskId}`),
  },

  // Research
  research: {
    get: () => apiClient.get<TaskResponse>('/agent/research/research'),
    getStatus: (taskId: string) => apiClient.get<TaskStatus>(`/agent/research/research/status/${taskId}`),
  },

  // Yield Intelligence
  yield: {
    start: () => apiClient.get<TaskResponse>('/agent/yield', {
      cache: 'no-store',
      next: { revalidate: 0 }
    }),
    getStatus: (taskId: string) => apiClient.get<TaskStatus<any[]>>(`/agent/yield/status/${taskId}`, {
      cache: 'no-store',
      next: { revalidate: 0 }
    }),
  },
};

// ============= Task Polling Helper =============

export async function pollTaskStatus<T>(
  getStatusFn: (taskId: string) => Promise<TaskStatus<T> | APIResponse<TaskStatus<T>>>,
  taskId: string,
  options: {
    interval?: number;
    timeout?: number;
    onProgress?: (progress: number, message?: string) => void;
  } = {}
): Promise<T> {
  const { interval = 2000, timeout = 120000, onProgress } = options;
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        if (Date.now() - startTime > timeout) {
          reject(new Error('Task timeout'));
          return;
        }

        const response = await getStatusFn(taskId);
        const status = 'data' in response ? response.data : response;

        if (status.status?.toLowerCase() === 'success' || status.status?.toLowerCase() === 'completed') {
          resolve(status.result as T);
          return;
        }

        if (status.status?.toLowerCase() === 'failure' || status.status?.toLowerCase() === 'failed') {
          reject(new Error(status.error || 'Task failed'));
          return;
        }

        if (onProgress && status.progress !== undefined) {
          onProgress(status.progress, status.message);
        }

        setTimeout(poll, interval);
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

// WebSocket URL helper for smart money tracking
export function getSmartMoneyWsUrl(): string {
  return `${API_BASE_URL.replace('http', 'ws')}/api/agent/onchain/smart_money`;
}

export default api;
