'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { api, pollTaskStatus } from '@/lib/api/client';
import { Alert, Transaction } from '@/types';
import { useFluxo as useFluxoContext } from '@/providers/FluxoProvider';

// ============= useFluxo Hook =============

/**
 * Main hook to access global Fluxo state and network info.
 * Now consumes from FluxoProvider context to ensure shared state.
 */
export function useFluxo() {
  return useFluxoContext();
}

/**
 * Intelligence Alerts hook.
 * Consumes global alert state from FluxoProvider.
 */
export function useAlerts() {
  const {
    alerts,
    trackedWallets,
    isAlertsLoading: isLoading,
    alertsError: error,
    fetchAlerts: refetch,
    addTrackWallet,
    removeTrackWallet,
    markDelivered
  } = useFluxoContext();

  return {
    alerts,
    trackedWallets,
    isLoading,
    error,
    refetch,
    addTrackWallet,
    removeTrackWallet,
    markDelivered
  };
}

// ============= usePortfolio Hook =============

export interface PortfolioState {
  isLoading: boolean;
  data: unknown | null;
  error: string | null;
}

export function usePortfolio() {
  const { address, isWalletConnected, backendStatus } = useFluxoContext();
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
      const data = response.data as any;

      if (data.task_id) {
        const result = await pollTaskStatus(
          api.portfolio.getStatus,
          data.task_id,
          { interval: 2000, timeout: 60000 }
        );
        setState({ isLoading: false, data: result, error: null });
      } else {
        setState({ isLoading: false, data: data, error: null });
      }
    } catch (err) {
      setState({
        isLoading: false,
        data: null,
        error: err instanceof Error ? err.message : 'Failed to fetch portfolio'
      });
    }
  }, [address, backendStatus.isConnected]);

  useEffect(() => {
    const isMounted = { current: true };
    if (isWalletConnected && backendStatus.isConnected) {
      fetchPortfolio();
    }
    return () => { isMounted.current = false; };
  }, [isWalletConnected, backendStatus.isConnected, fetchPortfolio]);

  return { ...state, refetch: fetchPortfolio };
}

// ============= useWhaleMovements Hook =============

export function useWhaleMovements() {
  const [movements, setMovements] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMovements = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.whale.track();
      const data = response.data as any;

      if (data.task_id) {
        const result = await pollTaskStatus(
          api.whale.getStatus,
          data.task_id,
          { interval: 2000, timeout: 60000 }
        );
        const resultData = result as any;
        setMovements(resultData.movements || []);
      } else {
        setMovements(data.movements || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch whale movements');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const isMounted = { current: true };
    fetchMovements();
    return () => { isMounted.current = false; };
  }, [fetchMovements]);

  return { movements, isLoading, error, refetch: fetchMovements };
}

// ============= useOnchainData Hook =============

export function useOnchainData() {
  const { address } = useFluxoContext();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    if (!address) return;
    setIsLoading(true);

    try {
      const response = await api.onchain.transactions(address);
      const data = response.data as any;
      if (data.task_id) {
        const result = await pollTaskStatus(
          api.onchain.getStatus,
          data.task_id,
          { interval: 2000, timeout: 60000 }
        );
        // Ensure result is mapped to the standard Transaction interface
        const mappedResult = (Array.isArray(result) ? result : []).map((tx: any) => ({
          ...tx,
          id: tx.id || tx.tx_hash,
          amount: tx.amount || tx.value || 0,
          token: tx.token || tx.tokenSymbol || '??',
          timestamp: tx.timestamp || tx.transaction_time || new Date().toISOString(),
          value_usd: tx.value_usd || 0,
        }));
        setTransactions(mappedResult as Transaction[]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions');
    } finally {
      setIsLoading(false);
    }
  }, [address]);

  useEffect(() => {
    const isMounted = { current: true };
    if (address) fetchTransactions();
    return () => { isMounted.current = false; };
  }, [address, fetchTransactions]);

  return { transactions, isLoading, error, refetch: fetchTransactions };
}

// ============= useX402 Hook =============

