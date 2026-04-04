def normalize_text(text: str) -> str:
    return " ".join(str(text or "").split())


DRIVER_HINTS = [
    "\u9a71\u52a8",
    "\u56e0\u7d20",
    "\u539f\u56e0",
    "\u4e3a\u4ec0\u4e48",
    "\u673a\u5236",
    "\u53d8\u91cf",
    "\u7ea6\u675f",
    "\u63a8\u52a8\u529b\u91cf",
]
CHANGE_HINTS = [
    "\u672a\u6765",
    "\u53d8\u5316",
    "\u6f14\u8fdb",
    "\u63a5\u4e0b\u6765",
    "\u65b9\u5411",
    "\u8d8b\u52bf",
    "\u5b8f\u89c2",
    "\u6e17\u900f",
    "\u90e8\u7f72",
]
RISK_HINTS = [
    "\u98ce\u9669",
    "\u9650\u5236",
    "\u6311\u6218",
    "\u4e89\u8bae",
    "\u6cbb\u7406",
    "\u5b89\u5168",
    "\u5408\u89c4",
]
COMPARISON_HINTS = [
    "\u5dee\u5f02",
    "\u4e0d\u540c",
    "\u6bd4\u8f83",
    "\u5bf9\u6bd4",
    "\u5206\u522b",
    "\u4e2d\u7f8e",
    "\u4f18\u7f3a\u70b9",
    "\u54ea\u4e2a\u66f4",
]
DEFINITION_HINTS = [
    "\u5b9a\u4e49",
    "\u542b\u4e49",
    "\u662f\u4ec0\u4e48",
    "\u57fa\u672c\u6982\u5ff5",
    "\u5de5\u4f5c\u539f\u7406",
    "\u533a\u522b",
]
RECOMMENDATION_HINTS = [
    "\u63a8\u8350",
    "\u6700\u597d",
    "\u9009\u62e9",
    "\u8f6f\u4ef6",
    "\u5de5\u5177",
    "\u503c\u5f97",
    "\u9002\u5408",
]
TIMELINE_HINTS = [
    "\u65f6\u95f4\u7ebf",
    "\u5386\u7a0b",
    "\u91cc\u7a0b\u7891",
    "\u8fc7\u53bb\u51e0\u5e74",
    "\u5173\u952e\u8282\u70b9",
    "\u9636\u6bb5",
]


def contains_any(text: str, hints: list[str]) -> bool:
    normalized = normalize_text(text).lower()
    return any(hint in normalized for hint in hints)


def infer_focus(sub_question: str) -> str:
    normalized = normalize_text(sub_question)

    # Prefer more concrete query intents before broad causal wording.
    if contains_any(normalized, TIMELINE_HINTS):
        return "timeline"
    if contains_any(normalized, RECOMMENDATION_HINTS):
        return "recommendation"
    if contains_any(normalized, COMPARISON_HINTS):
        return "comparison"
    if contains_any(normalized, CHANGE_HINTS):
        return "change"
    if contains_any(normalized, RISK_HINTS):
        return "risk"
    if contains_any(normalized, DRIVER_HINTS):
        return "driver"
    if contains_any(normalized, DEFINITION_HINTS):
        return "definition"
    return "general"


