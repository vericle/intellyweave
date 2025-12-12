# Dataset Requirements for IntellyWeave Backend Tests

This document outlines all datasets required to run the backend tests successfully, along with their sources and download instructions.

## Overview

The backend tests in `/home/vero/IntellyWeave/backend/tests/requires_env/llm/` require various datasets to be loaded into Weaviate collections. Some datasets are automatically loaded by the tests themselves, while others need to be manually imported.

## Dataset Status

### ✅ Working Datasets (Automatically Loaded in Tests)

These datasets are loaded automatically when running the tests if they don't exist:

1. **Weather** - `load_dataset("weaviate/agents", "query-agent-weather")`
2. **Ecommerce** - `load_dataset("weaviate/agents", "query-agent-ecommerce")` 
3. **Brands** - `load_dataset("weaviate/agents", "query-agent-brands")`
4. **Financial_contracts** - `load_dataset("weaviate/agents", "query-agent-financial-contracts")`
5. **Diabetes** - `datasets.load_diabetes()` from scikit-learn

### ❌ Missing Datasets (Need Manual Import)

These datasets are expected by the tests but are not automatically loaded:

1. **Example_verba_github_issues**
2. **Example_verba_email_chains** 
3. **Example_verba_slack_conversations**
4. **Ml_wikipedia**
5. **Weaviate_blogs**
6. **Weaviate_documentation**
7. **Recipes** (for personalization agent examples)

## Dataset Sources and Download Instructions

### 1. HuggingFace Weaviate Agents Collection

