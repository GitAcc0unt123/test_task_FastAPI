from sqlalchemy import MetaData, String, Integer, Table, Column

metadata = MetaData()

frame_service_informations = Table(
    "frame_service_information",
    metadata,
    Column("video_file_name", String, primary_key=True),
    Column("frame_number", Integer, primary_key=True),
    Column("frame_file_path", String(), nullable=False),
)
