import "./globals.css";
import { Inter, Poppins } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const poppins = Poppins({ subsets: ["latin"], weight: ["400","600"], variable: "--font-poppins" });

export const metadata = {
  title: "IDverse",
  description: "One Identity. Every Right.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <body className="bg-[#0a192f] text-white">
        <header className="w-full bg-[#071022] border-b border-[#112238] p-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="text-xl font-semibold">IDverse</div>
            <nav className="flex items-center gap-4 text-sm">
              <a href="/" className="hover:underline">Home</a>
              <a href="/verifier" className="hover:underline">Verifier</a>
              {/* Show Demo link only when NEXT_PUBLIC_DEMO_MODE is truthy */}
              {typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_DEMO_MODE === 'true' && (
                <a href="/demo" className="text-[#64ffda] hover:underline">Demo</a>
              )}
            </nav>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
