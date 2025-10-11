// components/Navbar.tsx
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-[#0d1b2a] text-gray-200 shadow-md">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold text-[#64ffda]">IDverse</h1>
      </div>
      <div className="flex gap-6">
        <Link href="/" className="hover:text-[#64ffda] transition">Home</Link>
        <Link href="/dashboard" className="hover:text-[#64ffda] transition">Dashboard</Link>
        <Link href="/verifier" className="hover:text-[#64ffda] transition">Verifier</Link>
        <Link href="/smartcard" className="hover:text-[#64ffda] transition">Smart Card</Link>
      </div>
    </nav>
  );
}
