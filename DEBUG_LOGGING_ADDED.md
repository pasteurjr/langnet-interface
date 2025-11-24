# Debug Logging Implementation - Phase 1, 2 & 3

**Date:** 2025-11-24
**Purpose:** Deep debugging analysis to identify where document_content is lost in the pipeline
**Context:** Multi-agent requirements generation system producing generic documents instead of using actual PDF content

---

## Problem Description

The system receives 2 PDF documents with specific company information (Farmac, Douglas, 10,000 ANVISA records, etc.) plus user instructions, but generates completely generic requirements documents filled with "To be filled by analysis" placeholders.

Server logs showed only "1 document, 2477 words analyzed" instead of the expected 2 PDFs with 6500+ words.

---

## Investigation Plan

The debugging follows a 4-phase approach to trace document_content through the entire data pipeline:

### PHASE 1: PDF Extraction (documents.py)
**Goal:** Verify PDF content is being extracted correctly from uploaded files

### PHASE 2: State Initialization (langnetstate.py + langnetagents.py)
**Goal:** Verify document_content is preserved when initializing state and passing to workflow

### PHASE 3: Task Formatting (langnetagents.py)
**Goal:** Verify document_content is correctly inserted into task prompts via `.format(**task_input)`

### PHASE 4: Agent Validation (langnet_tasks.yaml - NOT YET IMPLEMENTED)
**Goal:** Verify agents aren't ignoring inputs and returning template placeholders

---

## Changes Made

### 1. backend/app/routers/documents.py (Lines 58-183)

Added comprehensive logging to `execute_analysis_in_background()` function:

#### Before document loop:
```python
[PHASE 1 - EXTRACTION DEBUG] Starting document extraction
[PHASE 1] Total documents to process: N
```

#### For each document:
```python
[PHASE 1] Document X/N: filename
[PHASE 1] File type: pdf
[PHASE 1] File path: /path/to/file
[PHASE 1] File exists: True/False
[PHASE 1] File size: XXXXX bytes
[PHASE 1] Using process_pdf_for_agent with chunking...
[PHASE 1] ✅ PDF extracted successfully
[PHASE 1] Chunks: N
[PHASE 1] Word count: XXXX
[PHASE 1] Text length: XXXXX chars
[PHASE 1] First 200 chars: [preview]
[PHASE 1] Added XXXXX chars to all_documents_content
[PHASE 1] Total accumulated: XXXXX chars
```

#### After extraction complete:
```python
[PHASE 1 - FINAL] Extraction complete
[PHASE 1 - FINAL] Processed documents: N
[PHASE 1 - FINAL] Total content length: XXXXX characters
[PHASE 1 - FINAL] Total words: XXXX
[PHASE 1 - FINAL] Documents info:
  - filename1: XXXX words (pdf)
  - filename2: XXXX words (pdf)
[PHASE 1 - FINAL] Preview of all_documents_content (first 500 chars):
[preview]
[PHASE 1 - FINAL] Preview of all_documents_content (last 500 chars):
[preview]
```

#### Before workflow call:
```python
[PHASE 1] BEFORE calling execute_document_analysis_workflow
[PHASE 1] Parameters being passed:
  - project_id: XXX
  - document_id: XXX
  - document_path: Multiple documents: file1, file2
  - additional_instructions length: XXXX chars
  - additional_instructions preview: [preview]
  - enable_web_research: True/False
  - document_content length: XXXXX chars
  - document_content preview (first 300 chars): [preview]
  - document_type: multiple
  - project_name: Análise de Requisitos - Projeto XXX
  - project_description: [preview]
```

---

### 2. backend/agents/langnetstate.py (Lines 344-402)

Added logging to `init_full_state()` function:

#### On entry:
```python
[PHASE 2] init_full_state() called
[PHASE 2] Input parameters:
  - project_id: XXX
  - document_id: XXX
  - document_path: XXX
  - project_name: XXX
  - project_description length: XXXX chars
  - project_domain: XXX
  - additional_instructions length: XXXX chars
  - document_type: XXX
  - document_content length: XXXXX chars
  - document_content preview (first 300 chars): [preview or (EMPTY!)]
```

#### On return:
```python
[PHASE 2] init_full_state() RETURNED state
[PHASE 2] State keys: [list of keys]
[PHASE 2] State['document_content'] length: XXXXX chars
[PHASE 2] State['document_content'] preview: [preview or (MISSING!)]
```

---

### 3. backend/agents/langnetagents.py (Multiple sections)

#### A. execute_document_analysis_workflow() (Lines 1209-1242)

Added logging before and after state initialization:

