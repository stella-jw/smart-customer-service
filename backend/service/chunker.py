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


class TitleAwareChunker(ChunkStrategy):
    """
    标题感知分块器

    专门处理古诗、文档集等有明确标题结构的文本
    策略：
    1. 按标题（《...》）分割
    2. 每个标题下的内容作为一个独立chunk
    3. 如果单个块过大，按段落继续分割
    """

    def __init__(self, max_chunk_size: int = 800, min_chunk_size: int = 50):
        """
        Args:
            max_chunk_size: 每个块的最大字符数
            min_chunk_size: 每个块的最小字符数（太小的会合并到下一个）
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str, metadata: dict) -> List[Dict[str, Any]]:
        """执行分块"""
        # 按标题分割文本
        sections = self._split_by_titles(text)

        chunks = []
        for section_text, section_title in sections:
            if not section_text.strip():
                continue

            # 如果单个section就超过max_chunk_size，用FixedSize分块
            if len(section_text) > self.max_chunk_size:
                fixed_chunks = FixedSizeChunker(
                    chunk_size=self.max_chunk_size,
                    overlap=50
                ).chunk(section_text, metadata)

                # 为每个子chunk添加title信息
                for chunk in fixed_chunks:
                    chunk["metadata"]["section_title"] = section_title
                    chunk["metadata"]["is_section"] = True
                    chunks.append(chunk)
            else:
                chunks.append({
                    "content": section_text.strip(),
                    "metadata": {
                        **metadata.copy(),
                        "section_title": section_title,
                        "is_section": True
                    }
                })

        # 合并太小的chunk
        chunks = self._merge_small_chunks(chunks)

        # 添加index
        for i, chunk in enumerate(chunks):
            chunk["metadata"]["chunk_index"] = i
            chunk["metadata"]["total_chunks"] = len(chunks)

        return chunks

    def _split_by_titles(self, text: str) -> List[tuple]:
        """
        按标题分割文本

        Returns:
            [(content, title), ...]
        """
        # 使用《...》作为标题分隔符
        title_pattern = r'《([^》]+)》'

        sections = []
        current_section_lines = []
        current_title = "通用内容"

        # 找到所有标题的位置
        title_matches = list(re.finditer(title_pattern, text))

        if not title_matches:
            # 没有标题，整段作为一个section
            return [(text.strip(), "通用内容")]

        # 处理第一个标题之前的内容
        first_title_pos = title_matches[0].start()
        if first_title_pos > 0:
            before_text = text[:first_title_pos].strip()
            if before_text:
                for para in before_text.split('\n\n'):
                    if para.strip():
                        current_section_lines.append(para.strip())

        # 处理每个标题及其内容
        for i, match in enumerate(title_matches):
            title = match.group(1)
            title_start = match.end()

            # 确定当前标题的内容范围（到下一个标题之前）
            if i + 1 < len(title_matches):
                title_end = title_matches[i + 1].start()
            else:
                title_end = len(text)

            content_after_title = text[title_start:title_end]

            # 保存之前的section
            if current_section_lines:
                sections.append(('\n'.join(current_section_lines), current_title))

            # 开始新section
            current_title = title
            current_section_lines = []

            # 先添加标题标记
            current_section_lines.append(f"《{title}》")

            # 逐行处理内容，遇到章节标记（单元、课等）就停止
            section_header_pattern = re.compile(r'^(第[一二三四五六七八九十百零\d]+[单元课节]|第\d+课|语文园地|日积月累)')
            in_section_content = False

            for line in content_after_title.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # 检查是否是章节标记行
                if section_header_pattern.match(line):
                    if not in_section_content:
                        continue
                    else:
                        break

                # 检查是否是下一个标题的预告（如 "第4课古诗三首"）
                if re.match(r'^第\d+课', line) and '古诗' in line:
                    if not in_section_content:
                        continue
                    else:
                        break

                # 转换 [朝代]作者名 为 作者：作者名 格式
                line = self._convert_author_format(line)

                # 这行是诗歌内容
                current_section_lines.append(line)
                in_section_content = True

        # 保存最后一个section
        if current_section_lines:
            sections.append(('\n'.join(current_section_lines), current_title))

        return sections

    def _convert_author_format(self, line: str) -> str:
        """转换 [朝代]作者名 为 作者：作者名 格式"""
        # 匹配 [朝代]作者名 或 [朝代] 作者名 格式，转换为 作者：作者名
        # 例如: [清]袁枚 -> 作者：袁枚
        match = re.match(r'^\[([^\]]+)\]\s*([^\[【\n《》].+)$', line)
        if match:
            author = match.group(2).strip()
            return f"作者：{author}"
        return line

    def _merge_small_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """合并太小的chunk到下一个（仅限同标题）"""
        if not chunks:
            return chunks

        merged = []
        buffer = None

        for chunk in chunks:
            chunk_title = chunk["metadata"].get("section_title")

            if len(chunk["content"]) < self.min_chunk_size:
                # 小chunk
                if buffer is None:
                    buffer = chunk
                else:
                    # 检查标题是否相同
                    if buffer["metadata"].get("section_title") == chunk_title:
                        buffer["content"] += "\n\n" + chunk["content"]
                    else:
                        # 标题不同，buffer先输出，再把当前chunk放入buffer
                        merged.append(buffer)
                        buffer = chunk
            else:
                # 大chunk，先处理buffer
                if buffer is not None:
                    if buffer["metadata"].get("section_title") == chunk_title:
                        chunk["content"] = buffer["content"] + "\n\n" + chunk["content"]
                    else:
                        merged.append(buffer)
                    buffer = None
                merged.append(chunk)

        # 处理最后一个buffer
        if buffer is not None:
            merged.append(buffer)

        return merged


# 工厂函数
def get_chunker(chunker_type: str = "fixed", **kwargs) -> ChunkStrategy:
    """获取分块器"""
    chunkers = {
        "fixed": FixedSizeChunker,
        "semantic": SemanticChunker,
        "recursive": RecursiveChunker,
        "title_aware": TitleAwareChunker
    }

    chunker_class = chunkers.get(chunker_type.lower(), FixedSizeChunker)
    return chunker_class(**kwargs)
