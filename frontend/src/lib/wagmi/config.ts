'use client';

import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { mainnet, mantle, mantleSepoliaTestnet, base, baseSepolia } from 'wagmi/chains';

export const config = getDefaultConfig({
  appName: 'Fluxo',
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || 'demo-project-id',
  chains: [mantle, mantleSepoliaTestnet, mainnet, base, baseSepolia],
  ssr: true,
});

export { mantle, mantleSepoliaTestnet, mainnet, base, baseSepolia };
