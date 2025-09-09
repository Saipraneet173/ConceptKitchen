import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnableParallel
from dotenv import load_dotenv

load_dotenv()


class RestaurantConceptGenerator:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.json_parser = JsonOutputParser()

    def generate_complete_concept(self, cuisine, style="Casual Dining", price_range="$$"):
        """Generate a comprehensive restaurant concept with all business details."""

        concept_prompt = PromptTemplate(
            input_variables=['cuisine', 'style', 'price_range'],
            template="""Create a unique and compelling restaurant concept.

            Cuisine: {cuisine}
            Style: {style}
            Price Range: {price_range} ($ = budget, $$ = moderate, $$$ = upscale, $$$$ = luxury)

            Return a JSON object with EXACTLY this structure:
            {{
                "name": "Creative restaurant name",
                "tagline": "Memorable tagline that captures the essence",
                "concept": "2-3 sentence description of the restaurant's unique concept and atmosphere",
                "unique_selling_points": [
                    "First unique aspect",
                    "Second unique aspect", 
                    "Third unique aspect"
                ],
                "ambiance": "Detailed description of interior design, lighting, music, and overall vibe",
                "target_audience": "Description of ideal customers",
                "signature_dish": "Name and brief description of the restaurant's most famous dish"
            }}

            Be creative, specific, and ensure all content is relevant to {cuisine} cuisine.
            Return ONLY valid JSON, no additional text."""
        )

        concept_chain = concept_prompt | self.llm | self.json_parser
        concept = concept_chain.invoke({
            "cuisine": cuisine,
            "style": style,
            "price_range": price_range
        })

        return concept

    def generate_detailed_menu(self, restaurant_name, cuisine, concept, price_range):
        """Generate a detailed menu with prices and descriptions."""

        # Price multipliers based on range
        price_multipliers = {
            "$": 1,
            "$$": 2,
            "$$$": 3.5,
            "$$$$": 5
        }
        multiplier = price_multipliers.get(price_range, 2)
        base = int(8 * multiplier)

        # Create the menu prompt with properly formatted price ranges
        menu_prompt = PromptTemplate(
            input_variables=['name', 'cuisine', 'concept',
                             'app_min', 'app_max', 'main_min', 'main_max',
                             'dessert_min', 'dessert_max'],
            template="""Create a detailed menu for this restaurant:

            Restaurant: {name}
            Cuisine: {cuisine}
            Concept: {concept}
            Price Guidelines: 
            - Appetizers ${app_min}-${app_max}
            - Mains ${main_min}-${main_max}
            - Desserts ${dessert_min}-${dessert_max}

            Return a JSON object with EXACTLY this structure:
            {{
                "appetizers": [
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": ["vegetarian/vegan/gluten-free if applicable"]}},
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}},
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}}
                ],
                "mains": [
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}},
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}},
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}},
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}}
                ],
                "desserts": [
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}},
                    {{"name": "Dish name", "description": "Enticing 10-15 word description", "price": "$XX", "dietary": []}}
                ],
                "beverages": [
                    {{"name": "Drink name", "description": "Brief description", "price": "$XX", "dietary": []}},
                    {{"name": "Drink name", "description": "Brief description", "price": "$XX", "dietary": []}}
                ]
            }}

            Make all items authentic to {cuisine} cuisine. Return ONLY valid JSON."""
        )

        # Now invoke with all the variables properly defined
        menu_chain = menu_prompt | self.llm | self.json_parser
        menu = menu_chain.invoke({
            'name': restaurant_name,
            'cuisine': cuisine,
            'concept': concept,
            'app_min': base,
            'app_max': base * 2,
            'main_min': base * 3,
            'main_max': base * 5,
            'dessert_min': base,
            'dessert_max': base * 2
        })

        return menu

    def generate_full_restaurant(self, cuisine, style="Casual Dining", price_range="$$"):
        """Generate everything: concept + detailed menu."""

        # Generate concept first
        concept = self.generate_complete_concept(cuisine, style, price_range)

        # Then generate menu based on concept
        menu = self.generate_detailed_menu(
            concept['name'],
            cuisine,
            concept['concept'],
            price_range
        )

        # Combine everything
        return {
            'concept': concept,
            'menu': menu,
            'metadata': {
                'cuisine': cuisine,
                'style': style,
                'price_range': price_range
            }
        }


# Keep backward compatibility
def generate_restaurant_name_items(cuisine):
    """Legacy function for compatibility."""
    generator = RestaurantConceptGenerator()
    result = generator.generate_full_restaurant(cuisine)

    # Extract simple format for old code
    menu_items = []
    for item in result['menu']['mains'][:7]:
        menu_items.append(item['name'])

    return {
        'restaurant_name': result['concept']['name'],
        'menu_items': ", ".join(menu_items)
    }


