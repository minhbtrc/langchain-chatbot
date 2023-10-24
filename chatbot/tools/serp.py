from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.utilities import SerpAPIWrapper


class CustomSearchTool(BaseTool):
    name = "Custom search"
    description = "Useful for when you need to answer questions about current or newest events, date, ..."
    _search = SerpAPIWrapper(params={
        "engine": "google",
        "gl": "us",
        "hl": "vi",
    })

    def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return self._search.run(query)
