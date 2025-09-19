import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Clock, Tag, FileText } from "lucide-react";

const mockMemories = [
  {
    id: 1,
    title: "Project Architecture Design",
    content: "System design using microservices pattern with Docker and Kubernetes...",
    tags: ["architecture", "microservices", "docker"],
    created: "2024-01-15",
    type: "document"
  },
  {
    id: 2,
    title: "Q1 Planning Meeting Notes",
    content: "Key objectives for Q1: 1) Launch new AI features, 2) Improve performance...",
    tags: ["planning", "meetings", "q1-2024"],
    created: "2024-01-10",
    type: "note"
  },
  {
    id: 3,
    title: "Customer Feedback Analysis",
    content: "Analysis of customer feedback from December survey shows...",
    tags: ["feedback", "analysis", "customers"],
    created: "2024-01-08",
    type: "analysis"
  }
];

export default function KnowledgePage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Knowledge Base</h1>
        <p className="text-muted-foreground">
          Browse and manage your memories and knowledge items
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mockMemories.map((memory) => (
          <Card key={memory.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{memory.title}</CardTitle>
                <FileText className="h-5 w-5 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground line-clamp-2">
                {memory.content}
              </p>

              <div className="flex flex-wrap gap-1">
                {memory.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center text-xs text-muted-foreground">
                <Clock className="h-3 w-3 mr-1" />
                {memory.created}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}