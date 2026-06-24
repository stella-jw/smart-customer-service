## ADDED Requirements

### Requirement: RAG-based Question Answering
The system SHALL answer user questions by retrieving relevant knowledge from the vector database.

#### Scenario: Basic RAG query
- **WHEN** user asks "产品如何购买"
- **THEN** system retrieves top-k relevant chunks from ChromaDB
- **AND** LLM generates answer based on retrieved context

#### Scenario: No relevant context found
- **WHEN** user question has no relevant matches in knowledge base
- **THEN** system returns "抱歉，我没有找到相关答案，请联系人工客服"

### Requirement: Query Classification
The system SHALL classify incoming queries to determine the response strategy.

#### Scenario: RAG query classification
- **WHEN** user asks a question
- **THEN** classifier determines if it's a RAG query (knowledge-based)
- **OR** a QA direct match
- **OR** a general chat

### Requirement: Multi-turn Conversation
The system SHALL maintain conversation context across multiple messages.

#### Scenario: Follow-up question
- **WHEN** user asks follow-up "那保修期呢"
- **THEN** system considers previous context ("产品") in retrieval

### Requirement: Response Source Tracking
The system SHALL record whether response came from RAG, QA pairs, or LLM.

#### Scenario: Source attribution
- **WHEN** response is generated
- **THEN** source field is set to "rag", "qa", or "llm"
- **AND** conversation is stored with source information

### Requirement: User Feedback Collection
The system SHALL collect user ratings for each response.

#### Scenario: Rating submission
- **WHEN** user rates a response via `/api/rate`
- **THEN** rating (1-5) and optional feedback is stored
- **AND** satisfaction_rate is updated for QA pairs if source="qa"
