from sqlalchemy import MetaData, Integer, Text, JSON, Index
from sqlalchemy.orm import declarative_base, mapped_column

# Initialize metadata and base
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class SyntaxMorphologyConflict(Base):
    __tablename__ = "syntax_morphology_conflicts"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_id = mapped_column(Integer, nullable=False)
    sentence_id = mapped_column(Integer, nullable=False)

    verb_loc = mapped_column(Integer, nullable=False)
    compound_loc = mapped_column(JSON, nullable=True)

    phrase_root_loc = mapped_column(Integer, nullable=False)
    verb_phrase_loc = mapped_column(JSON, nullable=False)
    phrase_case = mapped_column(Text)
    phrase_deprel = mapped_column(Text)

    verb = mapped_column(Text, nullable=False)
    verb_compound = mapped_column(Text)
    phrase = mapped_column(Text, nullable=False)
    phrase_root_lemma = mapped_column(Text, nullable=False)
    current_analysis = mapped_column(Text, nullable=False)
    current_case = mapped_column(Text, nullable=False)
    possible_cases = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_v_verb_verb_compound", "verb", "verb_compound"),
        Index("ix_phrase_case", "phrase_case"),
        Index("ix_phrase_deprel", "phrase_deprel"),
        Index("ix_phrase_root_lemma", "phrase_root_lemma"),
    )
