"use client";
import { useState, ChangeEvent } from 'react';
import { vcAPI } from '@/lib/api';

export default function VerifierPortal() {
  const [vcJson, setVcJson] = useState<string>('');
  const [vcId, setVcId] = useState<string>('');
  const [disclosed, setDisclosed] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [issuerInfo, setIssuerInfo] = useState<any>(null);

  const handleVerify = async () => {
    setLoading(true);
    setResult(null);
    try {
      const { challenge } = await vcAPI.getChallenge();
      const body: any = { challenge };
      if (vcJson.trim()) {
        body.vc = JSON.parse(vcJson);
      } else if (vcId.trim()) {
        body.vc_id = vcId.trim();
        if (disclosed.trim()) {
          body.disclosed = JSON.parse(disclosed);
        }
      }
      const resp = await vcAPI.present(body);
      setResult(resp);
    } catch (e: any) {
      setResult({ error: (e as any)?.message || 'verification failed' });
    } finally {
      setLoading(false);
    }
  };

  const loadIssuerInfo = async (): Promise<void> => {
    try {
      const info = await vcAPI.getIssuerInfo();
      setIssuerInfo(info);
    } catch (e: any) {
      setIssuerInfo({ error: 'failed to load issuer info' });
    }
  };

  return (
    <main className="min-h-screen bg-[#0a192f] text-white p-8">
      <h1 className="text-3xl font-bold text-[#64ffda] mb-6">Verifier Portal</h1>

      <section className="bg-[#112240] p-6 rounded-lg shadow grid gap-4">
        <div className="flex items-center justify-between">
          <p className="mb-2">Paste full VC JSON (or use VC ID + disclosed fields)</p>
          <button onClick={loadIssuerInfo} className="text-sm underline text-[#64ffda]">Load Issuer Info</button>
        </div>
        {issuerInfo && (
          <div className="bg-black/40 p-3 rounded text-xs">
            <div>Issuer DID: {issuerInfo.issuer_did || '-'}</div>
            <div>Public Key: {issuerInfo.public_key_hex || '-'}</div>
            <div>Sign Mode: {issuerInfo.sign_mode || '-'}</div>
          </div>
        )}

        <textarea
          placeholder="Paste full VC JSON here (or use fields below)"
          value={vcJson}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setVcJson(e.target.value)}
          className="p-3 rounded-lg text-black w-full h-40"
        />

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="mb-2">VC ID:</p>
            <input
              type="text"
              placeholder="vc-..."
              value={vcId}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setVcId(e.target.value)}
              className="p-3 rounded-lg text-black w-full"
            />
          </div>
          <div>
            <p className="mb-2">Disclosed fields JSON (optional):</p>
            <textarea
              placeholder="{ \"aadhaarLast4\": \"1234\" }"
              value={disclosed}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setDisclosed(e.target.value)}
              className="p-3 rounded-lg text-black w-full h-24"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <button onClick={handleVerify} disabled={loading} className="bg-[#64ffda] text-[#0a192f] font-semibold px-6 py-3 rounded-lg hover:scale-105 transition disabled:opacity-50">
            {loading ? 'Verifying...' : 'Verify'}
          </button>
        </div>

        {result && (<pre className="bg-black/50 p-4 rounded overflow-x-auto text-sm">{JSON.stringify(result, null, 2)}</pre>)}
      </section>
    </main>
  );
}
