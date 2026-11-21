"""Initial schema with users, documents, chunks, conversations, and messages

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-20 20:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. Documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('processing_status', sa.String(length=30), nullable=False, default='uploaded'),
        sa.Column('page_count', sa.Integer(), nullable=False, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])
    op.create_index('ix_documents_status', 'documents', ['processing_status'])

    # 3. Document Chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('document_id', sa.CHAR(36), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('slide_number', sa.Integer(), nullable=True),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=False, default=0),
        sa.Column('metadata', sa.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_document_chunks_doc_id', 'document_chunks', ['document_id'])
    op.create_index('ix_document_chunks_user_id', 'document_chunks', ['user_id'])

    # 4. Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, default='New Conversation'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # 5. Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('conversation_id', sa.CHAR(36), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=False, default=[]),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_messages_conv_id', 'messages', ['conversation_id'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('users')
