from dotenv import load_dotenv
import os
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

pinecone_token = os.getenv("PINECONE_API_KEY")
open_ai_token = os.getenv("OPEN_AI_API_KEY")

client = OpenAI(api_key=open_ai_token)
pc = Pinecone(api_key=pinecone_token)

index_name = "s2orc"
index = pc.Index(index_name)



def generate_embeddings(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def extract_claims(text):
    prompt = f"Extract factual claims from the following text:\n\n{text}\n\nClaims:"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that identifies factual claims from text."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def retrieve_studies(claim, top_k=3):
    result = index.query(vector=generate_embeddings(claim), top_k=top_k, namespace="namespace-1", include_metadata=True)
    studies = []
    for match in result['matches']:
        studies.append({
            "title": match['metadata'].get('title', 'Unknown Title'),
            "authors": match['metadata'].get('authors', 'Unknown Authors'),
            "year": match['metadata'].get('year', 'Unknown Year'),
            "source": match['metadata'].get('source', 'Unknown Source'),
            "text": match['metadata'].get('text', 'No additional text available.')
        })
    return studies

def analyze_credibility(claim, studies):
    studies_text = "\n\n".join(
        [f"Study {i+1}:\n"
         f"Title: {study['title']}\n"
         f"Authors: {study['authors']}\n"
         f"Year: {study['year']}\n"
         f"Source: {study['source']}\n"
         f"Summary: {study['text']}" for i, study in enumerate(studies)]
    )
    prompt = f"""
    Analyze the credibility of the following claim based on the studies provided. Reference the studies by their numbers (e.g., Study 1, Study 2) in your reasoning.
    
    Claim: {claim}
    
    Studies:
    {studies_text}
    
    Provide an analysis of whether the claim is credible.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an expert in credibility analysis."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def chatbot_pipeline(text):
    # Step 1: Extract claims
    claims = extract_claims(text)
    
    credibility_results = []
    
    for claim in claims.split("\n"):
        # Step 2: Retrieve relevant studies
        studies = retrieve_studies(claim)
        
        # Step 3: Analyze credibility with citations
        analysis = analyze_credibility(claim, studies)
        
        # Collect results
        credibility_results.append({
            "claim": claim,
            "analysis": analysis,
            "studies": studies
        })
    
    return credibility_results


def main_result(text):
    pipeline_result = chatbot_pipeline(text)
    result = ""

    for i, item in enumerate(pipeline_result):
        result += f"Claim" + item["claim"]
        result += "\n"
        result += f"Analysis:" + item["analysis"]
        result += "\n"
        result += "The following is a list of the studies referenced:"

        for j, study in enumerate(item["studies"]):
            result += f"    Title: {study['title']}."
            result += f"    Authors: {study['authors']}"
            result += f"    Year: {study['year']}"
            result += f"    Source: {study['source']}"
            result += f"    Summary: {study['text']}"

        result += "\n\n"

    return result



if __name__=="__main__":
    text = "Vaccines cause autism. Drinking coffee reduces the risk of heart disease."

    result = main_result(text)

    print(result)