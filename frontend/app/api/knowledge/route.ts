import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// Define the knowledge storage path
const KNOWLEDGE_DIR = path.join(process.cwd(), 'data', 'knowledge');
const KNOWLEDGE_FILE = path.join(KNOWLEDGE_DIR, 'knowledge.json');

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
  filePath?: string;
}

// Ensure knowledge directory and file exist
async function ensureKnowledgeFile() {
  try {
    await fs.mkdir(KNOWLEDGE_DIR, { recursive: true });
    try {
      await fs.access(KNOWLEDGE_FILE);
    } catch {
      await fs.writeFile(KNOWLEDGE_FILE, JSON.stringify([]), 'utf-8');
    }
  } catch (error) {
    console.error('Error ensuring knowledge file:', error);
  }
}

// GET: Fetch all knowledge items
export async function GET() {
  try {
    await ensureKnowledgeFile();
    const data = await fs.readFile(KNOWLEDGE_FILE, 'utf-8');
    const knowledge = JSON.parse(data);
    return NextResponse.json(knowledge);
  } catch (error) {
    console.error('Error fetching knowledge:', error);
    return NextResponse.json([], { status: 500 });
  }
}

// POST: Create new knowledge item
export async function POST(request: NextRequest) {
  try {
    await ensureKnowledgeFile();

    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const title = formData.get('title') as string;
    const content = formData.get('content') as string || '';
    const tags = formData.get('tags') as string || '';
    const type = formData.get('type') as Knowledge['type'];

    // Read existing knowledge
    const data = await fs.readFile(KNOWLEDGE_FILE, 'utf-8');
    const knowledge: Knowledge[] = JSON.parse(data);

    // Create new knowledge item
    const newItem: Knowledge = {
      id: Date.now().toString(),
      title,
      content,
      tags: tags.split(',').map(t => t.trim()).filter(Boolean),
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      type
    };

    // Handle file upload if present
    if (file) {
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      // Create uploads directory
      const uploadsDir = path.join(KNOWLEDGE_DIR, 'uploads');
      await fs.mkdir(uploadsDir, { recursive: true });

      // Save file with unique name
      const fileName = `${Date.now()}_${file.name}`;
      const filePath = path.join(uploadsDir, fileName);
      await fs.writeFile(filePath, buffer);

      // Add file info to knowledge item
      newItem.fileName = file.name;
      newItem.fileSize = file.size;
      newItem.filePath = fileName;
    }

    // Add to knowledge array
    knowledge.push(newItem);

    // Save updated knowledge
    await fs.writeFile(KNOWLEDGE_FILE, JSON.stringify(knowledge, null, 2), 'utf-8');

    return NextResponse.json(newItem, { status: 201 });
  } catch (error) {
    console.error('Error creating knowledge:', error);
    return NextResponse.json(
      { error: 'Failed to create knowledge item' },
      { status: 500 }
    );
  }
}