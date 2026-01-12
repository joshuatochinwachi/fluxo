'use client';

import { Loader2, Shield, Activity, RefreshCw } from 'lucide-react';

export default function LoadingState({ message = "INITIALIZING_SYSTEM" }: { message?: string }) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-6 animate-fade-in">
            <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
                <div className="relative bg-background border border-primary/20 p-6 rounded-2xl shadow-2xl">
                    <Loader2 className="h-10 w-10 text-primary animate-spin" />
                </div>
                <div className="absolute -bottom-2 -right-2">
                    <div className="bg-primary text-primary-foreground text-[10px] font-black uppercase px-2 py-0.5 rounded-full border border-background shadow-lg">
                        v4.2.0
                    </div>
                </div>
            </div>

            <div className="flex flex-col items-center gap-2">
                <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                    <p className="text-xl font-[family-name:var(--font-vt323)] text-primary uppercase tracking-[0.2em]">
                        {message}
                    </p>
                </div>
                <p className="text-xs text-muted-foreground font-medium uppercase tracking-widest opacity-60">
                    Verifying security protocols...
                </p>
            </div>
        </div>
    );
}
