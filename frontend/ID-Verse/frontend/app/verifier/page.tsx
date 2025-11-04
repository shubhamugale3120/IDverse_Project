"use client";
import { useState, ChangeEvent } from 'react';
import { vcAPI } from '@/lib/api';

type VerifyResult = {
  verified?: boolean;
  checks?: { signature?: boolean; status?: boolean; disclosure_subset?: boolean; challenge?: boolean };
  status_info?: any;
  error?: string;
};

export default function VerifierPortal() {
  const [vcJson, setVcJson] = useState<string>('');
  const [vcId, setVcId] = useState<string>('');
  const [disclosed, setDisclosed] = useState<string>('');
  const [result, setResult] = useState<VerifyResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [issuerInfo, setIssuerInfo] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (): Promise<void> => {
    setLoading(true);
    setResult(null);
    setError(null);
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
      } else {
        setError('Provide a full VC JSON or a VC ID.');
        setLoading(false);
        return;
      }
      const resp = await vcAPI.present(body);
      setResult(resp as VerifyResult);
    } catch (e: any) {
      setError(e?.message || 'Verification failed');
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

  const pasteFromClipboard = async (): Promise<void> => {
    try {
      const text = await navigator.clipboard.readText();
      setVcJson(text);
    } catch {
      setError('Clipboard read not allowed. Paste manually.');
    }
  };

  const badge = (ok?: boolean, label?: string) => (
    <span className={`px-2 py-1 rounded text-xs ${ok ? 'bg-green-600/70' : 'bg-red-600/70'}`}>
      {label}: {ok ? 'ok' : 'fail'}
    </span>
  );

  return (
    <main className="min-h-screen bg-[#0a192f] text-white p-8">
      <h1 className="text-3xl font-bold text-[#64ffda] mb-6">Verifier Portal</h1>

      <section className="bg-[#112240] p-6 rounded-lg shadow grid gap-4">
        <div className="flex items-center justify-between">
          <p className="mb-2">Paste full VC JSON (or use VC ID + disclosed fields)</p>
          <div className="flex gap-3 items-center">
            <button onClick={loadIssuerInfo} className="text-sm underline text-[#64ffda]">Load Issuer Info</button>
            <button onClick={pasteFromClipboard} className="text-sm underline text-[#64ffda]">Paste from Clipboard</button>
          </div>
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
              placeholder='{"aadhaarLast4":"1234"}'
              value={disclosed}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setDisclosed(e.target.value)}
              className="p-3 rounded-lg text-black w-full h-24"
            />
          </div>
        </div>

        {error && <div className="bg-red-700/60 border border-red-400 rounded p-2 text-sm">{error}</div>}

        <div className="flex gap-3">
          <button onClick={handleVerify} disabled={loading} className="bg-[#64ffda] text-[#0a192f] font-semibold px-6 py-3 rounded-lg hover:scale-105 transition disabled:opacity-50">
            {loading ? 'Verifying...' : 'Verify'}
          </button>
        </div>

        {result && (
          <div className="grid gap-3">
            <div className={`px-3 py-2 rounded ${result.verified ? 'bg-green-700/40' : 'bg-red-700/40'}`}>
              Overall: {String(result.verified)}
            </div>
            <div className="flex flex-wrap gap-2">
              {badge(result.checks?.signature, 'signature')}
              {badge(result.checks?.status, 'status')}
              {badge(result.checks?.disclosure_subset, 'disclosure')}
              {badge(result.checks?.challenge, 'challenge')}
            </div>
            <pre className="bg-black/50 p-4 rounded overflow-x-auto text-xs">{JSON.stringify(result.status_info || result, null, 2)}</pre>
          </div>
        )}
      </section>
    </main>
  );
}