def extract_suggestion_keywords(suggestion: str) -> list[str]:
    normalized = normalize_text(suggestion)
    keywords = []

    if contains_any(normalized, ["\u539f\u56e0", "\u9a71\u52a8", "\u673a\u5236", "\u9700\u6c42\u53d8\u5316"]):
        keywords.extend(
            [
                "\u539f\u56e0",
                "\u9a71\u52a8\u56e0\u7d20",
                "\u4f5c\u7528\u673a\u5236",
                "\u9700\u6c42\u53d8\u5316",
            ]
        )
    if contains_any(normalized, ["\u6280\u672f\u673a\u5236", "\u7ea6\u675f", "\u6fc0\u52b1"]):
        keywords.extend(
            [
                "\u6280\u672f\u673a\u5236",
                "\u7ea6\u675f",
                "\u6fc0\u52b1",
            ]
        )
    if contains_any(normalized, ["\u6848\u4f8b", "\u5bf9\u6bd4\u5206\u6790", "\u8c03\u67e5"]):
        keywords.extend(
            [
                "\u6848\u4f8b",
                "\u5bf9\u6bd4\u5206\u6790",
                "\u8c03\u67e5",
            ]
        )
    if contains_any(normalized, ["\u672a\u6765\u6f14\u8fdb", "\u957f\u671f\u8d8b\u52bf", "\u7ed3\u6784\u8f6c\u5411"]):
        keywords.extend(
            [
                "\u672a\u6765\u6f14\u8fdb",
                "\u957f\u671f\u8d8b\u52bf",
                "\u7ed3\u6784\u8f6c\u5411",
            ]
        )
    if contains_any(normalized, ["\u6cbb\u7406", "\u5b89\u5168", "\u5408\u89c4"]):
        keywords.extend(["\u6cbb\u7406", "\u5b89\u5168", "\u5408\u89c4"])
    if contains_any(normalized, ["\u62a5\u544a", "\u767d\u76ae\u4e66", "\u7814\u7a76"]):
        keywords.extend(["\u62a5\u544a", "\u767d\u76ae\u4e66", "\u7814\u7a76"])

    deduped = []
    for keyword in keywords:
        if keyword not in deduped:
            deduped.append(keyword)
    return deduped[:4]


def assemble_query(sub_question: str, keywords: list[str], max_keywords: int) -> str:
    deduped = []
    for keyword in keywords:
        keyword = normalize_text(keyword)
        if not keyword:
            continue
        if keyword not in deduped:
            deduped.append(keyword)
    limited = deduped[:max_keywords]
    if not limited:
        return sub_question
    return f"{sub_question} {' '.join(limited)}"


def has_employment_signals(text: str) -> bool:
    return contains_any(
        text,
        [
            "\u5c31\u4e1a",
            "\u7a0b\u5e8f\u5458",
            "\u5f00\u53d1\u8005",
            "\u521d\u7ea7",
            "\u5c97\u4f4d",
            "\u62db\u8058",
            "\u85aa\u8d44",
            "\u52b3\u52a8\u529b",
            "\u52b3\u52a8\u5e02\u573a",
            "\u4e2d\u7f8e",
            "entry-level",
            "developer",
        ],
    )


def has_agent_signals(text: str) -> bool:
    return contains_any(
        text,
        [
            "agent",
            "agents",
            "ai agent",
            "AI Agent",
            "\u667a\u80fd\u4f53",
            "\u4ee3\u7406",
            "\u6570\u5b57\u5458\u5de5",
            "workflow",
        ],
    )


def has_macro_signals(text: str) -> bool:
    return contains_any(
        text,
        [
            "\u5b8f\u89c2",
            "\u5404\u884c\u5404\u4e1a",
            "\u884c\u4e1a",
            "\u8de8\u884c\u4e1a",
            "\u5c31\u4e1a\u7ed3\u6784",
            "\u52b3\u52a8\u529b\u5e02\u573a",
            "\u6e17\u900f",
            "\u90e8\u7f72",
            "\u5e94\u7528\u6a21\u5f0f",
            "\u8d8b\u52bf",
        ],
    )


def has_enterprise_agent_signals(text: str) -> bool:
    return contains_any(
        text,
        [
            "\u4f01\u4e1a",
            "\u90e8\u7f72",
            "\u4e1a\u52a1\u6d41\u7a0b",
            "\u5de5\u4f5c\u6d41",
            "\u7ec4\u7ec7\u96c6\u6210",
            "enterprise",
            "workflow",
            "business process",
        ],
    ) and contains_any(text, ["agent", "ai agent", "AI Agent", "\u667a\u80fd\u4f53"])


