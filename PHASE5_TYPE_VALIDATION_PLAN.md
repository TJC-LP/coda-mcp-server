# Phase 5: Pydantic Type Validation Integration

## Current Status

✅ **Phases 1-4 Complete:**
- Phase 1: 80+ Pydantic models extracted from OpenAPI spec (~72KB)
- Phase 2: All code converted to snake_case
- Phase 3: Modular architecture (client.py, tools/*, models/*)
- Phase 4: Explicit LLM descriptions on all 26 tools

✅ **Quality Metrics:**
- mypy: 0 errors across 16 source files
- pytest: 16/16 tests passing
- Code organization: 1 monolith → 16 focused modules

## Phase 5 Objectives

Add runtime type validation using the Pydantic models we created in Phase 1.

### Goals

1. **Request Validation**: Validate inputs match Pydantic schemas before API calls
2. **Response Validation**: Parse API responses into Pydantic models for type safety
3. **Better Error Messages**: Pydantic validation errors instead of API errors
4. **Full Type Safety**: End-to-end type checking from tool call to API response

## Implementation Strategy

### 1. Update Tool Function Signatures

**Current pattern (untyped):**
```python
async def create_doc(
    client: CodaClient,
    title: str,
    source_doc: str | None = None,
    timezone: str | None = None,
    folder_id: str | None = None,
    workspace_id: str | None = None,
    initial_page: InitialPage | None = None,
) -> Any:
    request_data = {"title": title, ...}
    return await client.request(Method.POST, "docs", json=request_data)
```

**New pattern (Pydantic-validated):**
```python
async def create_doc(
    client: CodaClient,
    request: DocCreate,
) -> DocumentCreationResult:
    """Create a new Coda doc.

    Args:
        client: The Coda client instance.
        request: DocCreate model with all doc creation parameters.

    Returns:
        DocumentCreationResult with the created doc's metadata.
    """
    result = await client.request(
        Method.POST,
        "docs",
        json=request.model_dump(by_alias=True, exclude_none=True)
    )
    return DocumentCreationResult.model_validate(result)
```

### 2. Update CodaClient.request()

**Add Pydantic serialization support:**
```python
from pydantic import BaseModel

class CodaClient:
    async def request(self, method: Method, endpoint: str, **kwargs: Any) -> Any:
        # Auto-serialize Pydantic models in json parameter
        if "json" in kwargs and isinstance(kwargs["json"], BaseModel):
            kwargs["json"] = kwargs["json"].model_dump(by_alias=True, exclude_none=True)

        # Make request...
        result = await session.request(...)

        # Return raw dict - validation happens in tool functions
        return result
```

### 3. Update Server.py Wrappers

**MCP wrappers construct Pydantic models:**
```python
@mcp.tool(description="...")
async def create_doc(
    title: str,
    source_doc: str | None = None,
    timezone: str | None = None,
    folder_id: str | None = None,
    workspace_id: str | None = None,
    initial_page: InitialPage | None = None,
) -> Any:
    """Create a new Coda doc."""
    # Construct Pydantic model from parameters
    request = DocCreate(
        title=title,
        source_doc=source_doc,
        timezone=timezone,
        folder_id=folder_id,
        workspace_id=workspace_id,
        initial_page=initial_page,
    )
    # Call tool function with validated model
    result = await docs.create_doc(client, request)
    # Return as dict for MCP (or keep as Pydantic model?)
    return result.model_dump(by_alias=True) if isinstance(result, BaseModel) else result
```

## Model Mapping

### Docs Tools (6 tools)

| Tool | Request Model | Response Model |
|------|---------------|----------------|
| whoami | None | Dict (no model in spec) |
| get_doc_info | None (just doc_id) | Doc |
| delete_doc | None (just doc_id) | DocDelete |
| update_doc | DocUpdate | DocUpdateResult |
| list_docs | Params only | DocList |
| create_doc | DocCreate | DocumentCreationResult |

### Pages Tools (7 tools)

| Tool | Request Model | Response Model |
|------|---------------|----------------|
| list_pages | Params only | PageList |
| get_page | None | Page |
| update_page | PageUpdate | PageUpdateResult |
| delete_page | None | PageDeleteResult |
| begin_page_content_export | BeginPageContentExportRequest | BeginPageContentExportResponse |
| get_page_content_export_status | None (params) | PageContentExportStatusResponse |
| create_page | PageCreate | PageCreateResult |

### Tables Tools (5 tools)

| Tool | Request Model | Response Model |
|------|---------------|----------------|
| list_tables | Params only | TableList |
| get_table | None | Table |
| list_columns | Params only | ColumnList |
| get_column | None | Column |
| push_button | None | PushButtonResult |

### Rows Tools (6 tools)

| Tool | Request Model | Response Model |
|------|---------------|----------------|
| list_rows | Params only | RowList |
| get_row | None | Row |
| upsert_rows | RowsUpsert | RowsUpsertResult |
| update_row | RowUpdate | RowUpdateResult |
| delete_row | None | RowDeleteResult |
| delete_rows | RowsDelete | RowsDeleteResult |

### Formulas Tools (2 tools)

| Tool | Request Model | Response Model |
|------|---------------|----------------|
| list_formulas | Params only | Dict (no model) |
| get_formula | None | Dict (no model) |

## Implementation Phases

### Phase 5.1: Update CodaClient

1. Add Pydantic import
2. Add auto-serialization for BaseModel in json parameter
3. Keep response as dict (validation in tools)
4. Test with existing tools

### Phase 5.2: Update Tool Functions (Gradual)

**Approach**: Update one domain at a time to test incrementally

1. **Start with docs.py** (simplest, 6 tools)
   - Update function signatures to use Pydantic models
   - Add response validation with model_validate()
   - Test thoroughly

2. **Then pages.py** (7 tools, includes export)
   - Handle export types carefully
   - Test export workflow with validation

3. **Then tables.py** (5 tools)
4. **Then rows.py** (6 tools, complex cell values)
5. **Finally formulas.py** (2 tools, no models yet)

### Phase 5.3: Update Server.py Wrappers

For each tool:
1. Construct Pydantic request model from parameters
2. Call tool function with model
3. Convert response back to dict for MCP compatibility
4. Handle validation errors gracefully

## Benefits of Phase 5

1. **Runtime Validation**
   - Catch invalid inputs before API calls
   - Better error messages for LLM
   - Prevent malformed API requests

2. **Type Safety**
   - Full type checking from MCP call → API response
   - IDE autocomplete for all fields
   - Compile-time + runtime guarantees

3. **Self-Documenting**
   - Pydantic models document expected structure
   - Field descriptions from OpenAPI spec
   - Examples for each field

4. **API Contract Enforcement**
   - Detect API changes early
   - Ensure responses match expected schema
   - Graceful degradation on schema mismatches

## Testing Strategy

1. **Unit Tests**
   - Test Pydantic model validation
   - Test serialization (snake_case ↔ camelCase)
   - Test optional field handling

2. **Integration Tests**
   - Test full tool execution with validation
   - Test error cases (invalid input, API errors)
   - Test export workflow end-to-end

3. **Compatibility Tests**
   - Ensure MCP tools still work
   - Verify TypedDict backwards compatibility
   - Test with real API (if token available)

## Migration Checklist

- [ ] Phase 5.1: Update CodaClient.request() for Pydantic serialization
- [ ] Phase 5.2a: Update tools/docs.py with Pydantic types
- [ ] Phase 5.2b: Update tools/pages.py with Pydantic types
- [ ] Phase 5.2c: Update tools/tables.py with Pydantic types
- [ ] Phase 5.2d: Update tools/rows.py with Pydantic types
- [ ] Phase 5.2e: Update tools/formulas.py (add missing models or keep as-is)
- [ ] Phase 5.3: Update server.py wrappers to construct Pydantic models
- [ ] Phase 5.4: Add validation error handling
- [ ] Phase 5.5: Add tests for Pydantic validation
- [ ] Phase 5.6: Update documentation
- [ ] Final: Run full test suite
- [ ] Final: Verify mypy/ruff clean
- [ ] Final: Commit and celebrate! 🎉

## Estimated Impact

**Code Changes:**
- client.py: +10 lines (Pydantic serialization)
- tools/*.py: ~100 lines total (signature updates, validation)
- server.py: ~150 lines (model construction in wrappers)
- tests/: +200 lines (new validation tests)

**Type Safety:**
- Before: 60% (models exist, not used)
- After: 95% (full request/response validation)

**Maintainability:**
- API contract enforcement
- Automatic validation
- Better error messages
- Self-documenting code

## Next Steps

Ready to begin Phase 5 implementation!
