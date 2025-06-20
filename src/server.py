import math
import re

import emoji
from playwright.async_api import async_playwright, TimeoutError
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Google-Reviews")

@mcp.tool()
async def get_reviews(url: str, num_reviews: int = 20) -> str:
    """
    This tool scrapes reviews based on the Google Maps URL and number of reviews to summarize
    provided by the user. The function returns a list of reviews concatenated and formatted into a text string,
    each review contains the information of the reviewer username, the review date, the star rating and the
    review text itself.
    
    Args:
        url (str): Google Maps URL of the place to extract reviews from.
        num_reviews (int): Number of reviews the user wants to collect and summarize.
        If the user does not specify the number of reviews, the default should be 20.

    
    Returns:
        str: A formatted string containing the summarization instructions and a list of reviews within the number of reviews
             specified by the user (defaults to 20 if not specified).
    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        await page.wait_for_timeout(5000)

        def clean_text(text):
            # Remove emojis
            text = emoji.replace_emoji(text, '')

            # Remove extra whitespaces
            text = re.sub(r'\s+', ' ', text)
            return text

        reviews = []
        try:
            await page.wait_for_timeout(2500)

            # Clicking on the Reviews tab
            reviews_section = page.get_by_role('tab', name='Reviews')
            await reviews_section.click()
            await page.wait_for_timeout(3000)

            # Sort by Newest reviews
            sort_button = page.get_by_role('button', name='Sort')
            await sort_button.click()
            await page.locator('#action-menu > [data-index="1"]').click()
            await page.wait_for_timeout(3000)

            # Scroll to load reviews based on num_reviews
            if num_reviews > 10:
                for _ in range(math.ceil(num_reviews / 10) - 1):
                    await page.mouse.wheel(0, 10000)
                    await page.wait_for_timeout(2000)

            # Extracting review information
            review_elements = page.locator("div[class*='jJc9Ad']")
            elements = await review_elements.all()

            for element in elements[:num_reviews]:
                reviewer = await element.locator("div[class*='d4r55']").inner_text()
                rating = await element.locator("span[aria-label]").get_attribute("aria-label")
                date = await element.locator("span[class*='rsqaWe']").inner_text()
                review_locator = element.locator("span[class*='wiI7pd']")
                
                try:
                    review_text = await review_locator.inner_text(timeout=1000)
                except TimeoutError:
                    review_text = 'No review'

                reviews.append({
                    'Reviewer': clean_text(reviewer),
                    'Rating': rating,
                    'Date': date,
                    'Review': clean_text(review_text)
                })

            full_text = "\n\n".join([
                (
                    f"==REVIEW {i+1}==\nReviewer: {rev['Reviewer']}\nDate: {rev['Date']}\n"
                    f"Rating: {rev['Rating']}\nReview: {rev['Review']}"
                )
                for i, rev in enumerate(reviews)
            ])

            return (
                "Summarize these collected reviews. The summarization should highlight both the positive and "
                "negative aspects of the place based on the review details:\n" + full_text
            )
        
        except Exception as e:
            return f"Unexpected error occurred when collecting the reviews: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")