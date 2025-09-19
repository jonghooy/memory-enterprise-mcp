import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Link2, Plus, CheckCircle, XCircle } from "lucide-react";

const connections = [
  {
    id: 1,
    name: "Google Docs",
    description: "Access and index your Google Docs in real-time",
    status: "connected",
    icon: "📄",
    lastSync: "5 minutes ago"
  },
  {
    id: 2,
    name: "Notion",
    description: "Sync your Notion workspace and databases",
    status: "disconnected",
    icon: "📝",
    lastSync: null
  },
  {
    id: 3,
    name: "GitHub",
    description: "Index code repositories and documentation",
    status: "disconnected",
    icon: "💻",
    lastSync: null
  },
  {
    id: 4,
    name: "Slack",
    description: "Archive and search Slack conversations",
    status: "disconnected",
    icon: "💬",
    lastSync: null
  }
];

export default function ConnectionsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Connections</h1>
        <p className="text-muted-foreground">
          Connect your external services to expand your knowledge base
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {connections.map((connection) => (
          <Card key={connection.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{connection.icon}</span>
                  <div>
                    <CardTitle className="text-lg">{connection.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {connection.description}
                    </CardDescription>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {connection.status === "connected" ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <Badge variant="secondary" className="text-xs">
                        Connected
                      </Badge>
                      {connection.lastSync && (
                        <span className="text-xs text-muted-foreground">
                          • Synced {connection.lastSync}
                        </span>
                      )}
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 text-muted-foreground" />
                      <Badge variant="outline" className="text-xs">
                        Not connected
                      </Badge>
                    </>
                  )}
                </div>
                <Button
                  variant={connection.status === "connected" ? "outline" : "default"}
                  size="sm"
                >
                  {connection.status === "connected" ? "Manage" : "Connect"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mt-6 border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-8">
          <Link2 className="h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-muted-foreground mb-4">Add custom integration</p>
          <Button variant="outline">
            <Plus className="h-4 w-4 mr-2" />
            Add Connection
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}