def has_battery_signals(text: str) -> bool:
    return contains_any(
        text,
        [
            "\u56fa\u6001\u7535\u6c60",
            "\u5168\u56fa\u6001",
            "\u7535\u89e3\u8d28",
            "\u91cf\u4ea7",
            "\u4e2d\u8bd5\u7ebf",
            "\u5546\u4e1a\u5316",
            "solid-state battery",
        ],
    )


def has_china_us_signals(text: str) -> bool:
    return contains_any(
        text,
        [
            "\u4e2d\u56fd",
            "\u7f8e\u56fd",
            "\u4e2d\u7f8e",
            "china",
            "us",
            "u.s.",
            "united states",
        ],
    )


def rewrite_driver_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = [
        "\u539f\u56e0",
        "\u9a71\u52a8\u56e0\u7d20",
        "\u4f5c\u7528\u673a\u5236",
        "\u7ea6\u675f",
        "ROI",
        "adoption",
    ]
    if round_num >= 2:
        base_keywords.extend(
            [
                "\u7814\u7a76\u62a5\u544a",
                "benchmark",
                "case study",
            ]
        )
    if round_num >= 3:
        base_keywords.extend(
            [
                "\u6df1\u5ea6\u5206\u6790",
                "\u6848\u4f8b",
            ]
        )

    if has_employment_signals(sub_question):
        base_keywords.extend(
            [
                "\u5c31\u4e1a",
                "\u52b3\u52a8\u5e02\u573a",
                "\u5c97\u4f4d\u7ed3\u6784",
                "\u62db\u8058\u9700\u6c42",
                "entry-level developer",
                "software engineer labor market",
                "China US comparison",
                "\u6280\u80fd\u95e8\u69db",
                "\u4eba\u529b\u6210\u672c",
            ]
        )

    if has_enterprise_agent_signals(sub_question):
        base_keywords.extend(
            [
                "\u4f01\u4e1a adoption",
                "\u4f01\u4e1a\u90e8\u7f72",
                "\u5de5\u4f5c\u6d41\u96c6\u6210",
                "\u6d41\u7a0b\u91cd\u6784",
                "\u6cbb\u7406",
                "\u96c6\u6210\u6210\u672c",
                "\u4f01\u4e1a ROI",
                "\u4e1a\u52a1\u4ef7\u503c",
                "enterprise adoption drivers",
                "workflow integration",
                "business process",
            ]
        )

    if has_battery_signals(sub_question):
        base_keywords.extend(
            [
                "\u56fa\u6001\u7535\u6c60 \u5546\u4e1a\u5316",
                "\u4ea7\u4e1a\u5316\u74f6\u9888",
                "\u4e2d\u8bd5\u7ebf",
                "\u91cf\u4ea7\u8282\u70b9",
                "\u6574\u8f66\u5382",
                "\u4f9b\u5e94\u94fe",
                "\u6210\u672c\u66f2\u7ebf",
                "\u754c\u9762\u7a33\u5b9a",
                "\u5236\u9020\u826f\u7387",
                "\u53ef\u5236\u9020\u6027",
                "\u653f\u7b56\u652f\u6301",
                "\u786b\u5316\u7269 \u6c27\u5316\u7269",
                "pilot line",
                "automaker",
                "scaling bottleneck",
                "manufacturing yield",
                "cost curve",
            ]
        )

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=12)


