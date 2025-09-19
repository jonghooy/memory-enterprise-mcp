"use client"

import { Bot, Home, Brain, Link2, Settings } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

interface SidebarProps {
  className?: string
}

const menuItems = [
  {
    title: "AI Assistant",
    icon: Bot,
    href: "/kms/",
    description: "Chat with AI about your knowledge"
  },
  {
    title: "Home",
    icon: Home,
    href: "/kms/home/",
    description: "Dashboard overview"
  },
  {
    title: "Knowledge Base",
    icon: Brain,
    href: "/kms/knowledge/",
    description: "Browse and manage memories"
  },
  {
    title: "Connections",
    icon: Link2,
    href: "/kms/connections/",
    description: "Manage integrations"
  },
  {
    title: "Settings",
    icon: Settings,
    href: "/kms/settings/",
    description: "System preferences"
  }
]

export function Sidebar({ className }: SidebarProps) {
  return (
    <div className={cn("pb-12 w-64", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="mb-6 px-4">
            <h1 className="text-xl font-bold tracking-tight">
              Memory Enterprise
            </h1>
            <p className="text-sm text-muted-foreground">
              Knowledge Management
            </p>
          </div>
          <div className="space-y-1">
            {menuItems.map((item) => (
              <Button
                key={item.href}
                variant={item.href === "/kms/" ? "secondary" : "ghost"}
                className="w-full justify-start"
                asChild
              >
                <a href={item.href}>
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.title}
                </a>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}