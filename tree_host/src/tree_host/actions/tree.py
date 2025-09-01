from tree_host.domain import tree_builder


async def load_index():
    return tree_builder.build_tree_html()


# async def update_tree(jsonl: dict):
#     return html.create_hall_page(jsonl)
