export default function VerifierPortal() {
  return (
    <main className="min-h-screen bg-[#0a192f] text-white p-8">
      <h1 className="text-3xl font-bold text-[#64ffda] mb-6">Verifier Portal</h1>

      <section className="bg-[#112240] p-6 rounded-lg shadow">
        <p className="mb-4">Enter IDverse Number or Scan QR:</p>
        <input
          type="text"
          placeholder="Enter IDverse Number"
          className="p-3 rounded-lg text-black w-full mb-4"
        />
        <button className="bg-[#64ffda] text-[#0a192f] font-semibold px-6 py-3 rounded-lg hover:scale-105 transition">
          Verify Identity
        </button>
      </section>
    </main>
  );
}
