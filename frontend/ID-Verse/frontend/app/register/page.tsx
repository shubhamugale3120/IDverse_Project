"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FaUser, FaLock, FaEnvelope, FaIdBadge } from "react-icons/fa";
import { authAPI } from "../../lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async () => {
    if (!formData.username || !formData.email || !formData.password) {
      setError("Please fill in all fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await authAPI.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      setSuccess("Account created successfully! Please login.");
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
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
            Create Account
          </h2>
          <p className="text-sm text-gray-400 mt-2">Join IDverse • Secure Digital Identity</p>
        </div>

        {/* Inputs */}
        <div className="flex flex-col gap-4">
          <div className="relative">
            <FaUser className="absolute left-3 top-3 text-gray-400" />
            <input
              type="text"
              name="username"
              placeholder="Username"
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#64ffda]"
              value={formData.username}
              onChange={handleInputChange}
            />
          </div>

          <div className="relative">
            <FaEnvelope className="absolute left-3 top-3 text-gray-400" />
            <input
              type="email"
              name="email"
              placeholder="Email Address"
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#64ffda]"
              value={formData.email}
              onChange={handleInputChange}
            />
          </div>

          <div className="relative">
            <FaLock className="absolute left-3 top-3 text-gray-400" />
            <input
              type="password"
              name="password"
              placeholder="Password (min 6 characters)"
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#5a5dee]"
              value={formData.password}
              onChange={handleInputChange}
            />
          </div>

          <div className="relative">
            <FaLock className="absolute left-3 top-3 text-gray-400" />
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              className="w-full p-3 pl-10 rounded-lg bg-[#112240] text-gray-200 border border-[#1d3557] focus:outline-none focus:ring-2 focus:ring-[#5a5dee]"
              value={formData.confirmPassword}
              onChange={handleInputChange}
            />
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="w-full mt-4 p-3 bg-red-900/20 border border-red-500 text-red-300 rounded-lg text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="w-full mt-4 p-3 bg-green-900/20 border border-green-500 text-green-300 rounded-lg text-sm">
            {success}
          </div>
        )}

        {/* Register Button */}
        <button
          onClick={handleRegister}
          disabled={loading}
          className="w-full mt-6 bg-gradient-to-r from-[#64ffda] to-[#5a5dee] text-[#0d1b2a] font-semibold px-4 py-3 rounded-lg shadow-lg hover:scale-105 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Creating Account..." : "Create Account"}
        </button>

        {/* Login Link */}
        <div className="text-center mt-6">
          <p className="text-gray-400 text-sm">
            Already have an account?{" "}
            <button 
              onClick={() => router.push("/login")}
              className="text-[#64ffda] hover:underline"
            >
              Login here
            </button>
          </p>
        </div>

        {/* Footer */}
        <p className="text-xs text-center text-gray-500 mt-6">
          © 2025 IDverse • National Digital Identity Platform
        </p>
      </div>
    </div>
  );
}
