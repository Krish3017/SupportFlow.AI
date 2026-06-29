'use client';

import { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { LoadingState } from '@/components/ui/loading-state';
import {
  fetchKnowledgeDocuments,
  fetchKnowledgeStatistics,
  searchKnowledge,
  uploadKnowledgeDocument,
  deleteKnowledgeDocument,
} from '@/lib/api-client';
import { Search, Upload, Trash2 } from 'lucide-react';
import { format } from 'date-fns';

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
        fetchKnowledgeStatistics()
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

  if (loading) return <LoadingState message="Loading knowledge base..." />;
  if (error) return <Card className="p-8 text-center text-red-500">{error}</Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-muted-foreground">Manage documents and embeddings</p>
        </div>
        <Button onClick={() => setShowUpload(!showUpload)}>
          <Upload className="mr-2 size-4" />
          Upload Document
        </Button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Documents</p>
              <p className="text-2xl font-bold">{stats.total_documents}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Chunks</p>
              <p className="text-2xl font-bold">{stats.total_chunks}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Indexed</p>
              <p className="text-2xl font-bold text-green-500">{stats.indexed_documents}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Total Retrievals</p>
              <p className="text-2xl font-bold">{stats.total_retrievals}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Upload Form */}
      {showUpload && (
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Upload Document</h3>
          <div className="space-y-4">
            <Input
              placeholder="Document title"
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
            />
            <Textarea
              placeholder="Paste document content here..."
              value={uploadContent}
              onChange={(e) => setUploadContent(e.target.value)}
              rows={8}
            />
            <div className="flex gap-2">
              <Button onClick={handleUpload} disabled={uploading}>
                {uploading ? 'Uploading...' : 'Upload'}
              </Button>
              <Button variant="ghost" onClick={() => setShowUpload(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Search */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Search Knowledge Base</h3>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Test semantic search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-9"
            />
          </div>
          <Button onClick={handleSearch} disabled={searching}>
            {searching ? 'Searching...' : 'Search'}
          </Button>
        </div>

        {searchResults && (
          <div className="mt-4 space-y-3">
            <p className="text-sm text-muted-foreground">
              {searchResults.results.length} results for "{searchResults.query}"
            </p>
            {searchResults.results.map((result: any, i: number) => (
              <div key={i} className="p-3 border rounded">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-muted-foreground">{result.source_document}</span>
                  <Badge variant="outline">{(result.similarity_score * 100).toFixed(1)}%</Badge>
                </div>
                <p className="text-sm">{result.chunk_content}</p>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Documents Table */}
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Chunks</TableHead>
              <TableHead>Retrievals</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Last Updated</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  No documents yet
                </TableCell>
              </TableRow>
            ) : (
              documents.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell className="font-medium">{doc.title}</TableCell>
                  <TableCell className="uppercase text-xs">{doc.type}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        doc.status === 'indexed'
                          ? 'bg-green-500/10 text-green-500'
                          : doc.status === 'pending'
                            ? 'bg-blue-500/10 text-blue-500'
                            : 'bg-red-500/10 text-red-500'
                      }
                    >
                      {doc.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{doc.chunks}</TableCell>
                  <TableCell>{doc.retrieval_count}</TableCell>
                  <TableCell>{doc.size}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {format(new Date(doc.last_updated), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <Trash2 className="size-4 text-red-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
