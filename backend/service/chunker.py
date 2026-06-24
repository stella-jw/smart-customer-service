"""
=============================================
文本分块服务
=============================================
"""

from typing import List, Dict, Any
import re


class ChunkStrategy:
    """分块策略基类"""

    def chunk(self, text: str, metadata: dict) -> List[Dict[str, Any]]:
        """
        将文本分块

        Args:
            text: 纯文本内容
            metadata: 元数据

        Returns:
            [{"content": str, "metadata": dict}, ...]
        """
        raise NotImplementedError


class FixedSizeChunker(ChunkStrategy):
    """
    固定大小分块（带重叠）

    策略：
    1. 按段落分割
    2. 如果段落超过chunk_size，强制按句子分割
    3. 保留段落边界完整性
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Args:
            chunk_size: 每个块的目标大小（字符数）
            overlap: 相邻块之间的重叠大小（字符数）
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: dict) -> List[Dict[str, Any]]:
        """执行分块"""
        chunks = []

        # 按段落分割
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果单个段落就超过chunk_size，需要强制分割
            if len(para) > self.chunk_size:
                # 先保存当前块
                if current_chunk.strip():
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": metadata.copy()
                    })

                # 按句子分割大段落
                sentences = self._split_sentences(para)
                current_chunk = ""

                for sent in sentences:
                    if len(current_chunk) + len(sent) > self.chunk_size:
                        if current_chunk.strip():
                            chunks.append({
                                "content": current_chunk.strip(),
                                "metadata": metadata.copy()
                            })

                        # 处理重叠
                        if self.overlap > 0 and len(current_chunk) > self.overlap:
                            current_chunk = current_chunk[-self.overlap:]
                        else:
                            current_chunk = ""

                    current_chunk += sent + "。"

            # 如果当前段落加上超过chunk_size，先保存当前块
            elif len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk.strip():
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": metadata.copy()
                    })

                # 处理重叠
                if self.overlap > 0 and len(current_chunk) > self.overlap:
                    current_chunk = current_chunk[-self.overlap:]
                else:
                    current_chunk = ""

                current_chunk = para
            else:
                # 追加到当前块
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # 处理最后一个块
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": metadata.copy()
            })

        # 添加chunk_index到metadata
        for i, chunk in enumerate(chunks):
            chunk["metadata"]["chunk_index"] = i
            chunk["metadata"]["total_chunks"] = len(chunks)

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """将文本按句子分割"""
        # 按常见句子结束符分割
        sentences = re.split(r'[。！？.!?；;]', text)
        return [s.strip() for s in sentences if s.strip()]


class SemanticChunker(ChunkStrategy):
    """
    语义分块（按段落+主题边界）

    使用 LLM 识别语义边界进行分块
    """

    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 1000):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, metadata: dict) -> List[Dict[str, Any]]:
        """执行语义分块"""
        # 简单的段落分块 + 合并策略
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)

            # 如果单个段落就超过max，直接作为独立块
            if para_len > self.max_chunk_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                chunks.append(para)
                continue

            # 检查添加后是否超过max
            current_len = sum(len(p) for p in current_chunk)
            if current_len + para_len + 2 > self.max_chunk_size:
                # 保存当前块
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                current_chunk.append(para)
            else:
                current_chunk.append(para)

        # 处理最后一个块
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # 构建返回结果
        result = []
        for i, chunk_text in enumerate(chunks):
            # 如果块太小，尝试与下一个合并
            if len(chunk_text) < self.min_chunk_size and i < len(chunks) - 1:
                chunks[i + 1] = chunk_text + "\n\n" + chunks[i + 1]
                continue

            result.append({
                "content": chunk_text,
                "metadata": {
                    **metadata.copy(),
                    "chunk_index": len(result),
                    "total_chunks": len(result) + 1  # 临时值，会更新
                }
            })

        # 更新total_chunks
        total = len(result)
        for chunk in result:
            chunk["metadata"]["total_chunks"] = total

        return result


class RecursiveChunker(ChunkStrategy):
    """
    递归字符分块

    按层级分割：段落 → 句子 → 单词
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50, separators: list = None):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators or ["\n\n", "\n", "。", ".", " ", ""]

    def chunk(self, text: str, metadata: dict) -> List[Dict[str, Any]]:
        """执行递归分块"""
        chunks = []
        self._split_text(text, metadata, chunks)
        return chunks

    def _split_text(self, text: str, metadata: dict, chunks: list):
        """递归分割文本"""
        # 尝试用不同分隔符分割
        for sep in self.separators:
            if sep and sep in text:
                parts = text.split(sep)
                self._merge_chunks(parts, sep, metadata, chunks)
                return

        # 无法再分割，直接添加
        if text.strip():
            chunks.append({
                "content": text.strip(),
                "metadata": metadata.copy()
            })

    def _merge_chunks(self, parts: list, sep: str, metadata: dict, chunks: list):
        """合并小块"""
        current = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if len(current) + len(sep) + len(part) <= self.chunk_size:
                if current:
                    current += sep + part
                else:
                    current = part
            else:
                if current.strip():
                    chunks.append({
                        "content": current.strip(),
                        "metadata": metadata.copy()
                    })

                # 处理重叠
                if self.overlap > 0 and len(current) > self.overlap:
                    current = current[-self.overlap:]
                else:
                    current = ""

                current = part

        if current.strip():
            chunks.append({
                "content": current.strip(),
                "metadata": metadata.copy()
            })

        # 更新chunk_index
        for i, chunk in enumerate(chunks):
            chunk["metadata"]["chunk_index"] = i
            chunk["metadata"]["total_chunks"] = len(chunks)


# 工厂函数
def get_chunker(chunker_type: str = "fixed", **kwargs) -> ChunkStrategy:
    """获取分块器"""
    chunkers = {
        "fixed": FixedSizeChunker,
        "semantic": SemanticChunker,
        "recursive": RecursiveChunker
    }

    chunker_class = chunkers.get(chunker_type.lower(), FixedSizeChunker)
    return chunker_class(**kwargs)
