'use client';

import { useState, useCallback } from 'react';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseApiReturn<T, Args extends unknown[]> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  execute: (...args: Args) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T, Args extends unknown[] = []>(
  apiFunction: (...args: Args) => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiReturn<T, Args> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const execute = useCallback(
    async (...args: Args): Promise<T | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await apiFunction(...args);
        setData(result);
        options.onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        options.onError?.(error);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [apiFunction, options]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return { data, error, isLoading, execute, reset };
}

// Hook for polling task status
export function useTaskPolling<T>(
  getStatus: (taskId: string) => Promise<{ data: { status: string; result?: T; error?: string } }>,
  options: {
    interval?: number;
    maxAttempts?: number;
    onComplete?: (result: T) => void;
    onError?: (error: string) => void;
  } = {}
) {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  const { interval = 2000, maxAttempts = 30, onComplete, onError } = options;

  const startPolling = useCallback(
    async (id: string) => {
      setTaskId(id);
      setIsPolling(true);
      setStatus('pending');
      setResult(null);
      setError(null);

      let attempts = 0;

      const poll = async () => {
        if (attempts >= maxAttempts) {
          setIsPolling(false);
          setError('Task timed out');
          onError?.('Task timed out');
          return;
        }

        try {
          const response = await getStatus(id);
          const taskStatus = response.data.status;
          setStatus(taskStatus);

          if (taskStatus === 'success' && response.data.result) {
            setResult(response.data.result as T);
            setIsPolling(false);
            onComplete?.(response.data.result as T);
            return;
          }

          if (taskStatus === 'failure') {
            setError(response.data.error || 'Task failed');
            setIsPolling(false);
            onError?.(response.data.error || 'Task failed');
            return;
          }

          attempts++;
          setTimeout(poll, interval);
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Polling failed';
          setError(errorMessage);
          setIsPolling(false);
          onError?.(errorMessage);
        }
      };

      poll();
    },
    [getStatus, interval, maxAttempts, onComplete, onError]
  );

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  return {
    taskId,
    status,
    result,
    error,
    isPolling,
    startPolling,
    stopPolling,
  };
}
