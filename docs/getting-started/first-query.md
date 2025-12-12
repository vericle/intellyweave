# First Query Guide

**Upload your first documents and run your first intelligence analysis.**

## What It Does

This guide walks you through:

- Uploading documents to IntellyWeave
- Understanding automatic entity extraction
- Running your first natural language query
- Exploring visualization features

## Use When

- You've completed installation and IntellyWeave is running
- You want to validate your setup works end-to-end
- You're learning how to use IntellyWeave

## Prerequisites

- IntellyWeave running at http://localhost:8000
- At least one document to upload (PDF, TXT, or DOCX)
- LLM provider configured and working

**Verify IntellyWeave is running:**

```bash
curl http://localhost:8000/api/health
```

**Expected response:**

```json
{"status": "healthy"}
```

## Step 1: Access the Application

Open your browser to **http://localhost:8000**

You'll see the IntellyWeave interface with:

- **Chat panel** - For natural language queries
- **Document panel** - For managing uploaded documents
- **Visualization area** - For maps, graphs, and charts

## Step 2: Upload Documents

### Using the Web Interface

1. Click the **Upload** button or document icon
2. Select one or more files (PDF, TXT, DOCX, MD)
3. Wait for processing to complete

### What Happens During Upload

IntellyWeave processes documents through this pipeline:

```
Upload → Parse → Extract Entities → Chunk → Vectorize → Store
```

**Console output example:**

```
INFO  Processing uploaded file: document.pdf
INFO  Extracted text from PDF (15 pages)
INFO  NER extracted entities summary: {
  'person': 8,
  'organization': 12,
  'location': 6,
  'date': 15,
  'event': 3
}
INFO  Created 45 chunks with entity metadata
INFO  Document processing complete
```

### Entity Types Extracted

| Entity Type | Examples |
|-------------|----------|
| **person** | John Smith, Dr. Maria Garcia |
| **organization** | CIA, United Nations, Acme Corp |
| **location** | Berlin, South America, 123 Main St |
| **date** | January 1945, 1960s, March 15 |
| **event** | World War II, Operation Paperclip |
| **law** | Geneva Convention, Executive Order 12333 |
| **cryptonym** | PBSUCCESS, MKULTRA |

## Step 3: Run Your First Query

### Basic Questions

Type natural language questions in the chat panel:

```
What organizations are mentioned in the documents?
```

```
Who are the key people discussed?
```

```
What locations appear in these documents?
```

### Analysis Questions

Ask analytical questions that require reasoning:

```
What is the relationship between [Person A] and [Organization B]?
```

```
What events happened in [Location] during [Time Period]?
```

```
Summarize the main themes across all documents.
```

### Multi-Agent Debate Questions

For complex analytical questions, IntellyWeave uses multiple AI agents:

```
Analyze the evidence for and against [specific claim].
```

The courthouse debate system will:
1. **Defense agent** - Argues one perspective
2. **Prosecution agent** - Argues the opposing view
3. **Judge agent** - Synthesizes and delivers a balanced conclusion

## Step 4: Explore Visualizations

### Geospatial Map

If locations are found in your documents:

1. Click the **Map** tab
2. See entities plotted on an interactive 3D map
3. Click markers for entity details

**Note:** Requires Mapbox token configured in `frontend/.env.local`

### Network Graph

To visualize entity relationships:

1. Click the **Network** tab
2. Explore connections between people, organizations, and locations
3. Drag nodes to rearrange the graph

### Charts

For quantitative analysis:

1. Ask chart-generating questions:
   - "Show a bar chart of entity types"
   - "Create a timeline of events"
2. View results in the visualization panel

## Step 5: Refine Your Queries

### Filter by Entity Type

```
Show me only the organizations mentioned.
```

```
List all dates found in the documents.
```

### Filter by Document

```
In document X, what locations are discussed?
```

### Cross-Document Analysis

```
Find connections between documents A and B.
```

```
What entities appear in multiple documents?
```

## Example Workflow

Here's a complete example workflow:

### 1. Upload a Historical Document

Upload a PDF about a historical event.

### 2. Entity Discovery

```
What entities were extracted from this document?
```

**Response example:**

```
I found the following entities:

**People (8):**
- Klaus Barbie
- Adolf Eichmann
- ...

**Organizations (5):**
- OSS
- CIA
- ...

**Locations (12):**
- Buenos Aires
- Rome
- ...
```

### 3. Geographic Analysis

```
Show these locations on a map.
```

### 4. Relationship Analysis

```
What connections exist between these people and organizations?
```

### 5. Deep Dive

```
Analyze the evidence for [specific person's] involvement with [organization].
```

## Troubleshooting

### No Entities Extracted

**Cause:** GLiNER not installed or model not loaded.

**Solution:**

```bash
cd backend
source .venv/bin/activate
pip install -e ".[ner]"
```

### Slow Document Processing

**Cause:** First upload downloads the GLiNER model (~500MB).

**Solution:** Wait for download to complete. Subsequent uploads are faster.

### Map Not Showing

**Cause:** Mapbox token not configured.

**Solution:** Add to `frontend/.env.local`:

```bash
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=pk.your-token-here
```

### Query Returns Generic Response

**Cause:** Documents not properly indexed or LLM not configured.

**Check:**

1. Documents appear in document panel
2. LLM API key is valid
3. Weaviate is running: `docker compose ps`

### "No documents found" Error

**Cause:** Documents haven't finished processing.

**Solution:** Wait for processing to complete, then retry.

## Performance Tips

### Optimal Document Size

- **Best:** 1-50 pages per document
- **Maximum:** 500 pages (may be slow)

### Query Speed

- Simple questions: 2-5 seconds
- Complex analysis: 10-30 seconds
- Multi-agent debate: 30-60 seconds

### Batch Uploads

Upload multiple related documents together for better cross-document analysis.

## See Also

- [Quick Start](index.md) - Initial setup
- [Installation Guide](installation.md) - Detailed configuration
- [Entity Extraction](../guides/entity-extraction/index.md) - Deep dive into GLiNER
- [Multi-Agent System](../guides/courthouse-debate/index.md) - Courthouse debate details
