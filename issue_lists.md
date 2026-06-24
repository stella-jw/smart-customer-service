# 智能客服项目 AI/大模型相关问题列表

## 1. MiniMax Embedding API 兼容性问题

**问题描述**: MiniMax 的 Embedding API 与 OpenAI 不兼容，需要用 HTTP 直接调用。

**代码位置**: `backend/db/chroma/manager.py`

**解决方案**: 自定义 `MiniMaxEmbeddingFunction` 类，使用 requests 直接调用 MiniMax Embedding API。

---

## 2. ChromaDB EmbeddingFunction 接口变更

**问题描述**: ChromaDB 0.4.16+ 更改了 EmbeddingFunction 接口，`__call__` 参数从 `texts` 改为 `input`，并要求 `name()` 方法。

**代码位置**: `backend/db/chroma/manager.py`

**修复内容**:
```python
class MiniMaxEmbeddingFunction:
    def __call__(self, input: List[str]) -> List[List[float]]:  # 原来是 texts
        ...

    def name(self) -> str:  # 新增方法
        return "minimax-embedding"
```

---

## 3. ChromaDB Where 子句操作符问题

**问题描述**: ChromaDB 1.5+ 的 where clause 必须使用操作符语法（如 `$eq`），不能直接使用字段名。

**代码位置**: `backend/db/chroma/manager.py`

**解决方案**: 使用辅助函数构建查询条件。
```python
def make_eq_clause(field, value):
    return {field: {"$eq": value}}
```

---

## 4. ChromaDB 持久化客户端问题

**问题描述**: 使用 `chromadb.Client()` 创建的客户端默认是内存模式，服务重启后数据丢失。需要使用 `chromadb.PersistentClient` 才能持久化。

**代码位置**: `backend/db/chroma/manager.py`

**修复内容**:
```python
# 错误（内存模式）
_chroma_client = chromadb.Client(Settings(persist_directory=...))

# 正确（持久化模式）
_chroma_client = chromadb.PersistentClient(path=...)
```

---

## 5. 文档解析器类定义顺序问题

**问题描述**: `DocumentParser` 基类的 `SUPPORTED_TYPES` 字典引用了子类，但子类定义在基类之后，导致 `NameError: name 'PDFParser' is not defined`。

**代码位置**: `backend/service/document_parser.py`

**解决方案**: 先定义所有子类，再在基类定义后添加 `SUPPORTED_TYPES` 字典。
```python
# 先定义子类
class PDFParser(DocumentParser): ...

# 再定义基类
class DocumentParser(ABC): ...

# 最后添加 SUPPORTED_TYPES
DocumentParser.SUPPORTED_TYPES = {
    "pdf": PDFParser,
    ...
}
```

---

## 6. SQLAlchemy Session 对象 Detached 问题

**问题描述**: 在 session 关闭后访问 SQLAlchemy 对象的属性，会导致 "Instance is not bound to a Session" 错误。

**代码位置**: `backend/api/routers/knowledge.py`

**解决方案**: 在 session 关闭前提取所有需要的数据到普通对象。
```python
with get_db_session() as db:
    doc = create_document(...)
    doc_id = doc.id  # 在 with 块内提取
    doc_title = doc.title
# session 已关闭，但 doc_id, doc_title 仍可访问
```

---

## 7. ChromaDB 删除文档时的实例冲突

**问题描述**: ChromaDB 1.5+ 可能存在内部全局实例冲突，删除文档时报错 "An instance of Chroma already exists for ./data/chroma_db with different settings"。

**代码位置**: `backend/api/routers/knowledge.py`

**解决方案**: 在删除向量库时添加错误处理，忽略 ChromaDB 相关的删除误差。
```python
try:
    chroma_manager.delete_kb_chunks(document_id)
except Exception as chroma_err:
    print(f"[API] ChromaDB 删除警告: {chroma_err}")
```

---

## 8. 后端依赖安装位置问题

**问题描述**: 后端服务可能使用不同的 Python 环境（venv 或系统 pyenv），依赖需要安装到正确的环境。

**解决方案**: 确认 uvicorn 使用的 Python 环境，将依赖安装到该环境。
```bash
# 查看 uvicorn 使用的 Python
ps aux | grep uvicorn

# 确认当前 Python 环境
which python

# 安装依赖
pip install python-docx PyPDF2
```

---

## 9. 文档上传大小限制

**问题描述**: 默认 10MB 限制可能不够用。

**代码位置**: `config.py` 和 `backend/api/routers/knowledge.py`

**当前限制**: 100MB

---

## 10. 文档处理后台任务丢失

**问题描述**: 服务重启后，后台处理任务丢失，文档状态停留在 pending 或 parsing。

**解决方案**:
1. 服务重启后重新上传文档
2. 或使用 `/api/admin/documents/{document_id}/reindex` 接口重新触发索引

---

## 11. ChromaDB 实例冲突导致无法删除

**问题描述**: 频繁创建/删除 ChromaDB 客户端可能导致 "different settings" 冲突。

**解决方案**:
1. 完全停止 uvicorn 服务（包括 --reload）
2. 删除旧的 chroma_db 目录
3. 重启服务

```bash
pkill -9 -f uvicorn
rm -rf data/chroma_db
python -m uvicorn backend.api.main:app --reload --port 8000
```

---

## 12. QA匹配返回None导致RAG兜底

**问题描述**: ChromaDB search_qa 匹配到了结果，但因为存储时 metadata 缺少 `question` 和 `answer` 字段，导致后续读取时返回 None。

**代码位置**: `backend/api/routers/admin.py` 第354-363行

**原因**: `add_qa_embeddings` 存储时只存了 `qa_id`, `keywords`, `category`，缺少 `question` 和 `answer`。

**修复内容**:
```python
"metadata": {
    "qa_id": qa.id,
    "question": qa.question,    # 新增
    "answer": qa.answer,       # 新增
    "keywords": qa.keywords,
    "category": qa.category
}
```

**影响**: 已添加的QA数据需要删除后重新添加才能生效。

---

## 13. 意图分类LLM调用失败

**问题描述**: classify_intent 节点调用 LLM 时报错 "Expecting value: line 1 column 1 (char 0)"，说明 API 返回的不是有效 JSON。

**代码位置**: `backend/graph/nodes/classify.py`

**原因**: LLM 返回格式不符合预期，或 API 调用失败。

**解决方案**: 在 except 块中捕获错误并降级为默认意图（QUESTION）。

---

## 14. SQLAlchemy Session Detached 在 get_history

**问题描述**: `get_history` 函数在 session 关闭后访问 Conversation 对象属性，导致 "Instance is not bound to a Session" 错误。

**代码位置**: `backend/api/routers/chat.py` 第204-216行

**修复内容**: 在 with 块内完成所有数据提取。
```python
with get_db_session() as db:
    conversations = get_session_conversations(db, bot_id, session_id)
    # 在with块内提取所有需要的数据
    messages = [
        Message(
            id=conv.id,
            content=conv.message,
            ...
        )
        for conv in conversations
    ]
return HistoryResponse(session_id=session_id, messages=messages)
```

---

## 15. respond节点未正确使用matched_qa_answer

**问题描述**: QA匹配成功后，respond 节点使用 `generated_response` 而不是 `matched_qa_answer`，导致返回空响应。

**代码位置**: `backend/graph/nodes/respond.py`

**修复内容**:
```python
else:
    # 先检查QA匹配结果（QA优先于RAG）
    matched_answer = state.get("matched_qa_answer", "")
    if matched_answer:
        response = matched_answer
    else:
        response = state.get("generated_response", "")
```
