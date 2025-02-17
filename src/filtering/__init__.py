def apply_filter_to(content_summaries):
    content_grouped = {
        "GENERAL": [],
        "POLITIC": [],
        "CULTURE": [],
        "SCIENT": [],
        "SPORTS": [],
        "WEATHER": []
    }

    for summary in content_summaries:
        category = summary.category
        if category and category in content_grouped:
            content_grouped[category].append(summary.content)
        elif not category:
            print("Summary without category found and ignored")
        else:
            print(f"Summary with unknown category: {category}")


    # if len(content_summaries['SCIENT']) > 2:
    #     grouped_summaries['SCIENT'] = [grouped_summaries['SCIENT'][0], grouped_summaries['SCIENT'][1]]
    #
    # if len(grouped_summaries['SPORTS']) > 2:
    #     grouped_summaries['SPORTS'] = [grouped_summaries['SPORTS'][0], grouped_summaries['SPORTS'][1]]
    #
    # if len(grouped_summaries['SPORTS']) > 1:
    #     grouped_summaries['WEATHER'] = [grouped_summaries['WEATHER'][0]]

    return content_grouped