def rewrite_change_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = [
        "\u672a\u6765\u6f14\u8fdb",
        "\u53d8\u5316\u65b9\u5411",
        "\u957f\u671f\u8d8b\u52bf",
        "\u7ed3\u6784\u8f6c\u5411",
    ]

    if has_employment_signals(sub_question):
        base_keywords.extend([
            "\u7814\u7a76\u62a5\u544a",
            "\u5c31\u4e1a\u7ed3\u6784",
            "\u52b3\u52a8\u529b\u5e02\u573a",
            "\u62db\u8058\u8d8b\u52bf",
            "future of work",
        ])

    if has_macro_signals(sub_question):
        base_keywords.extend([
            "\u7814\u7a76\u62a5\u544a",
            "\u5b8f\u89c2\u5206\u6790",
            "\u8de8\u884c\u4e1a",
            "\u4f01\u4e1a\u91c7\u7eb3",
        ])

    if has_agent_signals(sub_question):
        base_keywords.extend([
            "AI agent adoption",
            "agent deployment",
            "workflow automation",
        ])

    if has_enterprise_agent_signals(sub_question):
        base_keywords.extend([
            "ROI",
            "benchmark",
            "enterprise rollout",
        ])

    if round_num >= 2:
        base_keywords.extend(["\u9884\u6d4b", "\u5206\u6790", "outlook", "survey", "industry report"])
    if round_num >= 3:
        base_keywords.extend([
            "\u6848\u4f8b",
            "\u89e3\u91ca",
            "\u539f\u56e0",
            "\u9a71\u52a8\u56e0\u7d20",
            "adoption barrier",
            "structural shift",
        ])

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=11)


def rewrite_risk_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = [
        "\u98ce\u9669",
        "\u9650\u5236",
        "\u6311\u6218",
        "\u6cbb\u7406",
        "\u5b89\u5168",
        "\u5408\u89c4",
        "\u53ef\u9760\u6027",
    ]
    if round_num >= 2:
        base_keywords.extend(
            [
                "\u8d23\u4efb\u8fb9\u754c",
                "\u96c6\u6210\u6210\u672c",
                "\u6848\u4f8b",
            ]
        )
    if round_num >= 3:
        base_keywords.extend(["\u7814\u7a76", "\u767d\u76ae\u4e66", "\u5206\u6790"])

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=8)


def rewrite_comparison_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = [
        "\u5dee\u5f02",
        "\u5bf9\u6bd4",
        "\u539f\u56e0",
        "\u7ea6\u675f",
        "\u7ed3\u6784\u6027\u5dee\u5f02",
        "\u673a\u5236",
        "\u6848\u4f8b",
        "\u7ef4\u5ea6\u5bf9\u6bd4",
        "\u7ed3\u6784\u6027\u5dee\u5f02",
    ]
    if round_num >= 2:
        base_keywords.extend(
            [
                "\u6bd4\u8f83\u5206\u6790",
                "\u8de8\u56fd\u6bd4\u8f83",
                "\u673a\u5236\u89e3\u91ca",
                "\u5236\u5ea6\u73af\u5883",
                "\u5e02\u573a\u7ed3\u6784",
            ]
        )
    if round_num >= 3:
        base_keywords.extend(
            [
                "\u7814\u7a76",
                "\u62a5\u544a",
                "\u8bc1\u636e",
                "\u6570\u636e\u5bf9\u6bd4",
                "\u8de8\u56fd\u6bd4\u8f83",
            ]
        )

    if has_employment_signals(sub_question):
        base_keywords.extend(
            [
                "\u5c31\u4e1a",
                "\u52b3\u52a8\u5e02\u573a",
                "\u5c97\u4f4d\u7ed3\u6784",
                "\u62db\u8058\u9700\u6c42",
                "\u4e2d\u56fd \u7f8e\u56fd",
                "entry-level engineer",
                "\u57f9\u8bad\u6210\u672c",
                "\u4ea7\u4e1a\u7ed3\u6784",
            ]
        )

    if has_china_us_signals(sub_question):
        base_keywords.extend(
            [
                "\u4e2d\u7f8e\u5e02\u573a",
                "\u5546\u4e1a\u5316\u8def\u5f84",
                "\u7528\u6237\u9700\u6c42",
                "\u7ade\u4e89\u683c\u5c40",
            ]
        )

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=10)


