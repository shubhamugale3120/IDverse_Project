import { QRCode } from "react-qr-code";

export default function SmartCard() {
  const demoIDverseNumber = "IDV-1234-5678";

  return (
    <main className="min-h-screen bg-[#0a192f] text-white flex flex-col items-center justify-center p-8">
      <h1 className="text-3xl font-bold text-[#64ffda] mb-6">My IDverse Smart Card</h1>

      <div className="bg-[#112240] p-6 rounded-lg shadow text-center rounded-xl">
        <p className="mb-2">Citizen: Demo User</p>
        <p className="mb-4">IDverse No: {demoIDverseNumber}</p>
        <QRCode
          value={demoIDverseNumber}
          size={200}
          bgColor="#ffffff"
          fgColor="#0a192f"
        />
      </div>
    </main>
  );
}
