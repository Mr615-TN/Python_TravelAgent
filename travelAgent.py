import os
from playwright.sync_api import sync_playwright
from openai import OpenAI

def travel_agent(city, checkin, checkout):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(
            f"https://www.booking.com/searchresults.html?ss={city}&checkin={checkin}&checkout={checkout}",
            wait_until="load",  # Corrected wait_until argument
            timeout=60000,
        )
        page.wait_for_selector('[data-testid="property-card"]')

        hotels = page.query_selector_all('[data-testid="property-card"]')
        hotels_data = []
        for card in hotels[:5]:  # Limit to the top 5 hotels
            title_element = card.query_selector('[data-testid="title"]')
            price_element = card.query_selector('[data-testid="price-and-discounted-price"]')
            rating_element = card.query_selector('[data-testid="review-score"]')

            hotels_data.append({
                "title": title_element.inner_text() if title_element else None,
                "price": price_element.inner_text() if price_element else None,
                "rating": rating_element.inner_text() if rating_element else None,
            })

        browser.close()

    print("\n🏨 Top Hotels:\n")
    for hotel in hotels_data:
        print(f"  Title: {hotel['title']}, Price: {hotel['price']}, Rating: {hotel['rating']}")

    prompt = f"Here are some hotels in {city}:\n" + "\n".join(
        [f"  Title: {h['title']}, Price: {h['price']}, Rating: {h['rating']}" for h in hotels_data]
    ) + "\nCreate a 3-day trip plan based on these."

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Use os.environ
    response = client.chat.completions.create(
        model="gpt-4",  # Or your preferred model
        messages=[{"role": "user", "content": prompt}],
    )

    print("\n📅 Itinerary:\n", response.choices[0].message.content)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python travel_agent.py <city> <checkin_YYYY-MM-DD> <checkout_YYYY-MM-DD>")
        sys.exit(1)

    city, checkin, checkout = sys.argv[1], sys.argv[2], sys.argv[3]
    travel_agent(city, checkin, checkout)

    print("\n✅ Done!")
