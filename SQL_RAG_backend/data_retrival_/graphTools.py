from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
import re
import io
import base64
import matplotlib.pyplot as plt

class GraphGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["sqlAnswer"],
            template=("""
You are a data-visualization assistant.

Input is natural-language SQL agent output. Extract label–value pairs and generate Python code to visualize them.

TASKS
1) Parse text → extract names + numeric values
2) Normalize numbers (remove $, %, commas → float)
3) Identify meaningful relationships
4) Output Python plotting code

EXTRACT
- names / categories / labels
- numeric amounts / totals / sales / values
Ignore rankings (1., 2., 3.) and commentary.

If no numeric values → reply:
"No meaningful numeric relationship detected."

VISUALIZATION
You may use:
- matplotlib
- seaborn
- subplots (when useful)

Choose chart type by data meaning:
- categorical vs numeric → bar
- rankings → horizontal bar
- proportions → pie / donut
- trends → line
- distributions → hist / kde
- correlation → scatter

Prefer seaborn when clearer. Avoid redundant charts.

STYLE
- import seaborn as sns
- include title, axis labels, legend (if needed)

OUTPUT FORMAT
Return ONLY Python code containing a title:

```python
labels = [...]
values = [...]

import matplotlib.pyplot as plt
import seaborn as sns

# plotting code here
plt.show()

INPUT
{{ sqlAnswer }}
"""
            ),
            template_format="jinja2"
        )

    def generate_graph(self, sqlAnswer: str) -> str:
        prompt = self.prompt_template.format(
            sqlAnswer=sqlAnswer
        )

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}" 
        
        
    def generate_plot_base64(self, graphtext: str) -> str:
        code = re.search(r"```python(.*?)```", graphtext, re.S)

        if not code:
            return None

        code=code.group(1).replace("plt.show","").strip()

        # run chart code in isolated namespace
        exec_namespace = {"plt": plt}
        exec(code, exec_namespace)

        fig = plt.gcf()


        # Render image to memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
        plt.close(fig)
        buf.seek(0)

        # Encode as Base64 string
        return base64.b64encode(buf.read()).decode("utf-8")


class GraphExplainer:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["sqlAnswer"],
            template=("""
You are a data analysis assistant.

You will receive:
- a visualization title
- a short reason describing its purpose
- labels and numeric values that would be plotted in the chart

Your job is to analyze the relationship and return:

1) Description - What does the graph represents
2) Importance — why this relationship matters in a business/analytical context
3) Trend — what pattern is observed in the values (growth, decline, concentration, outliers, ranking behavior, etc.)
4) Insight Style — concise, factual, no speculation, no visualization code

Do NOT rewrite the data. Do NOT generate charts.

INPUT:
{{graph_summary_text}}

OUTPUT FORMAT:

Title:
<adequate title>

Importance:
<short explanation>

Trend Observed:
<short pattern description>
"""
            ),
            template_format="jinja2"
        )

    def generate_explanation(self, explainText: str) -> str:
        prompt = self.prompt_template.format(
            graph_summary_text=explainText
        )

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}" 
        
    def strip_plotting_lines(self, text: str) -> str:
        cleaned_lines = []

        for line in text.splitlines():
            stripped = line.strip()

            # skip plotting-related lines
            if stripped.startswith("import ") \
            or stripped.startswith("plt") \
            or stripped.startswith("sns"):
                continue

            if not stripped:
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()
