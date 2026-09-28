<!-- ## 🧠 LangGraph Multi-Agent Flow

```mermaid
graph TD
    __start__ --> supervisor_node

    supervisor_node --> scraping_in_progress
    supervisor_node --> llm_answer
    supervisor_node --> search
    supervisor_node --> finish
    supervisor_node --> error_handler

    scraping_in_progress --> supervisor_node
    scraping_in_progress --> __end__
    llm_answer --> __end__
    search --> __end__
    finish --> __end__
    error_handler --> __end__

    finish -. FINISH .-> __end__
    error_handler -. error .-> __end__
``` -->
