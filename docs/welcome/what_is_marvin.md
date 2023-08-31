<<<<<<< Updated upstream
# Hello, Marvin!
=======
<style>
    .admonition,details{margin-top:0px;padding:0px!important}
    .admonition-title,summary{margin:0px!important;margin-bottom:0px!important}
    .admonition > p:first-of-type{margin:0px!important;margin-bottom:0px!important}
    .tabbed-set{margin-top:0px!important}
    .tabbed-content{padding-left:1.25em; padding-right:1.25em}
</style>

# Marvin

## What is Marvin?

Marvin is a library that lets you use Large Language Models (LLMs) without writing prompts.

??? question "Explain like I'm five."

    === "I'm not technical."

        Marvin lets your software speak English and ask questions to ChatGPT. No prompts required.

        It turns out that ChatGPT and other *Large Language Models* are good at performing boring
        but incredibly valuable business-critical tasks beyond being a chatbot: you can use them to
        classify emails as spam, extract key figures from a report, etc. When you use something like ChatGPT 
        you spend a lot of time crafting the right *prompt* or *context* to get it to write your email, 
        plan your date night, etc. 
     
        If you want your software to use ChatGPT, you need to let it turn its objective into English. 
        Marvin handles this 'translation' for you, so you get to just write code like you normally would. Engineers 
        like using Marvin because it lets them write software like they're used to.
        
        Simply put, it lets you use Generative AI without feeling like you have to learn a framework.
        

    === "I'm mildly technical."

        Marvin lets your software speak English and ask questions to LLMs.

        It introspects the types and docstrings of your functions and data models, and lets you cast them
        to prompts automatically to pass to a Large Language Model. This lets you write code as you normally would
        instead of writing prompts, and we handle the translation back and forth for you. 

        This lets you focus on what you've always focused on: writing clean, versioned, reusable *code* and *data models*, 
        and not scrutinizing whether you begged your LLM hard enough to output JSON. 

        Extracting, generating, cleaning, or classifying data is as simple as writing a function or a data model.

Marvin gives you all the building blocks to build durable, custom, production-ready LLM applications. We remix those building blocks
together to expose a few batteries-included components that let you use LLMs to accomplish classical tasks. 

!!! abstract "What you can do with Marvin."

    === "AI Function"

        AI Functions let you write complex business logic and transformations, or generate synthetic data.

        ??? info "Installation Instructions"
            asfa

        ``` python
        from marvin import ai_fn

        @ai_fn
        def generate_fruits(n: int, color: str = 'red') -> list[str]:
            '''Generates a list of `n` fruits of color `color`'''

        generate_fruits(3) 
        # Returns ['strawberry', 'apple', 'cherry']

        ```

    === "🧩 AI Model"

        AI Models let you structure text into type-safe schemas.

        ??? info "Installation Instructions"
            asfa

        ``` python
        from marvin import ai_model
        from pydantic import BaseModel

        @ai_model
        class Location(BaseModel):
            city: str 
            state: str

        Location("He said he's from the big Apple") 
        # Returns Location(city = "New York", state = "New York")

        ```

    === "🏷️ AI Classifier"

        AI Models let you structure text into type-safe schemas.

        ??? info "Installation Instructions"
            asfa

        ``` python
        from marvin import ai_classifier
        from enum import Enum


        @ai_classifier
        class CustomerIntent(Enum):
            """Classifies the incoming users intent"""

            SALES = 1
            TECHNICAL_SUPPORT = 2
            BILLING_ACCOUNTS = 3
            PRODUCT_INFORMATION = 4
            RETURNS_REFUNDS = 5
            ORDER_STATUS = 6
            ACCOUNT_CANCELLATION = 7
            OPERATOR_CUSTOMER_SERVICE = 0


        CustomerIntent("I got double charged, can you help me out?") 
        # Returns <CustomerIntent.BILLING_ACCOUNTS: 3>
        ```


    === "AI Application"

        AI Applications are conversational interface to a stateful, AI-powered application that can use tools.

        ??? info "Installation Instructions"
            asfa

        ```python
        from datetime import datetime
        from pydantic import BaseModel
        from marvin import AIApplication


        class ToDo(BaseModel):
            title: str
            description: str
            due_date: datetime = None
            done: bool = False


        class ToDoState(BaseModel):
            todos: list[ToDo] = []


        todo_app = AIApplication(
            state=ToDoState(),
            description=(
                "A simple to-do tracker. Users will give instructions to add, remove, and"
                " update their to-dos."
            ),
        )

        response = todo_app("I need to go to the grocery store tomorrow")
        
        print(response.content) 
        # I've added your task to go to the grocery store tomorrow to your to-do list.

        print(todo_app.state)
        # todos=[ToDo(title='Go to the grocery store', description='Need to go to the grocery store', due_date=datetime.datetime(2023, 7, 19, 0, 0, tzinfo=datetime.timezone.utc), done=False)]
        ```