export function useX402() {
  const [isExecuting, setIsExecuting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const executePayment = async (params: any) => {
    setIsExecuting(true);
    setError(null);
    try {
      const response = await api.x402.get();

      if (response.task_id) {
        setStatus('Processing payment...');
        const result = await pollTaskStatus(
          api.x402.getStatus,
          response.task_id,
          { interval: 2000, timeout: 120000 }
        );
        setStatus('Payment successful');
        return result;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment execution failed');
      throw err;
    } finally {
      setIsExecuting(false);
    }
  };

  return { executePayment, isExecuting, status, error };
}

// ============= useYieldOpportunities Hook =============

export function useYieldOpportunities() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchYields = useCallback(async () => {
    setIsLoading(true);
    setOpportunities([]); // Clear previous state to trigger loading UI if desired
    try {
      const response = await api.yield.start();

      if (response && response.task_id) {
        const result = await pollTaskStatus(
          api.yield.getStatus,
          response.task_id,
          { interval: 2000, timeout: 60000 }
        );

        // Map Backend Data to Frontend Model
        const mappedYields = (Array.isArray(result) ? result : []).map((item: any) => {
          // Risk Calculation Algorithm
          let riskScore = 5; // Base medium risk

          // APY Risk Factors
          if (item.apy > 100) riskScore += 4;
          else if (item.apy > 50) riskScore += 3;
          else if (item.apy > 20) riskScore += 1;

          // TVL Safety Factors (Higher TVL = Lower Risk)
          if (item.tvlUsd > 1000000) riskScore -= 3;
          else if (item.tvlUsd > 500000) riskScore -= 2;
          else if (item.tvlUsd < 50000) riskScore += 2; // Low liquidity penalty

          // Clamp score 1-10
          riskScore = Math.max(1, Math.min(10, riskScore));

          return {
            protocol: item.project || 'Unknown',
            pool: item.symbol || 'Unknown Pair',
            apy: Number(item.apy) || 0,
            tvl: Number(item.tvlUsd) || 0,
            risk_score: riskScore,
            token_pair: (item.symbol || '').split('-'),
            network: 'Mantle'
          };
        });

        setOpportunities(mappedYields);
      }
    } catch (err) {
      console.error('Yield Fetch Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch yield opportunities');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchYields();
  }, [fetchYields]);

  return { opportunities, isLoading, error, refetch: fetchYields };
}

// ============= useRiskAnalysis Hook =============

export function useRiskAnalysis(walletAddress?: string) {
  const { address } = useFluxoContext();
  const targetAddress = walletAddress || address;
  const [analysis, setAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = useCallback(async () => {
    if (!targetAddress) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.risk.analyze(targetAddress);
      const data = response.data as any;
      if (data.task_id) {
        const result = await pollTaskStatus(
          api.risk.getStatus,
          data.task_id,
          { interval: 2000, timeout: 60000 }
        );

        // Extract the nested risk_analysis object from the result
        const riskAnalysis = (result as any)?.risk_analysis || result;
        setAnalysis(riskAnalysis);
      }
    } catch (err) {
      console.error('Risk Analysis Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to run risk analysis');
    } finally {
      setIsLoading(false);
    }
  }, [targetAddress]);

  useEffect(() => {
    if (targetAddress) runAnalysis();
  }, [targetAddress, runAnalysis]);

  return { analysis, isLoading, error, refetch: runAnalysis };
}

// ============= useSocialSentiment Hook =============

export function useSocialSentiment() {
  const [sentiment, setSentiment] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSentiment = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.social.analyze();
      const data = response.data as any;
      if (data?.task_id) {
        const result = await pollTaskStatus(
          api.social.getStatus,
          data.task_id,
          { interval: 2000, timeout: 60000 }
        );
        setSentiment(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch social sentiment');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSentiment();
  }, [fetchSentiment]);

  return { sentiment, isLoading, error, refetch: fetchSentiment };
}

// ============= useMarketData Hook =============

export function useMarketData() {
  const [marketData, setMarketData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMarket = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.market.getData() as any;
      if (response?.task_id) {
        const result = await pollTaskStatus(
          api.market.getStatus,
          response.task_id,
          { interval: 2000, timeout: 60000 }
        );
        setMarketData(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMarket();
  }, [fetchMarket]);

  return { marketData, isLoading, error, refetch: fetchMarket };
}