def generate_restaurant_name_items_parallel(cuisine):
    """Legacy function for compatibility with parallel generation."""
    generator = RestaurantConceptGenerator()
    result = generator.generate_full_restaurant(cuisine)

    # Extract with tagline for compatibility
    menu_items = []
    for item in result['menu']['mains'][:7]:
        menu_items.append(item['name'])

    return {
        'restaurant_name': result['concept']['name'],
        'tagline': result['concept']['tagline'],
        'menu_items': ", ".join(menu_items)
    }


if __name__ == "__main__":
    # Test the new comprehensive generator
    generator = RestaurantConceptGenerator()

    print("Testing comprehensive concept generation...")
    print("=" * 50)

    result = generator.generate_full_restaurant("Japanese", "Fine Dining", "$$$")

    print(f"\n🍽️ Restaurant: {result['concept']['name']}")
    print(f"📝 Tagline: {result['concept']['tagline']}")
    print(f"💡 Concept: {result['concept']['concept']}")
    print(f"\n🎯 Unique Selling Points:")
    for usp in result['concept']['unique_selling_points']:
        print(f"  • {usp}")

    print(f"\n📋 Sample Menu Items:")
    if result['menu'].get('mains'):
        for item in result['menu']['mains'][:2]:  # Show first 2 items
            print(f"  {item['name']} - {item['price']}")
            print(f"    {item['description']}")
            if item.get('dietary'):
                print(f"    Dietary: {', '.join(item['dietary'])}")


# def generate_restaurant_name_items(cuisine):
#     """
#     Generates restaurant name and menu items using LCEL pipeline.
#     Uses modern Langchain Expression Language instead of depreciated chains.
#     """
#     name_prompt = PromptTemplate(
#         input_variables = ['cuisine'],
#         template = """I want to open a restaurant for {cuisine} food.
#         Suggest a fancy, unique name for this restaurant.
#         Only provide the name, nothing else.
#         No preamble"""
#     )
#
#     menu_prompt = PromptTemplate(
#         input_variables = ['restaurant_name'],
#         template = """For a restaurant called '{restaurant_name}', suggest 7 menu items.
#         Make them sound authentic and appetizing.
#         Return them in this EXACT format with commas between items:
#         Dish One Name, Dish Two Name, Dish Three Name, Dish Four Name, Dish Five Name, Dish Six Name, Dish Seven Name
#         NO NUMBERS, NO LINE BREAKS, NO PREAMBLE, ONLY COMMA-SEPARATED.
#         """
#     )
#
#     name_chain = name_prompt | llm | StrOutputParser()
#     menu_chain = menu_prompt | llm | StrOutputParser()
#
#     restaurant_name = name_chain.invoke({"cuisine": cuisine})
#     menu_items = menu_chain.invoke({"restaurant_name": restaurant_name.strip()})
#
#     import re
#     menu_items = re.sub(r'\d+\.\s*', '', menu_items)
#
#     return{
#         'restaurant_name': restaurant_name.strip(),
#         'menu_items': menu_items.strip()
#     }

# def generate_restaurant_name_items_parallel(cuisine):
#     """ Advanced version: Generates name, tagline and menu items in parallel"""
#     name_chain = (
#         PromptTemplate.from_template(
#             "Create a unique {cuisine} restaurant name. No preamble. Only the name:"
#         )
#         | llm
#         | StrOutputParser()
#     )
#
#     restaurant_name = name_chain.invoke({"cuisine": cuisine})
#
#     tagline_chain = (
#             PromptTemplate.from_template(
#                 "Create a catchy tagline for '{name}' restaurant. No preamble. Only the tagline:"
#             )
#             | llm
#             | StrOutputParser()
#     )
#
#     menu_chain = (
#             PromptTemplate.from_template(
#                 """List 7 menu items for '{name}' restaurant.
#                 Format: Dish One, Dish Two, Dish Three, Dish Four, Dish Five, Dish Six, Dish Seven.
#                 use COMMAS only. NO preamble. NO numbers, NO line breaks."""
#             )
#             | llm
#             | StrOutputParser()
#     )
#
#     parallel_chain = RunnableParallel(
#         tagline = tagline_chain,
#         menu_items= menu_chain
#     )
#
#     results = parallel_chain.invoke({"name": restaurant_name})
#
#     import re
#     menu_items = re.sub(r'\d+\.\s*', '', results['menu_items'])
#
#     return {
#         'restaurant_name': restaurant_name.strip(),
#         'tagline': results['tagline'].strip(),
#         'menu_items': results['menu_items'].strip()
#     }


