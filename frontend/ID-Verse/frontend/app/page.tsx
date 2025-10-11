import Link from "next/link";

export default function IDverseHome() {
  return (
    <main className="min-h-screen bg-[#0d1b2a] text-gray-200 font-sans flex flex-col">

      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-6 bg-[#0d1b2a] shadow-md">
        {/* Logo + Tagline */}
        <div className="flex items-center gap-3">
          {/* Shield Icon */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-8 w-8"
            viewBox="0 0 24 24"
            fill="url(#grad1)"
          >
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
            <span className="text-sm text-[#8892b0] font-normal">Secure Digital Identity</span>
          </div>
        </div>

        {/* Middle Tagline / Status */}
        <div className="hidden md:flex flex-col items-center">
          <span className="text-sm font-medium text-[#ccd6f6]">
            Trusted by Citizens • Powered by AI + Blockchain
          </span>
          <span className="mt-1 px-2 py-0.5 text-xs rounded-full bg-[#112240] text-[#64ffda] border border-[#64ffda]">
            Beta v1.0
          </span>
        </div>

        {/* Navigation Links */}
        <div className="flex gap-6 text-[#ccd6f6]">
          <Link href="/" className="hover:text-[#64ffda] transition">Home</Link>
          <Link href="/login" className="hover:text-[#64ffda] transition">Login</Link>
          <Link href="/register" className="hover:text-[#64ffda] transition">Register</Link>
          <Link href="/verifier" className="hover:text-[#64ffda] transition">Verifier</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative flex-1 flex flex-col items-center justify-center text-center px-6 py-24 overflow-hidden">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0d1b2a] to-[#112240] -z-10"></div>

        {/* Animated blobs */}
        <div className="absolute -top-16 -left-16 w-60 h-60 bg-[#64ffda] rounded-full opacity-10 animate-blob mix-blend-multiply"></div>
        <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-[#5a5dee] rounded-full opacity-10 animate-blob animation-delay-4000 mix-blend-multiply"></div>
        <div className="absolute -top-32 -right-12 w-52 h-52 bg-[#3ae374] rounded-full opacity-10 animate-blob animation-delay-2000 mix-blend-multiply"></div>

        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-transparent bg-clip-text mb-6 max-w-3xl z-10 leading-snug">
          One Identity. Every Right.
        </h1>
        <p className="text-lg md:text-xl text-gray-300 mb-10 max-w-4xl z-10 leading-relaxed">
          IDverse unifies Aadhaar, PAN, Voter ID, and essential services into a secure, scalable digital identity and welfare wallet—making benefits automatic, traceable, and inclusive for every citizen.
        </p>

        {/* Hero CTAs */}
        <div className="flex gap-6 flex-wrap justify-center z-10">
          {/* Register Button → /register */}
          <Link
            href="/register"
            className="bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-[#0d1b2a] font-semibold px-8 py-3 rounded-lg shadow-lg hover:scale-105 transition text-center"
          >
            Create Account
          </Link>

          {/* Citizen Login Button → /login */}
          <Link
            href="/login"
            className="border border-[#64ffda] text-[#64ffda] px-8 py-3 rounded-lg shadow-lg hover:bg-[#112240] transition text-center"
          >
            Citizen Login
          </Link>

          {/* Verifier Portal Button → /verifier */}
          <Link
            href="/verifier"
            className="border border-[#5a5dee] text-[#5a5dee] px-8 py-3 rounded-lg shadow-lg hover:bg-[#112240] transition text-center"
          >
            Verifier Portal
          </Link>
        </div>

        {/* Quick stats below hero */}
        <div className="flex flex-wrap justify-center gap-12 mt-16 z-10">
          <div className="text-center">
            <p className="text-2xl md:text-3xl font-bold text-[#3ae374]">10M+</p>
            <p className="text-gray-400 text-sm md:text-base">Citizens Covered</p>
          </div>
          <div className="text-center">
            <p className="text-2xl md:text-3xl font-bold text-[#5a5dee]">50+</p>
            <p className="text-gray-400 text-sm md:text-base">Schemes Automated</p>
          </div>
          <div className="text-center">
            <p className="text-2xl md:text-3xl font-bold text-[#3ae374]">100%</p>
            <p className="text-gray-400 text-sm md:text-base">Fraud-proof Verification</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-[#112240]">
        <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-transparent bg-clip-text text-center mb-16">
          Why IDverse?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 max-w-6xl mx-auto">
          <div className="p-8 bg-[#0d1b2a] rounded-xl shadow-lg hover:shadow-xl transition transform hover:-translate-y-2">
            <h3 className="text-xl font-semibold text-[#64ffda] mb-4">For Citizens</h3>
            <p className="text-gray-300 leading-relaxed">
              Access government benefits, secure your documents, and prove your identity instantly. Offline & multilingual modes ensure inclusion for rural and low-connectivity regions.
            </p>
          </div>
          <div className="p-8 bg-[#0d1b2a] rounded-xl shadow-lg hover:shadow-xl transition transform hover:-translate-y-2">
            <h3 className="text-xl font-semibold text-[#64ffda] mb-4">For Verifiers</h3>
            <p className="text-gray-300 leading-relaxed">
              Instantly verify citizen identity, eligibility, and credentials using AI + Blockchain—ensuring fraud-proof verification and compliance.
            </p>
          </div>
          <div className="p-8 bg-[#0d1b2a] rounded-xl shadow-lg hover:shadow-xl transition transform hover:-translate-y-2">
            <h3 className="text-xl font-semibold text-[#64ffda] mb-4">For Government</h3>
            <p className="text-gray-300 leading-relaxed">
              Transparent, tamper-proof benefit distribution with modular, scalable, and globally adaptable infrastructure for national deployment.
            </p>
          </div>
        </div>
      </section>

      {/* Roadmap / Impact Section */}
      <section className="py-20 px-6">
        <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-transparent bg-clip-text text-center mb-16">
          Roadmap & Impact
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-6xl mx-auto text-center">
          <div className="p-6 bg-[#0d1b2a] rounded-xl shadow-lg">
            <p className="text-xl font-bold text-[#64ffda] mb-2">MVP</p>
            <p className="text-gray-300 text-sm leading-relaxed">Core ID + Wallet Features</p>
          </div>
          <div className="p-6 bg-[#0d1b2a] rounded-xl shadow-lg">
            <p className="text-xl font-bold text-[#64ffda] mb-2">Pilot</p>
            <p className="text-gray-300 text-sm leading-relaxed">Regional Deployment & Feedback</p>
          </div>
          <div className="p-6 bg-[#0d1b2a] rounded-xl shadow-lg">
            <p className="text-xl font-bold text-[#64ffda] mb-2">National Launch</p>
            <p className="text-gray-300 text-sm leading-relaxed">UIDAI / Digital India Integration</p>
          </div>
          <div className="p-6 bg-[#0d1b2a] rounded-xl shadow-lg">
            <p className="text-xl font-bold text-[#64ffda] mb-2">Global Adoption</p>
            <p className="text-gray-300 text-sm leading-relaxed">Modular architecture for other nations</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-gray-400 text-sm py-8 border-t border-gray-800">
        © 2025 IDverse. All rights reserved. Powered by AI + Blockchain.
      </footer>
    </main>
  );
}
