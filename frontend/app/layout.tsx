import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { Manrope, Space_Grotesk } from "next/font/google";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/toaster";
import { AgentProvider } from "./components/contexts/AgentContext";
import { ChatAttachmentProvider } from "./components/contexts/ChatAttachmentContext";
import { CollectionProvider } from "./components/contexts/CollectionContext";
import { ConversationProvider } from "./components/contexts/ConversationContext";
import { DocumentProvider } from "./components/contexts/DocumentContext";
import { EvaluationProvider } from "./components/contexts/EvaluationContext";
import { ProcessingProvider } from "./components/contexts/ProcessingContext";
import { RouterProvider } from "./components/contexts/RouterContext";
import { SessionProvider } from "./components/contexts/SessionContext";
import { SocketProvider } from "./components/contexts/SocketContext";
import { ToastProvider } from "./components/contexts/ToastContext";
import StartDialog from "./components/dialog/StartDialog";
import SidebarComponent from "./components/navigation/SidebarComponent";

const space_grotesk = Space_Grotesk({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-text",
  weight: ["300", "400", "500", "600", "700"],
});

const manrope = Manrope({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-heading",
  weight: ["200", "300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_BASE_URL || "https://intellyweave.ai"
  ),
  title: "IntellyWeave | AI-Powered OSINT Intelligence Platform",
  description:
    "IntellyWeave automates OSINT investigation with entity extraction, geospatial mapping, network graphs, and multi-agent reasoning backed by GPT-powered intelligence orchestration.",
  keywords: [
    "OSINT",
    "intelligence analysis",
    "entity extraction",
    "geospatial intelligence",
    "agent orchestration",
  ],
  openGraph: {
    title: "IntellyWeave | AI-Powered OSINT Intelligence Platform",
    description:
      "Flexible OSINT workflows combining GLiNER extraction, Mapbox geospatial views, vis-network graphing, and archival investigation agents for actionable intelligence.",
    url: "https://github.com/vericle/intellyweave",
    siteName: "IntellyWeave",
    images: [
      {
        url: "/assets/header.png",
        width: 1200,
        height: 630,
        alt: "IntellyWeave | AI-Powered OSINT Intelligence Platform",
      },
    ],
    locale: "en_US",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`bg-background h-screen w-screen overflow-hidden ${space_grotesk.variable} ${manrope.variable} font-text antialiased flex`}
      >
        <Suspense fallback={<div>Loading...</div>}>
          <ToastProvider>
            <RouterProvider>
              <SessionProvider>
                <CollectionProvider>
                  <DocumentProvider>
                    <AgentProvider>
                      <ConversationProvider>
                        <ChatAttachmentProvider>
                          <SocketProvider>
                            <EvaluationProvider>
                              <ProcessingProvider>
                                <SidebarProvider>
                                  <SidebarComponent />
                                  <main className="flex flex-1 min-w-0 flex-col md:flex-row w-full gap-2 md:gap-6 items-start justify-start p-2 md:p-6 overflow-auto">
                                  <SidebarTrigger className="lg:hidden flex text-secondary hover:text-primary hover:bg-foreground_alt z-50" />
                                  <StartDialog />
                                  {children}
                                </main>
                              </SidebarProvider>
                              </ProcessingProvider>
                              <Toaster />
                            </EvaluationProvider>
                          </SocketProvider>
                        </ChatAttachmentProvider>
                      </ConversationProvider>
                    </AgentProvider>
                  </DocumentProvider>
                </CollectionProvider>
              </SessionProvider>
            </RouterProvider>
          </ToastProvider>
        </Suspense>
      </body>
    </html>
  );
}
