"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { schemesAPI, benefitsAPI } from "../../lib/api";

export default function Dashboard() {
  const router = useRouter();
  const [schemes, setSchemes] = useState([]);
  const [wallet, setWallet] = useState({ balance: "₹0", transactions: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('jwt_token');
    if (!token) {
      router.push('/login');
      return;
    }
    
    loadDashboardData();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_email');
    router.push('/login');
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load schemes and wallet data in parallel
      const [schemesResponse, walletResponse] = await Promise.all([
        schemesAPI.getSchemes(),
        benefitsAPI.getWallet()
      ]);
      
      setSchemes(schemesResponse.schemes || []);
      setWallet(walletResponse);
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyScheme = async (schemeId: number) => {
    try {
      const response = await benefitsAPI.apply({
        scheme_id: schemeId,
        citizen_data: {
          email: localStorage.getItem('user_email'),
          role: localStorage.getItem('user_role')
        }
      });
      
      alert(`Application submitted! Application ID: ${response.application_id}`);
      loadDashboardData(); // Refresh data
    } catch (err: any) {
      alert(err.response?.data?.error || "Failed to apply for scheme");
    }
  };

  const citizen = {
    name: "Demo User", // This would come from user profile API
    idverseNo: "IDV-9876-5432",
    lastLogin: new Date().toLocaleString(),
    walletBalance: wallet.balance,
  };

  return (
    <main className="min-h-screen bg-[#0a192f] text-gray-200">
      {/* Navigation Bar */}
      <nav className="flex items-center justify-between px-8 py-6 bg-[#0d1b2a] shadow-md">
        <div className="flex items-center gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="url(#grad1)">
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: "#64ffda", stopOpacity: 1 }} />
                <stop offset="100%" style={{ stopColor: "#5a5dee", stopOpacity: 1 }} />
              </linearGradient>
            </defs>
            <path d="M12 1l9 4v6c0 5-3 9-9 11S3 16 3 11V5l9-4z" />
          </svg>
          <div className="flex flex-col leading-tight">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-transparent bg-clip-text">
              IDverse
            </h1>
            <span className="text-sm text-[#8892b0] font-normal">Citizen Dashboard</span>
          </div>
        </div>
        
        <div className="flex gap-4">
          <button 
            onClick={() => router.push('/smartcard')}
            className="text-[#ccd6f6] hover:text-[#64ffda] transition"
          >
            Smart Card
          </button>
          <button 
            onClick={handleLogout}
            className="text-[#ccd6f6] hover:text-[#64ffda] transition"
          >
            Logout
          </button>
        </div>
      </nav>

      <div className="p-8">
        {/* Header */}
        <header className="flex items-center justify-between bg-[#112240] p-6 rounded-lg shadow mb-6">
          <div>
            <h1 className="text-2xl font-bold text-[#64ffda]">Welcome, {citizen.name}</h1>
            <p className="text-sm text-gray-400">IDverse No: {citizen.idverseNo}</p>
            <p className="text-sm text-gray-400">Last Login: {citizen.lastLogin}</p>
          </div>
          <div className="bg-[#64ffda] text-[#0a192f] px-4 py-2 rounded-lg font-semibold">
            ✅ Verified Citizen
          </div>
        </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Linked IDs */}
        <section className="bg-[#112240] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Linked IDs</h2>
          <ul className="space-y-2 text-gray-300">
            <li>🆔 Aadhaar: ****1234</li>
            <li>💳 PAN: ****5678</li>
            <li>🗳 Voter ID: Linked</li>
            <li>🌐 Passport: Not Linked</li>
          </ul>
        </section>

        {/* Eligibility */}
        <section className="bg-[#112240] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Available Schemes</h2>
          {loading ? (
            <p className="text-gray-400">Loading schemes...</p>
          ) : error ? (
            <p className="text-red-400">{error}</p>
          ) : schemes.length > 0 ? (
            <>
              <p className="mb-3 text-green-400 font-medium">
                You are eligible for {schemes.length} scheme(s)!
              </p>
              <ul className="list-disc ml-6 text-gray-300 mb-4">
                {schemes.map((scheme: any) => (
                  <li key={scheme.id}>
                    {scheme.name} (Score: {scheme.score}) ✅
                  </li>
                ))}
              </ul>
              <button 
                onClick={() => handleApplyScheme(schemes[0].id)}
                className="w-full bg-[#64ffda] text-[#0a192f] font-semibold px-4 py-2 rounded-lg hover:scale-105 transition"
              >
                Apply for {schemes[0]?.name}
              </button>
            </>
          ) : (
            <p className="text-gray-400">No schemes available at the moment.</p>
          )}
        </section>

        {/* Wallet */}
        <section className="bg-[#112240] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">IDverse Wallet</h2>
          <p className="text-gray-300 mb-2">Balance: {citizen.walletBalance}</p>
          <p className="text-gray-300">Last Benefit: Old Age Pension (₹500)</p>
          <button className="mt-4 w-full bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-[#0a192f] font-semibold px-4 py-2 rounded-lg hover:scale-105 transition">
            View Transactions
          </button>
        </section>

        {/* Document Vault */}
        <section className="bg-[#112240] p-6 rounded-lg shadow col-span-2">
          <h2 className="text-xl font-semibold mb-4">Secure Document Vault</h2>
          <p className="text-gray-400 mb-4">Your documents are encrypted & stored via IPFS.</p>
          <div className="flex gap-4">
            <button className="bg-[#64ffda] text-[#0a192f] px-4 py-2 rounded-lg">Upload Document</button>
            <button className="border border-[#64ffda] text-[#64ffda] px-4 py-2 rounded-lg">View Stored Docs</button>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="bg-[#112240] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <ul className="space-y-3">
            <li><button className="w-full bg-[#64ffda] text-[#0a192f] px-3 py-2 rounded-lg">Generate QR</button></li>
            <li><button className="w-full border border-[#64ffda] text-[#64ffda] px-3 py-2 rounded-lg">View Smart Card</button></li>
            <li><button className="w-full border border-[#5a5dee] text-[#5a5dee] px-3 py-2 rounded-lg">Check Scheme Status</button></li>
          </ul>
        </section>
      </div>
      </div>
    </main>
  );
}
