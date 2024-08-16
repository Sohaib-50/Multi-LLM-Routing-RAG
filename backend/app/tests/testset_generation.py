import os
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context

script_dir = os.path.dirname(os.path.abspath(__file__))
loader = TextLoader(file_path=os.path.join(script_dir, 'datasets', 'Meezan-HR.txt'))    
documents = loader.load()

generator_llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
critic_llm = ChatOpenAI(model="gpt-4o-2024-05-13")
embeddings = OpenAIEmbeddings()

generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

testset = generator.generate_with_langchain_docs(documents, test_size=10, distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25})
df = testset.to_pandas()
print(df)

df.to_csv(os.path.join(script_dir, 'datasets', 'Meezan-HR-synthetic-testset.csv'), index=False)