def rewrite_definition_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = ["\u5b9a\u4e49", "\u6982\u5ff5\u89e3\u91ca", "\u5de5\u4f5c\u539f\u7406", "\u533a\u522b"]
    if round_num >= 2:
        base_keywords.extend(["\u57fa\u7840\u4ecb\u7ecd", "\u56fe\u89e3", "\u6559\u7a0b"])
    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=7)


def rewrite_recommendation_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = [
        "\u63a8\u8350",
        "\u5bf9\u6bd4",
        "\u8bc4\u6d4b",
        "\u4f18\u7f3a\u70b9",
        "\u9002\u7528\u4eba\u7fa4",
    ]
    if round_num >= 2:
        base_keywords.extend(
            [
                "\u9884\u7b97",
                "\u4f7f\u7528\u573a\u666f",
                "\u9009\u62e9\u6807\u51c6",
            ]
        )
    if round_num >= 3:
        base_keywords.extend(["\u6df1\u5ea6\u6d4b\u8bc4", "\u6848\u4f8b"])

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=9)


def rewrite_timeline_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = [
        "\u65f6\u95f4\u7ebf",
        "\u91cc\u7a0b\u7891",
        "\u5173\u952e\u8282\u70b9",
        "\u9636\u6bb5",
        "\u6848\u4f8b",
        "\u8f6c\u6298\u70b9",
    ]
    if round_num >= 2:
        base_keywords.extend(
            [
                "\u63a8\u52a8\u56e0\u7d20",
                "\u6f14\u8fdb",
                "\u5546\u4e1a\u5316",
                "\u4ea7\u4e1a\u5316",
                "\u7814\u7a76\u62a5\u544a",
            ]
        )
    if round_num >= 3:
        base_keywords.extend(
            [
                "\u672a\u6765\u65b9\u5411",
                "\u957f\u671f\u8d8b\u52bf",
                "\u4e2d\u8bd5\u7ebf",
                "\u4f9b\u5e94\u94fe",
            ]
        )

    if has_battery_signals(sub_question):
        base_keywords.extend(
            [
                "\u56fa\u6001\u7535\u6c60",
                "\u6750\u6599\u8def\u7ebf",
                "\u7535\u89e3\u8d28",
                "\u6574\u8f66\u5382",
                "\u4e2d\u8bd5\u7ebf",
                "\u4ea7\u4e1a\u91cc\u7a0b\u7891",
            ]
        )

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=10)


def rewrite_general_query(sub_question: str, round_num: int, suggestion: str) -> str:
    base_keywords = ["\u80cc\u666f", "\u5206\u6790", "\u6848\u4f8b"]
    if round_num >= 2:
        base_keywords.extend(["\u5bf9\u6bd4", "\u89e3\u91ca"])
    if round_num >= 3:
        base_keywords.extend(["\u7814\u7a76", "\u62a5\u544a"])

    base_keywords.extend(extract_suggestion_keywords(suggestion))
    return assemble_query(sub_question, base_keywords, max_keywords=7)


def rewrite_query(sub_question: str, reflection: dict, round_num: int) -> str:
    if reflection.get("status") == "enough":
        return sub_question

    suggestion = normalize_text(reflection.get("suggestion", ""))
    focus = infer_focus(sub_question)

    if focus == "driver":
        return rewrite_driver_query(sub_question, round_num, suggestion)
    if focus == "change":
        return rewrite_change_query(sub_question, round_num, suggestion)
    if focus == "risk":
        return rewrite_risk_query(sub_question, round_num, suggestion)
    if focus == "comparison":
        return rewrite_comparison_query(sub_question, round_num, suggestion)
    if focus == "recommendation":
        return rewrite_recommendation_query(sub_question, round_num, suggestion)
    if focus == "timeline":
        return rewrite_timeline_query(sub_question, round_num, suggestion)
    if focus == "definition":
        return rewrite_definition_query(sub_question, round_num, suggestion)
    return rewrite_general_query(sub_question, round_num, suggestion)





