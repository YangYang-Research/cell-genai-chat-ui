from enum import Enum
import base64
from helpers.config import FileConfig
from dataclasses import dataclass
from typing import Optional
from helpers.loog import logger

class FileProcessStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class FileMetadata:
    name: str
    type: str
    size: int
    bytes: bytes
    base64: Optional[str] = None
    content: Optional[str] = None
    status: FileProcessStatus = FileProcessStatus.PENDING
    error: Optional[str] = None

    @property
    def size_kb(self) -> float:
        """Return size in kilobytes."""
        return self.size / 1024
    
    @property
    def is_image(self) -> bool:
        """Check if the file is an image based on its MIME type."""
        return self.type.startswith("image/")
    
    @property
    def is_document(self) -> bool:
        """Check if the file is a document based on its MIME type."""
        document_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        return self.type in document_types
    
    @property
    def is_text(self) -> bool:
        """Check if the file is a text file based on its MIME type."""
        return self.type.startswith("text/")

class Utils:
    def __init__(self):
        self.file_conf = FileConfig()
    
    def process_multiple_files(self, files) -> list[FileMetadata]:
        """Process multiple uploaded files and return their metadata."""
        processed_files = []
        for file in files:
            processed_file = self.process_single_file(file)
            processed_files.append(processed_file)
        return processed_files
    
    def process_single_file(self, file) -> FileMetadata:
        """Process a single uploaded file and return its metadata."""
        try:
            file_content = file.read()
            if len(file_content) > self.file_conf.max_upload_size_mb * 1024 * 1024:
                return FileMetadata(
                    name=file.name,
                    type=file.type,
                    size=len(file_content),
                    bytes=b'',
                    base64=None,
                    status=FileProcessStatus.FAILED,
                    error="File size exceeds the maximum limit."
                )
            
            attachment = FileMetadata(
                name=file.name,
                type=file.type,
                size=len(file_content),
                bytes=file_content,
                status=FileProcessStatus.PROCESSING,
                error=None
            )
            
            if self.is_allow_image_file(file):
                attachment.base64 = base64.b64encode(file_content).decode('utf-8')
            elif self.is_allow_document_file(file):
                pass
            elif self.is_allow_text_file(file):
                attachment.content = file_content.decode('utf-8')
            else:
                return FileMetadata(
                    name=file.name,
                    type=file.type,
                    size=len(file_content),
                    bytes=b'',
                    status=FileProcessStatus.FAILED,
                    error="Unsupported file type."
                )
            
            attachment.status = FileProcessStatus.COMPLETED
            
            return attachment
        
        except Exception as e:
            logger.error(f"[FE-FILE_PROCESSING] Error processing file : {e}")
            return FileMetadata(
                name=file.name,
                type=file.type,
                size=0,
                content=b'',
                base64=None,
                status=FileProcessStatus.FAILED,
                error=str(e)
            )
        
    def is_allow_image_file(self, file) -> bool:
        return (file.type in ["image/png", "image/jpg", "image/jpeg"] and file.name.split('.')[-1].lower() in self.file_conf.allowed_file_types)
    
    def is_allow_document_file(self, file) -> bool:
        return (file.type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ] and file.name.split('.')[-1].lower() in self.file_conf.allowed_file_types)
    
    def is_allow_text_file(self, file) -> bool:
        return (file.type.startswith("text/") and file.name.split('.')[-1].lower() in self.file_conf.allowed_file_types)