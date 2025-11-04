from langgraph.graph import StateGraph, START, END

import pydantic
from typing import Dict

class State(pydantic.BaseModel):
    request: str
    response: str = ""

graph = StateGraph(State)

def say_hi(state: State)->State:
    state.response = state.request + "   hello!"
    return state


graph.add_node(say_hi)
graph.add_edge(START, "say_hi")
graph.add_edge("say_hi",END)

def get_lg_greeter()->StateGraph:
    return graph



if __name__ == "__main__":

    request = State(request="Azahar")
    print(graph.compile().invoke(request))


