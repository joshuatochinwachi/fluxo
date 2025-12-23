'use client';

import { useState } from 'react';
import { useAccount } from 'wagmi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  Bell,
  Wallet,
  Shield,
  Eye,
  Moon,
  Globe,
  Zap,
  Save,
  Trash2,
  CreditCard,
  Lock,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Copy,
} from 'lucide-react';
import { useX402 } from '@/hooks/useFluxo';
import { cn, copyToClipboard } from '@/lib/utils';

export default function SettingsPage() {
  const { address, isConnected } = useAccount();
  const { executePayment, isProcessing, result, error: paymentError } = useX402();
  
  const [notifications, setNotifications] = useState({
    priceAlerts: true,
    whaleMovements: true,
    portfolioUpdates: true,
    yieldOpportunities: false,
    socialSentiment: true,
    riskAlerts: true,
  });

  const [apiKey, setApiKey] = useState('');
  const [walletAddress, setWalletAddress] = useState('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb');
  
  // x402 Payment Configuration
  const x402Config = {
    payToAddress: '0xEd04925173FAD6A8e8939338ccF23244cae1fF12',
    network: 'base-sepolia',
    facilitatorUrl: 'https://x402.treasure.lol/facilitator',
    pricePerRequest: '$0.01',
  };

  const [premiumFeatures] = useState([
    { name: 'Daily Digest', price: '$0.01', enabled: true, endpoint: '/api/v1/daily/digest' },
    { name: 'Premium Insights', price: '$0.05', enabled: false, endpoint: '/api/v1/premium/insights' },
    { name: 'Advanced Analytics', price: '$0.10', enabled: false, endpoint: '/api/v1/premium/analytics' },
  ]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your preferences and configurations</p>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="wallet">Wallet</TabsTrigger>
          <TabsTrigger value="payments">Payments (x402)</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>Customize your dashboard experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Moon className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Dark Mode</p>
                    <p className="text-sm text-muted-foreground">Toggle dark/light theme</p>
                  </div>
                </div>
                <Badge variant="secondary">Enabled</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Globe className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Default Network</p>
                    <p className="text-sm text-muted-foreground">Primary blockchain network</p>
                  </div>
                </div>
                <Badge>Mantle</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Zap className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Real-time Updates</p>
                    <p className="text-sm text-muted-foreground">WebSocket data streaming</p>
                  </div>
                </div>
                <Badge variant="success">Connected</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Eye className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">Privacy Mode</p>
                    <p className="text-sm text-muted-foreground">Hide sensitive information</p>
                  </div>
                </div>
                <Badge variant="secondary">Disabled</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Choose which alerts you want to receive</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {Object.entries(notifications).map(([key, enabled]) => (
                <div key={key} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bell className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications for {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant={enabled ? 'default' : 'outline'}
                    size="sm"
                    onClick={() =>
                      setNotifications((prev) => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))
                    }
                  >
                    {enabled ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Wallet Settings */}
        <TabsContent value="wallet">
          <Card>
            <CardHeader>
              <CardTitle>Wallet Configuration</CardTitle>
              <CardDescription>Manage your connected wallets</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="text-sm font-medium mb-2 block">Primary Wallet</label>
                <div className="flex gap-3">
                  <Input
                    value={walletAddress}
                    onChange={(e) => setWalletAddress(e.target.value)}
                    placeholder="0x..."
                    className="font-mono"
                  />
                  <Button variant="outline">
                    <Wallet className="h-4 w-4 mr-2" />
                    Connect
                  </Button>
                </div>
              </div>
              <Separator />
              <div>
                <p className="font-medium mb-4">Connected Wallets</p>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Wallet className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-mono text-sm">0x742d...0bEb</p>
                        <p className="text-xs text-muted-foreground">Mantle Network</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="success">Primary</Badge>
                      <Button variant="ghost" size="icon">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* x402 Payment Settings */}
        <TabsContent value="payments">
          <div className="space-y-6">
            {/* Payment Protocol Info */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5 text-primary" />
                  <CardTitle>x402 Payment Protocol</CardTitle>
                </div>
                <CardDescription>
                  Pay-per-request micropayments for premium API features using the x402 HTTP payment protocol
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                  <div className="flex items-start gap-3">
                    <Shield className="h-5 w-5 text-primary mt-0.5" />
                    <div>
                      <p className="font-medium text-sm">How x402 Works</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        x402 enables seamless micropayments for API requests. When you access a premium feature, 
                        your connected wallet automatically signs a payment transaction. No subscriptions needed - 
                        pay only for what you use.
                      </p>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Connection Status */}
                <div>
                  <p className="font-medium mb-4">Wallet Connection</p>
                  <div className="flex items-center justify-between p-4 rounded-lg border border-border/50">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "h-10 w-10 rounded-full flex items-center justify-center",
                        isConnected ? "bg-green-500/10" : "bg-yellow-500/10"
                      )}>
                        {isConnected ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <AlertCircle className="h-5 w-5 text-yellow-500" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">
                          {isConnected ? 'Wallet Connected' : 'Wallet Not Connected'}
                        </p>
                        {isConnected && address && (
                          <p className="text-sm text-muted-foreground font-mono">
                            {address.slice(0, 6)}...{address.slice(-4)}
                          </p>
                        )}
                      </div>
                    </div>
                    <Badge variant={isConnected ? 'success' : 'warning'}>
                      {isConnected ? 'Ready for Payments' : 'Connect Wallet'}
                    </Badge>
                  </div>
                </div>

                <Separator />

                {/* Payment Configuration */}
                <div>
                  <p className="font-medium mb-4">Payment Configuration</p>
                  <div className="grid gap-4">
                    <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                      <span className="text-sm text-muted-foreground">Payment Network</span>
                      <Badge variant="secondary">{x402Config.network}</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                      <span className="text-sm text-muted-foreground">Facilitator</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-mono">x402.treasure.lol</span>
                        <Button variant="ghost" size="icon" className="h-6 w-6" asChild>
                          <a href={x402Config.facilitatorUrl} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                      <span className="text-sm text-muted-foreground">Pay-to Address</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-mono">
                          {x402Config.payToAddress.slice(0, 6)}...{x402Config.payToAddress.slice(-4)}
                        </span>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-6 w-6"
                          onClick={() => copyToClipboard(x402Config.payToAddress)}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Premium Features */}
            <Card>
              <CardHeader>
                <CardTitle>Premium Features</CardTitle>
                <CardDescription>Pay-per-use features powered by x402</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {premiumFeatures.map((feature) => (
                    <div 
                      key={feature.name}
                      className="flex items-center justify-between p-4 rounded-lg border border-border/50"
                    >
                      <div className="flex items-center gap-4">
                        <div className={cn(
                          "h-10 w-10 rounded-full flex items-center justify-center",
                          feature.enabled ? "bg-primary/10" : "bg-muted"
                        )}>
                          {feature.enabled ? (
                            <Zap className="h-5 w-5 text-primary" />
                          ) : (
                            <Lock className="h-5 w-5 text-muted-foreground" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium">{feature.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {feature.price} per request
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant={feature.enabled ? 'success' : 'secondary'}>
                          {feature.enabled ? 'Active' : 'Coming Soon'}
                        </Badge>
                        {feature.enabled && (
                          <Button 
                            size="sm" 
                            disabled={!isConnected || isProcessing}
                            onClick={executePayment}
                          >
                            {isProcessing ? 'Processing...' : 'Test Payment'}
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {paymentError && (
                  <div className="mt-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20">
                    <p className="text-sm text-destructive">{paymentError}</p>
                  </div>
                )}

                {result !== null && (
                  <div className="mt-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                    <p className="text-sm text-green-600">Payment successful!</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Usage History */}
            <Card>
              <CardHeader>
                <CardTitle>Payment History</CardTitle>
                <CardDescription>Recent x402 payment transactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <CreditCard className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No payment history yet</p>
                  <p className="text-sm mt-1">Your x402 transactions will appear here</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* API Settings */}
        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API Configuration</CardTitle>
              <CardDescription>Manage API keys and integrations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="text-sm font-medium mb-2 block">Backend API URL</label>
                <Input
                  value="http://localhost:8000"
                  disabled
                  className="font-mono bg-muted"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Configure in .env.local file
                </p>
              </div>
              <Separator />
              <div>
                <label className="text-sm font-medium mb-2 block">Custom API Key (Optional)</label>
                <div className="flex gap-3">
                  <Input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter API key..."
                    className="font-mono"
                  />
                  <Button>
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </Button>
                </div>
              </div>
              <Separator />
              <div>
                <p className="font-medium mb-4">API Status</p>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                    <span className="text-sm">Portfolio API</span>
                    <Badge variant="success">Online</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                    <span className="text-sm">Market Data API</span>
                    <Badge variant="success">Online</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                    <span className="text-sm">Social API</span>
                    <Badge variant="success">Online</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                    <span className="text-sm">WebSocket</span>
                    <Badge variant="success">Connected</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
