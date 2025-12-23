'use client';

import { useAccount, useChainId, useChains } from 'wagmi';
import { useState, useEffect, useCallback } from 'react';
import { api, pollTaskStatus, type TaskStatus, type APIResponse } from '@/lib/api/client';

// ============= Types =============

export interface BackendStatus {
  isConnected: boolean;
  version?: string;
  error?: string;
}

export interface PortfolioState {
  isLoading: boolean;
  data: unknown | null;
  error: string | null;
}

// ============= useFluxo Hook =============

export function useFluxo() {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const chains = useChains();
  
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({
    isConnected: false,
  });
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      setIsCheckingBackend(true);
      try {
        const response = await api.system.root();
        setBackendStatus({
          isConnected: response.success,
          version: response.version,
        });
      } catch (error) {
        setBackendStatus({
          isConnected: false,
          error: error instanceof Error ? error.message : 'Backend unreachable',
        });
      } finally {
        setIsCheckingBackend(false);
      }
    };

    checkBackend();
    // Re-check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  // Get current chain info
  const currentChain = chains.find((c) => c.id === chainId);

  // Get network name for API calls
  const getNetworkName = useCallback(() => {
    if (!currentChain) return 'mantle';
    switch (currentChain.id) {
      case 5000: return 'mantle';
      case 5003: return 'mantle-sepolia';
      case 1: return 'ethereum';
      case 8453: return 'base';
      case 84532: return 'base-sepolia';
      default: return 'mantle';
    }
  }, [currentChain]);

  return {
    // Wallet state
    address,
    isWalletConnected: isConnected,
    chainId,
    currentChain,
    networkName: getNetworkName(),
    
    // Backend state
    backendStatus,
    isCheckingBackend,
    isFullyConnected: isConnected && backendStatus.isConnected,
  };
}

// ============= usePortfolio Hook =============

export function usePortfolio() {
  const { address, isWalletConnected, backendStatus } = useFluxo();
  const [state, setState] = useState<PortfolioState>({
    isLoading: false,
    data: null,
    error: null,
  });

  const fetchPortfolio = useCallback(async () => {
    if (!address || !backendStatus.isConnected) return;
    
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await api.portfolio.get(address);
      const responseData = response.data as Record<string, unknown> | undefined;
      setState({
        isLoading: false,
        data: responseData?.result || responseData || null,
        error: null,
      });
    } catch (error) {
      setState({
        isLoading: false,
        data: null,
        error: error instanceof Error ? error.message : 'Failed to fetch portfolio',
      });
    }
  }, [address, backendStatus.isConnected]);

  // Fetch portfolio when wallet connects - this is intentional synchronization
  useEffect(() => {
    if (isWalletConnected && backendStatus.isConnected) {
      fetchPortfolio();
    }
  }, [isWalletConnected, backendStatus.isConnected, fetchPortfolio]);

  return {
    ...state,
    refetch: fetchPortfolio,
  };
}

// ============= useRiskAnalysis Hook =============

