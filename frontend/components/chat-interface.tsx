"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Sparkles, Paperclip, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  relatedMemories?: Array<{
    id: string
    title: string
    relevance: number
  }>
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI assistant with access to your knowledge base. How can I help you today?",
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Scroll to bottom when new messages are added
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm analyzing your question and searching through your knowledge base. In a production environment, this would connect to your RAG backend.",
        timestamp: new Date(),
        relatedMemories: [
          { id: "mem1", title: "Project Documentation", relevance: 0.92 },
          { id: "mem2", title: "Meeting Notes - Q1 Planning", relevance: 0.85 }
        ]
      }
      setMessages(prev => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4 max-w-3xl mx-auto">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-3",
                message.role === "user" && "justify-end"
              )}
            >
              <Card
                className={cn(
                  "p-4 max-w-[80%]",
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <div className="space-y-2">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  {message.relatedMemories && message.relatedMemories.length > 0 && (
                    <div className="pt-2 space-y-1 border-t border-border/50">
                      <p className="text-xs font-medium opacity-70">Related Memories:</p>
                      <div className="flex flex-wrap gap-1">
                        {message.relatedMemories.map((memory) => (
                          <Badge
                            key={memory.id}
                            variant="secondary"
                            className="text-xs"
                          >
                            {memory.title}
                            <span className="ml-1 opacity-60">
                              {Math.round(memory.relevance * 100)}%
                            </span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <p className="text-xs opacity-50">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </Card>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <Card className="p-4 bg-muted">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 animate-pulse" />
                  <span className="text-sm">Thinking...</span>
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your knowledge base..."
              className="pr-24 min-h-[60px] resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <div className="absolute right-2 bottom-2 flex gap-1">
              <Button
                type="button"
                size="icon"
                variant="ghost"
                className="h-8 w-8"
              >
                <Paperclip className="h-4 w-4" />
              </Button>
              <Button
                type="submit"
                size="icon"
                className="h-8 w-8"
                disabled={!input.trim() || isLoading}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="flex items-center justify-between mt-2">
            <div className="flex gap-2">
              <Badge variant="outline" className="text-xs">
                <Sparkles className="h-3 w-3 mr-1" />
                RAG Enabled
              </Badge>
              <Badge variant="outline" className="text-xs">
                Connected to MCP
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}