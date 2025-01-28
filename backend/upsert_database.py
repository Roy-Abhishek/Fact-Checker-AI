from main import index, generate_embeddings
from tqdm import tqdm
import pandas as pd


if __name__=="__main__":
    df = pd.read_json("sample.jsonl", lines=True)

    # Keep only relevant columns (e.g., `paper_id`, `title`, `abstract`)
    df = df[['paper_id', 'title', 'abstract']].dropna()

    # Combine title and abstract for embedding
    df['content'] = "Title: " + df['title'] + "; Abstract: " + df['abstract']

    # Creating an embeddings column
    df['embedding'] = df['content'].apply(generate_embeddings)




    to_upsert = []

    for _, row in df.iterrows():
        item = dict()
        item["id"] = str(row["paper_id"])
        item["values"] = row['embedding']
        item["metadata"] = {"title": row["title"], "abstract": row["abstract"]}

        to_upsert.append(item)



    def upsert_to_index(batch_size):
        for i in tqdm(range(0, len(to_upsert), batch_size)):
            batch = to_upsert[i:i+batch_size]
            index.upsert(vectors=batch, namespace="namespace-1")


    upsert_to_index(50)
    print(index.describe_index_stats())