import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

// Import your new components (Path apne project structure ke hisaab se adjust kar lena)
import Navbar from "@/components/Navbar"; 
import Footer from "@/components/Footer"; 

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "UniOS.ai | The Unified OS for Students",
  description: "UniOS integrates project management, internship tracking, and personalized roadmaps into one AI-powered workspace.",
};

export default function RootLayout({
  children,
}: LayoutProps<"/">) { // Keeping your exact prop types
  
  // TODO: Replace this with your actual global auth state (e.g., from Supabase session or Context)
  const isLoggedIn = false; 

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-white">
        <Providers>
          
          {/* Top Navigation */}
          <Navbar isLoggedIn={isLoggedIn} />
          
          {/* Main Content Area - 'flex-grow' ensures footer is pushed to bottom */}
          <main className="flex-grow flex flex-col">
            {children}
          </main>
          
          {/* Global Footer */}
          <Footer />
          
        </Providers>
      </body>
    </html>
  );
}