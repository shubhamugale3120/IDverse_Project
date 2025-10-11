"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FaUser, FaLock, FaIdBadge } from "react-icons/fa";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState("citizen");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {
    if (role === "citizen") router.push("/dashboard");
    else router.push("/verifier");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#0d1b2a] to-[#112240]">
      
      {/* Language toggle */}
      <div className="absolute top-4 right-6 text-sm text-gray-400">
        <button className="hover:text-[#64ffda]">English</button> |{" "}
        <button className="hover:text-[#64ffda]">हिंदी</button>
      </div>

      {/* Card */}
      <div className="w-full max-w-md bg-[#0d1b2a] rounded-2xl shadow-2xl p-8 border border-[#112f49]">
        
        {/* Logo + Title */}
        <div className="flex flex-col items-center mb-8">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" viewBox="0 0 24 24" fill="url(#grad1)">
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#64ffda" />
                <stop offset="100%" stopColor="#5a5dee" />
              </linearGradient>
            </defs>
            <path d="M12 1l9 4v6c0 5-3 9-9 11S3 16 3 11V5l9-4z" />
          </svg>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-transparent bg-clip-text">
            IDverse Login
          </h2>
          <p className="text-sm text-gray-400 mt-2">Secure Access • Verified Identity</p>
        </div>

        {/* Inputs */}
        <div className="flex flex-col gap-4">
          <div className="relative">
            <FaUser className="absolute left-3 top-3 text-gray-400" />
            <input
              type="email"
              placeholder="Email Address"
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#64ffda]"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="relative">
            <FaLock className="absolute left-3 top-3 text-gray-400" />
            <input
              type="password"
              placeholder="Password"
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#5a5dee]"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="relative">
            <FaIdBadge className="absolute left-3 top-3 text-gray-400" />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#64ffda]"
            >
              <option value="citizen">Citizen</option>
              <option value="verifier">Verifier</option>
            </select>
          </div>
        </div>

        {/* Forgot Password + Help */}
        <div className="flex justify-between mt-4 text-sm text-gray-400">
          <button className="hover:text-[#64ffda]">Forgot Password?</button>
          <button className="hover:text-[#64ffda]">Need Help?</button>
        </div>

        {/* Login Button */}
        <button
          onClick={handleLogin}
          className="w-full mt-6 bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-[#0d1b2a] font-semibold px-4 py-3 rounded-lg shadow-lg hover:scale-105 transition"
        >
          Login
        </button>

        {/* Footer */}
        <p className="text-xs text-center text-gray-500 mt-6">
          © 2025 IDverse • National Digital Identity Platform
        </p>
      </div>
    </div>
  );
}