<!-- # Hello, Marvin!
![](../img/heroes/it_hates_me_hero.png)
>>>>>>> Stashed changes

```python
from marvin import ai_fn

@ai_fn
def quote_marvin(topic: str) -> str:
    """Quote Marvin the robot from Hitchhiker's Guide on a topic"""

quote_marvin(topic="humans") # "I've seen it. It's rubbish."
```

Marvin is a lightweight AI engineering framework for building natural language interfaces that are reliable, scalable, and easy to trust.

Sometimes the most challenging part of working with generative AI is remembering that it's not magic; it's software. It's new, it's nondeterministic, and it's incredibly powerful - but still software.

Marvin's goal is to bring the best practices for building dependable, observable software to generative AI. As the team behind [Prefect](https://github.com/prefecthq/prefect), which does something very similar for data engineers, we've poured years of open-source developer tool experience and lessons into Marvin's design.

## Core Components

🧩 [**AI Models**](/components/ai_model) for structuring text into type-safe schemas

🏷️ [**AI Classifiers**](/components/ai_classifier) for bulletproof classification and routing

🪄 [**AI Functions**](/components/ai_function) for complex business logic and transformations

🤝 [**AI Applications**](/components/ai_application) for interactive use and persistent state

## Ambient AI

With Marvin, we’re taking the first steps on a journey to deliver [Ambient AI](https://twitter.com/DrJimFan/status/1657782710344249344): omnipresent but unobtrusive autonomous routines that act as persistent translators for noisy, real-world data. Ambient AI makes unstructured data universally accessible to traditional software, allowing the entire software stack to embrace AI technology without interrupting the development workflow. Marvin brings simplicity and stability to AI engineering through abstractions that are reliable and easy to trust.

<<<<<<< Updated upstream
Interested? [Join our community](../../community)!
=======
## What Makes Marvin Different?

There's no shortage of tools and libraries out there for integrating LLMs into your software. So what makes Marvin different? In addition to a relentless focus on incrementally-adoptable, familiar abstractions, Marvin embraces five pillars:

1. **User-Centric Design:** We built Marvin with you in mind. It's not just about what it does, but how it does it. Marvin is designed to be as user-friendly as possible, with a focus on an easy, intuitive experience. Whether you're a coding expert or just starting, Marvin works for you.

1. **Flexibility:** Marvin is built to adapt to your needs, not the other way around. You can use as much or as little of Marvin as you need. Need a full suite of LLM integration tools? We've got you covered. Just need a component or two for a quick project? Marvin can do that too.

1. **Community Driven:** Marvin isn't just a tool, it's a community. We value feedback and collaboration from users like you. We're always learning, iterating, and improving based on what our community tells us.

1. **Velocity:** We believe that getting started should be quick and easy. That's why with Marvin, you can get up and running in no time. Marvin is not here to do everything for you, it's here to eliminate the the most cumbersome parts of working with AI in order to accelerate your ability to take advantage of it.

1. **Open-Source:** Marvin is fully open-source, which means it's not only free to use, but you're also free to modify and adapt as you see fit. The [Prefect](https://www.prefect.io) team has years of open-source experience and is fully committed to supporting Marvin as an open-source product. We believe in the power of collective intelligence, and we're excited to see what you can create. 

Marvin's 1.0 release reflects our confidence that its core abstractions are locked-in. And why wouldn't they be? They're the same interfaces you use every day: Python functions, classes, enums, and Pydantic models. Our next objectives are leveraging these primitives to build production deployment patterns and an observability platform.


If our mission is exciting to you and you’d like to build Marvin with us, [join our community](../../community)! -->
>>>>>>> Stashed changes
