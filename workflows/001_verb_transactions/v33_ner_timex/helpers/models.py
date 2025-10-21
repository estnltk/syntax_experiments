from sqlalchemy import MetaData, Integer, Text, Index
from sqlalchemy.orm import declarative_base, mapped_column

# Initialize metadata and base
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Ner(Base):
    __tablename__ = "ner"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    sentence_id = mapped_column(Integer, nullable=False, index=True)
    loc = mapped_column(Integer, nullable=False, index=True)
    ner_id = mapped_column(Integer, nullable=False)
    ner_tag = mapped_column(Text, nullable=False, index=True)
    ner_members = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_ner_sentence_loc", "sentence_id", "loc"),
        Index("ix_ner_sentence_loc_ner_nid", "sentence_id", "loc", ner_id, unique=True),
    )


class Timex(Base):
    __tablename__ = "timex"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    sentence_id = mapped_column(Integer, nullable=False, index=True)
    loc = mapped_column(Integer, nullable=False, index=True)
    timex_id = mapped_column(Integer, nullable=False)
    timex_type = mapped_column(Text, nullable=False, index=True)
    part_of_interval = mapped_column(Text, nullable=False, default="", index=True)
    timex_members = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_timex_sentence_loc", "sentence_id", "loc"),
        Index(
            "ix_timex_sentence_loc_tid", "sentence_id", "loc", "timex_id", unique=True
        ),
    )


class TransactionProcessed:
    __tablename__ = "tmp_transaction_processed"
    collection_id = mapped_column(Integer, nullable=False)
