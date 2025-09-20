import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

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

// Ensure knowledge file exists
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

// GET: Fetch single knowledge item
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await ensureKnowledgeFile();
    const data = await fs.readFile(KNOWLEDGE_FILE, 'utf-8');
    const knowledge: Knowledge[] = JSON.parse(data);
    const item = knowledge.find(k => k.id === params.id);

    if (!item) {
      return NextResponse.json(
        { error: 'Knowledge item not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(item);
  } catch (error) {
    console.error('Error fetching knowledge item:', error);
    return NextResponse.json(
      { error: 'Failed to fetch knowledge item' },
      { status: 500 }
    );
  }
}

// PUT: Update knowledge item
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await ensureKnowledgeFile();

    const body = await request.json();
    const { title, content, tags, type } = body;

    // Read existing knowledge
    const data = await fs.readFile(KNOWLEDGE_FILE, 'utf-8');
    const knowledge: Knowledge[] = JSON.parse(data);

    // Find and update the item
    const index = knowledge.findIndex(k => k.id === params.id);
    if (index === -1) {
      return NextResponse.json(
        { error: 'Knowledge item not found' },
        { status: 404 }
      );
    }

    // Update the item
    knowledge[index] = {
      ...knowledge[index],
      title,
      content,
      tags: typeof tags === 'string'
        ? tags.split(',').map(t => t.trim()).filter(Boolean)
        : tags,
      type,
      updated: new Date().toISOString()
    };

    // Save updated knowledge
    await fs.writeFile(KNOWLEDGE_FILE, JSON.stringify(knowledge, null, 2), 'utf-8');

    return NextResponse.json(knowledge[index]);
  } catch (error) {
    console.error('Error updating knowledge item:', error);
    return NextResponse.json(
      { error: 'Failed to update knowledge item' },
      { status: 500 }
    );
  }
}

// DELETE: Delete knowledge item
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await ensureKnowledgeFile();

    // Read existing knowledge
    const data = await fs.readFile(KNOWLEDGE_FILE, 'utf-8');
    const knowledge: Knowledge[] = JSON.parse(data);

    // Find the item to delete
    const index = knowledge.findIndex(k => k.id === params.id);
    if (index === -1) {
      return NextResponse.json(
        { error: 'Knowledge item not found' },
        { status: 404 }
      );
    }

    // If it has a file, delete the file too
    const item = knowledge[index];
    if (item.filePath) {
      try {
        const filePath = path.join(KNOWLEDGE_DIR, 'uploads', item.filePath);
        await fs.unlink(filePath);
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    }

    // Remove from array
    knowledge.splice(index, 1);

    // Save updated knowledge
    await fs.writeFile(KNOWLEDGE_FILE, JSON.stringify(knowledge, null, 2), 'utf-8');

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting knowledge item:', error);
    return NextResponse.json(
      { error: 'Failed to delete knowledge item' },
      { status: 500 }
    );
  }
}