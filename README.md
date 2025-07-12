# Ramcharitmanas Chatbot

A simple chatbot application that answers questions about the Ramcharitmanas, the sacred Hindu epic written by Tulsidas. Built using modern AI technologies including LangChain, OpenAI, and Pinecone for intelligent document retrieval and response generation.

## Features

- **Intelligent Q&A**: Ask questions about Ramcharitmanas and get contextually accurate answers
- **Beautiful UI**: Streamlit interface with culturally authentic Sanskrit styling
- **Document Processing**: Automated ingestion of PDF documents using advanced text extraction
- **Vector Search**: Pinecone-powered semantic search for relevant content retrieval
- **Response Validation**: LangChain integration for coherent and accurate responses

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd ramcharitmanas-chatbot

# Install dependencies
uv sync

# Edit .env with your API keys
```

## Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

## Usage

### Web Interface (Recommended)

```bash
# Run the Streamlit app
streamlit run src/streamlit_app.py
```

Access the application at `http://localhost:8501`

### Command Line Interface

```bash
# Run the CLI version
python src/main.py
```

### Document Ingestion

To process new documents:

```bash
# Uncomment the ingestion line in main.py and run
python src/main.py
```



## Technologies Used

- **Python 3.12+**: Modern Python with type hints
- **LangChain**: LLM orchestration and document processing
- **OpenAI**: Language model for response generation
- **Pinecone**: Vector database for semantic search
- **Streamlit**: Web interface framework
- **uv**: Fast Python package installer and resolver

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Tulsidas for the original Ramcharitmanas text
- The open-source community for the excellent tools and libraries used