import pandas as pd
import asyncio
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Ensure your OpenAI API key is set in your environment variables
# or replace os.getenv("OPENAI_API_KEY") with your key.
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

# Initialize the LLM
llm = ChatOpenAI(temperature=0.0, model_name="gpt-4o", openai_api_key=API_KEY)

# --- Prompts ---
# Prompt for classifying a batch of emails
review_prompt = PromptTemplate(
    input_variables=["emails"],
    template="""
    You are an expert email analyst. Please review the following batch of emails and classify each one into one of the following categories:
    - Sales Inquiry
    - Customer Support
    - Technical Issue
    - Spam
    - Other

    Here are the emails:
    {emails}

    Provide the classification for each email in the format:
    [Email X]: [Category]
    """
)

# Prompt for summarizing the reviews
summary_prompt = PromptTemplate(
    input_variables=["reviews"],
    template="""
    You are a reporting analyst. Please summarize the following email classifications.
    Provide a high-level overview of the topics discussed and their distribution.

    Classifications:
    {reviews}

    Your summary should be concise and informative.
    """
)

# --- Core Functions ---

async def process_batch(batch_content: str, chain: LLMChain) -> str:
    """Sends a single batch of emails to the LLM for review."""
    try:
        response = await chain.ainvoke({"emails": batch_content})
        return response['text']
    except Exception as e:
        return f"Error processing batch: {e}"

async def run_concurrent_reviews(email_batches: list, chain: LLMChain) -> list:
    """Processes email batches concurrently with a concurrency limit of 2."""
    semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent requests
    tasks = []

    async def task_wrapper(batch):
        async with semaphore:
            return await process_batch(batch, chain)

    for batch in email_batches:
        tasks.append(task_wrapper(batch))
    
    results = await asyncio.gather(*tasks)
    return results

def summarize_reviews(all_reviews: str, chain: LLMChain) -> str:
    """Summarizes all the generated LLM reviews."""
    try:
        summary = chain.run(all_reviews)
        return summary
    except Exception as e:
        return f"Error generating summary: {e}"

# --- Main Execution ---

async def main():
    start_time = time.time()

    # 1. Load the Excel file
    try:
        df = pd.read_excel("comments.xlsx")
    except FileNotFoundError:
        print("Error: 'comments.xlsx' not found. Please ensure the file is in the correct directory.")
        return

    # Ensure the 'comment' column exists
    if 'comment' not in df.columns:
        print("Error: 'comment' column not found in the Excel file.")
        return

    # 2. Add a unique Email ID to each comment
    df['email_id_comment'] = df.apply(lambda row: f"[Email {row.name + 1}]: {row['comment']}", axis=1)

    # 3. Concatenate every 100 emails
    batch_size = 100
    email_batches = [
        "\n".join(df['email_id_comment'][i:i + batch_size])
        for i in range(0, len(df), batch_size)
    ]

    print(f"Created {len(email_batches)} batches of approximately {batch_size} emails each.")

    # 4. Asynchronously send batches for review
    print("Sending email batches for classification...")
    review_chain = LLMChain(llm=llm, prompt=review_prompt)
    llm_reviews = await run_concurrent_reviews(email_batches, review_chain)

    # Add reviews to a new column (one review per batch)
    df['Review'] = pd.Series([review for review in llm_reviews for _ in range(batch_size)])

    # 5. Summarize all LLM reviews
    print("Generating final summary...")
    all_reviews_text = "\n".join(llm_reviews)
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
    final_summary = summarize_reviews(all_reviews_text, summary_chain)
    
    # Add the summary to a new column
    df['Summary'] = final_summary

    # 6. Save the results to a new Excel file
    output_filename = "classified_comments.xlsx"
    df.to_excel(output_filename, index=False)

    end_time = time.time()
    print(f"\nProcessing complete! Results saved to '{output_filename}'.")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    # To run the async main function
    asyncio.run(main())