**Source**: [https://huggingface.co/datasets/weaviate/agents](https://huggingface.co/datasets/weaviate/agents)

These datasets can be loaded using the HuggingFace `datasets` library:

```python
from datasets import load_dataset

# Weather dataset
weather_dataset = load_dataset("weaviate/agents", "query-agent-weather", split="train", streaming=True)

# E-commerce dataset
ecommerce_dataset = load_dataset("weaviate/agents", "query-agent-ecommerce", split="train", streaming=True)

# Brands dataset
brands_dataset = load_dataset("weaviate/agents", "query-agent-brands", split="train", streaming=True)

# Financial contracts dataset
financial_dataset = load_dataset("weaviate/agents", "query-agent-financial-contracts", split="train", streaming=True)

# Recipes dataset (for personalization agent)
recipes_dataset = load_dataset("weaviate/agents", "personalization-agent-recipes", split="train", streaming=True)

# Movies dataset (for personalization agent)
movies_dataset = load_dataset("weaviate/agents", "personalization-agent-movies", split="train", streaming=True)
```

### 2. Wikipedia Dataset

**Official Documentation**: [https://docs.weaviate.io/weaviate/tutorials/wikipedia](https://docs.weaviate.io/weaviate/tutorials/wikipedia)

**Download Instructions**:
1. Download the Simple English Wikipedia dataset (25,000 articles with OpenAI embeddings)
2. File: ~700MB ZIP, expands to ~1.7GB CSV
3. Contains columns: `id`, `url`, `title`, `text`, `content_vector` (1536-dimensional OpenAI embedding)

**Alternative Source**: [GitHub Repository](https://github.com/weaviate/semantic-search-through-wikipedia-with-weaviate)

### 3. Scikit-learn Datasets

**Diabetes Dataset** (Already working):
```python
from sklearn import datasets

data = datasets.load_diabetes()
X, Y = data.data, data.target
```

### 4. Verba Example Datasets

**Note**: No official example datasets are provided for Verba-specific data (GitHub issues, email chains, Slack conversations). These need to be created manually or use your own data.

**Alternatives**:
- Export your own GitHub issues using GitHub API with `GITHUB_TOKEN`
- Format email chains as `.txt` or `.pdf` files
- Export Slack conversations as JSON or text files

**Demo Repositories**:
- [DEMO-Verba-Unstructured](https://github.com/weaviate/DEMO-Verba-Unstructured) - PDF import examples
- [weaviate-verba-demo](https://github.com/dlt-hub/weaviate-verba-demo) - Zendesk ticket import (similar structure)

### 5. Weaviate Documentation and Blogs

These collections likely need to be created by:
1. Scraping or downloading Weaviate documentation from [https://docs.weaviate.io](https://docs.weaviate.io)
2. Collecting blog posts from [https://weaviate.io/blog](https://weaviate.io/blog)
3. Processing and importing into Weaviate collections

## Test Files Affected

The following test files depend on these datasets:

1. **test_generic_prompts.py**:
   - Requires: All Example_verba_* collections, Weather, Ml_wikipedia, Weaviate_blogs, Weaviate_documentation, Ecommerce, Brands, Financial_contracts
   
2. **test_complex_prompts.py**:
   - Requires: Weather, Weaviate_documentation, Weaviate_blogs

3. **test_docs_examples.py**:
   - Uses: Diabetes dataset (scikit-learn)

4. **test_advanced_save_load.py**, **test_general.py**: 
   - May use various datasets depending on specific test cases

## Recommendations

### For Immediate Testing

1. **Focus on tests with working datasets**: The Weather, Ecommerce, Brands, Financial_contracts, and Diabetes datasets are already functional.

2. **Skip tests for missing datasets**: Tests will skip automatically if collections don't exist (using `pytest.skip()`).

### For Complete Test Coverage

1. **Create mock Verba datasets**: Generate sample data mimicking GitHub issues, email chains, and Slack conversations.

2. **Download Wikipedia dataset**: Follow the official Weaviate tutorial to get the Wikipedia dataset.

3. **Scrape Weaviate content**: Create scripts to collect documentation and blog posts from Weaviate's official sites.

4. **Use HuggingFace datasets**: All datasets under `weaviate/agents` namespace are readily available.

## Loading Datasets Programmatically

Here's a template for loading all available HuggingFace datasets:

```python
import weaviate.classes.config as wvc
from datasets import load_dataset
from elysia.util.client import ClientManager
from elysia import preprocess

def load_all_available_datasets():
    client_manager = ClientManager()
    
    # Dataset configurations
    datasets_config = [
        {
            "name": "Weather",
            "hf_split": "query-agent-weather",
            "description": "Daily weather information",
            "properties": [
                wvc.Property(name="date", data_type=wvc.DataType.DATE),
                wvc.Property(name="humidity", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="precipitation", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="wind_speed", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="visibility", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="pressure", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="temperature", data_type=wvc.DataType.NUMBER)
            ]
        },
        # Add other dataset configurations...
    ]
    
    with client_manager.connect_to_client() as client:
        for config in datasets_config:
            if not client.collections.exists(config["name"]):
                # Create collection
                client.collections.create(
                    config["name"],
                    description=config["description"],
                    vector_config=wvc.Configure.Vectorizer.self_provided(),
                    properties=config["properties"]
                )
                
                # Load and import data
                dataset = load_dataset("weaviate/agents", config["hf_split"], split="train", streaming=True)
                collection = client.collections.get(config["name"])
                
                with collection.batch.dynamic() as batch:
                    for item in dataset:
                        batch.add_object(properties=item["properties"])
                
                # Preprocess for Elysia
                preprocess(config["name"])
                print(f"✅ Loaded {config['name']} dataset")
```

## Summary

- **Working**: Weather, Diabetes (via scikit-learn), Ecommerce, Brands, Financial_contracts
- **Missing**: Verba examples (GitHub/Email/Slack), ML Wikipedia, Weaviate docs/blogs
- **Solution**: Use HuggingFace datasets where available, create mock data for Verba examples, download Wikipedia dataset from official tutorial
- **Tests**: Will automatically skip if collections don't exist, preventing failures

This documentation should help identify which datasets need to be obtained to achieve full test coverage.