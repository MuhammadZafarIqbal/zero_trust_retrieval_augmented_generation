from langchain_core.documents import Document

def get_raw_data(data_folder, file_names, ):
    raw_documents = []
    for file_name in file_names:
        file_path = data_folder / file_name
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                # Try to extract AccessLevel
                access_level_line = next(
                    (line for line in content.splitlines() if "AccessLevel:" in line),
                    None
                )
                access_level = access_level_line.split(":")[1].strip() if access_level_line else "PUBLIC"

                # Wrap content as a LangChain Document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_name,
                        "access_level": access_level
                    }
                )
                raw_documents.append(doc)
    return raw_documents