```python
[PHASE 2] execute_document_analysis_workflow() called
[PHASE 2] Parameters received:
  - document_content length: XXXXX chars
  - document_content preview (first 300 chars): [preview or (EMPTY!)]

[PHASE 2] State returned from init_full_state
[PHASE 2] state['document_content'] length: XXXXX chars
[PHASE 2] state['additional_instructions'] length: XXXX chars

[PHASE 2] About to execute analyze_document task
[PHASE 2] State passed to task has document_content: XXXXX chars
```

#### B. Input Functions (Lines 333-382)

Added logging to `analyze_document_input_func()` and `extract_requirements_input_func()`:

```python
[PHASE 3] [function_name] called
[PHASE 3] state['document_content'] length: XXXXX chars
[PHASE 3] state['additional_instructions'] length: XXXX chars

[PHASE 3] [function_name] RETURNED
[PHASE 3] task_input['document_content'] length: XXXXX chars
[PHASE 3] task_input['document_content'] preview (first 300 chars): [preview or (EMPTY!)]
```

#### C. execute_task_with_context() (Lines 1065-1088)

Added logging before and after prompt formatting:

```python
[PHASE 3] BEFORE formatting task description for 'task_name'
[PHASE 3] task_input keys: [list]
[PHASE 3] task_input['document_content'] length: XXXXX chars
[PHASE 3] task_input['additional_instructions'] length: XXXX chars
[PHASE 3] Raw task description template (first 500 chars): [template preview]

[PHASE 3] AFTER formatting task description for 'task_name'
[PHASE 3] Formatted description length: XXXXX chars
[PHASE 3] Formatted description preview (first 800 chars): [formatted preview]
[PHASE 3] Formatted description preview (search for 'document_content' keyword):
  [content around 'document_content:' or "⚠️ 'document_content:' NOT FOUND in formatted description!"]
```

---

## What These Logs Will Reveal

### Phase 1 will show:
- ✅ PDFs are being extracted correctly
- ✅ Content is being accumulated in `all_documents_content`
- ✅ Correct length and preview are passed to workflow
- ❌ Extraction is failing or returning minimal content

### Phase 2 will show:
- ✅ document_content arrives at workflow function
- ✅ document_content is correctly stored in state dict
- ✅ State passes validation and reaches task execution
- ❌ document_content is lost/corrupted during state initialization

### Phase 3 will show:
- ✅ Input functions extract document_content from state
- ✅ Prompt formatting substitutes {document_content} with actual text
- ✅ Formatted prompt contains PDF text (not placeholder)
- ❌ Input functions don't extract document_content
- ❌ Prompt formatting fails or doesn't substitute variables
- ❌ Formatted prompt contains placeholders instead of actual text

### Phase 4 (TO BE IMPLEMENTED) will show:
- ✅ Agent receives correct prompt with PDF content
- ❌ Agent ignores prompt and returns template

---

## Next Steps

1. **Restart backend server** to load new logging code
2. **Upload 2 test PDFs** and trigger analysis
3. **Collect complete server logs**
4. **Analyze logs** to identify exact failure point:
   - If Phase 1 fails → Problem is PDF extraction
   - If Phase 2 fails → Problem is state passing
   - If Phase 3 fails → Problem is prompt formatting
   - If all pass but output is still generic → Problem is agent behavior (Phase 4)

5. **Apply surgical fix** based on findings

---

## Expected Behavior

With these logs, we should see a clear trail of document_content from extraction through to the formatted prompt:

```
[PHASE 1] Total content length: 64234 characters
↓
[PHASE 2] document_content length: 64234 chars
↓
[PHASE 3] task_input['document_content'] length: 64234 chars
↓
[PHASE 3] Formatted description contains actual PDF text
```

If at any point the content length drops to ~2500 chars (size of instructions only) or becomes empty, we've found the bug location.

---

## Files Modified

1. `backend/app/routers/documents.py` - Phase 1 extraction logging
2. `backend/agents/langnetstate.py` - Phase 2 state initialization logging
3. `backend/agents/langnetagents.py` - Phase 2 workflow + Phase 3 formatting logging

---

## Commit Message

```
Add comprehensive debug logging to trace document_content pipeline

- Phase 1: Log PDF extraction in documents.py (per-document details, content preview, aggregation)
- Phase 2: Log state initialization in langnetstate.py and langnetagents.py (parameters, state contents)
- Phase 3: Log input functions and prompt formatting in langnetagents.py (before/after formatting)

Purpose: Identify exact point where document content is lost or ignored in requirements generation workflow.

Related to bug: Agents generating generic documents with placeholders instead of using actual PDF content.
```
