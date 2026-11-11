import uuid
from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Literal, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import Message, add_message
from langgraph.checkpoint.memory import InMemeorySaver
from langchain.chat_models import init_chat_model

load_dotenv()

llm  = init_chat_model('openai:gpt-4.1-mini')

class Intent(BaseModel):
    msg_intent: Literal["chat", "code", "gyan"] = Field(..., description="The intent of the message, can be 'chat', 'code', or 'gyan'.")

class State(TypedDict):
    msg: Annotated[list, add_message]
    msg_intent: str | None


def classify_msg(state: State):
    str_llm = llm.with_structured_output(Intent)
    result = str_llm.invoke([
        {"role": "system", "content": "You are a helpful assistant that classifies the intent of messages. classify the intent of the message as either 'chat', 'code', or 'gyan'."},
        {"role": "user", "content": state["msg"][-1]["content"]}
    ])
    return {"msg_intent": result.msg_intent}

def create_code_agent(state: State):
    '''coding agent'''
    lang_resp = llm.invoke([
        {"role": 'system', 'content': "I'm a coding agent i dont do any other tasks except codeing"}
    ] + state['msg'])

    return {'role': 'assistant', 'content': lang_resp.content}

def create_rag_agent(state: State):
    '''rag agent'''
    lang_resp = llm.invoke([
        {"role": 'system', 'content': "I'm a rag agent i dont do any other tasks except fetching relevent knowledge from knowledge source"}
    ] + state['msg'])

    return {'role': 'assistant', 'content': lang_resp.content}

def create_gyan_agent(state: State):
    '''gyan agent'''
    lang_resp = llm.invoke([
        {"role": 'system', 'content': "I'm a gyan agent i dont do any other tasks except giving general knowedge like chatting"}
    ] + state['msg'])

    return {'role': 'assistant', 'content': lang_resp.content}


wf = StateGraph(State)

wf.add_node('classifier', classify_msg)
wf.add_node('codeing', create_code_agent)
wf.add_node('chatting', create_gyan_agent)
wf.add_node('rag', create_rag_agent)

wf.add_edge(START, 'classifier')
wf.add_conditional_edge('classifier', lambda state: state["msg_intent"] , {
    "code": "codeing",
    "chat": "chatting",
    "gyan": "gyan"
})

wf.add_edge('codeing', END)
wf.add_edge('chatting', END)
wf.add_edge('rag', END)

checkpointer = InMemeorySaver()
graph = wf.compile(checkpointer=checkpointer)
config = {'configurable': {'thread_id': str(uuid.uuid4())}}

while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break

    initial_state = {
        "msg": [{"role": "user", "content": user_input}],
        "msg_intent": None
    }

    final_state = graph.run(initial_state, config=config)
    assistant_response = final_state["msg"][-1]["content"]
    print(f"Assistant: {assistant_response}")