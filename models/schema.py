from pydantic import BaseModel


class SearchResult(BaseModel):
    """
    SearchResult（搜索结果）
    表示搜索工具返回的一条搜索结果
    """

    title: str
    url: str
    snippet: str


class DocumentContent(BaseModel):
    """
    DocumentContent（网页正文内容）
    表示读取网页后的正文信息
    """

    title: str
    url: str
    text: str