"use client";
import { useEffect, useState, ChangeEvent } from 'react';
import { vcAPI } from '@/lib/api';

type VCRecord = {
  vc_id: string;
  ipfs_cid?: string;
  onchain_status?: any;
};

export default function DemoPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jsonText, setJsonText] = useState<string>('');
  const [issueType, setIssueType] = useState<string>('DemoVC');
  const [subjectId, setSubjectId] = useState<string>('demo-subject');
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>(null);
  const [selectedVcId, setSelectedVcId] = useState<string>('');
  const [verifyResult, setVerifyResult] = useState<any>(null);

  const refreshState = async () => {
    try {
      const s = await vcAPI.demo.state();
      setState(s);
    } catch (e: any) {
      setMessage('Failed to load demo state');
    }
  };

  useEffect(() => {
    refreshState();
  }, []);

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setFile(f);
  };

  const handleUpload = async () => {
    setLoading(true);
    setMessage(null);
    try {
      if (file) {
        const res = await vcAPI.demo.upload(file);
        setMessage(`Uploaded -> cid: ${res.cid}`);
      } else if (jsonText.trim()) {
        const parsed = JSON.parse(jsonText);
        const res = await vcAPI.demo.upload(undefined, parsed);
        setMessage(`Uploaded JSON -> cid: ${res.cid}`);
      } else {
        setMessage('Select a file or paste JSON');
      }
    } catch (e: any) {
      setMessage(`Upload failed: ${e?.message || e}`);
    } finally {
      setLoading(false);
      refreshState();
    }
  };

  const handleIssue = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const claims = jsonText.trim() ? JSON.parse(jsonText) : {};
      const res = await vcAPI.demo.issue({ type: issueType, subject_id: subjectId, claims });
      setMessage(`Issued ${res.vc_id} (cid ${res.cid})`);
      setSelectedVcId(res.vc_id);
    } catch (e: any) {
      setMessage(`Issue failed: ${e?.message || e}`);
    } finally {
      setLoading(false);
      refreshState();
    }
  };

  const handleVerify = async () => {
    setLoading(true);
    setVerifyResult(null);
    try {
      if (!selectedVcId) {
        setMessage('Select a VC id from the list');
        setLoading(false);
        return;
      }
      const res = await vcAPI.demo.verify({ vc_id: selectedVcId });
      setVerifyResult(res);
    } catch (e: any) {
      setMessage(`Verify failed: ${e?.message || e}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = async () => {
    setLoading(true);
    try {
      if (!selectedVcId) {
        setMessage('Select a VC id to revoke');
        setLoading(false);
        return;
      }
      const res = await vcAPI.demo.revoke(selectedVcId);
      setMessage(`Revoked: ${JSON.stringify(res)}`);
      refreshState();
    } catch (e: any) {
      setMessage(`Revoke failed: ${e?.message || e}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#071022] text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-[#64ffda]">Demo Panel</h1>

        <section className="grid gap-6 mb-6">
          <div className="card">
            <h2 className="font-semibold text-lg">Upload (file or JSON)</h2>
            <div className="mt-3 grid gap-3 md:grid-cols-2 items-start">
              <input type="file" onChange={onFileChange} className="text-sm" />
              <textarea value={jsonText} onChange={(e) => setJsonText(e.target.value)} placeholder="Paste JSON claims or document" className="w-full h-28 mt-0 p-2" />
            </div>
            <div className="mt-3">
              <button onClick={handleUpload} disabled={loading} className={`btn btn-primary`}>
                Upload
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="font-semibold text-lg">Issue Demo VC</h2>
            <div className="mt-3 grid md:grid-cols-2 gap-3">
              <input value={issueType} onChange={(e) => setIssueType(e.target.value)} className="p-2" />
              <input value={subjectId} onChange={(e) => setSubjectId(e.target.value)} className="p-2" />
            </div>
            <div className="mt-3">
              <button onClick={handleIssue} disabled={loading} className="btn btn-primary">Issue</button>
            </div>
          </div>

          <div className="card">
            <h2 className="font-semibold text-lg">Known VCs</h2>
            <div className="mt-2">
              <button onClick={refreshState} className="btn btn-ghost text-sm">Refresh</button>
            </div>
            <div className="mt-3 grid gap-2">
              {state?.vcs?.length ? (
                state.vcs.map((v: VCRecord) => (
                  <div key={v.vc_id} className={`p-3 rounded-lg ${selectedVcId === v.vc_id ? 'bg-green-800/20' : 'bg-black/10'} hover:scale-[1.01] transition`}> 
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-sm font-medium">{v.vc_id}</div>
                        <div className="text-xs muted">cid: {v.ipfs_cid || '-'}</div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => setSelectedVcId(v.vc_id)} className="text-sm underline">Select</button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-sm">No known VCs</div>
              )}
            </div>
          </div>

          <div className="card">
            <h2 className="font-semibold text-lg">Actions</h2>
            <div className="flex gap-3 mt-3">
              <button onClick={handleVerify} disabled={loading || !selectedVcId} className="btn btn-primary">{loading ? 'Verifying...' : 'Verify'}</button>
              <button onClick={handleRevoke} disabled={loading || !selectedVcId} className="btn" style={{ background: '#fb7185', color: '#06121a' }}>Revoke</button>
            </div>

            {verifyResult && (
              <pre className="bg-black/20 mt-3 p-3 text-xs rounded-lg overflow-x-auto">{JSON.stringify(verifyResult, null, 2)}</pre>
            )}
          </div>

          {message && <div className="text-sm bg-black/20 p-3 rounded-lg">{message}</div>}
        </section>
      </div>
    </main>
  );
}
