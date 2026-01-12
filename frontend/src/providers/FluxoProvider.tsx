'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, useRef, ReactNode } from 'react';
import { useAccount, useChainId, useChains } from 'wagmi';
import { api, pollTaskStatus } from '@/lib/api/client';
import { Alert, Transaction } from '@/types';

interface BackendStatus {
    isConnected: boolean;
    version?: string;
    error?: string;
}

interface FluxoContextType {
    // Wallet & Network
    address: `0x${string}` | undefined;
    isWalletConnected: boolean;
    chainId: number;
    currentChain: any;
    networkName: string;

    // Backend Status
    backendStatus: BackendStatus;
    isCheckingBackend: boolean;
    isFullyConnected: boolean;

    // Alerts System (Shared State)
    alerts: Alert[];
    trackedWallets: string[];
    isAlertsLoading: boolean;
    alertsError: string | null;
    fetchAlerts: (walletAddress?: string, limit?: number, silent?: boolean) => Promise<void>;
    addTrackWallet: (walletAddress: string) => Promise<void>;
    removeTrackWallet: (walletAddress: string) => Promise<void>;
    markDelivered: (alertId: string, walletAddress: string) => Promise<void>;
}

const FluxoContext = createContext<FluxoContextType | undefined>(undefined);

export function FluxoProvider({ children }: { children: ReactNode }) {
    const { address, isConnected } = useAccount();
    const chainId = useChainId();
    const chains = useChains();

    // 1. Backend Status State
    const [backendStatus, setBackendStatus] = useState<BackendStatus>({ isConnected: false });
    const [isCheckingBackend, setIsCheckingBackend] = useState(true);

    // 2. Alerts System State
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [trackedWallets, setTrackedWallets] = useState<string[]>([]);
    const [isAlertsLoading, setIsAlertsLoading] = useState(false);
    const [alertsError, setAlertsError] = useState<string | null>(null);

    // --- Network Logic ---
    const currentChain = chains.find((c) => c.id === chainId);
    const networkName = (() => {
        if (!currentChain) return 'mantle';
        switch (currentChain.id) {
            case 5000: return 'mantle';
            case 5003: return 'mantle-sepolia';
            case 1: return 'ethereum';
            case 8453: return 'base';
            case 84532: return 'base-sepolia';
            default: return 'mantle';
        }
    })();

    // --- Backend Check Logic ---
    const checkBackend = useCallback(async () => {
        setIsCheckingBackend(true);
        try {
            const response = await api.system.root();
            setBackendStatus({ isConnected: response.success, version: response.version });
        } catch (error) {
            setBackendStatus({
                isConnected: false,
                error: error instanceof Error ? error.message : 'Backend unreachable',
            });
        } finally {
            setIsCheckingBackend(false);
        }
    }, []);

    useEffect(() => {
        checkBackend();
        const interval = setInterval(checkBackend, 30000);
        return () => clearInterval(interval);
    }, [checkBackend]);

    // --- Alerts Intel Logic ---
    const fetchTrackedWallets = useCallback(async () => {
        try {
            const response = await api.alerts.fetchTrackedWallets();
            const data = response.data as any;
            setTrackedWallets(data.wallets || []);
        } catch (err) {
            console.error('Failed to fetch tracked wallets:', err);
        }
    }, []);

    // --- Synchronization & Guard Logic ---
    const isFetchingRef = useRef(false);
    const lastTrackedRef = useRef<string[]>([]);

    const fetchAlerts = useCallback(async (walletAddress?: string, limit = 50, silent = false) => {
        if (isFetchingRef.current && !silent) return; // Prevent concurrent noisy fetches

        if (!silent) setIsAlertsLoading(true);
        setAlertsError(null);
        isFetchingRef.current = true;

        try {
            if (walletAddress) {
                const response = await api.alerts.fetchAlerts(walletAddress, limit);
                const data = response.data as any;
                const fetchedAlerts = Array.isArray(data) ? data : (data?.alerts || []);
                setAlerts(fetchedAlerts);
            } else {
                const walletsToFetch = [...new Set([...trackedWallets, address].filter(Boolean) as string[])];
                if (walletsToFetch.length === 0) {
                    setAlerts([]);
                    return;
                }

                const results = await Promise.allSettled(
                    walletsToFetch.map(w => api.alerts.fetchAlerts(w, Math.max(10, Math.floor(limit / walletsToFetch.length))))
                );

                const allAlerts: Alert[] = [];
                results.forEach(result => {
                    if (result.status === 'fulfilled') {
                        const data = result.value.data as any;
                        const alertsFromSource = Array.isArray(data) ? data : (data?.alerts || []);
                        allAlerts.push(...alertsFromSource);
                    }
                });

                const uniqueAlerts = Array.from(new Map(allAlerts.map(a => [a.alert_id || (a as any).id, a])).values());
                const sorted = uniqueAlerts.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

                // Stability: only update if data changed (simple length/id check)
                if (sorted.length > 0 || !silent) {
                    setAlerts(sorted);
                }
            }
        } catch (err) {
            console.error('Fetch alerts error:', err);
            setAlertsError(err instanceof Error ? err.message : 'Failed to fetch alerts');
        } finally {
            isFetchingRef.current = false;
            if (!silent) setIsAlertsLoading(false);
        }
    }, [address, trackedWallets]);

    const addTrackWallet = async (walletAddress: string) => {
        try {
            await api.alerts.addTrackWallet(walletAddress);
            await fetchTrackedWallets();
        } catch (err) {
            console.error('Failed to add wallet:', err);
            throw err;
        }
    };

    const removeTrackWallet = async (walletAddress: string) => {
        try {
            await api.alerts.removeTrackWallet(walletAddress);
            await fetchTrackedWallets();
        } catch (err) {
            console.error('Failed to remove wallet:', err);
            throw err;
        }
    };

    const markDelivered = async (alertId: string, walletAddress: string) => {
        // Optimistic update
        setAlerts(prev => prev.map(a => a.alert_id === alertId ? { ...a, delivered: true } : a));
        try {
            await api.alerts.markDelivered(alertId, walletAddress, 'in-app');
        } catch (err) {
            console.error('Failed to mark delivered:', err);
            // Revert optimism if failed
            setAlerts(prev => prev.map(a => a.alert_id === alertId ? { ...a, delivered: false } : a));
        }
    };

    // Sync on mount & address change - Add deep comparison or ref guard
    useEffect(() => {
        if (!backendStatus.isConnected) return;

        const currentWallets = [...trackedWallets, address].filter(Boolean).sort();
        const lastWallets = lastTrackedRef.current;

        if (JSON.stringify(currentWallets) !== JSON.stringify(lastWallets)) {
            lastTrackedRef.current = currentWallets as string[];
            fetchTrackedWallets();
            fetchAlerts();
        }
    }, [isConnected, backendStatus.isConnected, address, trackedWallets, fetchTrackedWallets, fetchAlerts]);

    // Central Polling
    useEffect(() => {
        if (!isConnected || !backendStatus.isConnected) return;
        const interval = setInterval(() => {
            fetchAlerts(undefined, 50, true);
        }, 30000);
        return () => clearInterval(interval);
    }, [isConnected, backendStatus.isConnected, fetchAlerts]);

    const value = React.useMemo(() => ({
        address,
        isWalletConnected: isConnected,
        chainId,
        currentChain,
        networkName,
        backendStatus,
        isCheckingBackend,
        isFullyConnected: isConnected && backendStatus.isConnected,
        alerts,
        trackedWallets,
        isAlertsLoading,
        alertsError,
        fetchAlerts,
        addTrackWallet,
        removeTrackWallet,
        markDelivered,
    }), [
        address,
        isConnected,
        chainId,
        currentChain,
        networkName,
        backendStatus,
        isCheckingBackend,
        alerts,
        trackedWallets,
        isAlertsLoading,
        alertsError,
        fetchAlerts,
    ]);

    return <FluxoContext.Provider value={value}>{children}</FluxoContext.Provider>;
}

export function useFluxo() {
    const context = useContext(FluxoContext);
    if (context === undefined) {
        throw new Error('useFluxo must be used within a FluxoProvider');
    }
    return context;
}
