import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { Manrope, Space_Grotesk } from "next/font/google";
import { SessionProvider } from "./components/contexts/SessionContext";
import SidebarComponent from "./components/navigation/SidebarComponent";
import { CollectionProvider } from "./components/contexts/CollectionContext";
import { DocumentProvider } from "./components/contexts/DocumentContext";
import { AgentProvider } from "./components/contexts/AgentContext";
import { ConversationProvider } from "./components/contexts/ConversationContext";
import { SocketProvider } from "./components/contexts/SocketContext";
import { EvaluationProvider } from "./components/contexts/EvaluationContext";
import StartDialog from "./components/dialog/StartDialog";
import { ToastProvider } from "./components/contexts/ToastContext";
import { ChatAttachmentProvider } from "./components/contexts/ChatAttachmentContext";

import { Toaster } from "@/components/ui/toaster";


import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { RouterProvider } from "./components/contexts/RouterContext";
import { ProcessingProvider } from "./components/contexts/ProcessingContext";

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
  title: "Elysia",
  description: "Your AI Platform",
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
