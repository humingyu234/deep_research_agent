from agent.planner import plan_subquestions
from agent.reflector import reflect
from agent.reporter import generate_report
from agent.rewriter import rewrite_query
from agent.search import search
from agent.selector import select_top_results
from agent.state import ResearchState
from agent.summarizer import summarize


MAX_ROUNDS = 3
TOP_K_RESULTS = 3


def main():
    """
    项目主入口。

    整体流程可以理解为：
    大问题 -> 拆题 -> 搜索 -> 筛选 -> 反思 -> 改写 -> 总结 -> 总报告
    """
    query = input("\n>>> 请输入你的研究问题：").strip()
    state = ResearchState(query=query)

    state = plan_subquestions(state)

    print("\n[拆解出的子问题]")
    for index, sub_question in enumerate(state.sub_questions, 1):
        print(f"{index}. {sub_question}")

    print("\n[开始搜索、筛选、反思、改写与总结]")
    for sub_question in state.sub_questions:
        round_num = 1
        current_query = sub_question
        all_results = []
        reflection = {
            "status": "insufficient",
            "reason": "尚未完成搜索。",
            "suggestion": "",
        }

        while round_num <= MAX_ROUNDS:
            results = search(current_query, round_num)
            all_results.extend(results)

            # Selector 在这里像“资料编辑台”。
            # 它先把脏结果、重复转述、营销稿压掉，
            # 再挑出最值得进入总结阶段的少数结果。
            selected_results = select_top_results(sub_question, all_results, top_k=TOP_K_RESULTS)
            reflection = reflect(sub_question, selected_results)

            print(f"\n原始问题：{sub_question}")
            print(f"当前搜索 query：{current_query}")
            print(f"第 {round_num} 轮搜索结果：")
            for index, item in enumerate(results, 1):
                print(f"  {index}. 标题：{item['title']}")
                print(f"     摘要：{item['snippet']}")
                print(f"     来源：{item['source']}")

            print("\n筛选后保留的结果：")
            for index, item in enumerate(selected_results, 1):
                print(f"  {index}. 标题：{item['title']}")
                print(f"     摘要：{item['snippet']}")
                print(f"     来源：{item['source']}")

            print(f"判断状态：{reflection['status']}")
            print(f"原因：{reflection['reason']}")

            if reflection["status"] == "enough":
                break

            print(f"改写建议：{reflection['suggestion']}")
            current_query = rewrite_query(sub_question, reflection, round_num)
            print("信息不足，准备使用新 query 进行下一轮搜索...\n")

            round_num += 1

        if round_num > MAX_ROUNDS and reflection["status"] != "enough":
            print(f"\n[提示] 子问题《{sub_question}》已达到最大搜索轮数，停止继续搜索。")

        final_selected_results = select_top_results(sub_question, all_results, top_k=TOP_K_RESULTS)
        state.search_results[sub_question] = final_selected_results

        summary = summarize(sub_question, final_selected_results)
        state.summaries[sub_question] = summary

        print(f"总结：\n{summary}")

    report = generate_report(state.query, state.summaries)

    print("\n[最终研究报告]")
    print(report)
    print("\n[流程结束]")


if __name__ == "__main__":
    main()
