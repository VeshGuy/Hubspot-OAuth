import React, { useState } from 'react';
import axios from 'axios';

const UploadForm = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:5000/upload", formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setResult({ error: "Upload failed" });
    }
    setLoading(false);
  };

  return (
    <div className="p-4 max-w-lg mx-auto bg-white rounded shadow">
      <h2 className="text-xl font-bold mb-4">📄 Upload Insurance Claim PDF</h2>

      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button
        onClick={handleUpload}
        className="bg-blue-600 text-white px-4 py-2 mt-2 rounded"
      >
        {loading ? "Processing..." : "Upload"}
      </button>

      {result && (
        <div className="mt-4 bg-gray-100 p-3 rounded">
          <h3 className="font-semibold mb-2">🧾 Result:</h3>
          <pre className="text-sm text-left overflow-x-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default UploadForm;
