## ADDED Requirements

### Requirement: Document Upload
The system SHALL allow admin users to upload documents in PDF, DOCX, TXT, and MD formats.

#### Scenario: Successful PDF upload
- **WHEN** admin uploads a PDF file via `/api/admin/document`
- **THEN** system stores the file and returns document_id with status "pending"

#### Scenario: Unsupported format rejection
- **WHEN** admin uploads a file with unsupported format (e.g., .exe)
- **THEN** system returns 400 error with message "Unsupported file format"

### Requirement: Document Parsing
The system SHALL parse uploaded documents and extract text content.

#### Scenario: PDF parsing
- **WHEN** document with status "pending" is processed
- **THEN** system extracts text and splits into chunks of ~500 characters

#### Scenario: Parsing failure handling
- **WHEN** document parsing fails
- **THEN** document status is set to "failed" with error message stored

### Requirement: Document Indexing
The system SHALL generate embeddings for parsed chunks and store in ChromaDB.

#### Scenario: Successful indexing
- **WHEN** document is parsed successfully
- **THEN** chunks are embedded and stored in ChromaDB with document metadata
- **AND** document status is updated to "indexed"
- **AND** chunk_count is recorded

### Requirement: Knowledge Base Management
The system SHALL allow admins to view, search, and delete documents.

#### Scenario: Document list retrieval
- **WHEN** admin requests `/api/admin/document`
- **THEN** system returns paginated list of documents with status, title, file_type

#### Scenario: Document deletion
- **WHEN** admin deletes a document via `/api/admin/document/{id}`
- **THEN** document is removed from SQLite
- **AND** associated chunks are removed from ChromaDB

### Requirement: QA Pair Management
The system SHALL allow admins to create, update, and delete QA pairs.

#### Scenario: Add new QA pair
- **WHEN** admin creates QA pair via `/api/admin/qa`
- **THEN** QA pair is stored with question, answer, keywords

#### Scenario: QA list retrieval
- **WHEN** admin requests `/api/admin/qa`
- **THEN** system returns paginated list of QA pairs with usage statistics