export function useRiskAnalysis() {
  const { address, backendStatus } = useFluxo();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const analyze = useCallback(async (marketCorrelation?: number) => {
    if (!address || !backendStatus.isConnected) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await api.risk.analyze(address, marketCorrelation);
      const responseData = response.data as Record<string, unknown> | undefined;
      const taskIdFromResponse = responseData?.task_id as string | undefined;
      
      if (taskIdFromResponse) {
        setTaskId(taskIdFromResponse);
        const analysisResult = await pollTaskStatus(
          api.risk.getStatus as (taskId: string) => Promise<APIResponse<TaskStatus<unknown>>>,
          taskIdFromResponse,
          { interval: 2000, timeout: 60000 }
        );
        setResult(analysisResult);
      } else {
        setResult(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Risk analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  }, [address, backendStatus.isConnected]);

  return {
    analyze,
    isAnalyzing,
    result,
    error,
    taskId,
  };
}

// ============= useAlerts Hook =============

export function useAlerts() {
  const { address, backendStatus } = useFluxo();
  const [alerts, setAlerts] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async (limit = 50) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.alerts.list(address || undefined, limit);
      const responseData = response.data as Record<string, unknown> | undefined;
      setAlerts((responseData?.alerts as unknown[]) || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts');
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  }, [address]);

  const markDelivered = useCallback(async (alertId: string, deliveryMethod = 'web') => {
    if (!address) return;
    
    try {
      await api.alerts.markDelivered(alertId, address, deliveryMethod);
      await fetchAlerts();
    } catch (err) {
      console.error('Failed to mark alert as delivered:', err);
    }
  }, [address, fetchAlerts]);

  useEffect(() => {
    if (backendStatus.isConnected) {
      fetchAlerts();
    }
  }, [backendStatus.isConnected, fetchAlerts]);

  return {
    alerts,
    isLoading,
    error,
    refetch: fetchAlerts,
    markDelivered,
  };
}

// ============= useSocialSentiment Hook =============

export function useSocialSentiment() {
  const { backendStatus } = useFluxo();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (timeframe = '24h') => {
    if (!backendStatus.isConnected) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await api.social.analyze(timeframe);
      const responseData = response.data as Record<string, unknown> | undefined;
      const taskIdFromResponse = responseData?.task_id as string | undefined;
      
      if (taskIdFromResponse) {
        const analysisResult = await pollTaskStatus(
          api.social.getStatus as (taskId: string) => Promise<APIResponse<TaskStatus<unknown>>>,
          taskIdFromResponse,
          { interval: 2000, timeout: 60000 }
        );
        setResult(analysisResult);
      } else {
        setResult(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Social analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  }, [backendStatus.isConnected]);

  const getTokenSentiment = useCallback(async (tokenSymbol: string) => {
    if (!backendStatus.isConnected) return null;
    
    try {
      const response = await api.social.sentiment(tokenSymbol);
      return response.data;
    } catch (err) {
      console.error('Failed to get token sentiment:', err);
      return null;
    }
  }, [backendStatus.isConnected]);

  return {
    analyze,
    getTokenSentiment,
    isAnalyzing,
    result,
    error,
  };
}

// ============= useYieldOpportunities Hook =============

export function useYieldOpportunities() {
  const { backendStatus } = useFluxo();
  const [opportunities, setOpportunities] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOpportunities = useCallback(async () => {
    if (!backendStatus.isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.yield.get();
      if (response.task_id) {
        const result = await pollTaskStatus(
          api.yield.getStatus as unknown as (taskId: string) => Promise<TaskStatus<unknown[]>>,
          response.task_id,
          { interval: 2000, timeout: 60000 }
        );
        setOpportunities(Array.isArray(result) ? result : []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch yield opportunities');
      setOpportunities([]);
    } finally {
      setIsLoading(false);
    }
  }, [backendStatus.isConnected]);

  useEffect(() => {
    if (backendStatus.isConnected) {
      fetchOpportunities();
    }
  }, [backendStatus.isConnected, fetchOpportunities]);

  return {
    opportunities,
    isLoading,
    error,
    refetch: fetchOpportunities,
  };
}

// ============= useWhaleTracking Hook =============

export function useWhaleTracking() {
  const { backendStatus } = useFluxo();
  const [movements, setMovements] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const track = useCallback(async (timeframe = '24h', minValueUsd = 100000) => {
    if (!backendStatus.isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.whale.track(timeframe, minValueUsd);
      const responseData = response.data as Record<string, unknown> | undefined;
      const taskIdFromResponse = responseData?.task_id as string | undefined;
      
      if (taskIdFromResponse) {
        const result = await pollTaskStatus(
          api.whale.getStatus as unknown as (taskId: string) => Promise<APIResponse<TaskStatus<unknown[]>>>,
          taskIdFromResponse,
          { interval: 2000, timeout: 60000 }
        );
        setMovements(Array.isArray(result) ? result : []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to track whales');
      setMovements([]);
    } finally {
      setIsLoading(false);
    }
  }, [backendStatus.isConnected]);

  return {
    movements,
    isLoading,
    error,
    track,
  };
}
// ============= useOnchainData Hook =============

export function useOnchainData() {
  const { address, backendStatus } = useFluxo();
  const [protocols, setProtocols] = useState<unknown[]>([]);
  const [transactions, setTransactions] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProtocols = useCallback(async () => {
    if (!backendStatus.isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.onchain.protocols();
      const responseData = response.data as Record<string, unknown> | undefined;
      const taskIdFromResponse = responseData?.task_id as string | undefined;
      if (taskIdFromResponse) {
        const result = await pollTaskStatus(
          api.onchain.getStatus as unknown as (taskId: string) => Promise<APIResponse<TaskStatus<unknown[]>>>,
          taskIdFromResponse,
          { interval: 2000, timeout: 60000 }
        );
        setProtocols(Array.isArray(result) ? result : []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch protocols');
    } finally {
      setIsLoading(false);
    }
  }, [backendStatus.isConnected]);

  const fetchTransactions = useCallback(async () => {
    if (!address || !backendStatus.isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.onchain.transactions(address);
      setTransactions((response.data as unknown[]) || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions');
    } finally {
      setIsLoading(false);
    }
  }, [address, backendStatus.isConnected]);

  useEffect(() => {
    if (backendStatus.isConnected) {
      fetchProtocols();
      if (address) {
        fetchTransactions();
      }
    }
  }, [backendStatus.isConnected, address, fetchProtocols, fetchTransactions]);

  return {
    protocols,
    transactions,
    isLoading,
    error,
    refetchProtocols: fetchProtocols,
    refetchTransactions: fetchTransactions,
  };
}

// ============= useMarketData Hook =============

export function useMarketData() {
  const { backendStatus } = useFluxo();
  const [data, setData] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMarketData = useCallback(async () => {
    if (!backendStatus.isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.market.getData();
      if (response.task_id) {
        const result = await pollTaskStatus(
          api.market.getStatus as unknown as (taskId: string) => Promise<TaskStatus<unknown>>,
          response.task_id,
          { interval: 2000, timeout: 60000 }
        );
        setData(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market data');
    } finally {
      setIsLoading(false);
    }
  }, [backendStatus.isConnected]);

  useEffect(() => {
    if (backendStatus.isConnected) {
      fetchMarketData();
    }
  }, [backendStatus.isConnected, fetchMarketData]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchMarketData,
  };
}

// ============= useDailyDigest Hook =============

export function useDailyDigest() {
  const { backendStatus } = useFluxo();
  const [digest, setDigest] = useState<unknown[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDigest = useCallback(async () => {
    if (!backendStatus.isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.digest.get();
      setDigest(Array.isArray(response) ? response : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch digest');
      setDigest([]);
    } finally {
      setIsLoading(false);
    }
  }, [backendStatus.isConnected]);

  useEffect(() => {
    if (backendStatus.isConnected) {
      fetchDigest();
    }
  }, [backendStatus.isConnected, fetchDigest]);

  return {
    digest,
    isLoading,
    error,
    refetch: fetchDigest,
  };
}

// ============= useX402 Hook =============

export function useX402() {
  const { backendStatus } = useFluxo();
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);

  const executePayment = useCallback(async () => {
    if (!backendStatus.isConnected) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await api.x402.get();
      if (response.task_id) {
        const paymentResult = await pollTaskStatus(
          api.x402.getStatus,
          response.task_id,
          { interval: 2000, timeout: 60000 }
        );
        setResult(paymentResult);
        return paymentResult;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment failed');
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, [backendStatus.isConnected]);

  return {
    executePayment,
    isProcessing,
    result,
    error,
  };
}

export default useFluxo;
