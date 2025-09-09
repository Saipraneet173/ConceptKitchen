from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def generate_restaurant_name_items(cuisine):
    """
    Generates restaurant name and menu items using LCEL pipeline.
    Uses modern Langchain Expression Language instead of depreciated chains.
    """
    name_prompt = PromptTemplate(
        input_variables = ['cuisine'],
        template = """I want to open a restaurant for {cuisine} food. 
        Suggest a fancy, unique name for this restaurant. 
        Only provide the name, nothing else. 
        No preamble"""
    )

    menu_prompt = PromptTemplate(
        input_variables = ['restaurant_name'],
        template = """For a restaurant called '{restaurant_name}', suggest 7 menu items.
        Make them sound authentic and appetizing.
        Return them in this EXACT format with commas between items:
        Dish One Name, Dish Two Name, Dish Three Name, Dish Four Name, Dish Five Name, Dish Six Name, Dish Seven Name
        NO NUMBERS, NO LINE BREAKS, NO PREAMBLE, ONLY COMMA-SEPARATED.
        """
    )

    name_chain = name_prompt | llm | StrOutputParser()
    menu_chain = menu_prompt | llm | StrOutputParser()

    restaurant_name = name_chain.invoke({"cuisine": cuisine})
    menu_items = menu_chain.invoke({"restaurant_name": restaurant_name.strip()})

    import re
    menu_items = re.sub(r'\d+\.\s*', '', menu_items)

    return{
        'restaurant_name': restaurant_name.strip(),
        'menu_items': menu_items.strip()
    }

def generate_restaurant_name_items_parallel(cuisine):
    """ Advanced version: Generates name, tagline and menu items in parallel"""
    name_chain = (
        PromptTemplate.from_template(
            "Create a unique {cuisine} restaurant name. No preamble. Only the name:"
        )
        | llm
        | StrOutputParser()
    )

    restaurant_name = name_chain.invoke({"cuisine": cuisine})

    tagline_chain = (
            PromptTemplate.from_template(
                "Create a catchy tagline for '{name}' restaurant. No preamble. Only the tagline:"
            )
            | llm
            | StrOutputParser()
    )

    menu_chain = (
            PromptTemplate.from_template(
                """List 7 menu items for '{name}' restaurant. 
                Format: Dish One, Dish Two, Dish Three, Dish Four, Dish Five, Dish Six, Dish Seven.
                use COMMAS only. NO preamble. NO numbers, NO line breaks."""
            )
            | llm
            | StrOutputParser()
    )

    parallel_chain = RunnableParallel(
        tagline = tagline_chain,
        menu_items= menu_chain
    )

    results = parallel_chain.invoke({"name": restaurant_name})

    import re
    menu_items = re.sub(r'\d+\.\s*', '', results['menu_items'])

    return {
        'restaurant_name': restaurant_name.strip(),
        'tagline': results['tagline'].strip(),
        'menu_items': results['menu_items'].strip()
    }


if __name__ == "__main__":
    # Test the updated function
    print("Testing basic generation...")
    result = generate_restaurant_name_items("Korean")
    print(f"Restaurant: {result['restaurant_name']}")
    print(f"Menu: {result['menu_items']}")

    print("\n" + "=" * 50 + "\n")

    print("Testing parallel generation...")
    result = generate_restaurant_name_items_parallel("Italian")
    print(f"Restaurant: {result['restaurant_name']}")
    print(f"Tagline: {result.get('tagline', 'N/A')}")
    print(f"Menu: {result['menu_items']}")