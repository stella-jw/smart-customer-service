## ADDED Requirements

### Requirement: Conversation history management
The system SHALL store user messages and AI responses in the conversations table, indexed by session_id, to enable multi-turn dialogue context.

#### Scenario: User asks follow-up question
- **WHEN** user asks "内容是什么？" after previously asking "《所见》的作者是谁？" within the same session
- **THEN** the system SHALL include the previous question and answer in the context passed to LLM
- **AND** LLM SHALL understand "内容" refers to the poem "《所见》"

#### Scenario: User asks about previously mentioned entity
- **WHEN** user asks "作者还有哪些其它作品？" after learning the author is 袁枚
- **THEN** the system SHALL include the conversation where author was identified as 袁枚
- **AND** LLM SHALL correctly identify the author and provide related works

### Requirement: History context formatting
The system SHALL format conversation history as a string prefixed with "【对话历史】", with each turn prefixed by "用户:" or "客服:".

#### Scenario: History formatted correctly
- **WHEN** there are 2 previous turns in session
- **THEN** the history string SHALL be:
  ```
  用户: 第一个问题
  客服: 第一个回答
  用户: 第二个问题
  客服: 第二个回答
  ```

### Requirement: Configurable history turns
The system SHALL limit conversation history to a configurable number of turns (default: 5), prioritizing the most recent turns.

#### Scenario: History truncated to max turns
- **WHEN** session has 10 previous turns and max_history_turns is set to 3
- **THEN** only the 3 most recent turns (6 messages) SHALL be included in context

### Requirement: Token limit estimation
The system SHALL estimate token usage and truncate history if needed, reserving approximately 500 tokens for current input and generation.

#### Scenario: History truncated due to token limit
- **WHEN** combined history exceeds estimated token limit
- **THEN** the system SHALL truncate from the oldest turns first
- **AND** ensure current user input always fits within context

### Requirement: Backward compatibility
The system SHALL work correctly when there is no conversation history (first message in session).

#### Scenario: First message in session
- **WHEN** user sends first message in a new session
- **THEN** the system SHALL generate response without any history context
- **AND** behave exactly as before this feature was added

### Requirement: LLM knowledge fallback for factual questions
When RAG and QA searches do not return results, the system SHALL allow LLM to answer factual questions using its own knowledge, with appropriate disclaimer.

#### Scenario: Factual question answered by LLM knowledge
- **WHEN** user asks "《所见》的作者还写过哪些诗？" and RAG/QA returns no results
- **AND** the question contains factual indicators (who/what/which/etc.)
- **THEN** the system SHALL generate response using LLM's own knowledge
- **AND** include disclaimer "以下仅供参考，实际情况请以官方为准"

#### Scenario: Non-factual question falls back to guidance
- **WHEN** user asks "你觉得我应该买哪个？" and RAG/QA returns no results
- **AND** the question is subjective or requires specific knowledge
- **THEN** the system SHALL generate response guiding user to contact customer service

### Requirement: Factual question detection
The system SHALL detect factual questions based on question words and entity indicators.

#### Scenario: Question with "谁" detected as factual
- **WHEN** user asks "《所见》的作者是谁？"
- **THEN** the system SHALL identify this as a factual question based on presence of "谁"

#### Scenario: Question with "哪些" detected as factual
- **WHEN** user asks "作者还有哪些其它作品？"
- **THEN** the system SHALL identify this as a factual question based on presence of "哪些"
