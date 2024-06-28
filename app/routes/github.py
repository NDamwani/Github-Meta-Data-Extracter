from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import os
import shutil
from git import Repo
from database import get_db
from models import Function
from schemas import RepoOperationSchema
from oauth2 import get_current_user
import logging

router = APIRouter(tags=['Github Operations'])

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

@router.post("/operate-repo")
async def operate_repo(repo_data: RepoOperationSchema, db: Session = Depends(get_db), user_id:int = Depends(get_current_user)):
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting repo operation for: %s", repo_data.repo_url)
    repo_url = repo_data.repo_url
    temp_dir = "temp_repo"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    try:
        repo = Repo.clone_from(repo_url, temp_dir)
        logging.info("Repo cloned successfully")
        for root, dirs, files in os.walk(temp_dir):
            logging.info("Walking in directory: %s", root)
            for file in files:
                if file.endswith(".py"):
                    try:
                        file_path = os.path.join(root, file)
                        logging.info("Processing Python file: %s", file_path)
                        with open(file_path, 'r') as f:
                            code = f.read()
                        tree = parser.parse(bytes(code, 'utf8'))
                        functions = parse_functions(tree, code, file_path)
                        store_functions_in_db(db, file, functions)
                        logging.info("Stored functions from file: %s", file_path)
                    except Exception as e:
                        logging.error("Error processing file %s: %s", file_path, str(e))
                        continue
        return {"message": "Repository processed"}
    finally:
        shutil.rmtree(temp_dir)
        logging.info("Cleaned up temporary directory")

def parse_functions(tree, code, file_path):
    logging.info("Inside parse function")
    functions = []

    def recurse_nodes(node):
        if node.type == 'function_definition':
            function_name = node.child_by_field_name('name').text.decode('utf8')
            start_byte, end_byte = node.start_byte, node.end_byte
            function_code = code[start_byte:end_byte]
            class_node = find_parent(node, 'class_definition')
            class_name = class_node.child_by_field_name('name').text.decode('utf8') if class_node else None
            functions.append({
                'file_name': os.path.basename(file_path),
                'function_name': function_name,
                'class_name': class_name,
                'code': function_code
            })

        for child in node.children:
            recurse_nodes(child)

    def find_parent(node, node_type):
        while node.parent:
            node = node.parent
            if node.type == node_type:
                return node
        return None

    recurse_nodes(tree.root_node)
    return functions


def store_functions_in_db(db, file_name, functions):
    try:
        for function in functions:
            new_function = Function(**function)
            db.add(new_function)
        db.commit()
        logging.info("Database commit successful for file: %s", file_name)
    except Exception as e:
        db.rollback()
        logging.error("Failed to commit functions to database: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
