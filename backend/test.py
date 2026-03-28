from pinecone import ServerlessSpec

# Check if index already exists (it shouldn't if this is first time running the notebook)
if not pc.has_index(name=index_name):
    # If does not exist, create index
    pc.create_index(
        index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index_name="ticket-search"

# Instantiate the index client
index = pc.Index(name=index_name)
# View index stats
index.describe_index_stats()