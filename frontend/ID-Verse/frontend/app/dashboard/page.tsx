export default function Dashboard() {
  const citizen = {
    name: "Aishwarya Sharma",
    idverseNo: "IDV-9876-5432",
    lastLogin: "24 Sep 2025, 10:45 AM",
    walletBalance: "₹1,200",
  };

  return (
    <main className="min-h-screen bg-[#0a192f] text-gray-200 p-8">
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
          <h2 className="text-xl font-semibold mb-4">Scheme Eligibility</h2>
          <p className="mb-3 text-green-400 font-medium">You are eligible for 2 new schemes!</p>
          <ul className="list-disc ml-6 text-gray-300">
            <li>Pension Yojana ✅</li>
            <li>Health Insurance Scheme ✅</li>
          </ul>
          <button className="mt-4 w-full bg-[#64ffda] text-[#0a192f] font-semibold px-4 py-2 rounded-lg hover:scale-105 transition">
            Apply Now
          </button>
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
    </main>
  );
}
