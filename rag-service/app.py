from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI components
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Load face recognition documentation
def create_knowledge_base():
    # Sample content about face registration
    docs = [
        "Users can register their face by taking photos using the webcam.",
        "Multiple photos can improve recognition accuracy.",
        "The system supports multi-face detection and recognition.",
        "Face embeddings are stored securely in the PostgreSQL database.",
        "Recognition results include confidence scores."
    ]
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.create_documents(docs)
    
    vectorstore = FAISS.from_documents(texts, embeddings)
    return vectorstore

vectorstore = create_knowledge_base()
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"success": False, "message": "Message required"}), 400
    
    user_message = data['message']
    
    try:
        result = qa_chain({"question": user_message})
        return jsonify({
            "success": True,
            "response": result['answer']
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5001)
