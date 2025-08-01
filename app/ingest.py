import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
from PyPDF2 import PdfReader
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import UploadFile

from .settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class DocumentIngestor:
    def __init__(self):
        # Inicializar ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Obtener o crear colección
        try:
            self.collection = self.chroma_client.get_collection(settings.RAG_COLLECTION)
        except:
            self.collection = self.chroma_client.create_collection(
                name=settings.RAG_COLLECTION,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Inicializar modelo de embeddings
        self.embedder = SentenceTransformer(settings.RAG_EMBEDDING_MODEL)
        
        # Inicializar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extrayendo texto de PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_csv(self, file_path: str) -> str:
        """Extrae texto de un archivo CSV"""
        try:
            df = pd.read_csv(file_path)
            # Convertir todas las columnas a string y concatenar
            text = ""
            for _, row in df.iterrows():
                row_text = " ".join([str(val) for val in row.values if pd.notna(val)])
                text += row_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extrayendo texto de CSV {file_path}: {e}")
            return ""
    
    def extract_text_from_md(self, file_path: str) -> str:
        """Extrae texto de un archivo Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error extrayendo texto de MD {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extrae texto según el tipo de archivo"""
        if file_type.lower() == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type.lower() == 'csv':
            return self.extract_text_from_csv(file_path)
        elif file_type.lower() in ['md', 'markdown']:
            return self.extract_text_from_md(file_path)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_type}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Divide el texto en fragmentos"""
        return self.text_splitter.split_text(text)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos"""
        return self.embedder.encode(texts).tolist()
    
    def ingest_file(self, file_path: str, source_name: str = None) -> Dict[str, Any]:
        """Ingesta un archivo completo"""
        try:
            # Determinar tipo de archivo
            file_extension = Path(file_path).suffix.lower().lstrip('.')
            
            # Extraer texto
            text = self.extract_text(file_path, file_extension)
            if not text.strip():
                return {"status": "error", "message": "No se pudo extraer texto del archivo"}
            
            # Dividir en fragmentos
            chunks = self.chunk_text(text)
            if not chunks:
                return {"status": "error", "message": "No se generaron fragmentos de texto"}
            
            # Generar embeddings
            embeddings = self.generate_embeddings(chunks)
            
            # Preparar metadatos
            source = source_name or Path(file_path).name
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{source}_{i}"
                metadata = {
                    "source": source,
                    "chunk_index": i,
                    "file_type": file_extension,
                    "chunk_size": len(chunk)
                }
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Agregar a ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Archivo {source} ingestado exitosamente: {len(chunks)} fragmentos")
            
            return {
                "status": "success",
                "message": f"Archivo ingestado exitosamente",
                "chunks_created": len(chunks),
                "source": source
            }
            
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def ingest_upload_file(self, upload_file: UploadFile) -> Dict[str, Any]:
        """Ingesta un archivo subido via FastAPI"""
        try:
            # Guardar archivo temporalmente
            temp_path = f"/tmp/{upload_file.filename}"
            
            with open(temp_path, "wb") as buffer:
                content = await upload_file.read()
                buffer.write(content)
            
            # Ingestar archivo
            result = self.ingest_file(temp_path, upload_file.filename)
            
            # Limpiar archivo temporal
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing upload file {upload_file.filename}: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la colección"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": settings.RAG_COLLECTION
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

# Instancia global
ingestor = DocumentIngestor()