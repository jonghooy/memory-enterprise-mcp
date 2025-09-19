import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Settings, User, Bell, Shield, Database, Zap } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your preferences and system configuration
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5" />
              <CardTitle>Profile</CardTitle>
            </div>
            <CardDescription>
              Manage your account information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Name</label>
              <Input placeholder="Your name" defaultValue="John Doe" />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">Email</label>
              <Input placeholder="email@example.com" defaultValue="john@example.com" />
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              <CardTitle>RAG Configuration</CardTitle>
            </div>
            <CardDescription>
              Configure retrieval and generation settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Vector Store</p>
                <p className="text-sm text-muted-foreground">Pinecone (Active)</p>
              </div>
              <Badge>Connected</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Embedding Model</p>
                <p className="text-sm text-muted-foreground">BAAI/bge-m3</p>
              </div>
              <Button variant="outline" size="sm">Configure</Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Chunk Size</p>
                <p className="text-sm text-muted-foreground">512 tokens</p>
              </div>
              <Button variant="outline" size="sm">Adjust</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              <CardTitle>MCP Integration</CardTitle>
            </div>
            <CardDescription>
              Model Context Protocol settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">MCP Server Status</p>
                <p className="text-sm text-muted-foreground">Running on port 3001</p>
              </div>
              <Badge variant="secondary">Active</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Claude/Cursor Integration</p>
                <p className="text-sm text-muted-foreground">Enabled</p>
              </div>
              <Button variant="outline" size="sm">Test Connection</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}