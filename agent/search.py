from ddgs import DDGS
import time


SEARCH_MODE = "real"


def clean_text(text: str, max_len: int = 300) -> str:
    """
    基础清洗：
    1. 防止 None
    2. 去掉多余空白
    3. 限制长度，避免后面 summary / token 爆掉
    """
    if not text:
        return ""

    text = " ".join(str(text).split())
    return text[:max_len]


def mock_search(query: str, round_num: int = 1) -> list[dict]:
    """
    mock版搜索，用来保证系统在没联网或调试阶段也能跑通
    """
    if round_num == 1:
        return [
            {
                "title": f"{query} - 初步结果",
                "snippet": f"这是关于【{query}】的一条初步信息，当前信息量较少。",
                "source": "mock_source_1"
            }
        ]

    if "定义" in query:
        return [
            {
                "title": "AI教育定义",
                "snippet": "AI教育通常指将人工智能技术用于教学、学习支持和教育管理的过程。",
                "source": "edu_mock_1"
            },
            {
                "title": "AI教师的概念",
                "snippet": "AI教师更像是一种智能教学助手，能够辅助答疑、推荐内容和跟踪学习进度。",
                "source": "edu_mock_2"
            },
            {
                "title": "教师角色变化",
                "snippet": "在AI参与教学后，教师角色可能从单纯知识传授者转向学习引导者和情感支持者。",
                "source": "edu_mock_3"
            }
        ]

    if "关键概念" in query:
        return [
            {
                "title": "个性化学习",
                "snippet": "个性化学习是AI教育中的核心概念，强调根据学生差异动态调整内容与节奏。",
                "source": "concept_mock_1"
            },
            {
                "title": "人机协同",
                "snippet": "人机协同意味着AI负责高频重复任务，人类教师负责价值引导、情感沟通与复杂判断。",
                "source": "concept_mock_2"
            },
            {
                "title": "教育公平",
                "snippet": "AI可能帮助扩大优质教育资源覆盖面，但也可能带来新的技术鸿沟问题。",
                "source": "concept_mock_3"
            }
        ]

    if "应用场景" in query:
        return [
            {
                "title": "智能答疑",
                "snippet": "AI可以在课后答疑、知识点解释和练习反馈中承担高频交互任务。",
                "source": "scene_mock_1"
            },
            {
                "title": "自动批改",
                "snippet": "AI在客观题批改、作文辅助评分和作业分析中已经表现出较高效率。",
                "source": "scene_mock_2"
            },
            {
                "title": "学习路径推荐",
                "snippet": "AI能够根据学生行为数据推荐个性化学习路径和复习计划。",
                "source": "scene_mock_3"
            }
        ]

    if "优势" in query or "局限" in query:
        return [
            {
                "title": "AI的优势",
                "snippet": "AI的优势包括高效率、可规模化、可持续提供个性化反馈和低边际成本。",
                "source": "pros_mock_1"
            },
            {
                "title": "AI的局限",
                "snippet": "AI的局限包括缺乏真实情感、难以进行价值塑造，以及对复杂教育情境理解有限。",
                "source": "cons_mock_2"
            },
            {
                "title": "教师不可替代性",
                "snippet": "教师在人格示范、关系建立、课堂氛围塑造和道德引导方面仍具有明显不可替代性。",
                "source": "cons_mock_3"
            }
        ]

    return [
        {
            "title": f"{query} - 结果1",
            "snippet": f"这是关于【{query}】的补充模拟信息1。",
            "source": "mock_default_1"
        },
        {
            "title": f"{query} - 结果2",
            "snippet": f"这是关于【{query}】的补充模拟信息2。",
            "source": "mock_default_2"
        },
        {
            "title": f"{query} - 结果3",
            "snippet": f"这是关于【{query}】的补充模拟信息3。",
            "source": "mock_default_3"
        }
    ]


def real_search(query: str, round_num: int = 1, max_results: int = 5, retries: int = 3) -> list[dict]:
    """
    真实搜索：
    - 使用 DDGS
    - 加 retry，减少网络抖动带来的直接失败
    - 输出结构统一成 title / snippet / source
    """
    last_error = None

    for attempt in range(retries):
        try:
            results = []

            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    title = clean_text(r.get("title", ""), max_len=120)
                    snippet = clean_text(r.get("body", ""), max_len=300)
                    source = r.get("href", "")

                    # 跳过完全空结果
                    if not title and not snippet:
                        continue

                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "source": source
                    })

            return results

        except Exception as e:
            last_error = e
            time.sleep(1)

    # 如果多次失败，返回一个结构化错误结果，避免系统直接崩
    return [
        {
            "title": "SEARCH_ERROR",
            "snippet": f"真实搜索失败：{str(last_error)}",
            "source": "system_error"
        }
    ]


def search(query: str, round_num: int = 1) -> list[dict]:
    """
    对外统一入口
    """
    if SEARCH_MODE == "mock":
        return mock_search(query, round_num)

    if SEARCH_MODE == "real":
        return real_search(query, round_num)

    raise ValueError(f"不支持的 SEARCH_MODE: {SEARCH_MODE}")


if __name__ == "__main__":
    test_query = "AI teacher definition"
    results = search(test_query)

    print(f"SEARCH_MODE: {SEARCH_MODE}")
    print(f"查询词: {test_query}")
    print(f"结果数量: {len(results)}")
    print("-" * 60)

    for i, r in enumerate(results, 1):
        print(f"结果 {i}")
        print("标题:", r["title"])
        print("摘要:", r["snippet"])
        print("来源:", r["source"])
        print("-" * 60)