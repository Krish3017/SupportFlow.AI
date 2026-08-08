'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  fetchKnowledgeDocuments,
  fetchKnowledgeStatistics,
  searchKnowledge,
  uploadKnowledgeDocument,
  deleteKnowledgeDocument,
} from '@/lib/api-client';
import { Search, Upload, Trash2, RotateCw, BookOpen, Database, Sparkles, FileText } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any>(null);
  const [searching, setSearching] = useState(false);

  // Upload
  const [showUpload, setShowUpload] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadContent, setUploadContent] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [docsResult, statsResult] = await Promise.all([
        fetchKnowledgeDocuments({ limit: 50 }),
        fetchKnowledgeStatistics(),
      ]);
      setDocuments(docsResult.documents || []);
      setStats(statsResult);
      setError(null);
    } catch (err) {
      setError('Failed to load knowledge base');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      setSearching(true);
      const result = await searchKnowledge(searchQuery, 5);
      setSearchResults(result);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleUpload = async () => {
    if (!uploadTitle.trim() || !uploadContent.trim()) return;
    try {
      setUploading(true);
      await uploadKnowledgeDocument(uploadTitle, uploadContent, 'txt');
      setUploadTitle('');
      setUploadContent('');
      setShowUpload(false);
      await loadData();
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      await deleteKnowledgeDocument(documentId);
      await loadData();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-50">Knowledge Base</h1>
          <p className="text-xs text-zinc-400">RAG Vector embeddings & semantic retrieval documents</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="px-3 py-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800/60 text-emerald-300 text-xs font-semibold hover:bg-emerald-900 transition-colors flex items-center gap-1.5"
          >
            <Upload className="h-3.5 w-3.5" />
            <span>Upload Document</span>
          </button>
          <button
            onClick={loadData}
            className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
          >
            <RotateCw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Total Documents</span>
            <div className="text-xl font-extrabold text-zinc-50 my-1">{stats.total_documents || 0}</div>
            <span className="text-[9px] text-zinc-500">Vector Store Active</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Indexed Chunks</span>
            <div className="text-xl font-extrabold text-zinc-50 my-1">{stats.total_chunks || 0}</div>
            <span className="text-[9px] text-emerald-400 font-medium">Chroma DB Chunks</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Indexed Status</span>
            <div className="text-xl font-extrabold text-emerald-400 my-1">{stats.indexed_documents || 0}</div>
            <span className="text-[9px] text-zinc-500">Ready for RAG</span>
          </div>

          <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-3 flex flex-col justify-between">
            <span className="text-[10px] text-zinc-400 font-medium">Retrieval Queries</span>
            <div className="text-xl font-extrabold text-zinc-50 my-1">{stats.total_retrievals || 0}</div>
            <span className="text-[9px] text-zinc-500">Semantic Hits</span>
          </div>
        </div>
      )}

      {/* Upload Panel */}
      {showUpload && (
        <div className="bg-[#111113] border border-zinc-800 rounded-xl p-4 space-y-3">
          <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider">Add New Knowledge Document</h3>
          <input
            type="text"
            placeholder="Document title (e.g. Return Policy 2026)"
            value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            className="w-full bg-[#09090b] border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-700"
          />
          <textarea
            placeholder="Paste document text contents here for automatic chunking and vector embedding..."
            value={uploadContent}
            onChange={(e) => setUploadContent(e.target.value)}
            rows={5}
            className="w-full bg-[#09090b] border border-zinc-800 rounded-lg p-3 text-xs text-zinc-200 focus:outline-none focus:border-zinc-700 font-mono"
          />
          <div className="flex gap-2">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="px-3 py-1.5 bg-emerald-950 border border-emerald-800 text-emerald-300 rounded-lg text-xs font-bold hover:bg-emerald-900 transition-colors"
            >
              {uploading ? 'Embedding...' : 'Upload & Embed'}
            </button>
            <button
              onClick={() => setShowUpload(false)}
              className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-400 rounded-lg text-xs hover:text-zinc-200"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Semantic Search Tester */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4 space-y-3">
        <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider">Test Vector Semantic Search</h3>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Query vector database (e.g. What is the refund process?)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full bg-[#09090b] border border-zinc-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-700"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={searching}
            className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-xl text-xs font-semibold hover:bg-zinc-800"
          >
            {searching ? 'Searching...' : 'Vector Search'}
          </button>
        </div>

        {searchResults && (
          <div className="space-y-2 pt-2 border-t border-zinc-800">
            <p className="text-[10px] text-zinc-400">
              Found {searchResults.results?.length || 0} match(es) for &quot;{searchResults.query}&quot;
            </p>
            {searchResults.results?.map((res: any, i: number) => (
              <div key={i} className="p-2.5 bg-[#09090b] border border-zinc-800 rounded-lg text-xs space-y-1">
                <div className="flex justify-between text-[10px]">
                  <span className="text-zinc-400 font-mono">{res.source_document}</span>
                  <span className="text-emerald-400 font-bold">
                    {((res.similarity_score || 0.85) * 100).toFixed(1)}% match
                  </span>
                </div>
                <p className="text-zinc-300 leading-relaxed">{res.chunk_content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Documents Table */}
      <div className="bg-[#111113] border border-zinc-800/80 rounded-xl p-4">
        <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider mb-3">Indexed Documents</h3>
        <div className="border border-zinc-800/80 rounded-lg overflow-hidden">
          <table className="w-full text-left text-xs text-zinc-300 border-collapse">
            <thead className="bg-[#09090b] text-[10px] text-zinc-500 font-bold uppercase tracking-wider border-b border-zinc-800/80">
              <tr>
                <th className="py-2.5 px-3">Title</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Chunks</th>
                <th className="py-2.5 px-3">Retrievals</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60 font-medium">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-zinc-500 text-xs">
                    No documents indexed in knowledge base
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-zinc-800/40 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-zinc-100">{doc.title}</td>
                    <td className="py-2.5 px-3 font-mono text-[10px] text-zinc-400 uppercase">{doc.type || 'txt'}</td>
                    <td className="py-2.5 px-3">
                      <span className="text-[9px] font-bold px-2 py-0.5 rounded-full border bg-emerald-950/60 text-emerald-400 border-emerald-800/40 uppercase">
                        {doc.status || 'indexed'}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-zinc-400">{doc.chunks || 1}</td>
                    <td className="py-2.5 px-3 text-zinc-400">{doc.retrieval_count || 0}</td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1 rounded text-rose-400 hover:bg-rose-950/60 transition-colors"
                        title="Delete Document"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
