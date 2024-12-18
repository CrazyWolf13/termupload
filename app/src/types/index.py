class FileUpload(BaseModel):
    filename: str
    content_type: str
    size: int