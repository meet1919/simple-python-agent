up---
name: llm-wiki-maintainer
description: LLM Wiki Maintainer - Use this skill to manage a persistent personal knowledge base (LLM Wiki). Trigger this when the user asks to ingest a new document/source, query the knowledge base, or maintain/lint the wiki.
allowed-tools: [view_file, edit_file, run_bash_command]
requires-pfc: true
---

# LLM Wiki Maintainer

A pattern for building personal knowledge bases using LLMs.
Instead of rediscovering knowledge from scratch using RAG on raw documents, you will build and maintain a persistent wiki — a structured, interlinked collection of markdown files.

## Architecture

There are three layers:
1. **Raw sources**: The user's curated collection of source documents. These are immutable — read from them but never modify them.
2. **The wiki**: A directory of markdown files (summaries, entity pages, concept pages, synthesis). You own this layer entirely. You create pages, update them when new sources arrive, maintain cross-references, and keep everything consistent.
3. **The schema**: This instruction set. It dictates how you manage the wiki.

## Special Files

You must maintain two special files to help navigate the wiki:
1. `index.md` (Content-oriented): A catalog of everything in the wiki. Each page listed with a link, a one-line summary, and optionally metadata. Organized by category (entities, concepts, sources). Read this first when answering a query.
2. `log.md` (Chronological): An append-only record of what happened and when. Format each entry as: `## [YYYY-MM-DD] action | Description` (e.g., `## [2026-04-27] ingest | Article Title`). 

## Operations

### 1. Ingest

When the user drops a new source and tells you to process it:
1. Read the raw source.
2. Discuss key takeaways with the user if needed.
3. Write a summary page in the wiki.
4. Update `index.md` to include the new summary page.
5. Update relevant entity and concept pages across the wiki. Note where new data contradicts old claims, strengthening or challenging the evolving synthesis.
6. Append an entry to `log.md`.

### 2. Query

When the user asks questions against the wiki:
1. Read `index.md` to find relevant pages.
2. Read the identified pages.
3. Synthesize an answer with citations to the wiki pages.
4. If the answer involves a valuable new comparison, analysis, or connection, file it back into the wiki as a new page and update `index.md` and `log.md`.

### 3. Lint

When the user asks to health-check the wiki:
1. Look for contradictions between pages.
2. Find stale claims that newer sources have superseded.
3. Find orphan pages with no inbound links.
4. Find important concepts mentioned but lacking their own page.
5. Identify missing cross-references.
6. Suggest new questions to investigate and new sources to look for.

## Rules
- The wiki is a persistent, compounding artifact. Cross-references must be maintained.
- Never modify raw sources.
- Do not ask the user to write the wiki. You are the maintainer, the user provides the direction.
