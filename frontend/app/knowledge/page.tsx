"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import {
  Brain,
  Clock,
  Tag,
  FileText,
  Plus,
  Upload,
  Edit,
  Trash2,
  Search,
  File,
  X,
  Loader2,
  Download,
  Eye
} from "lucide-react";

interface Knowledge {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created: string;
  updated: string;
  type: 'document' | 'note' | 'analysis' | 'file';
  fileName?: string;
  fileSize?: number;
}

export default function KnowledgePage() {
  const [knowledgeItems, setKnowledgeItems] = useState<Knowledge[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState("all");
  const [isLoading, setIsLoading] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Knowledge | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const { toast } = useToast();

  // Form states
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    tags: "",
    type: "document" as Knowledge['type']
  });

  // Fetch knowledge items
  const fetchKnowledge = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/knowledge");
      if (response.ok) {
        const data = await response.json();
        setKnowledgeItems(data);
      }
    } catch (error) {
      console.error("Failed to fetch knowledge:", error);
      // Use mock data as fallback
      setKnowledgeItems([
        {
          id: "1",
          title: "Project Architecture Design",
          content: "System design using microservices pattern with Docker and Kubernetes...",
          tags: ["architecture", "microservices", "docker"],
          created: "2024-01-15",
          updated: "2024-01-15",
          type: "document"
        },
        {
          id: "2",
          title: "Q1 Planning Meeting Notes",
          content: "Key objectives for Q1: 1) Launch new AI features, 2) Improve performance...",
          tags: ["planning", "meetings", "q1-2024"],
          created: "2024-01-10",
          updated: "2024-01-10",
          type: "note"
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchKnowledge();
  }, []);

  // Filter knowledge items
  const filteredItems = knowledgeItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesType = selectedType === "all" || item.type === selectedType;
    return matchesSearch && matchesType;
  });

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setFormData({
        ...formData,
        title: file.name,
        type: 'file'
      });
    }
  };

  // Add new knowledge
  const handleAdd = async () => {
    setIsLoading(true);
    try {
      const formDataToSend = new FormData();

      if (uploadedFile) {
        formDataToSend.append('file', uploadedFile);
      }
      formDataToSend.append('title', formData.title);
      formDataToSend.append('content', formData.content);
      formDataToSend.append('tags', formData.tags);
      formDataToSend.append('type', formData.type);

      const response = await fetch("/api/knowledge", {
        method: "POST",
        body: formDataToSend
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Knowledge added successfully"
        });
        fetchKnowledge();
        setIsAddDialogOpen(false);
        resetForm();
      } else {
        throw new Error("Failed to add knowledge");
      }
    } catch (error) {
      // Fallback: Add to local state
      const newItem: Knowledge = {
        id: Date.now().toString(),
        title: formData.title,
        content: formData.content,
        tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
        created: new Date().toISOString().split('T')[0],
        updated: new Date().toISOString().split('T')[0],
        type: formData.type,
        fileName: uploadedFile?.name,
        fileSize: uploadedFile?.size
      };
      setKnowledgeItems([...knowledgeItems, newItem]);
      toast({
        title: "Success",
        description: "Knowledge added locally"
      });
      setIsAddDialogOpen(false);
      resetForm();
    } finally {
      setIsLoading(false);
    }
  };

  // Edit knowledge
  const handleEdit = async () => {
    if (!editingItem) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/knowledge/${editingItem.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Knowledge updated successfully"
        });
        fetchKnowledge();
        setIsEditDialogOpen(false);
        setEditingItem(null);
        resetForm();
      } else {
        throw new Error("Failed to update knowledge");
      }
    } catch (error) {
      // Fallback: Update local state
      const updatedItems = knowledgeItems.map(item =>
        item.id === editingItem.id
          ? {
              ...item,
              title: formData.title,
              content: formData.content,
              tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
              updated: new Date().toISOString().split('T')[0],
              type: formData.type
            }
          : item
      );
      setKnowledgeItems(updatedItems);
      toast({
        title: "Success",
        description: "Knowledge updated locally"
      });
      setIsEditDialogOpen(false);
      setEditingItem(null);
      resetForm();
    } finally {
      setIsLoading(false);
    }
  };

  // Delete knowledge
  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this knowledge item?")) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/knowledge/${id}`, {
        method: "DELETE"
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Knowledge deleted successfully"
        });
        fetchKnowledge();
      } else {
        throw new Error("Failed to delete knowledge");
      }
    } catch (error) {
      // Fallback: Remove from local state
      setKnowledgeItems(knowledgeItems.filter(item => item.id !== id));
      toast({
        title: "Success",
        description: "Knowledge deleted locally"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: "",
      content: "",
      tags: "",
      type: "document"
    });
    setUploadedFile(null);
  };

  const openEditDialog = (item: Knowledge) => {
    setEditingItem(item);
    setFormData({
      title: item.title,
      content: item.content,
      tags: item.tags.join(', '),
      type: item.type
    });
    setIsEditDialogOpen(true);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Knowledge Base</h1>
            <p className="text-muted-foreground">
              Manage your documents, notes, and knowledge items
            </p>
          </div>
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => resetForm()}>
                <Plus className="h-4 w-4 mr-2" />
                Add Knowledge
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[625px]">
              <DialogHeader>
                <DialogTitle>Add New Knowledge</DialogTitle>
                <DialogDescription>
                  Create a new knowledge item or upload a document
                </DialogDescription>
              </DialogHeader>
              <Tabs defaultValue="manual" className="mt-4">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="manual">Manual Entry</TabsTrigger>
                  <TabsTrigger value="upload">Upload File</TabsTrigger>
                </TabsList>
                <TabsContent value="manual" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      placeholder="Enter knowledge title"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="content">Content</Label>
                    <Textarea
                      id="content"
                      placeholder="Enter knowledge content"
                      rows={6}
                      value={formData.content}
                      onChange={(e) => setFormData({...formData, content: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tags">Tags (comma separated)</Label>
                    <Input
                      id="tags"
                      placeholder="e.g., architecture, docker, kubernetes"
                      value={formData.tags}
                      onChange={(e) => setFormData({...formData, tags: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="type">Type</Label>
                    <Select
                      value={formData.type}
                      onValueChange={(value) => setFormData({...formData, type: value as Knowledge['type']})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="document">Document</SelectItem>
                        <SelectItem value="note">Note</SelectItem>
                        <SelectItem value="analysis">Analysis</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>
                <TabsContent value="upload" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="file">Upload File</Label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <input
                        type="file"
                        id="file"
                        className="hidden"
                        onChange={handleFileUpload}
                        accept=".pdf,.doc,.docx,.txt,.md,.json"
                      />
                      <label htmlFor="file" className="cursor-pointer">
                        {uploadedFile ? (
                          <div className="space-y-2">
                            <File className="h-12 w-12 mx-auto text-blue-500" />
                            <p className="text-sm font-medium">{uploadedFile.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {(uploadedFile.size / 1024).toFixed(2)} KB
                            </p>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.preventDefault();
                                setUploadedFile(null);
                              }}
                            >
                              <X className="h-4 w-4 mr-1" />
                              Remove
                            </Button>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Upload className="h-12 w-12 mx-auto text-gray-400" />
                            <p className="text-sm text-muted-foreground">
                              Click to upload or drag and drop
                            </p>
                            <p className="text-xs text-muted-foreground">
                              PDF, DOC, TXT, MD, JSON (max 10MB)
                            </p>
                          </div>
                        )}
                      </label>
                    </div>
                  </div>
                  {uploadedFile && (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="file-tags">Tags (comma separated)</Label>
                        <Input
                          id="file-tags"
                          placeholder="e.g., document, report, analysis"
                          value={formData.tags}
                          onChange={(e) => setFormData({...formData, tags: e.target.value})}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="file-content">Description (optional)</Label>
                        <Textarea
                          id="file-content"
                          placeholder="Add a description for this file"
                          rows={3}
                          value={formData.content}
                          onChange={(e) => setFormData({...formData, content: e.target.value})}
                        />
                      </div>
                    </>
                  )}
                </TabsContent>
              </Tabs>
              <div className="flex justify-end gap-2 mt-4">
                <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAdd} disabled={isLoading || !formData.title}>
                  {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Add Knowledge
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Search and Filter */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Search knowledge..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={selectedType} onValueChange={setSelectedType}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="document">Documents</SelectItem>
              <SelectItem value="note">Notes</SelectItem>
              <SelectItem value="analysis">Analysis</SelectItem>
              <SelectItem value="file">Files</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Knowledge Grid */}
      {isLoading && knowledgeItems.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="text-center py-12">
          <Brain className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">
            {searchQuery ? "No knowledge items found matching your search" : "No knowledge items yet"}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredItems.map((item) => (
            <Card key={item.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg line-clamp-1">{item.title}</CardTitle>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => openEditDialog(item)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {item.content || "No description available"}
                </p>

                {item.fileName && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <File className="h-4 w-4" />
                    <span className="truncate">{item.fileName}</span>
                    {item.fileSize && (
                      <span className="text-xs">({(item.fileSize / 1024).toFixed(2)} KB)</span>
                    )}
                  </div>
                )}

                <div className="flex flex-wrap gap-1">
                  {item.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      <Tag className="h-3 w-3 mr-1" />
                      {tag}
                    </Badge>
                  ))}
                </div>

                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center">
                    <Clock className="h-3 w-3 mr-1" />
                    {item.updated || item.created}
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {item.type}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[625px]">
          <DialogHeader>
            <DialogTitle>Edit Knowledge</DialogTitle>
            <DialogDescription>
              Update the knowledge item details
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                placeholder="Enter knowledge title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-content">Content</Label>
              <Textarea
                id="edit-content"
                placeholder="Enter knowledge content"
                rows={6}
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-tags">Tags (comma separated)</Label>
              <Input
                id="edit-tags"
                placeholder="e.g., architecture, docker, kubernetes"
                value={formData.tags}
                onChange={(e) => setFormData({...formData, tags: e.target.value})}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-type">Type</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({...formData, type: value as Knowledge['type']})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="document">Document</SelectItem>
                  <SelectItem value="note">Note</SelectItem>
                  <SelectItem value="analysis">Analysis</SelectItem>
                  <SelectItem value="file">File</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={isLoading || !formData.title}>
              {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}